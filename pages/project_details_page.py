import streamlit as st
from db_connection import get_connection

st.set_page_config(page_title="Project Details")
st.title("🔍 Project Details")

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("Please login to view details.")
    st.stop()

project_id = st.number_input("Enter Project ID to view", min_value=1, step=1)

if st.button("Fetch Details"):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.callproc("GetProjectDetails", [project_id])

    result_sets = []

    # 🔹 Loop through all available result sets
    while True:
        if cursor.description:  # ✅ only fetch if a result set is present
            rows = cursor.fetchall()
            result_sets.append(rows)
        if not cursor.nextset():
            break

    cursor.close()
    conn.close()

    # 🔹 Safely unpack the results
    project_info = result_sets[0] if len(result_sets) > 0 else []
    tech_info = result_sets[1] if len(result_sets) > 1 else []
    comments = result_sets[2] if len(result_sets) > 2 else []

    if project_info:
        p = project_info[0]
        st.header(p["title"])
        st.write(f"**Domain:** {p['domain']}")
        st.write(f"**Abstract:** {p['abstract']}")
        st.write(f"**Implementation Steps:** {p['implementation_steps']}")
        st.write(f"**Results:** {p['results']}")
        st.write(f"**Lessons Learned:** {p['lessons_learned']}")
        st.write(
            f"**Uploaded by:** {p['student_name']} ({p['department']}, {p['batch_year']})")
        st.write(f"**Uploaded Date:** {p['uploaded_date']}")

        if tech_info:
            st.subheader("🧰 Technologies Used")
            for t in tech_info:
                st.write(
                    f"- {t['tech_name']} ({t['tech_type']}) — {t['usage_purpose']}")
        else:
            st.info("No technology data available for this project.")

        if comments:
            st.subheader("💬 Comments")
            for c in comments:
                st.info(
                    f"{c['commented_by']} ({c['posted_date']}): {c['content']}")
        else:
            st.info("No comments yet.")
    else:
        st.error("No project found with that ID.")
