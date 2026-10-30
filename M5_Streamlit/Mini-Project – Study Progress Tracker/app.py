from datetime import date

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Study Progress Tracker", layout="wide")

st.title("Study Progress Tracker")
st.write("Log your study sessions and see how your time adds up.")

columns = ["Date", "Subject", "Topic", "Minutes", "Notes"]

if "study_sessions" not in st.session_state:
    st.session_state.study_sessions = pd.DataFrame(columns=columns)

add_tab, dashboard_tab, data_tab = st.tabs(
    ["Add a session", "Progress dashboard", "Import and export"]
)

with add_tab:
    st.subheader("Log a study session")

    with st.form("study_session_form"):
        session_date = st.date_input("Date", value=date.today())
        subject_choice = st.selectbox(
            "Subject",
            ["Python", "Machine Learning", "Deep Learning", "LangChain", "MCP", "LangGraph", "Other"],
        )
        subject = subject_choice
        if subject_choice == "Other":
            subject = st.text_input("Subject name")
        topic = st.text_input("What did you study?")
        minutes = st.number_input("Study time (minutes)", min_value=1, value=30, step=5)
        notes = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Add session")

    if submitted:
        if not subject.strip() or not topic.strip():
            st.error("Enter a subject and a topic before adding the session.")
        else:
            new_session = pd.DataFrame(
                [[session_date, subject.strip(), topic.strip(), int(minutes), notes.strip()]],
                columns=columns,
            )
            st.session_state.study_sessions = pd.concat(
                [st.session_state.study_sessions, new_session], ignore_index=True
            )
            st.success("Study session added.")

with dashboard_tab:
    st.subheader("Your progress")
    sessions = st.session_state.study_sessions

    if sessions.empty:
        st.info("No sessions yet. Add one or import a study log to get started.")
    else:
        total_minutes = int(sessions["Minutes"].sum())
        total_sessions = len(sessions)
        subjects_count = sessions["Subject"].nunique()

        metric1, metric2, metric3 = st.columns(3)
        metric1.metric("Study time", f"{total_minutes // 60} hr {total_minutes % 60} min")
        metric2.metric("Sessions", total_sessions)
        metric3.metric("Subjects", subjects_count)

        selected_subject = st.selectbox(
            "Filter by subject",
            ["All subjects", *sorted(sessions["Subject"].dropna().unique())],
        )
        filtered_sessions = sessions
        if selected_subject != "All subjects":
            filtered_sessions = sessions[sessions["Subject"] == selected_subject]

        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.write("Study time by subject")
            subject_minutes = (
                filtered_sessions.groupby("Subject", as_index=False)["Minutes"].sum()
            )
            st.bar_chart(subject_minutes, x="Subject", y="Minutes")

        with chart_col2:
            st.write("Study time by date")
            daily_minutes = filtered_sessions.groupby("Date", as_index=False)["Minutes"].sum()
            st.line_chart(daily_minutes, x="Date", y="Minutes")

        st.write("Session history")
        st.dataframe(filtered_sessions, hide_index=True, use_container_width=True)

with data_tab:
    st.subheader("Import a study log")
    st.write("Upload a CSV with Date, Subject, Topic, and Minutes columns. Notes are optional.")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if st.button("Import CSV", disabled=uploaded_file is None):
        try:
            imported_sessions = pd.read_csv(uploaded_file)
            imported_sessions.columns = [column.strip().title() for column in imported_sessions.columns]
            required_columns = {"Date", "Subject", "Topic", "Minutes"}
            missing_columns = required_columns - set(imported_sessions.columns)

            if missing_columns:
                st.error("Missing required columns: " + ", ".join(sorted(missing_columns)))
            else:
                imported_sessions["Date"] = pd.to_datetime(
                    imported_sessions["Date"], errors="coerce"
                ).dt.date
                imported_sessions["Minutes"] = pd.to_numeric(
                    imported_sessions["Minutes"], errors="coerce"
                )
                imported_sessions["Notes"] = imported_sessions.get("Notes", "")
                imported_sessions = imported_sessions[columns]
                imported_sessions = imported_sessions.dropna(
                    subset=["Date", "Subject", "Topic", "Minutes"]
                )
                imported_sessions = imported_sessions[imported_sessions["Minutes"] > 0]
                imported_sessions["Minutes"] = imported_sessions["Minutes"].astype(int)

                st.session_state.study_sessions = imported_sessions.reset_index(drop=True)
                st.success(f"Imported {len(imported_sessions)} valid sessions.")
        except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
            st.error(f"Could not read this CSV: {error}")

    st.subheader("Export your study log")
    sessions = st.session_state.study_sessions
    st.download_button(
        "Download CSV",
        data=sessions.to_csv(index=False).encode("utf-8"),
        file_name="study_log.csv",
        mime="text/csv",
        disabled=sessions.empty,
    )
