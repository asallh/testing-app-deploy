import streamlit as st
import os
import psycopg2
import time
import uuid
import logging
from databricks.sdk import WorkspaceClient

logger = logging.getLogger(__name__)


class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)


class Constants:
    _postgres_password = None
    _last_password_refresh = None
    _workspace_client = None
    _database_instance_name = None

    @classmethod
    def get_environment(cls):
        environment = os.getenv("ENVIRONMENT")
        return environment

    @classmethod
    def _refresh_token_if_needed(cls):
        current_time = time.time()

        if (
            cls._postgres_password is None
            or cls._last_password_refresh is None
            or (current_time - cls._last_password_refresh) > (50 * 60)
        ):

            try:
                if cls._workspace_client is None:
                    # Fix: Get client_secret from environment variable, not hardcoded string
                    client_id = os.getenv("DATABRICKS_CLIENT_ID")
                    client_secret = os.getenv("DATABRICKS_CLIENT_SECRET")

                    if not client_id or not client_secret:
                        raise MissingEnvironmentVariables("DATABRICKS_CLIENT_ID or DATABRICKS_CLIENT_SECRET")

                    cls._workspace_client = WorkspaceClient(
                        host=cls.get_lakebase_host(),
                        client_id=client_id,
                        client_secret=client_secret,
                    )

                if cls._database_instance_name is None:
                    cls._database_instance_name = os.getenv("PGDATABASE")
                    if not cls._database_instance_name:
                        raise MissingEnvironmentVariables("PGDATABASE")

                logger.info("Generating fresh PostgreSQL OAuth token")

                cred = cls._workspace_client.database.generate_database_credential(
                    instance_names=[cls._database_instance_name],
                )

                cls._postgres_password = cred.token
                cls._last_password_refresh = current_time
                logger.info("Token updated successfully")

                return cred

            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                raise

    @classmethod
    def get_database_token(cls, workspace_client, database_name):
        # Fix: Complete this method implementation
        try:
            cred = workspace_client.database.generate_database_credential(
                instance_names=[database_name],
            )
            return cred.token
        except Exception as e:
            logger.error(f"Failed to get database token: {e}")
            raise

    @classmethod
    def get_lakebase_host(cls):
        env = cls.get_environment()
        if env:
            return os.getenv("PGHOST")
        else:
            return st.secrets["PGHOST"]

    @classmethod
    def get_lakebase_port(cls):
        env = cls.get_environment()
        if env:
            return os.getenv("PGPORT")
        else:
            return st.secrets["PGPORT"]

    @classmethod
    def get_lakebase_username(cls):
        env = cls.get_environment()
        if env:
            return os.getenv("PGUSER")
        else:
            return st.secrets["PGUSER"]

    @classmethod
    def get_lakebase_database(cls):
        env = cls.get_environment()
        if env:
            return os.getenv("PGDATABASE")
        else:
            return st.secrets["PGDATABASE"]

    @classmethod
    def get_lakebase_password(cls):
        env = cls.get_environment()
        if env:
            cls._refresh_token_if_needed()
            return cls._postgres_password
        else:
            return st.secrets["PGPASSWORD"]

    @classmethod
    def get_database_credentials(cls):
        env = cls.get_environment()
        if env:
            credentials = {
                "host": os.getenv("PGHOST"),
                "dbname": os.getenv("PGDATABASE"),
                "user": os.getenv("PGUSER"),
                "port": os.getenv("PGPORT"),
                "sslmode": os.getenv("PGSSLMODE"),
                "application_name": os.getenv("PGAPPNAME"),
                "password": cls.get_lakebase_password(),
            }
        else:
            credentials = {
                "host": cls.get_lakebase_host(),
                "dbname": cls.get_lakebase_database(),
                "user": cls.get_lakebase_username(),
                "password": cls.get_lakebase_password(),
            }

        return psycopg2.connect(**credentials)
