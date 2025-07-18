import streamlit as st
import os
import psycopg2

class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)

class Constants:
    ENV = st.secrets.get("ENV", os.environ.get("ENV", "LOCAL")).upper()

    @classmethod
    def get_env(cls):
        return cls.ENV

    @classmethod
    def get_secrets(cls, key: str, required: bool = True):
        env_secrets = st.secrets.get(cls.ENV, {})

        if not env_secrets:
            raise MissingEnvironmentVariables(f"Secrets for environment '{cls.ENV}' not found")

        value = env_secrets.get(key)
        if value is None and required:
            raise MissingEnvironmentVariables(f"{key} not found in secrets for '{cls.ENV}'")
        return value

    @classmethod
    def get_database_credentials(cls):
        # Use secrets.toml for LOCAL, environment variable for DEV/PROD (Databricks)
        if cls.ENV == "LOCAL":
            return {
                "host": cls.get_secrets("HOST"),
                "dbname": cls.get_secrets("DBNAME"),
                "user": cls.get_secrets("USER"),
                "password": cls.get_secrets("TOKEN")
            }
        else:
            conn_str = os.environ.get("database")
            if not conn_str:
                raise MissingEnvironmentVariables("Environment variable 'database' not found (set via resource key)")
            return {"connection_string": conn_str}

    @classmethod
    def get_database_connection(cls):
        creds = cls.get_database_credentials()
        if cls.ENV == "LOCAL":
            return psycopg2.connect(**creds)
        else:
            return psycopg2.connect(creds["connection_string"])
