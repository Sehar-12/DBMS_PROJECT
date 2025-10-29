import streamlit as st
import warnings
from db_connection import get_connection

# ✅ Suppress MySQL Connector stored_results() deprecation warning
warnings.filterwarnings(
    "ignore",
    message=".*stored_results.*will be added in a future release.*",
    category=DeprecationWarning
)

st.set_page_config(page_title="Project Details")
st.title("🔍 Project Details")

# ---------- Auth Check ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view project details.")
    st.stop()

# ---------- Get Project ID ----------
project_id = st.session_state.get("selected_project_id")

if not project_id:
    st.error("No project selected. Please go back and choose one.")
    st.stop()

st.info(f"Fetching details for Project ID: {project_id}")

# ---------- Database Query ----------
conn = get_connection()
cursor = conn.cursor(dictionary=True)

try:
    cursor.callproc("GetProjectDetails", [project_id])
    result_sets = [result.fetchall() for result in cursor.stored_results()]

    project_info = result_sets[0] if len(result_sets) > 0 else []
    tech_info = result_sets[1] if len(result_sets) > 1 else []
    comments = result_sets[2] if len(result_sets) > 2 else []

finally:
    cursor.close()
    conn.close()

# ---------- Display ----------
if project_info:
    p = project_info[0]
    st.header(p["title"])
    st.write(f"**Domain:** {p['domain']}")
    st.write(f"**Abstract:** {p['abstract']}")
    st.write(f"**Implementation Steps:** {p['implementation_steps']}")
    st.write(f"**Lessons Learned:** {p['lessons_learned']}")
    st.write(f"**Results:** {p['results']}")
    st.write(
        f"**Uploaded by:** {p['student_name']} ({p['department']}, {p['batch_year']})")
    st.write(f"**Uploaded Date:** {p['uploaded_date']}")

    st.subheader("🧰 Technologies Used")
    if tech_info:
        for t in tech_info:
            st.write(
                f"- {t['tech_name']} ({t['tech_type']}) — {t['usage_purpose']}")
    else:
        st.info("No technology data available for this project.")

    st.subheader("💬 Comments")
    if comments:
        for c in comments:
            st.info(f"{c['commented_by']} ({c['posted_date']}): {c['content']}")
    else:
        st.info("No comments yet.")

    # ---------- 🆕 ADD COMMENT SECTION ----------
    st.divider()
    st.subheader("✍️ Add a Comment")

    # Initialize control keys
    if "new_comment_input" not in st.session_state:
        st.session_state["new_comment_input"] = ""
    if "clear_new_comment" not in st.session_state:
        st.session_state["clear_new_comment"] = False

    # If a clear was requested in the previous run, clear before creating the widget
    if st.session_state.get("clear_new_comment"):
        st.session_state["new_comment_input"] = ""
        st.session_state["clear_new_comment"] = False

    # Create the widget (backed by session_state["new_comment_input"])
    new_comment = st.text_area(
        "Write your comment here...",
        key="new_comment_input"
    )

    if st.button("Post Comment"):
        if new_comment.strip():
            student_id = st.session_state.get("student_id")
            if not student_id:
                st.error(
                    "Your student ID is missing in session. Please log out and log back in.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.callproc(
                        "AddComment", [new_comment, student_id, project_id])
                    conn.commit()
                    cursor.close()
                    conn.close()

                    # Mark to clear the text area on the next run
                    st.session_state["clear_new_comment"] = True
                    st.success("✅ Comment added successfully!")
                    st.rerun()  # Refresh page to show updated comments
                except Exception as e:
                    st.error(f"Database error: {e}")
        else:
            st.warning("Please enter a comment before posting.")

else:
    st.error(f"No project found in the database for ID: {project_id}")
