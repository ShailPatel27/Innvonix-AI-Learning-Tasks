import streamlit as st

st.title("Layouts")

with st.sidebar:
    st.header("Sidebar")
    page_color = st.selectbox("Choose a color", ["Blue", "Green", "Orange"])

left, right = st.columns(2)

with left:
    st.subheader("Column 1")
    st.write("Content can be arranged in columns.")

with right:
    st.subheader("Column 2")
    st.write(f"Selected color: {page_color}")

with st.expander("More information"):
    st.write("Expanders hide content until they are opened.")
