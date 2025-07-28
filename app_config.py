import time
import streamlit as st
import os
import psycopg2
from databricks.sdk.core import Config
from databricks import sdk
import uuid


class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)

class Constants:
    
    @classmethod
    def get_environment(cls):
        environment = os.getenv("ENVIRONMENT")
        return environment

    @classmethod
    def get_lakebase_host(cls):
        env = cls.get_environment()
        if env:
            return os.getenv("PGHOST")
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
            return cls.get_oauth_token()
        else:
            return st.secrets["PGPASSWORD"]
        
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
        env = cls.get_environment()
        if env:
            credentials = {
                "host":os.getenv("PGHOST"),
                "dbname":os.getenv("PGDATABASE"),
                "user":os.getenv("PGUSER"),
                "password": cls.get_oauth_token(),
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
