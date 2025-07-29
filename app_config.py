import time
import streamlit as st
import os
import psycopg2
from databricks.sdk.core import Config
from databricks import sdk
import uuid

class MissingEnvironmentVariables(EnvironmentError):
    def __init__(self, env_var_name, environment_type="environment variable"):
        self.message = f"Required {environment_type} '{env_var_name}' not set."
        super().__init__(self.message)

class Constants:
    # Class variables to store the detected environment type and name
    is_local_dev = True
    current_environment_name = "AJAY-DEV"
    
    # Internal cache for the OAuth token
    _lakebase_password = None
    _last_password_refresh = 0

    @classmethod
    def initialize_environment(cls):
        """
        Initializes the environment settings.
        Checks if an 'ENVIRONMENT' environment variable is set.
        If not set, assumes local development and uses 'AJAY-DEV' as the environment name.
        If set, uses the value of 'ENVIRONMENT' as the environment name.
        """
        environment_from_env_var = os.getenv("ENVIRONMENT")
        
        if environment_from_env_var:
            cls.is_local_dev = False
            cls.current_environment_name = environment_from_env_var
            st.info(f"Detected deployed environment: {cls.current_environment_name}. Using environment variables for secrets.")
        else:
            cls.is_local_dev = True
            cls.current_environment_name = "AJAY-DEV" # Default for local development
            st.info(f"Detected local development environment: {cls.current_environment_name}. Using st.secrets for secrets.")
            
            # For local dev, ensure the section exists in secrets.toml
            if cls.current_environment_name not in st.secrets:
                raise MissingEnvironmentVariables(
                    f"[{cls.current_environment_name}]", environment_type="section in secrets.toml"
                )

    @classmethod
    def get_secret(cls, key, required=True):
        """
        Retrieves a secret. For local development, it fetches from st.secrets.
        For deployed environments, it fetches from os.getenv.
        """
        value = None
        if cls.is_local_dev:
            # Access secrets for the specific local environment
            local_secrets = st.secrets.get(cls.current_environment_name, {})
            value = local_secrets.get(key)
            if value is None and required:
                raise MissingEnvironmentVariables(key, environment_type=f"'{key}' under [{cls.current_environment_name}] in secrets.toml")
        else:
            value = os.getenv(key)
            if value is None and required:
                raise MissingEnvironmentVariables(key, environment_type="environment variable")
        return value

    @classmethod
    def get_oauth_token(cls):
        """
        Caches token and refreshes every 15 minutes.
        This method is specifically for retrieving the Databricks OAuth token
        when deployed and using environment variables.
        """
        if cls._lakebase_password is None or time.time() - cls._last_password_refresh > 900:
            st.info("Refreshing Databricks OAuth token...")
            try:
                # Ensure Databricks SDK is configured correctly (e.g., DATABRICKS_HOST, DATABRICKS_TOKEN/client credentials)
                # The SDK will pick up credentials from environment variables automatically.
                app_config = Config() # SDK will try to resolve credentials from env vars
                workspace_client = sdk.WorkspaceClient(config=app_config)
                
                # Get the database name (which is also the instance name for token generation)
                dbname = cls.get_secret("PGDATABASE")
                if not dbname:
                    raise MissingEnvironmentVariables("PGDATABASE", "environment variable")
                    
                request_id = str(uuid.uuid4())  # Generate a unique request ID
                
                # Using the correct method from the databricks SDK based on common patterns
                # You might need to adjust this if your Databricks setup uses a different
                # way to generate credentials for SQL Endpoints or databases.
                # Refer to Databricks SDK documentation for the exact method for generating database credentials.
                
                # Example for SQL endpoint token if using service principals:
                # You might need to authenticate your service principal and then
                # generate a token for SQL access. This often involves using a PAT
                # generated for the service principal, or leveraging instance profiles.
                
                # For simplicity and based on your original code, assuming `database.generate_database_credential`
                # is the correct method for your specific Databricks setup.
                cred = workspace_client.database.generate_database_credential(
                    instance_names=[dbname],
                    request_id=request_id
                )
                cls._lakebase_password = cred.token
                cls._last_password_refresh = time.time()
                st.success("Databricks OAuth token refreshed.")
            except Exception as e:
                st.error(f"Failed to generate Databricks OAuth token: {e}")
                raise
        return cls._lakebase_password
        
    @classmethod
    def get_database_credentials(cls):
        """
        Constructs and returns the database connection object.
        """
        st.info("Attempting to get database credentials...")
        if cls.is_local_dev:
            password = cls.get_secret("PGPASSWORD")
        else:
            # When deployed, use the OAuth token
            password = cls.get_oauth_token()

        credentials = {
            "host": cls.get_secret("PGHOST"),
            "dbname": cls.get_secret("PGDATABASE"),
            "user": cls.get_secret("PGUSER"),
            "password": password,
            "port": cls.get_secret("PGPORT", required=False), # Port might not always be required or set
            "sslmode": cls.get_secret("PGSSLMODE", required=False),
            "application_name": cls.get_secret("PGAPPNAME", required=False),
        }

        # Filter out None values from credentials before connecting
        credentials = {k: v for k, v in credentials.items() if v is not None}
        
        try:
            conn = psycopg2.connect(**credentials)
            st.success("Successfully connected to the database.")
            return conn
        except psycopg2.Error as e:
            st.error(f"Error connecting to database: {e}")
            raise


if __name__ == "__main__":
    print(Constants.get_hello_world())