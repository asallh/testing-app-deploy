import time
import streamlit as st
import os
import psycopg2
from databricks.sdk.core import Config
from databricks import sdk
import uuid

SECRETS_FILE_PATH = os.path.join(os.path.dirname(__file__), ".streamlit", "secrets.toml")
USE_SECRETS_FILE = os.path.exists(SECRETS_FILE_PATH)

class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)

class Constants:
    ENV = "AJAY-DEV"
    SECRETS = st.secrets.get(ENV, {}) if USE_SECRETS_FILE else {}

    @classmethod
    def get_environment(cls):
        environment = os.getenv("ENVIRONMENT")
        if USE_SECRETS_FILE and cls.ENV not in st.secrets:
            print(cls.ENV)
            raise MissingEnvironmentVariables(
                f"{cls.ENV} not found in secrets.toml"
            )
        return environment

    @classmethod
    def get_secrets(cls, env_var, required=True):
        if USE_SECRETS_FILE:
            env_var_value = cls.SECRETS.get(env_var)
        else:
            env_var_value = os.getenv(env_var)
        if env_var_value is None and required is True:
            raise MissingEnvironmentVariables(env_var)
        return env_var_value

    @classmethod
    def get_hello_world(cls):
        return cls.get_secrets("HelloWorld")

    @classmethod
    def get_lakebase_host(cls):
        return cls.get_secrets("PGHOST")

    @classmethod
    def get_lakebase_port(cls):
        return cls.get_secrets("PGPORT")

    @classmethod
    def get_lakebase_username(cls):
        return cls.get_secrets("PGUSER")

    @classmethod
    def get_lakebase_database(cls):
        return cls.get_secrets("PGDATABASE")

    @classmethod
    def get_lakebase_password(cls):
        if USE_SECRETS_FILE:
            return cls.get_secrets("PGPASSWORD")
        else:
            return cls.get_oauth_token()

    @classmethod
    def get_oauth_token(cls):
        # Caches token and refreshes every 15 minutes
        if not hasattr(cls, "_lakebase_password"):
            cls._lakebase_password = None
            cls._last_password_refresh = 0
        if cls._lakebase_password is None or time.time() - cls._last_password_refresh > 900:
            app_config = Config()
            workspace_client = sdk.WorkspaceClient()
            dbname = cls.get_lakebase_database()
            request_id = str(uuid.uuid4())  # Generate a unique request ID
            cred = workspace_client.database.generate_database_credential(
                instance_names=[dbname],
                request_id=request_id
            )
            cls._lakebase_password = cred.token
            cls._last_password_refresh = time.time()
        return cls._lakebase_password

    @classmethod
    def get_database_credentials(cls):
        credentials = {
            "host": cls.get_lakebase_host(),
            "dbname": cls.get_lakebase_database(),
            "user": cls.get_lakebase_username(),
            "password": cls.get_lakebase_password(),
        }
        if not USE_SECRETS_FILE:
            credentials["port"] = os.getenv("PGPORT")
            credentials["sslmode"] = os.getenv("PGSSLMODE")
            credentials["application_name"] = os.getenv("PGAPPNAME")
        return psycopg2.connect(**credentials)

if __name__ == "__main__":
    print(Constants.get_hello_world())
