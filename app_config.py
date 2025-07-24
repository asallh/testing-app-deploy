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
        credentials =  {
            "host": st.secrets["HOST"],
            "dbname": st.secrets["DBNAME"],
            "user": st.secrets["USER"],
            "password": st.secrets["TOKEN"],
        }
        return psycopg2.connect(**credentials)
