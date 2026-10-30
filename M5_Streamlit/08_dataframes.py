import pandas as pd
import streamlit as st

st.title("DataFrames")

students = pd.DataFrame(
    {
        "Name": ["Shail", "Meet", "Raj"],
        "Course": ["Python", "ML", "AI"],
        "Score": [88, 92, 85],
    }
)

st.dataframe(students, use_container_width=True)
st.write("Average score:", students["Score"].mean())
