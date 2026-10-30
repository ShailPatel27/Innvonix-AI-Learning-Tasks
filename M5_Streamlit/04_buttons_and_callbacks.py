import streamlit as st

st.title("Buttons and Callbacks")

if st.button("Show a message"):
    st.write("The button was clicked.")

color = st.selectbox("Choose a color", ["Red", "Green", "Blue"])

if st.button("Show selected color"):
    st.success(f"You selected {color}.")
