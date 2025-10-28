import streamlit as st
from db_connection import run_query

st.set_page_config(page_title="View Feedback")
st.title("💬 View Subject Feedback")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view feedback.")
    st.stop()

subject_filter = st.selectbox("Filter by Subject", [
                              "All"] + [c["name"] for c in run_query("SELECT name FROM course", fetch=True)])

query = """
SELECT f.feedback_id, c.name AS subject, f.difficulty_level, f.real_world_relevance, 
       f.grading_pattern, f.resource_recommendations, f.suggestions, s.name AS student_name
FROM feedback f
LEFT JOIN course c ON f.course_id = c.course_id
LEFT JOIN student s ON f.student_id = s.student_id
"""
if subject_filter != "All":
    query += " WHERE c.name=%s"
    feedback_data = run_query(query, (subject_filter,), fetch=True)
else:
    feedback_data = run_query(query, fetch=True)

for fb in feedback_data:
    st.subheader(f"📘 {fb['subject']} — by {fb['student_name']}")
    st.write(f"Difficulty: {fb['difficulty_level']}")
    st.write(f"Relevance: {fb['real_world_relevance']}")
    st.write(f"Grading: {fb['grading_pattern']}")
    st.write(f"Resources: {fb['resource_recommendations']}")
    st.info(f"💬 {fb['suggestions']}")
    st.divider()
