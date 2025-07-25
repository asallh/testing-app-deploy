import streamlit as st
import os
import psycopg2


class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)

class Constants:
    # --- Databricks OAuth token for Lakebase (psycopg2) ---
    _lakebase_password = None
    _last_password_refresh = 0
    _workspace_client = None

    @classmethod
    def _get_workspace_client(cls):
        if cls._workspace_client is None:
            try:
                from databricks import sdk
                from databricks.sdk.core import Config
                app_config = Config()
                cls._workspace_client = sdk.WorkspaceClient()
                cls._lakebase_username = app_config.client_id
            except Exception as e:
                raise MissingEnvironmentVariables(f"Databricks SDK not configured: {e}")
        return cls._workspace_client

    @classmethod
    def get_lakebase_token(cls):
        import time
        dbname = cls.get_lakebase_database()
        if cls._lakebase_password is None or time.time() - cls._last_password_refresh > 900:
            client = cls._get_workspace_client()
            cred = client.database.generate_database_credential(instance_names=[dbname])
            cls._lakebase_password = cred.token
            cls._last_password_refresh = time.time()
        return cls._lakebase_password

    @classmethod
    def get_lakebase_psycopg2_connection(cls):
        """
        Returns a psycopg2 connection to Lakebase using a fresh Databricks OAuth token as password.
        """
        import psycopg2
        password = cls.get_lakebase_token()
        conn = psycopg2.connect(
            host=cls.get_lakebase_host(),
            port=cls.get_lakebase_port(),
            dbname=cls.get_lakebase_database(),
            user=cls.get_lakebase_username(),
            password=password,
            sslmode="require"
        )
        return conn

    @classmethod
    def get_environment(cls):
        environment = os.getenv("ENVIRONMENT")
        return environment

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
            return os.getenv("PGPASSWORD")
        else:
            return st.secrets["PGPASSWORD"]


    @classmethod
    def get_database_credentials(cls):
        env = cls.get_environment()
        if env:
            credentials = {
                "host":os.getenv("PGHOST"),
                "dbname":os.getenv("PGDATABASE"),
                "user":os.getenv("PGUSER"),
                "port":os.getenv("PGPORT"),
                "sslmode":os.getenv("PGSSLMODE"),
                "application_name":os.getenv("PGAPPNAME"),
            }
        else: 
            credentials = {
                "host": cls.get_lakebase_host(),
                "dbname": cls.get_lakebase_database(),
                "user": cls.get_lakebase_username(),
                "password": cls.get_lakebase_password(),
            }

        return psycopg2.connect(**credentials)
