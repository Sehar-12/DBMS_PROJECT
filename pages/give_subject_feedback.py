import streamlit as st
from db_connection import run_query

st.set_page_config(page_title="Give Feedback")
st.title("📝 Give Subject Feedback")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to submit feedback.")
    st.stop()

# Fetch existing courses
courses = run_query("SELECT course_id, name FROM course", fetch=True)
course_map = {c["name"]: c["course_id"] for c in courses}

# Input for subject
subject_input = st.text_input("Enter Subject Name")

# Check if subject exists
if subject_input not in course_map and subject_input != "":
    st.info("This is a new subject. Please fill additional course details:")
    course_type = st.selectbox("Course Type", ["Core", "Elective", "Other"])
    course_code = st.text_input("Course Code")
    credits = st.number_input("Credits", min_value=1, max_value=10, value=3)
    department = st.text_input("Department")

difficulty = st.selectbox("Difficulty Level", ["Low", "Medium", "High"])
relevance = st.slider("Real-world Relevance", 1, 5, 4)
grading = st.slider("Grading Pattern Fairness", 1, 5, 3)
resources = st.text_area("Recommended Resources")
comments = st.text_area("Additional Comments")

if st.button("Submit Feedback"):
    if not subject_input:
        st.error("Please enter a subject name.")
    else:
        # If subject exists, use its course_id
        if subject_input in course_map:
            course_id = course_map[subject_input]
        else:
            # Insert new course with all details
            run_query(
                "INSERT INTO course (name, type, code, credits, department) VALUES (%s, %s, %s, %s, %s)",
                (subject_input, course_type, course_code, credits, department)
            )
            # Retrieve new course_id
            course_id = run_query(
                "SELECT course_id FROM course WHERE name=%s",
                (subject_input,),
                fetch=True
            )[0]["course_id"]

        # Insert feedback
        run_query(
            "CALL AddFeedback(%s, %s, %s, %s, %s, %s, %s)",
            (difficulty, str(relevance), str(grading), resources,
             comments, course_id, st.session_state.student_id)
        )

        st.success(
            f"Feedback for **{subject_input}** submitted by {st.session_state.username}.")
