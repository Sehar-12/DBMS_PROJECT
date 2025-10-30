import streamlit as st
from db_connection import run_query

st.set_page_config(page_title="View Feedback")
st.title("💬 View Subject Feedback")

# ---------- LOGIN CHECK ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view feedback.")
    st.stop()

# ---------- SUBJECT FILTER ----------
subjects = run_query("SELECT course_id, name FROM course", fetch=True)
subject_map = {c["name"]: c["course_id"] for c in subjects}
subject_filter = st.selectbox(
    "Filter by Subject", ["All"] + list(subject_map.keys()))

# ---------- BASE QUERY ----------
query = """
SELECT f.feedback_id, c.course_id, c.name AS subject, f.difficulty_level, f.real_world_relevance, 
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

# ---------- DISPLAY DATA ----------
if not feedback_data:
    st.info("No feedback available.")
else:
    # When a specific subject is selected → show its average difficulty
    if subject_filter != "All":
        avg_difficulty = run_query(
            "SELECT GetAverageFeedbackDifficulty(%s) AS avg_diff",
            (subject_map[subject_filter],),
            fetch=True
        )[0]["avg_diff"]

        if avg_difficulty is not None:
            difficulty_map = {1: "Low", 2: "Medium", 3: "High"}
            rounded = round(avg_difficulty, 2)
            label = difficulty_map.get(round(rounded), "Medium")
            st.markdown(
                f"<h4 style='color:#00BFFF;'>📊 Average Difficulty for {subject_filter}: "
                f"<b>{rounded} ({label})</b></h4>",
                unsafe_allow_html=True
            )
        else:
            st.info(f"No feedback yet for {subject_filter}.")

    st.divider()

    # Show each feedback
    for fb in feedback_data:
        st.subheader(f"📘 {fb['subject']} — by {fb['student_name']}")
        st.write(f"**Difficulty:** {fb['difficulty_level']}")
        st.write(f"**Relevance:** {fb['real_world_relevance']}")
        st.write(f"**Grading:** {fb['grading_pattern']}")
        st.write(f"**Resources:** {fb['resource_recommendations']}")
        st.info(f"💬 {fb['suggestions']}")
        st.divider()
