import pandas as pd
import streamlit as st

st.title("File Uploader")

file = st.file_uploader("Upload a CSV file", type="csv")

if file is not None:
    data = pd.read_csv(file)
    st.dataframe(data, use_container_width=True)
    st.write("Rows:", len(data))
    st.write("Columns:", list(data.columns))
