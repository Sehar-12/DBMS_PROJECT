import streamlit as st
from db_connection import run_query

st.set_page_config(page_title="View Projects")
st.title("📂 All Projects")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view projects.")
    st.stop()

search = st.text_input("🔍 Search Projects")

query = "SELECT p.project_id, p.title, p.domain, s.name AS uploaded_by FROM project p JOIN student s ON p.student_id = s.student_id"
if search:
    query += " WHERE p.title LIKE %s"
    projects = run_query(query, (f"%{search}%",), fetch=True)
else:
    projects = run_query(query, fetch=True)

for p in projects:
    st.subheader(p["title"])
    st.write(f"**Domain:** {p['domain']}")
    st.write(f"**Uploaded by:** {p['uploaded_by']}")
    st.page_link("pages/project_details_page.py",
                 label="View Details", icon="🔍")
    if p["uploaded_by"] == st.session_state.username:
        if st.button(f"🗑️ Delete {p['title']}"):
            run_query("CALL DeleteProject(%s)", (p["project_id"],))
            st.warning(f"Deleted '{p['title']}'")
    st.divider()
