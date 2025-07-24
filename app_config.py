import streamlit as st
import os
import psycopg2


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
                "password": os.getenv("DATABRICKS_CLIENT_SECRET")
            }
        else: 
            credentials = {
                "host": cls.get_lakebase_host(),
                "dbname": cls.get_lakebase_database(),
                "user": cls.get_lakebase_username(),
                "password": cls.get_lakebase_password(),
            }

        return psycopg2.connect(**credentials)
