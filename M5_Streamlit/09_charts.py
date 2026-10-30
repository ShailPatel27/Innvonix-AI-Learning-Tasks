import pandas as pd
import streamlit as st

st.title("Charts")

scores = pd.DataFrame(
    {
        "Student": ["Shail", "Meet", "Raj", "Soham"],
        "Python": [88, 92, 85, 78],
        "Math": [90, 84, 91, 87],
    }
)

st.bar_chart(scores, x="Student", y=["Python", "Math"])
