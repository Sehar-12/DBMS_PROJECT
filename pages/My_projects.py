import streamlit as st
from db_connection import get_connection, run_query

st.set_page_config(page_title="My Projects", page_icon="📁")
st.title("📁 My Projects")

# ---------- Auth Check ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to access your projects.")
    st.stop()

student_id = st.session_state.get("student_id")

# ---------- Fetch Projects ----------
query = """
SELECT project_id, title, domain, abstract, implementation_steps,
       lessons_learned, results, uploaded_date
FROM project
WHERE student_id = %s
ORDER BY uploaded_date DESC
"""
projects = run_query(query, (student_id,), fetch=True)

if not projects:
    st.info("You haven't uploaded any projects yet.")
    st.stop()

# ---------- Project Selection ----------
selected_project_title = st.selectbox(
    "Select a project to view or edit:",
    [p["title"] for p in projects]
)
selected_project = next(p for p in projects if p["title"] == selected_project_title)

# ---------- Display Project Details ----------
st.subheader("📄 Project Details")
st.write(f"**Domain:** {selected_project['domain']}")
st.write(f"**Abstract:** {selected_project['abstract']}")
st.write(f"**Implementation Steps:** {selected_project['implementation_steps']}")
st.write(f"**Lessons Learned:** {selected_project['lessons_learned']}")
st.write(f"**Results:** {selected_project['results']}")
st.write(f"**Uploaded Date:** {selected_project['uploaded_date']}")

st.divider()

# ---------- Update Project Section ----------
st.subheader("✏️ Update Project Information")
with st.form(key="update_form"):
    new_title = st.text_input("Title", selected_project["title"])
    new_domain = st.text_input("Domain", selected_project["domain"])
    new_abstract = st.text_area("Abstract", selected_project["abstract"])
    new_steps = st.text_area("Implementation Steps", selected_project["implementation_steps"])
    new_lessons = st.text_area("Lessons Learned", selected_project["lessons_learned"])
    new_results = st.text_area("Results / Output Summary", selected_project["results"])
    
    update_btn = st.form_submit_button("💾 Update Project")

    if update_btn:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            update_query = """
                UPDATE project
                SET title=%s, domain=%s, abstract=%s, implementation_steps=%s,
                    lessons_learned=%s, results=%s
                WHERE project_id=%s AND student_id=%s
            """
            cursor.execute(update_query, (
                new_title, new_domain, new_abstract, new_steps,
                new_lessons, new_results, selected_project["project_id"], student_id
            ))
            conn.commit()
            cursor.close()
            conn.close()
            st.success("✅ Project updated successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"Error updating project: {e}")

st.divider()

# ---------- Delete Project ----------
st.subheader("🗑️ Delete Project")
st.warning("⚠️ Deleting a project is permanent and cannot be undone.")
if st.button(f"Delete '{selected_project['title']}'", type="primary"):
    try:
        run_query("CALL DeleteProject(%s)", (selected_project["project_id"],))
        st.success(f"🗑️ Project '{selected_project['title']}' deleted successfully.")
        st.rerun()
    except Exception as e:
        st.error(f"Error deleting project: {e}")
