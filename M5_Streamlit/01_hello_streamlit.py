import streamlit as st

st.title("Hello, Streamlit!")
st.write("Build interactive apps with Python.")

name = st.text_input("Enter your name")

if st.button("Submit"):
    st.write(f"Hello, {name}!")
