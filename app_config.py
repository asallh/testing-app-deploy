import streamlit as st
import os
import psycopg2


class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)


class Constants:

    @classmethod
    def get_database_credentials(cls):
        try:
            credentials = {
                "host": st.secrets["HOST"],
                "dbname": st.secrets["DBNAME"],
                "user": st.secrets["USER"],
                "password": st.secrets["TOKEN"],
            }
        except (AttributeError, KeyError):
            credentials = {
                "host": os.environ.get("HOST"),
                "dbname": os.environ.get("DBNAME"),
                "user": os.environ.get("USER"),
                "password": os.environ.get("TOKEN"),
            }
            # Optionally, raise if any are missing
            for key, value in credentials.items():
                if value is None:
                    raise MissingEnvironmentVariables(key)
        return psycopg2.connect(**credentials)
