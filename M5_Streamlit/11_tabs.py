import streamlit as st

st.title("Tabs")

overview, details, example = st.tabs(["Overview", "Details", "Example"])

with overview:
    st.write("Tabs divide related content into separate views.")

with details:
    st.write("Each tab can contain text, widgets, tables, or charts.")

with example:
    number = st.number_input("Choose a number", value=5)
    st.write("Square:", number**2)
