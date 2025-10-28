import streamlit as st
from db_connection import run_query

st.set_page_config(page_title="Add Project")
st.title("➕ Add New Project")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to add projects.")
    st.stop()

title = st.text_input("Project Title")
domain = st.text_input("Domain (e.g., Web + AI, IoT, etc.)")
abstract = st.text_area("Abstract / Description")
steps = st.text_area("Implementation Steps")
results = st.text_area("Results / Output Summary")
lessons = st.text_area("Lessons Learned")

if st.button("Submit Project"):
    run_query(
        "CALL AddProject(%s, %s, %s, %s, %s, %s, %s)",
        (title, domain, abstract, steps, lessons,
         results, st.session_state.student_id)
    )
    st.success(f"✅ Project '{title}' uploaded by {st.session_state.username}!")
