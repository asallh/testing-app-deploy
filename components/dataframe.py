import psycopg2
import pandas as pd
import streamlit as st

class DataViewer:
    """
    A component to connect to a PostgreSQL database configured in
    Streamlit's App resources and display data.
    """

    def __init__(self):
        """
        Initializes the DataViewer and establishes the database connection.
        """
        # The connection is now initialized using Streamlit's secrets
        self.conn = self.init_connection()

    # Use st.cache_resource to only run this function once and cache the result.
    # This prevents creating a new database connection on every app rerun, which is much more efficient.
    @st.cache_resource
    def init_connection(_self):
        """
        Initializes a connection to the PostgreSQL database using credentials
        stored in Streamlit's secrets management.
        The `_self` parameter is a convention for methods inside st.cache_resource.
        """
        try:
            # This is the key part. st.secrets["database"] will automatically
            # be populated with the connection parameters for the resource you
            # configured with the key "database" in the UI.
            # The ** operator unpacks the dictionary of credentials
            # into keyword arguments for the connect function.
            return psycopg2.connect(**st.secrets["database"])
        except Exception as e:
            st.error(f"Failed to connect to the database. Please ensure the 'database' resource is configured correctly. Error: {e}")
            return None

    def fetch_data(self, query):
        """
        Fetches data from the database using the provided SQL query.
        """
        if self.conn:
            try:
                # pandas uses the connection object to fetch the data.
                return pd.read_sql_query(query, self.conn)
            except Exception as e:
                st.error(f"Failed to execute query: {e}")
                return pd.DataFrame() # Return empty dataframe on error
        else:
            # This message will show if the initial connection failed.
            st.warning("Database connection not available.")
            return pd.DataFrame()

    def view_data(self):
        """
        A method to display data from a specific table.
        """
        st.header("My Dogs")
        query = "SELECT * FROM dogs.my_dogs"
        df = self.fetch_data(query)

        if not df.empty:
            st.dataframe(df)
        else:
            st.info("No data to display. This could be due to an empty table or a query error.")

# --- Example of how to use the class in your Streamlit app ---
# if __name__ == "__main__":
#     viewer = DataViewer()
#     viewer.view_data()

