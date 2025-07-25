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
        """Refresh token if it's older than 50 minutes"""
        current_time = time.time()

        if (
            cls._postgres_password is None
            or cls._last_password_refresh is None
            or (current_time - cls._last_password_refresh) > (50 * 60)
        ):

            try:
                if cls._workspace_client is None:
                    cls._workspace_client = WorkspaceClient(
                        host=cls.get_lakebase_host(),
                        client_id=os.getenv("DATABRICKS_CLIENT_ID"),
                        client_secret="DATABRICKS_CLIENT_SECRET",
                        auth_type="oauth-m2m",
                    )

                if cls._database_instance_name is None:
                    cls._database_instance_name = os.getenv("PGDATABASE")

                logger.info("Generating fresh PostgreSQL OAuth token")

                cred = cls._workspace_client.database.generate_database_credential(
                    request_id=str(uuid.uuid4()),
                    instance_names=[cls._database_instance_name],
                )

                cls._postgres_password = cred.token
                cls._last_password_refresh = current_time
                logger.info("Token updated successfully")

            except Exception as e:
                logger.error(f"Token refresh failed: {e}")
                raise

    @classmethod
    def get_database_token(workspace_client, database_name):
        pg_password = workspace_client.da

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
            return cls._postgres_password or os.getenv("PGPASSWORD")
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
