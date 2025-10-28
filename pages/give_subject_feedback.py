import streamlit as st
from db_connection import run_query

st.set_page_config(page_title="Give Feedback")
st.title("📝 Give Subject Feedback")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to submit feedback.")
    st.stop()

courses = run_query("SELECT course_id, name FROM course", fetch=True)
course_map = {c["name"]: c["course_id"] for c in courses}
subject = st.selectbox("Select Subject", list(course_map.keys()))

difficulty = st.selectbox("Difficulty Level", ["Low", "Medium", "High"])
relevance = st.slider("Real-world Relevance", 1, 5, 4)
grading = st.slider("Grading Pattern Fairness", 1, 5, 3)
resources = st.text_area("Recommended Resources")
comments = st.text_area("Additional Comments")

if st.button("Submit Feedback"):
    run_query(
        "CALL AddFeedback(%s, %s, %s, %s, %s, %s, %s)",
        (difficulty, str(relevance), str(grading), resources,
         comments, course_map[subject], st.session_state.student_id)
    )
    st.success(
        f"Feedback for **{subject}** submitted by {st.session_state.username}.")
