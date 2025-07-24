import streamlit as st
import os
import psycopg2


class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)


def _get_secrets_credentials():
    try:
        return {
            "host": st.secrets["HOST"],
            "dbname": st.secrets["DBNAME"],
            "user": st.secrets["USER"],
            "password": st.secrets["TOKEN"],
        }
    except (AttributeError, KeyError, FileNotFoundError):
        return None


def _get_env_credentials():
    return {
        "host": os.environ.get("HOST"),
        "dbname": os.environ.get("DBNAME"),
        "user": os.environ.get("USER"),
        "password": os.environ.get("TOKEN"),
    }


def _validate_credentials(credentials):
    for key, value in credentials.items():
        if value is None:
            raise MissingEnvironmentVariables(key)


class Constants:

    @classmethod
    def get_database_credentials(cls):
        credentials = _get_secrets_credentials() or _get_env_credentials()
        _validate_credentials(credentials)
        return psycopg2.connect(**credentials)
