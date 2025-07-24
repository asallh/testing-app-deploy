import os
import psycopg2
import pandas as pd
import streamlit as st

from app_config import Constants


class DataViewer:

    def __init__(self):
        # self.conn = Constants.get_database_credentials()
        self.conn = psycopg2.connect(
            host=os.getenv("PGHOST"),
            dbname=os.getenv("PGDATABASE"),
            user=os.getenv("PGUSER"),
            sslmode=os.getenv("PGSSLMODE"),
        )
        

    def fetch_data(self, query):
        return pd.read_sql_query(query, self.conn)

    def view_data(self):
        query = "SELECT * FROM my_dogs.dogs"
        df = self.fetch_data(query)
        st.dataframe(df)
