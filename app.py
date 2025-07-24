import os
import streamlit as st
import time

from components.dataframe import DataViewer

# Set page config
st.set_page_config(page_title="🚀 My Awesome App", page_icon="🔥", layout="centered")

pages = {
    "Menu": [
        st.Page("views/homepage.py", title="Homepage"),
    ],
}

pg = st.navigation(pages)
pg.run()