import streamlit as st

st.title("Forms")

with st.form("student_form"):
    name = st.text_input("Student name")
    course = st.selectbox("Course", ["Python", "Machine Learning", "AI"])
    submitted = st.form_submit_button("Submit")

if submitted:
    st.write(f"{name} enrolled in {course}.")
