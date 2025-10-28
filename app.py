import streamlit as st
from datetime import datetime
from db_connection import run_query
import hashlib

# ---------- CONFIG ----------
st.set_page_config(page_title="Capstone Portal", page_icon="🎓", layout="wide")

# ---------- SESSION ----------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "student_id" not in st.session_state:
    st.session_state.student_id = None


# ---------- PASSWORD UTIL ----------
def hash_password(password):
    """Return hashed password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()


# ---------- LOGIN / SIGNUP ----------
def login_page():
    st.title("🔐 Login / Signup")
    tab1, tab2 = st.tabs(["Login", "Signup"])

    # --- LOGIN TAB ---
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login", key="login_button"):
            if not email or not password:
                st.warning("Please enter both email and password.")
                return

            data = run_query(
                "SELECT * FROM student WHERE email=%s AND password=%s",
                (email, hash_password(password)),
                fetch=True
            )
            if data:
                student = data[0]
                st.session_state.logged_in = True
                st.session_state.username = student["name"]
                st.session_state.student_id = student["student_id"]
                st.session_state.user_role = "student"
                st.success(f"Welcome {student['name']}!")
                st.rerun()
            else:
                st.error("Invalid credentials or user not registered.")

    # --- SIGNUP TAB ---
    with tab2:
        name = st.text_input("Full Name", key="signup_name")
        github = st.text_input("GitHub Profile (optional)", key="signup_github")
        batch = st.text_input("Batch Year (e.g., 2025)", key="signup_batch")
        dept = st.text_input("Department", key="signup_dept")
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Create Password", type="password", key="signup_pass")

        if st.button("Signup", key="signup_button"):
            if name and dept and email and password:
                hashed_pw = hash_password(password)
                run_query(
                    "INSERT INTO student (name, github_profile, batch_year, department, email, password) VALUES (%s,%s,%s,%s,%s,%s)",
                    (name, github, batch, dept, email, hashed_pw)
                )
                st.success("Account created! Please login.")
            else:
                st.error("All fields are required (except GitHub).")


# ---------- PROFILE ----------
def profile_section():
    """Display user profile on sidebar once logged in"""
    with st.sidebar:
        st.markdown("<h3 style='color:#2E8B57;'>👤 My Profile</h3>", unsafe_allow_html=True)
        st.write(f"**Name:** {st.session_state.username}")
        st.write(f"**Role:** {st.session_state.user_role.capitalize()}")
        st.write(f"**Email:** (hidden for privacy)")
        st.write(f"**Last Login:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.markdown("---")

        if st.button("Logout", key="logout_btn"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


# ---------- HOME ----------
def home_page():
    profile_section()

    st.title("🎓 Capstone Project & Feedback Portal")
    st.markdown("""
    Welcome to the **Centralized Capstone & Feedback Portal**  
    - Upload and explore student projects  
    - Share feedback on subjects  
    - Learn from others’ experiences  
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.page_link("pages/add_new_project.py", label="➕ Add New Project")
    with col2:
        st.page_link("pages/view_all_projects.py", label="📂 View All Projects")
    with col3:
        st.page_link("pages/give_subject_feedback.py", label="📝 Give Subject Feedback")

    st.page_link("pages/view_feedback.py", label="💬 View Feedback")

    st.divider()
    st.success(f"Logged in as {st.session_state.username} ({st.session_state.user_role})")


# ---------- ROUTER ----------
if not st.session_state.logged_in:
    login_page()
else:
    home_page()