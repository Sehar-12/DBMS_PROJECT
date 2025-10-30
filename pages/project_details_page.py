import streamlit as st
import warnings
from db_connection import get_connection

warnings.filterwarnings(
    "ignore",
    message=".*stored_results.*will be added in a future release.*",
    category=DeprecationWarning
)

st.set_page_config(page_title="Project Details")
st.title("🔍 Project Details")

# ---------- AUTH CHECK ----------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view project details.")
    st.stop()

project_id = st.session_state.get("selected_project_id")

if not project_id:
    st.error("No project selected. Please go back and choose one.")
    st.stop()

# ---------- FETCH PROJECT DETAILS ----------
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

# ---------- DISPLAY PROJECT INFO ----------
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

    # ---------- COMMENTS SECTION ----------
    st.subheader("💬 Comments")

    if not comments:
        st.info("No comments yet.")

    for idx, c in enumerate(comments):
        comment_id = c.get("comment_id", idx)  # fallback if ID missing
        author = c["commented_by"]
        content = c["content"]
        date = c["posted_date"]

        # Comment box styling
        st.markdown(
            f"<div style='background-color:#0f2537;padding:10px;border-radius:8px;margin-bottom:8px;'>"
            f"<b style='color:#00BFFF;'>{author}</b> "
            f"(<span style='color:gray;'>{date}</span>): "
            f"<span style='color:white;'>{content}</span>"
            f"</div>",
            unsafe_allow_html=True
        )

        # Show edit/delete buttons only for the comment author
        if author == st.session_state.username:
            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("✏️ Edit", key=f"edit_{comment_id}"):
                    st.session_state["edit_mode"] = comment_id

            with col2:
                if st.button("🗑️ Delete", key=f"delete_{comment_id}"):
                    try:
                        conn = get_connection()
                        cursor = conn.cursor()
                        cursor.callproc("DeleteComment", [comment_id])
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.warning("🗑️ Comment deleted successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Database error: {e}")

        # If the user clicked edit on this comment
        if st.session_state.get("edit_mode") == comment_id:
            edited_text = st.text_area(
                "Edit your comment:",
                value=content,
                key=f"edit_text_{comment_id}"
            )
            col3, col4 = st.columns([1, 1])
            with col3:
                if st.button("💾 Save Changes", key=f"save_{comment_id}"):
                    if edited_text.strip():
                        try:
                            conn = get_connection()
                            cursor = conn.cursor()
                            cursor.callproc("UpdateComment", [
                                            comment_id, edited_text])
                            conn.commit()
                            cursor.close()
                            conn.close()
                            st.success("✅ Comment updated successfully!")
                            del st.session_state["edit_mode"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"Database error: {e}")
                    else:
                        st.warning("Comment cannot be empty.")
            with col4:
                if st.button("❌ Cancel", key=f"cancel_{comment_id}"):
                    del st.session_state["edit_mode"]
                    st.rerun()

    st.divider()

    # ---------- ADD COMMENT ----------
    st.subheader("✍️ Add a Comment")
    new_comment = st.text_area(
        "Write your comment here...", key="new_comment_input")

    if st.button("Post Comment"):
        if new_comment.strip():
            student_id = st.session_state.get("student_id")
            if not student_id:
                st.error(
                    "Your student ID is missing. Please log out and log back in.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor()
                    cursor.callproc(
                        "AddComment", [new_comment, student_id, project_id])
                    conn.commit()
                    cursor.close()
                    conn.close()
                    st.success("✅ Comment added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Database error: {e}")
        else:
            st.warning("Please enter a comment before posting.")

else:
    st.error(f"No project found in the database for ID: {project_id}")
