import streamlit as st

st.title("Input Widgets")

name = st.text_input("Name")
age = st.number_input("Age", min_value=0, max_value=120, value=18)
language = st.selectbox("Choose a language", ["Python", "Java", "C++"])
level = st.slider("Experience level", 1, 10, 5)
likes_python = st.checkbox("I like Python")

st.write("Name:", name)
st.write("Age:", age)
st.write("Language:", language)
st.write("Experience:", level)
st.write("Likes Python:", likes_python)
