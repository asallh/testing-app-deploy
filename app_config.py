import streamlit as st
import os
import psycopg2
import urllib


class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name):
        self.message = f"Required environment variable {env_var_name} not set"
        super().__init__(self.message)


class Constants:
    try:
        ENV = st.secrets.get("ENV", "LOCAL").upper()
    except FileNotFoundError:
        ENV = os.environ.get("ENV", "LOCAL").upper()

    @classmethod
    def get_env(cls):
        return cls.ENV

    @classmethod
    def get_secrets(cls, key: str, required: bool = True):
        if cls.ENV == "LOCAL":
            try:
                env_secrets = st.secrets[cls.ENV]
            except (FileNotFoundError, KeyError):
                raise MissingEnvironmentVariables(
                    f"Secrets for environment '{cls.ENV}' not found"
                )

            value = env_secrets.get(key)
            if value is None and required:
                raise MissingEnvironmentVariables(
                    f"{key} not found in secrets for '{cls.ENV}'"
                )
            return value
        else:
            # Use environment variable in Databricks Apps
            value = os.environ.get(key)
            if value is None and required:
                raise MissingEnvironmentVariables(
                    f"Environment variable '{key}' not found"
                )
            return value

    @classmethod
    def get_database_credentials(cls):
        if cls.ENV == "LOCAL":
            return {
                "host": cls.get_secrets("HOST"),
                "dbname": cls.get_secrets("DBNAME"),
                "user": cls.get_secrets("USER"),
                "password": cls.get_secrets("TOKEN"),
            }
        else:
            conn_str = os.environ.get("database")
            if not conn_str:
                raise MissingEnvironmentVariables(
                    "Environment variable 'database' not found (set via resource key)"
                )

            import urllib.parse

            parsed = urllib.parse.urlparse(conn_str)
            return {
                "host": parsed.hostname,
                "dbname": parsed.path[1:],
                "user": parsed.username,
                "password": parsed.password,
                "port": parsed.port or 5432,
            }

    @classmethod
    def get_database_connection(cls):
        creds = cls.get_database_credentials()
        return psycopg2.connect(**creds)
