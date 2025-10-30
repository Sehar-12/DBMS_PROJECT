import streamlit as st
from datetime import datetime
from db_connection import run_query
import hashlib

# ---------- CONFIG ----------
st.set_page_config(page_title="Capstone Portal", page_icon="🎓", layout="wide")
st.markdown("""
    <style>
        /* Hide Streamlit’s default page navigation */
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR STYLE ----------
st.markdown("""
    <style>
        [data-testid="stSidebarNav"]::before {
            content: "🎓 Capstone Portal";
            display: block;
            font-size: 1.6rem;
            font-weight: 700;
            color: #2563EB;
            padding: 1rem;
            text-align: center;
        }

        section[data-testid="stSidebar"] {
            background-color: #f8fafc;
            border-right: 2px solid #e5e7eb;
        }

        div[data-testid="stSidebarNav"] a {
            font-size: 1rem;
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            color: #374151;
        }

        div[data-testid="stSidebarNav"] a:hover {
            background-color: #e0e7ff;
            color: #1e3a8a;
        }
    </style>
""", unsafe_allow_html=True)

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
                "SELECT student_id, name, role FROM student WHERE email=%s AND password=%s",
                (email, hash_password(password)),
                fetch=True
            )

            if data:
                user = data[0]
                st.session_state.logged_in = True
                st.session_state.username = user["name"]
                st.session_state.student_id = user["student_id"]
                st.session_state.user_role = user["role"]
                st.success(f"Welcome {user['name']} ({user['role'].capitalize()})!")
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
        role = st.selectbox("Register As", ["student", "faculty"], key="signup_role")

        if st.button("Signup", key="signup_button"):
            if name and dept and email and password:
                hashed_pw = hash_password(password)
                run_query(
                    "INSERT INTO student (name, github_profile, batch_year, department, email, password, role) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                    (name, github, batch, dept, email, hashed_pw, role.lower())
                )
                st.success(f"✅ Account created successfully as {role.capitalize()}! Please login.")
            else:
                st.error("All fields are required (except GitHub).")

# ---------- PROFILE ----------
def profile_section():
    """Display user profile and custom sidebar"""
    with st.sidebar:
        st.markdown("### 📂 Navigation")

        if st.session_state.user_role == "student":
            st.page_link("Home.py", label="🏠 Home")
            st.page_link("pages/add_new_project.py", label="➕ Add Project")
            st.page_link("pages/My_projects.py", label="📁 My Projects")
            st.page_link("pages/give_subject_feedback.py", label="📝 Give Feedback")
            st.page_link("pages/view_all_projects.py", label="📚 View Projects")
            st.page_link("pages/view_feedback.py", label="💬 View Feedback")

        elif st.session_state.user_role == "faculty":
            st.page_link("Home.py", label="🏠 Home")
            st.page_link("pages/view_all_projects.py", label="📚 View Projects")
            st.page_link("pages/view_feedback.py", label="💬 View Feedback")

        # ---------- PROFILE CARD STYLING ----------
        st.markdown("""
            <style>
                .profile-card {
                    background-color: #f0fdf4;
                    padding: 1.3rem;
                    border-radius: 1rem;
                    margin-top: 1.5rem;
                    text-align: center;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }
                .profile-pic {
                    width: 120px;
                    height: 120px;
                    border-radius: 50%;
                    object-fit: cover;
                    border: 3px solid #22c55e;
                    margin-bottom: 0.6rem;
                    transition: all 0.3s ease;
                }
                .profile-pic:hover {
                    transform: scale(1.05);
                }
                .profile-name {
                    font-size: 1.1rem;
                    font-weight: 600;
                    color: #111827;
                    margin-top: 0.3rem;
                }
                .profile-role {
                    font-size: 0.9rem;
                    color: #6b7280;
                    margin-bottom: 0.7rem;
                }
                .small-text {
                    font-size: 0.85rem;
                    color: #374151;
                }
                .logout-btn button {
                    width: 100%;
                    background-color: #ef4444 !important;
                    color: white !important;
                    border-radius: 0.5rem;
                    border: none;
                }
                .logout-btn button:hover {
                    background-color: #dc2626 !important;
                }
            </style>
        """, unsafe_allow_html=True)

        # ---------- PROFILE CARD ----------
        st.markdown("<div class='profile-card'>", unsafe_allow_html=True)

        # --- Profile Picture Upload ---
        if "profile_pic" not in st.session_state:
            st.session_state.profile_pic = None

        uploaded_pic = st.file_uploader("📸 Upload Profile Picture", type=["png", "jpg", "jpeg"], label_visibility="collapsed")

        if uploaded_pic:
            st.session_state.profile_pic = uploaded_pic

        # Display image live without refresh
        if st.session_state.profile_pic:
            st.image(st.session_state.profile_pic, width=120)
        else:
            st.image("https://cdn-icons-png.flaticon.com/512/149/149071.png", width=120)

        st.markdown(f"<div class='profile-name'>{st.session_state.username}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='profile-role'>{st.session_state.user_role.capitalize()}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='small-text'>📅 Last Login: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # ---------- LOGOUT ----------
        st.markdown("<div class='logout-btn'>", unsafe_allow_html=True)
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# ---------- HOME ----------
def home_page():
    profile_section()

    if st.session_state.user_role == "student":
        st.title("🎓 Capstone Project & Feedback Portal")
        st.markdown("""
        Welcome to the **Student Portal** 🎒  
        - Add and manage your capstone projects  
        - Share feedback on subjects  
        - Explore other projects
        """)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.page_link("pages/add_new_project.py", label="➕ Add New Project")
        with col2:
            st.page_link("pages/My_projects.py", label="📁 My Projects")
        with col3:
            st.page_link("pages/view_all_projects.py", label="📂 View All Projects")

        st.page_link("pages/give_subject_feedback.py", label="📝 Give Subject Feedback")
        st.page_link("pages/view_feedback.py", label="💬 View Feedback")

    elif st.session_state.user_role == "faculty":
        st.title("🎓 Capstone Project & Feedback Portal")
        st.markdown("""
        Welcome to the **Faculty Portal** 🧑‍🏫  
        - Review student projects  
        - View and analyze subject feedback
        """)
        col1, col2 = st.columns(2)
        with col1:
            st.page_link("pages/view_all_projects.py", label="📂 View All Projects")
        with col2:
            st.page_link("pages/view_feedback.py", label="💬 View Feedback")

    st.divider()
    st.success(f"Logged in as {st.session_state.username} ({st.session_state.user_role.capitalize()})")

# ---------- ROUTER ----------
if not st.session_state.logged_in:
    login_page()
else:
    home_page()
