import time

import streamlit as st

st.title("Caching")


@st.cache_data
def load_data():
    time.sleep(2)
    return {"Python": 10, "Machine Learning": 8, "AI": 6}


if st.button("Load course data"):
    data = load_data()
    st.write(data)
