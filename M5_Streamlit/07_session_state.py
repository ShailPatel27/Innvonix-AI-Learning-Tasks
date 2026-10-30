import streamlit as st

st.title("Session State")

if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Increase"):
    st.session_state.count += 1

if st.button("Reset"):
    st.session_state.count = 0

st.write("Count:", st.session_state.count)
