import streamlit as st
import os
import psycopg2


class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)

def _get_secrets_credentials():
    try:
        creds = {
            "host": st.secrets["PGHOST"],
            "dbname": st.secrets["PGDATABASE"],
            "user": st.secrets["PGUSER"],
            "password": st.secrets["PGPASSWORD"],
        }
        return creds
    except Exception:
        return None

def _get_env_credentials():
    return {
        "host": os.environ.get("PGHOST"),
        "dbname": os.environ.get("PGDATABASE"),
        "user": os.environ.get("PGUSER"),
        "password": os.environ.get("PGPASSWORD"),
        "port": os.environ.get("PGPORT", 5432),
        "sslmode": os.environ.get("PGSSLMODE", "prefer"),
        "application_name": os.environ.get("PGAPPNAME", "streamlit-app"),
    }

def _validate_credentials(credentials):
    required_keys = ["host", "dbname", "user", "password"]
    for key in required_keys:
        if not credentials.get(key):
            raise MissingEnvironmentVariables(key)


class Constants:

    @classmethod
    def get_database_credentials(cls):
        credentials = _get_secrets_credentials() or _get_env_credentials()
        _validate_credentials(credentials)
        return psycopg2.connect(**credentials)
