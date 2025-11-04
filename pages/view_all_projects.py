import streamlit as st
from db_connection import run_query

st.set_page_config(page_title="View Projects")
st.title("📂 All Projects")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view projects.")
    st.stop()

search = st.text_input("🔍 Search Projects")

# Include comment_count in query
query = """
SELECT 
    p.project_id,
    p.title,
    p.domain,
    s.name AS uploaded_by,
    -- Nested query to count comments dynamically
    (SELECT COUNT(*) 
     FROM comments c 
     WHERE c.project_id = p.project_id) AS comment_count
FROM project p
JOIN student s ON p.student_id = s.student_id

"""

if search:
    query += " WHERE p.title LIKE %s"
    projects = run_query(query, (f"%{search}%",), fetch=True)
else:
    projects = run_query(query, fetch=True)

for p in projects:
    st.subheader(p["title"])
    st.write(f"**Domain:** {p['domain']}")
    st.write(f"**Uploaded by:** {p['uploaded_by']}")
    # trigger-controlled
    st.write(f"💬 **Comments:** {p.get('comment_count', 0)}")

    # ✅ Button to view details
    if st.button(f"🔍 View Details - {p['title']}", key=f"view_{p['project_id']}"):
        st.session_state["selected_project_id"] = p["project_id"]
        st.switch_page("pages/project_details_page.py")

    # ✅ Delete Project (fires trg_project_delete)
    if p["uploaded_by"] == st.session_state.username:
        if st.button(f"🗑️ Delete {p['title']}", key=f"delete_{p['project_id']}"):
            run_query("CALL DeleteProject(%s)", (p["project_id"],))
            st.warning(f"Deleted '{p['title']}' — logged in audit table.")
    st.divider()
