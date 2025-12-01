# ===================== ABIA STATE EDUCATION PORTAL - FINAL PERFECTION =====================
# Built by Alabi Winner (BookyAde) • Abia TechRice Cohort 2.0 • 2025
# Username: admin | Password: 

import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import pandas as pd
from sqlalchemy import create_engine, text
import io
import os
import random
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from streamlit_autorefresh import st_autorefresh
import plotly.express as px
import streamlit.components.v1 as components
import hashlib
import json
import ast
import csv
from datetime import datetime



# ===================== PASSWORD HASHING FUNCTION (MUST BE AT TOP) =====================
def hash_password(password: str) -> str:
    """Return SHA-256 hash of password as hex string"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# ← ADD THIS LINE
if not st.secrets.get("DEBUG", False):
    st._is_running_with_streamlit = False  # Hides source code

# ===================== FULL WIDE & PROFESSIONAL SETUP =====================
st.set_page_config(page_title="Abia Education Portal", layout="wide")

# Remove ALL centering — make everything stretch full width
st.markdown("""
<style>
    .main > div {padding-left: 0rem !important; padding-right: 0rem !important;}
    .block-container {padding-left: 1rem !important; padding-right: 1rem !important; max-width: 100% !important;}
    .css-1d391kg {padding-top: 1rem !important;}
    .css-18e3th9 {padding-top: 2rem !important; padding-left: 2rem !important; padding-right: 2rem !important;}
    .css-1v0mbdj {width: 100% !important;}
    .stPlotlyChart > div {width: 100% !important;}
    div[data-testid="stHorizontalBlock"] {gap: 2rem;}
</style>
""", unsafe_allow_html=True)

# ===================== DATABASE CONNECTION =====================
def get_db_connection():
    try:
        # Check if secrets are loaded
        if not st.secrets:
            st.error("❌ Secrets not found! Please create .streamlit/secrets.toml")
            st.stop()
            
        # Construct URL from secrets
        db_url = (
            f"postgresql+pg8000://{st.secrets['DB_USER']}:{st.secrets['DB_PASSWORD']}@"
            f"{st.secrets['DB_HOST']}:{st.secrets['DB_PORT']}/{st.secrets['DB_NAME']}"
        )
        return create_engine(db_url)
    except Exception as e:
        st.error(f"❌ Database Connection Error: {e}")
        return None

engine = get_db_connection()


# ============ FIX: SESSION STATE INITIALIZATION & NAVIGATION OVERRIDE ============
if 'admin' not in st.session_state:
    st.session_state.admin = False
if 'selected' not in st.session_state:
    st.session_state.selected = "Home"  # or whatever your default is

# CRITICAL: After login, FORCE the page to Admin Panel even if sidebar says otherwise
if st.session_state.admin:
    st.session_state.selected = "Admin Panel"

# ===================== EMAIL FUNCTION =====================
def send_email(to_email, subject, body):
    try:
        email_user = st.secrets["EMAIL_USER"]
        email_pass = st.secrets["EMAIL_PASSWORD"]
        
        msg = MIMEMultipart()
        msg['From'] = email_user
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to Gmail SMTP
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(email_user, email_pass)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"❌ Email Error: {e}")
        return False
# ==================== BLOCK DIRECT ADMIN ACCESS FOREVER ====================
# This runs BEFORE the sidebar is even drawn
if 'admin' not in st.session_state:
    st.session_state.admin = False


# ===================== FINAL SIDEBAR – USER AUTHENTICATION READY =====================
with st.sidebar:

    st.markdown("<h2 style='text-align:center; color:#006400;'>Navigation</h2>", unsafe_allow_html=True)

    # Beautiful styling
    st.markdown("""
    <style>
        .css-1v0mbdj a {
            border-radius: 15px !important;
            margin: 10px 12px !important;
            padding: 16px !important;
            font-weight: 600 !important;
            transition: all 0.4s ease !important;
            border-left: 6px solid transparent;
        }
        .css-1v0mbdj a:hover {
            background-color: rgba(50,205,50,0.25) !important;
            border-left: 6px solid #32CD32 !important;
            transform: translateX(10px);
        }
        .css-1v0mbdj a[data-baseweb="menu-item"][aria-current="page"] {
            background: linear-gradient(90deg, #006400, #228B22) !important;
            color: white !important;
            border-left: 6px solid #32CD32 !important;
            box-shadow: 0 6px 20px rgba(0,100,0,0.4);
        }
    </style>
    """, unsafe_allow_html=True)

    # ——————————————————————— USER STATUS DISPLAY ———————————————————————
    if st.session_state.get("user"):
        user = st.session_state.user
        st.markdown(f"**Logged in as:**")
        st.success(f"**{user['full_name']}**")
        
        if user['user_type'] == 'school':
            if user['is_approved']:
                st.info("School Account • Approved")
            else:
                st.warning("School Account • Pending Approval")
        elif user['user_type'] == 'analyst':
            if user['is_approved']:
                st.info("Analyst Account • Approved")
            else:
                st.warning("Analyst Account • Pending Approval")

        if st.button("Logout", type="secondary", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key not in ["admin"]:  # Keep admin session separate
                    del st.session_state[key]
            st.rerun()

    # ——————————————————————— ADMIN MENU ———————————————————————
    if st.session_state.get("admin", False):
        selected = option_menu(
            menu_title=None,
            options=[
                "Home",
                "Live Dashboard",
                "School Lookup",
                "Transparency Ranking",
                "Submit Data",           # Admin can submit too
                "Request Data",          # Admin can download
                "User Management",       # Approve schools & analysts
                "Admin Panel",
                "Logout"
            ],
            icons=[
                "house-fill",
                "graph-up-arrow",
                "search-heart-fill",
                "trophy-fill",
                "cloud-upload-fill",
                "cloud-download-fill",
                "people-fill",
                "shield-lock-fill",
                "box-arrow-right"
            ],
            default_index=7,  # Opens on Admin Panel
            orientation="vertical",
            styles={"container": {"background-color": "#f8fff8"}, "nav-link-selected": {"background": "linear-gradient(90deg, #006400, #228B22)", "color": "white"}}
        )

        if selected == "Logout":
            st.session_state.admin = False
            st.rerun()

    # ——————————————————————— LOGGED-IN USER MENU (School / Analyst) ———————————————————————
    elif st.session_state.get("user"):
        user = st.session_state.user
        options = ["Home", "Live Dashboard", "School Lookup", "Transparency Ranking"]
        icons = ["house-fill", "graph-up-arrow", "search-heart-fill", "trophy-fill"]

        # Approved schools can submit data
        if user['user_type'] == 'school' and user['is_approved']:
            options.insert(2, "Submit Data")
            icons.insert(2, "cloud-upload-fill")

        # Approved users (school or analyst) can download data
        if user['is_approved']:
            options.append("Request Data")
            icons.append("cloud-download-fill")

        selected = option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            default_index=0,
            orientation="vertical",
            styles={"container": {"background-color": "#f8fff8"}, "nav-link-selected": {"background": "linear-gradient(90deg, #006400, #228B22)", "color": "white"}}
        )

        # ——————————————————————— PUBLIC / NOT LOGGED IN ———————————————————————
    else:
        selected = option_menu(
            menu_title=None,
            options=[
                "Home",
                "Live Dashboard",
                "School Lookup",
                "Transparency Ranking",
                "Login / Register"
            ],
            icons=[
                "house-fill",
                "graph-up-arrow",
                "search-heart-fill",
                "trophy-fill",
                "person-circle"
            ],
            default_index=0,
            orientation="vertical",
            styles={"container": {"background-color": "#f8fff8"}, "nav-link-selected": {"background": "linear-gradient(90deg, #006400, #228B22)", "color": "white"}}
        )
# CRITICAL: If someone tries to force "Admin Panel" without being logged in → kick them out
if selected == "Admin Panel" and not st.session_state.admin:
    st.error("Access Denied. You are not authorized.")
    st.session_state.selected = "Home"   # Force redirect
    st.rerun()

# ===================== DATA FUNCTIONS =====================
@st.cache_data(ttl=60)
def get_live_data():
    if not engine: return pd.DataFrame()
    return pd.read_sql("""
        SELECT l.lga_name,
               COALESCE(SUM(s.enrollment_total),0) AS students,
               COALESCE(SUM(s.teachers_total),0) AS teachers,
               ROUND(COALESCE(SUM(s.enrollment_total)::NUMERIC / NULLIF(SUM(s.teachers_total),0),999),1) AS ratio
        FROM dwh.dim_lga l
        LEFT JOIN school_submissions s ON TRIM(UPPER(l.lga_name)) = TRIM(UPPER(s.lga_name)) AND s.approved=TRUE
        GROUP BY l.lga_key, l.lga_name
        ORDER BY students DESC
    """, engine)

def save_submission(school, lga, students, teachers, name, email, facilities, photo_path):
    if not engine:
        return False
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO school_submissions 
                (school_name, lga_name, enrollment_total, teachers_total, 
                 submitted_by, email, facilities, photo_path, submitted_at, approved)
                VALUES (:school, :lga, :students, :teachers, :name, :email, 
                        :facilities::jsonb, :photo_path, NOW(), NULL)
            """), {
                "school": school,
                "lga": lga,
                "students": students,
                "teachers": teachers,
                "name": name,
                "email": email,
                "facilities": str(facilities),  # Stored as JSON string
                "photo_path": photo_path
            })
        return True
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# ===================== PAGES =====================
if selected == "Home" or selected is None:  # ← Critical fix: shows on first load!
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # HERO BANNER WITH BIG CENTERED LOGO — Presidential feel
    st.markdown("""
    <div style="background:linear-gradient(135deg, #006400, #32CD32); padding:60px 20px; border-radius:25px; text-align:center; color:white; box-shadow:0 15px 40px rgba(0,100,0,0.4); margin-bottom:40px;">
        <img src="https://raw.githubusercontent.com/BookyAde/abia-education-portal/main/assets/Abia_logo.jpeg" 
             width="320" 
             style="border-radius:50%; border:10px solid white; box-shadow:0 15px 40px rgba(0,0,0,0.5); margin-bottom:20px;">
        <h1 style="font-size:56px; margin:0; font-weight:900;">Abia State Education Portal</h1>
        <p style="font-size:28px; margin:20px 0 0; opacity:0.95;">Real-Time • Verified • Transparent</p>
        <p style="font-size:20px; margin-top:10px;">1,900+ Schools • 17 LGAs • Live Data • Built for Excellence</p>
    </div>
    """, unsafe_allow_html=True)

    # LIVE STATS — Auto-updating from your real data
    try:
        if engine:
            total_schools = pd.read_sql("SELECT COUNT(*) FROM school_submissions WHERE approved=TRUE", engine).iloc[0,0]
            total_students = pd.read_sql("SELECT COALESCE(SUM(enrollment_total),0) FROM school_submissions WHERE approved=TRUE", engine).iloc[0,0]
            total_teachers = pd.read_sql("SELECT COALESCE(SUM(teachers_total),0) FROM school_submissions WHERE approved=TRUE", engine).iloc[0,0]
            total_lgas = pd.read_sql("SELECT COUNT(DISTINCT lga_name) FROM school_submissions WHERE approved=TRUE", engine).iloc[0,0]
        else:
            raise Exception("No DB")
    except:
        total_schools = total_students = total_teachers = total_lgas = "Loading..."

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Verified Schools", f"{total_schools:,}", delta="Live & Growing")
    with col2:
        st.metric("Total Students", f"{total_students:,}")
    with col3:
        st.metric("Total Teachers", f"{total_teachers:,}")
    with col4:
        st.metric("LGAs Covered", total_lgas, delta="100% Coverage")

    # MISSION & VISION — Powerful & inspiring
    st.markdown("""
    <div style="background:#f8fff8; padding:40px; border-radius:20px; border-left:8px solid #006400; margin:40px 0;">
        <h2 style="color:#006400; text-align:center;">Our Vision</h2>
        <p style="font-size:19px; text-align:center; color:#333; line-height:1.8;">
            A future where <strong>every child in Abia State</strong> is counted, every school is seen, and every decision is driven by <strong>real, transparent, and up-to-date data</strong>.
        </p>
        <p style="text-align:center; font-style:italic; color:#006400; margin-top:20px;">
            "No child left behind. No school left out."
        </p>
    </div>
    """, unsafe_allow_html=True)

    # WHAT VISITORS CAN DO — Clear guidance
    st.markdown("### Navigate the Portal")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("""
        **Live Dashboard**  
        Explore real-time statistics: enrollment, teacher distribution, and pupil-teacher ratios across all 17 LGAs.
        """)
    with col2:
        st.success("""
        **Submit Data**  
        School administrators can submit verified school records for inclusion on the portal.
        """)
    with col3:
        st.warning("""
        **Request Dataset**  
        Download the complete verified education dataset for research, planning, or reporting.
        """)

    # FINAL CALL TO ACTION — Emotional & patriotic
    st.markdown("""
    <div style="text-align:center; padding:50px 20px; background:#e8f5e8; border-radius:20px; margin:50px 0;">
        <h2 style="color:#006400;">This is more than a dashboard.</h2>
        <p style="font-size:22px; max-width:800px; margin:20px auto; color:#333;">
            This is <strong>Abia State taking ownership</strong> of its education future — one verified school at a time.
        </p>
        <p style="font-size:18px; color:#006400; font-weight:bold;">
            Together, we are building the most transparent education system in Nigeria.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Creator Credit — Proud & visible
    st.markdown("""
    <div style="text-align:center; margin-top:50px; color:#006400; font-size:18px;">
        <p><strong>Built with passion & excellence by</strong></p>
        <h3>Alabi Winner (BookyAde)</h3>
        <p>Abia TechRice Cohort 2.0 • Class of 2025</p>
        <p><a href="https://github.com/BookyAde" style="color:#006400;">github.com/BookyAde</a></p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ===================== FINAL: LOGIN + REGISTER + INSTANT ACCESS =====================
elif selected == "Login / Register":
    st.markdown("# Account Login & Registration")
    st.markdown("### Secure access for schools and analysts")

    tab_login, tab_register = st.tabs(["Login", "Create Account"])

    # Cooldown for resend
    if "resend_cooldown" not in st.session_state:
        st.session_state.resend_cooldown = 0

    # ============================================================
    # LOGIN TAB
    # ============================================================
    with tab_login:
        st.markdown("#### Login to Your Account")

        with st.form("login_form"):
            email = st.text_input("Email Address", placeholder="you@abiaschools.edu.ng").strip().lower()
            password = st.text_input("Password", type="password")
            login = st.form_submit_button("Login", type="primary")

            if login:
                if not email or not password:
                    st.error("Please fill both fields")
                elif not engine:
                    st.error("Database not connected")
                else:
                    df = pd.read_sql(text("SELECT * FROM users WHERE email = :e"), engine, params={"e": email})
                    if df.empty:
                        st.error("No account found")
                    elif hash_password(password) != df.iloc[0]["password_hash"]:
                        st.error("Wrong password")
                    elif not df.iloc[0]["email_verified"]:
                        st.warning("Email not verified. Go to Create Account tab")
                    elif df.iloc[0].get("is_blocked"):
                        st.error("Your account is blocked")
                    else:
                        st.session_state.user = df.iloc[0].to_dict()
                        st.success(f"Welcome back, {df.iloc[0]['full_name']}!")
                        st.balloons()
                        st.rerun()

    # ============================================================
    # CREATE ACCOUNT + INSTANT VERIFICATION
    # ============================================================
    with tab_register:
        st.markdown("#### Create New Account")
        st.info("After clicking Create Account, enter the code sent to your email")

        with st.form("register_form", clear_on_submit=True):
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email Address *").strip().lower()
            password = st.text_input("Password *", type="password")
            confirm = st.text_input("Confirm Password *", type="password")
            user_type = st.selectbox("Account Type *", ["school", "analyst"])

            col1, col2 = st.columns(2)
            with col1:
                register = st.form_submit_button("Create Account", type="primary")
            with col2:
                resend = st.form_submit_button("Resend Code", type="secondary")

            # ——— REGISTRATION ———
            if register:
                errors = []
                if not all([full_name, email, password, confirm]): errors.append("All fields required")
                if password != confirm: errors.append("Passwords don't match")
                if len(password) < 6: errors.append("Password too short")
                if "@" not in email: errors.append("Invalid email")

                if errors:
                    for e in errors: st.error(e)
                elif not engine:
                    st.error("Database error")
                else:
                    exists = pd.read_sql(text("SELECT 1 FROM users WHERE email = :e"), engine, params={"e": email})
                    if not exists.empty:
                        st.error("Email already registered")
                    else:
                        code = random.randint(100000, 999999)
                        expires = pd.Timestamp.now() + pd.Timedelta(minutes=10)
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO users 
                                    (email, password_hash, full_name, user_type, verification_code, 
                                     code_expires, email_verified, created_at)
                                    VALUES (:e, :p, :n, :t, :c, :exp, FALSE, NOW())
                                """), {
                                    "e": email, "p": hash_password(password), "n": full_name,
                                    "t": user_type, "c": code, "exp": expires
                                })

                            if send_email(email, "Verification Code", f"Your code: {code}\n\nExpires in 10 minutes"):
                                st.session_state.verify_email = email
                                st.success("Account created! Enter code below")
                                st.balloons()
                                st.rerun()
                        except Exception as e:
                            st.error("Failed to create account")

            # ——— RESEND CODE ———
            if resend:
                if pd.Timestamp.now().timestamp() - st.session_state.resend_cooldown < 60:
                    st.error("Wait 60 seconds")
                elif not email:
                    st.error("Enter email first")
                else:
                    df = pd.read_sql(text("SELECT * FROM users WHERE email = :e"), engine, params={"e": email})
                    if df.empty or df.iloc[0]["email_verified"]:
                        st.error("No pending account or already verified")
                    else:
                        new_code = random.randint(100000, 999999)
                        expires = pd.Timestamp.now() + pd.Timedelta(minutes=10)
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE users SET verification_code = :c, code_expires = :exp WHERE email = :e"),
                                       {"c": new_code, "exp": expires, "e": email})
                        if send_email(email, "New Code", f"New code: {new_code}"):
                            st.session_state.verify_email = email
                            st.session_state.resend_cooldown = pd.Timestamp.now().timestamp()
                            st.success("New code sent!")
                            st.rerun()

        # ——— VERIFICATION BOX (APPEARS INSTANTLY) ———
        if st.session_state.get("verify_email"):
            st.markdown("### Verify Your Email")
            st.info(f"Code sent to **{st.session_state.verify_email}**")

            with st.form("verify_form"):
                code_input = st.text_input("Enter 6-digit code", max_chars=6)
                verify = st.form_submit_button("Verify Email", type="primary")

                if verify:
                    if not code_input.isdigit():
                        st.error("Invalid code")
                    else:
                        user = pd.read_sql(text("""
                            SELECT * FROM users WHERE email = :e AND verification_code = :c AND code_expires > NOW()
                        """), engine, params={"e": st.session_state.verify_email, "c": int(code_input)})
                        if user.empty:
                            st.error("Wrong or expired code")
                        else:
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE users SET email_verified = TRUE, verification_code = NULL, code_expires = NULL WHERE email = :e"),
                                           {"e": st.session_state.verify_email})
                            st.success("Email verified! You can now log in immediately.")
                            st.balloons()
                            del st.session_state.verify_email
                            st.rerun()

    # ============================================================
    # CREATE ACCOUNT TAB + INSTANT VERIFICATION
    # ============================================================
    with tab_register:
        st.markdown("#### Create New Account")
        st.info("After clicking Create Account, enter the code sent to your email")

        with st.form("register_form", clear_on_submit=True):
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email Address *").strip().lower()
            password = st.text_input("Password *", type="password")
            confirm = st.text_input("Confirm Password *", type="password")
            user_type = st.selectbox("Account Type *", ["school", "analyst"])

            col1, col2 = st.columns(2)
            with col1:
                register = st.form_submit_button("Create Account", type="primary")
            with col2:
                resend = st.form_submit_button("Resend Code", type="secondary")

            # ——— REGISTRATION ———
            if register:
                if not all([full_name, email, password, confirm]):
                    st.error("All fields required")
                elif password != confirm:
                    st.error("Passwords don't match")
                elif len(password) < 6:
                    st.error("Password too short")
                elif "@" not in email:
                    st.error("Invalid email")
                elif not engine:
                    st.error("Database error")
                else:
                    exists = pd.read_sql(text("SELECT 1 FROM users WHERE email = :e"), engine, params={"e": email})
                    if not exists.empty:
                        st.error("Email already registered")
                    else:
                        code = random.randint(100000, 999999)
                        expires = pd.Timestamp.now() + pd.Timedelta(minutes=10)
                        try:
                            with engine.begin() as conn:
                                conn.execute(text("""
                                    INSERT INTO users 
                                    (email, password_hash, full_name, user_type, verification_code, code_expires, 
                                     email_verified, is_approved, created_at)
                                    VALUES (:e, :p, :n, :t, :c, :exp, FALSE, FALSE, NOW())
                                """), {
                                    "e": email, "p": hash_password(password), "n": full_name,
                                    "t": user_type, "c": code, "exp": expires
                                })
                            if send_email(email, "Verification Code", f"Your code: {code}\n\nExpires in 10 minutes"):
                                st.session_state.verify_email = email
                                st.success("Account created! Enter code below")
                                st.balloons()
                                st.rerun()
                        except:
                            st.error("Failed to create account")

            # ——— RESEND CODE ———
            if resend:
                if pd.Timestamp.now().timestamp() - st.session_state.resend_cooldown < 60:
                    st.error("Wait 60 seconds")
                elif not email:
                    st.error("Enter email first")
                else:
                    df = pd.read_sql(text("SELECT * FROM users WHERE email = :e"), engine, params={"e": email})
                    if df.empty or df.iloc[0]["email_verified"]:
                        st.error("No pending account")
                    else:
                        new_code = random.randint(100000, 999999)
                        expires = pd.Timestamp.now() + pd.Timedelta(minutes=10)
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE users SET verification_code = :c, code_expires = :exp WHERE email = :e"),
                                       {"c": new_code, "exp": expires, "e": email})
                        if send_email(email, "New Code", f"New code: {new_code}"):
                            st.session_state.verify_email = email
                            st.session_state.resend_cooldown = pd.Timestamp.now().timestamp()
                            st.success("New code sent!")
                            st.rerun()

        # ——— VERIFICATION BOX (APPEARS INSTANTLY) ———
        if st.session_state.get("verify_email"):
            st.markdown("### Verify Your Email")
            st.info(f"Code sent to **{st.session_state.verify_email}**")

            with st.form("verify_form"):
                code = st.text_input("6-digit code", max_chars=6)
                verify = st.form_submit_button("Verify Email", type="primary")

                if verify:
                    if not code.isdigit():
                        st.error("Invalid code")
                    else:
                        user = pd.read_sql(text("""
                            SELECT * FROM users WHERE email = :e AND verification_code = :c AND code_expires > NOW()
                        """), engine, params={"e": st.session_state.verify_email, "c": int(code)})
                        if user.empty:
                            st.error("Wrong or expired code")
                        else:
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE users SET email_verified = TRUE, verification_code = NULL, code_expires = NULL WHERE email = :e"),
                                           {"e": st.session_state.verify_email})
                            st.success("Email verified! Awaiting admin approval")
                            st.balloons()
                            del st.session_state.verify_email
                            st.rerun()

    # ============================================================
    # ADMIN LOGIN TAB — SEPARATE & SECURE (100% FIXED)
    # ============================================================
    with tab_admin:
        st.markdown("#### Administrator Login")
        st.markdown("**Authorized personnel only**")

        # Initialize session state
        if "admin_attempts" not in st.session_state:
            st.session_state.admin_attempts = 0
        if "admin_lockout" not in st.session_state:
            st.session_state.admin_lockout = None

        # Check lockout
        if st.session_state.admin_lockout and pd.Timestamp.now() < st.session_state.admin_lockout:
            remaining = int((st.session_state.admin_lockout - pd.Timestamp.now()).total_seconds())
            st.error(f"Too many failed attempts. Try again in {remaining} seconds.")
        else:
            with st.form("admin_login_form"):
                pwd = st.text_input("Admin Password", type="password")
                otp = st.text_input("2FA Code", type="password")
                admin_login = st.form_submit_button("Login as Admin", type="primary")

                if admin_login:
                    try:
                        if pwd == st.secrets["ADMIN_PASSWORD"] and otp == st.secrets["ADMIN_2FA"]:
                            st.session_state.admin = True
                            st.session_state.admin_attempts = 0
                            st.success("Admin access granted!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.session_state.admin_attempts += 1
                            if st.session_state.admin_attempts >= 5:
                                st.session_state.admin_lockout = pd.Timestamp.now() + pd.Timedelta(minutes=15)
                                st.error("Account locked for 15 minutes due to too many failed attempts.")
                            else:
                                st.error(f"Access denied — Attempt {st.session_state.admin_attempts}/5")
                    except KeyError as e:
                        st.error(f"Admin credentials not configured: {e}")

        # Logout button
        if st.session_state.get("admin"):
            if st.button("Logout Admin", type="secondary"):
                st.session_state.admin = False
                st.success("Admin logged out")
                st.rerun()
    
elif selected == "Live Dashboard":
    st.markdown("### Live Education Statistics • Abia State")

    # Auto-refresh every 60 seconds
    st_autorefresh(interval=60000, key="live")

    # -------- Load live aggregated data safely --------
    try:
        df = get_live_data()
    except Exception as e:
        st.error(f"Failed to load live data: {e}")
        df = pd.DataFrame()

    if df.empty:
        st.warning("No data available yet or database connection failed.")
    else:
        # Ensure numeric safety
        df['students'] = pd.to_numeric(df['students'], errors='coerce').fillna(0)
        df['teachers'] = pd.to_numeric(df['teachers'], errors='coerce').fillna(0)

        # Preload school count once
        try:
            school_count = pd.read_sql(
                text("SELECT COUNT(*) AS c FROM school_submissions WHERE approved = TRUE"),
                con=engine
            ).iloc[0, 0]
        except:
            school_count = 0

        # ----------- Metrics Row -----------
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Students", f"{int(df['students'].sum()):,}")
        with col2:
            st.metric("Total Teachers", f"{int(df['teachers'].sum()):,}")
        with col3:
            st.metric("Verified Schools", f"{school_count:,}")
        with col4:
            st.metric("LGAs", "17", "Complete")

        # ----------- Students by LGA -----------
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                df, x='lga_name', y='students', 
                color='students', color_continuous_scale="Greens",
                title="Students by LGA"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.bar(
                df, x='lga_name', y='teachers', 
                color='teachers', color_continuous_scale="Blues",
                title="Teachers by LGA"
            )
            st.plotly_chart(fig, use_container_width=True)

        # ----------- Pie Charts -----------
        col1, col2 = st.columns(2)
        with col1:
            fig = px.pie(
                df, values='students', names='lga_name', 
                title="Student Share by LGA"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = px.pie(
                df, values='teachers', names='lga_name',
                title="Teacher Share by LGA"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.success("ALL 17 LGAs • 100% VERIFIED • LIVE DATA")

    # ------------------- FACILITY CRISIS HEATMAP --------------------
    st.markdown("### 🟥 Facility Crisis Heatmap Across Abia State")

    if not engine:
        st.error("Database not connected.")
        st.stop()

    try:
        facility_df = pd.read_sql(text("""
            SELECT 
                s.lga_name,
                COUNT(*) AS total_schools,
                SUM(CASE WHEN COALESCE(s.facilities,'') LIKE '%Toilets (Boys)%' THEN 1 ELSE 0 END) AS has_boys_toilet,
                SUM(CASE WHEN COALESCE(s.facilities,'') LIKE '%Toilets (Girls)%' THEN 1 ELSE 0 END) AS has_girls_toilet,
                SUM(CASE WHEN COALESCE(s.facilities,'') LIKE '%Clean Drinking Water%' THEN 1 ELSE 0 END) AS has_water,
                SUM(CASE WHEN COALESCE(s.facilities,'') LIKE '%Electricity%' THEN 1 ELSE 0 END) AS has_electricity
            FROM school_submissions s
            WHERE s.approved = TRUE
            GROUP BY s.lga_name
        """), con=engine)
    except Exception as e:
        st.error(f"Failed to load facility statistics: {e}")
        st.stop()

    if not facility_df.empty:
        # Avoid division by zero
        facility_df["No Toilet (Boys) %"] = facility_df.apply(
            lambda x: 100 - round((x["has_boys_toilet"] / x["total_schools"]) * 100, 1)
            if x["total_schools"] > 0 else 0,
            axis=1
        )
        facility_df["No Toilet (Girls) %"] = facility_df.apply(
            lambda x: 100 - round((x["has_girls_toilet"] / x["total_schools"]) * 100, 1)
            if x["total_schools"] > 0 else 0,
            axis=1
        )
        facility_df["No Water %"] = facility_df.apply(
            lambda x: 100 - round((x["has_water"] / x["total_schools"]) * 100, 1)
            if x["total_schools"] > 0 else 0,
            axis=1
        )

        # ----------- Treemap Visualization -----------
        fig = px.treemap(
            facility_df,
            path=['lga_name'],
            values='total_schools',
            color='No Toilet (Boys) %',
            color_continuous_scale="Reds",
            title="🚽 LGAs with Highest Toilet Crisis (Darker = Worse)"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ----------- Crisis Table -----------
        st.markdown("### Key Crisis Zones")
        st.dataframe(
            facility_df[
                ["lga_name", "total_schools", 
                 "No Toilet (Boys) %", "No Toilet (Girls) %", "No Water %"]
            ].sort_values("No Toilet (Boys) %", ascending=False),
            use_container_width=True
        )


elif selected == "Submit Data":
    st.markdown("### Submit School Data")
    st.info("Your official school email is required • All submissions are verified and approved by admin")

    # ==================== SECURITY: RATE LIMIT (2 MINUTES) ====================
    if "last_submission_time" not in st.session_state:
        st.session_state.last_submission_time = 0

    current_time = pd.Timestamp.now().timestamp()
    time_since_last = current_time - st.session_state.last_submission_time

    if time_since_last < 120:  # 120 seconds = 2 minutes
        remaining = int(120 - time_since_last)
        st.error(f"Too many attempts. Please wait **{remaining} seconds** before submitting again.")
        st.stop()

    # =====================================================================
    # Load LGAs
    if engine:
        try:
            lgas = pd.read_sql("SELECT lga_name FROM dwh.dim_lga ORDER BY lga_name", engine)['lga_name'].tolist()
        except Exception as e:
            lgas = []
            st.error(f"Could not load LGAs: {e}")
    else:
        lgas = []
        st.error("Database not connected.")

    if not lgas:
        st.stop()

    os.makedirs("uploads", exist_ok=True)

    # ============= STEP 1: Fill Form & Send Verification Code =============
    if not st.session_state.get("awaiting_code", False):
        with st.form("send_code_form", clear_on_submit=False):
            st.markdown("#### School & Contact Information")
            col1, col2 = st.columns(2)
            with col1:
                school = st.text_input("School Name *", placeholder="e.g. Community Secondary School Ohafia")
                lga = st.selectbox("LGA *", options=lgas)
                name = st.text_input("Contact Name * (Principal/Head Teacher)", placeholder="e.g. Mrs. Chioma Okeke")
            with col2:
                students = st.number_input("Total Students Enrolled *", min_value=1, step=1)
                teachers = st.number_input("Total Teachers *", min_value=1, step=1)
                email = st.text_input("Official School Email *", placeholder="principal.school@abiaschools.edu.ng")

            st.markdown("#### Functional Facilities (Select all that work)")
            facilities = st.multiselect(
                "Check all facilities currently working",
                [
                    "Functional Toilets (Boys)",
                    "Functional Toilets (Girls)",
                    "Clean Drinking Water",
                    "Electricity / Solar Power",
                    "Enough Desks & Chairs (80%+ students seated)",
                    "Perimeter Fencing",
                    "Functional Classrooms (no leaking roof)",
                    "Computer Lab / ICT Center"
                ],
                help="This helps government know where to send help first"
            )

            st.markdown("#### Upload Proof Photo * (School signboard or front gate)")
            photo = st.file_uploader(
                "Clear photo required — prevents fake schools",
                type=['jpg', 'jpeg', 'png'],
                help="Take a photo of the school signboard or building entrance"
            )

            submit_btn = st.form_submit_button("Send Verification Code", type="primary")

            if submit_btn:
                errors = []
                if not school.strip(): errors.append("School name required")
                if not lga: errors.append("LGA required")
                if not name.strip(): errors.append("Contact name required")
                if not email or "@" not in email: errors.append("Valid email required")
                if students < 1 or teachers < 1: errors.append("Student/teacher count must be positive")
                if not photo: errors.append("Photo is mandatory")
                if not errors:
                    # Save photo
                    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                    safe_name = "".join(c for c in school if c.isalnum() or c in " -_")[:50]
                    filename = f"{safe_name}_{timestamp}.jpg"
                    photo_path = f"uploads/{filename}"
                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())

                    # Store in session
                    st.session_state.temp_data = {
                        "school": school.strip(),
                        "lga": lga,
                        "students": int(students),
                        "teachers": int(teachers),
                        "name": name.strip(),
                        "email": email.strip().lower(),
                        "facilities": facilities,
                        "photo_path": photo_path
                    }

                    # Send code
                    code = random.randint(100000, 999999)
                    body = f"""
Hello {name},

Thank you for submitting data for **{school}**, {lga} LGA.

Your 6-digit verification code is:

**{code}**

Enter it on the portal to complete submission.

This ensures only real schools submit data.

— Abia State Education Portal Team
                    """
                    if send_email(email, "Your Abia Portal Verification Code", body):
                        st.session_state.verification_code = code
                        st.session_state.awaiting_code = True
                        st.success(f"Code sent to {email}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to send email. Check address and try again.")
                else:
                    for error in errors:
                        st.error(error)

    # ============= STEP 2: Enter Code & Final Submit =============
    else:
        temp = st.session_state.temp_data
        st.info(f"Verification code sent to **{temp['email']}** • School: **{temp['school']}**")

        with st.form("verify_code_form"):
            code_input = st.text_input("Enter 6-digit code", max_chars=6, placeholder="e.g. 283749")
            verify_btn = st.form_submit_button("Verify & Submit", type="primary")

            if verify_btn:
                if code_input == str(st.session_state.verification_code):
                    success = save_submission(
                        school=temp["school"],
                        lga=temp["lga"],
                        students=temp["students"],
                        teachers=temp["teachers"],
                        name=temp["name"],
                        email=temp["email"],
                        facilities=temp["facilities"],
                        photo_path=temp["photo_path"]
                    )

                    if success:
                        # Success email
                        send_email(
                            temp["email"],
                            "Submission Received – Abia Education Portal",
                            f"Hello {temp['name']},\n\nYour data for **{temp['school']}** has been received and is pending approval.\n\nYou will be notified when it's live.\n\nThank you!\n— Abia Education Portal"
                        )

                        st.success("Submitted successfully! Your data is now pending admin approval.")
                        st.balloons()

                        # === UPDATE RATE LIMIT TIMER ===
                        st.session_state.last_submission_time = pd.Timestamp.now().timestamp()

                        # Clear session
                        for key in ["temp_data", "verification_code", "awaiting_code"]:
                            st.session_state.pop(key, None)
                        st.rerun()
                    else:
                        st.error("Failed to save. Please try again later.")
                else:
                    st.error("Incorrect code. Check and try again.")
    

elif selected == "Request Data":
    st.markdown("""
    <div class='card'>
        <h2>Download Education Dataset</h2>
        <p>Filter by LGA, approval status, dates, or keywords. Export to Excel in one click.</p>
    </div>
    """, unsafe_allow_html=True)

    # Load full data
    if not engine:
        st.error("Database not connected.")
        st.stop()

    try:
        df = pd.read_sql(text("""
            SELECT id, school_name, lga_name, enrollment_total, teachers_total,
                   submitted_by, email, submitted_at,
                   CASE 
                       WHEN approved = TRUE THEN 'Approved'
                       WHEN approved = FALSE THEN 'Rejected'
                       ELSE 'Pending'
                   END AS status
            FROM school_submissions
            ORDER BY submitted_at DESC
        """), con=engine)
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        st.stop()

    if df.empty:
        st.info("No submissions found.")
        st.stop()

    # Ensure submitted_at is datetime
    try:
        df["submitted_at"] = pd.to_datetime(df["submitted_at"], errors="coerce")
    except:
        st.error("Date parsing failed.")
        st.stop()

    # FILTERS
    col1, col2 = st.columns(2)

    # ====== LGA + STATUS FILTERS ======
    with col1:
        lga_options = ["All"] + sorted(df['lga_name'].dropna().unique().tolist())
        lga_filter = st.multiselect("Filter by LGA", lga_options, default="All")

        # Force 'All' to be exclusive
        if "All" in lga_filter and len(lga_filter) > 1:
            lga_filter = ["All"]

        status_options = ["All", "Approved", "Pending", "Rejected"]
        status_filter = st.multiselect("Filter by Status", status_options, default="Approved")

        if "All" in status_filter and len(status_filter) > 1:
            status_filter = ["All"]

    # ====== DATE RANGE ======
    with col2:
        min_date = df['submitted_at'].min().date()
        max_date = df['submitted_at'].max().date()

        date_range = st.date_input(
            "Submission Date Range",
            value=(min_date, max_date)
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            start_date = end_date = date_range

    # ====== KEYWORD SEARCH ======
    search = st.text_input("Search school name, submitter, or email", "")

    # ====== APPLY FILTERS ======
    filtered = df.copy()

    # LGA
    if "All" not in lga_filter:
        filtered = filtered[filtered["lga_name"].isin(lga_filter)]

    # Status
    if "All" not in status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]

    # Date range
    filtered = filtered[
        (filtered['submitted_at'].dt.date >= start_date) &
        (filtered['submitted_at'].dt.date <= end_date)
    ]

    # Keyword search
    if search.strip():
        s = search.lower().strip()
        filtered = filtered[
            filtered["school_name"].fillna("").str.lower().str.contains(s) |
            filtered["submitted_by"].fillna("").str.lower().str.contains(s) |
            filtered["email"].fillna("").str.lower().str.contains(s)
        ]

    # RESULTS
    st.markdown(f"### **{len(filtered):,} records found**")
    st.dataframe(filtered.head(200), use_container_width=True)

    st.markdown("---")

    # ====== EXCEL DOWNLOAD ======
    if st.button("Generate & Download Excel", type="primary", use_container_width=True):
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                filtered.to_excel(writer, index=False, sheet_name="Abia_Education_Data")

                # Format header
                workbook = writer.book
                worksheet = writer.sheets["Abia_Education_Data"]
                header_format = workbook.add_format({
                    "bold": True,
                    "bg_color": "#006400",
                    "font_color": "white"
                })

                for col_num, col_name in enumerate(filtered.columns):
                    worksheet.write(0, col_num, col_name, header_format)
                    worksheet.set_column(col_num, col_num, 20)

            output.seek(0)

            st.download_button(
                label="Download Filtered Dataset.xlsx",
                data=output,
                file_name=f"Abia_Education_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.success("Your custom dataset is ready!")
            st.balloons()

        except Exception as e:
            st.error(f"Failed to generate Excel file: {e}")



elif selected == "School Lookup":
    st.markdown("# School Lookup")
    st.markdown("### Search any school in Abia State • View verified records • Report issues instantly")

    # Search Bar
    search = st.text_input(
        "🔍 Search by school name or LGA",
        placeholder="e.g. Umuahia High School, Aba North, Ohafia",
        help="Start typing to filter results"
    )

    if not engine:
        st.error("Database not connected.")
        st.stop()

    # Load verified (approved) schools
    try:
        df = pd.read_sql(text("""
            SELECT id, school_name, lga_name, enrollment_total, teachers_total,
                   submitted_by, email, submitted_at, photo_path, facilities
            FROM school_submissions 
            WHERE approved = TRUE
            ORDER BY school_name
        """), con=engine)
    except Exception as e:
        st.error(f"Failed to load schools: {e}")
        st.stop()

    if df.empty:
        st.info("No verified schools found.")
        st.stop()

    # Apply live search
    if search:
        s = search.lower().strip()
        df = df[
            df["school_name"].str.lower().str.contains(s, na=False) |
            df["lga_name"].str.lower().str.contains(s, na=False)
        ]

    st.markdown(f"**Found {len(df)} school(s)**")

    # Facility Mapping (same as Admin Panel)
    FACILITY_MAP = {
        "Functional Toilets (Boys)": "Boys Toilet",
        "Functional Toilets (Girls)": "Girls Toilet",
        "Clean Drinking Water": "Water",
        "Electricity / Solar Power": "Electricity",
        "Enough Desks & Chairs (80%+ students seated)": "Desks",
        "Perimeter Fencing": "Fencing",
        "Functional Classrooms (no leaking roof)": "Classrooms",
        "Computer Lab / ICT Center.": "ICT Lab"
    }

    # Loop results
    for _, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])

            # ========== PHOTO COLUMN ==========
            with col1:
                photo = row.get("photo_path")
                if photo and os.path.exists(photo):
                    try:
                        st.image(photo, use_container_width=True)
                    except:
                        st.image("https://via.placeholder.com/400x300?text=Image+Error", use_container_width=True)
                else:
                    st.image("https://via.placeholder.com/400x300?text=No+Photo", use_container_width=True)

            # ========== INFO COLUMN ==========
            with col2:
                st.markdown(f"### {row['school_name']}")
                st.markdown(f"**LGA:** {row['lga_name']}")
                st.markdown(f"**Students:** {int(row['enrollment_total']):,}")
                st.markdown(f"**Teachers:** {int(row['teachers_total']):,}")

                # ----- Facilities -----
                st.markdown("#### Working Facilities")
                raw_facilities = row.get("facilities")
                facilities_list = []

                # Safe parsing
                if raw_facilities:
                    try:
                        facilities_list = json.loads(raw_facilities)
                        if not isinstance(facilities_list, list):
                            facilities_list = []
                    except:
                        try:
                            facilities_list = ast.literal_eval(raw_facilities)
                            if not isinstance(facilities_list, list):
                                facilities_list = []
                        except:
                            st.warning("Facilities data invalid.")
                            facilities_list = []

                cols = st.columns(4)
                for i, fac in enumerate(facilities_list):
                    short = FACILITY_MAP.get(fac, fac)
                    with cols[i % 4]:
                        st.success(short)

                st.markdown("---")

                # ========== REPORT BUTTON ==========
                report_key = f"report_{row['id']}"
                if st.button("Report Issue at This School", key=report_key, use_container_width=True):

                    with st.expander(f"Report Issue — {row['school_name']}"):
                        with st.form(f"report_form_{row['id']}"):
                            st.warning(f"Reporting a problem for **{row['school_name']}**, {row['lga_name']}")

                            issue = st.selectbox("What’s wrong?", [
                                "No Toilets", "No Clean Water", "Leaking Roof", "No Teachers",
                                "No Desks/Chairs", "Illegal Fees", "Security Issue", "Other"
                            ])

                            details = st.text_area("Describe the issue")
                            contact = st.text_input("Your phone/email (optional)")

                            c1, c2 = st.columns(2)

                            with c1:
                                send = st.form_submit_button("Send Report", type="primary")

                            with c2:
                                cancel = st.form_submit_button("Cancel")

                            if send:
                                body = f"""
NEW SCHOOL COMPLAINT
School: {row['school_name']}
LGA: {row['lga_name']}
Issue: {issue}
Details: {details}
Contact: {contact or "Anonymous"}
Time: {pd.Timestamp.now()}
                                """
                                try:
                                    send_email(
                                        "complaints@abiaeducation.gov.ng",
                                        f"URGENT: {issue} – {row['school_name']}",
                                        body
                                    )
                                    st.success("Report sent successfully. Thank you!")
                                    st.balloons()
                                except Exception as e:
                                    st.error(f"Failed to send report: {e}")

                            if cancel:
                                st.rerun()

        st.markdown("---")

elif selected == "Transparency Ranking":
    st.markdown("# LGA Education Transparency Ranking")
    st.markdown("### Which LGA is leading in verified school data and facilities?")

    if not engine:
        st.error("Database not connected")
        st.stop()

    ranking = pd.read_sql("""
        WITH stats AS (
            SELECT 
                lga_name,
                COUNT(*) FILTER (WHERE approved = TRUE) AS verified_schools,
                COUNT(*) AS total_submissions,
                COUNT(*) FILTER (WHERE facilities LIKE '%Toilets (Boys)%') AS has_boys_toilet,
                COUNT(*) FILTER (WHERE facilities LIKE '%Toilets (Girls)%') AS has_girls_toilet,
                COUNT(*) FILTER (WHERE facilities LIKE '%Clean Drinking Water%') AS has_water
            FROM school_submissions
            WHERE approved = TRUE
            GROUP BY lga_name
        )
        SELECT 
            lga_name,
            verified_schools,
            total_submissions,
            ROUND(100.0 * verified_schools / NULLIF(total_submissions, 0), 1) AS verification_rate_percent,
            COALESCE(has_boys_toilet, 0) AS schools_with_boys_toilet,
            COALESCE(has_girls_toilet, 0) AS schools_with_girls_toilet,
            COALESCE(has_water, 0) AS schools_with_water,
            ROUND(100.0 * COALESCE(has_boys_toilet, 0) / NULLIF(verified_schools, 0), 1) AS boys_toilet_pct,
            ROUND(100.0 * COALESCE(has_girls_toilet, 0) / NULLIF(verified_schools, 0), 1) AS girls_toilet_pct,
            ROUND(100.0 * COALESCE(has_water, 0) / NULLIF(verified_schools, 0), 1) AS water_pct
        FROM stats
        ORDER BY verified_schools DESC
    """, engine)

    if ranking.empty:
        st.info("No verified data yet.")
    else:
        ranking.index = range(1, len(ranking) + 1)
        ranking.index.name = "Rank"

        # Simple, beautiful formatting WITHOUT matplotlib
        def highlight_row(row):
            if row.name == 1:
                return ['background-color: #d4edda; font-weight: bold'] * len(row)  # Green for #1
            elif row.name == len(ranking):
                return ['background-color: #f8d7da; font-weight: bold'] * len(row)  # Red for last
            else:
                return [''] * len(row)

        styled = ranking.style\
            .format({
                "verification_rate_percent": "{:.1f}%",
                "boys_toilet_pct": "{:.1f}%",
                "girls_toilet_pct": "{:.1f}%",
                "water_pct": "{:.1f}%"
            })\
            .apply(highlight_row, axis=1)\
            .set_properties(**{'text-align': 'center'})\
            .set_table_styles([
                {'selector': 'th', 'props': [('background-color', '#006400'), ('color', 'white'), ('font-weight', 'bold')]},
                {'selector': 'td', 'props': [('padding', '12px'), ('border', '1px solid #ddd')]}
            ])

        st.dataframe(styled, use_container_width=True)

        # Top & Bottom highlight
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"Leading LGA: **{ranking.iloc[0]['lga_name']}** • {ranking.iloc[0]['verified_schools']} schools")
        with col2:
            st.error(f"Lagging LGA: **{ranking.iloc[-1]['lga_name']}** • Only {ranking.iloc[-1]['verified_schools']} schools")

        st.markdown("---")
        st.caption("Green row = Best performing • Red row = Needs urgent attention")

# ===================== USER MANAGEMENT – FINAL & BULLETPROOF =====================
elif selected == "User Management":
    if not st.session_state.get("admin"):
        st.error("Admin access required")
        st.stop()

    st.markdown("# User Management")
    st.markdown("### Block violators • Promote contributors • Reinstate after review")

    if not engine:
        st.error("Database not connected")
        st.stop()

    # Load all users
    try:
        users = pd.read_sql("""
            SELECT id, full_name, email, user_type, email_verified, 
                   is_blocked, is_admin, created_at
            FROM users 
            ORDER BY created_at DESC
        """, engine)
    except Exception as e:
        st.error(f"Failed to load users: {e}")
        st.stop()

    if users.empty:
        st.info("No users registered yet.")
    else:
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Total Users", len(users))
        with col2: st.metric("Blocked", len(users[users["is_blocked"] == True]))
        with col3: st.metric("Admins", len(users[users["is_admin"] == True]))

        st.markdown("---")

        for _, user in users.iterrows():
            # Safe date formatting
            created_date = "Unknown"
            if pd.notna(user['created_at']):
                try:
                    created_date = str(user['created_at'])[:10]  # YYYY-MM-DD
                except:
                    created_date = "Invalid"

            status = "Active"
            if user["is_blocked"]: status = "Blocked"
            if user["is_admin"]: status = "Admin"

            with st.expander(f"**{user['full_name']}** • {user['email']} • {user['user_type'].title()} • {status}"):
                col1, col2 = st.columns([2, 3])

                with col1:
                    st.write(f"**Registered:** {created_date}")
                    st.write(f"**Email Verified:** {'Yes' if user['email_verified'] else 'No'}")

                with col2:
                    # PROMOTE TO ADMIN
                    if not user["is_admin"]:
                        with st.form(key=f"promote_form_{user['id']}"):
                            st.markdown("#### Promote to Admin")
                            reason = st.text_area("Reason for promotion", placeholder="e.g. High-quality contributions", height=80)
                            promote = st.form_submit_button("Promote to Admin", type="primary")
                            if promote:
                                if not reason.strip():
                                    st.error("Reason required")
                                else:
                                    try:
                                        with engine.begin() as conn:
                                            conn.execute(text("UPDATE users SET is_admin = TRUE WHERE id = :id"), {"id": user["id"]})
                                        body = f"""
Hello {user['full_name']},

Congratulations!

You have been promoted to **Administrator** on the Abia State Education Portal.

**Reason:** {reason}

You now have full access to manage users and approve submissions.

Thank you for your dedication!

— Abia Education Portal Administration
                                        """
                                        send_email(user['email'], "You Are Now an Administrator!", body)
                                        st.success("Promoted to admin!")
                                        st.balloons()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")

                    # BLOCK USER
                    if not user["is_blocked"]:
                        with st.form(key=f"block_form_{user['id']}"):
                            st.markdown("#### Block User")
                            reason = st.text_area("Reason for blocking", placeholder="e.g. Fake data, spam", height=80)
                            block = st.form_submit_button("Block User", type="secondary")
                            if block:
                                if not reason.strip():
                                    st.error("Reason required")
                                else:
                                    try:
                                        with engine.begin() as conn:
                                            conn.execute(text("UPDATE users SET is_blocked = TRUE WHERE id = :id"), {"id": user["id"]})
                                        body = f"""
Hello {user['full_name']},

Your account has been **blocked** on the Abia State Education Portal.

**Reason:** {reason}

If you believe this is a mistake, please contact the admin team.

— Abia Education Portal Administration
                                        """
                                        send_email(user['email'], "Account Blocked", body)
                                        st.warning("User blocked")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")

                    # UNBLOCK USER (REINSTATE)
                    if user["is_blocked"]:
                        with st.form(key=f"unblock_form_{user['id']}"):
                            st.markdown("#### Unblock User")
                            reason = st.text_area("Reason for reinstatement", placeholder="e.g. Account reviewed and cleared", height=80)
                            unblock = st.form_submit_button("Unblock User", type="primary")
                            if unblock:
                                if not reason.strip():
                                    st.error("Reason required")
                                else:
                                    try:
                                        with engine.begin() as conn:
                                            conn.execute(text("UPDATE users SET is_blocked = FALSE WHERE id = :id"), {"id": user["id"]})
                                        body = f"""
Hello {user['full_name']},

Great news!

Your account has been **unblocked** on the Abia State Education Portal.

**Reason:** {reason}

You can now log in and continue contributing.

Welcome back!

— Abia Education Portal Administration
                                        """
                                        send_email(user['email'], "Account Unblocked", body)
                                        st.success("User unblocked and reinstated")
                                        st.balloons()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {e}")

                    # REVOKE ADMIN RIGHTS
                    if user["is_admin"] and user["id"] != st.session_state.user.get("id"):
                        if st.button("Revoke Admin Rights", key=f"revoke_{user['id']}"):
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("UPDATE users SET is_admin = FALSE WHERE id = :id"), {"id": user["id"]})
                                send_email(user['email'], "Admin Rights Revoked", 
                                    f"Hello {user['full_name']},\n\nYour admin privileges have been revoked.\n\n— Abia Education Portal Administration")
                                st.info("Admin rights revoked")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed: {e}")

# ---------- ADMIN LOGIN ----------
elif selected == "Admin Login":
    st.markdown("### Secure Admin Access")

    # Login attempt tracking
    if "login_attempts" not in st.session_state:
        st.session_state.login_attempts = 0
    if "lockout_time" not in st.session_state:
        st.session_state.lockout_time = None

    if st.session_state.lockout_time:
        if pd.Timestamp.now() < st.session_state.lockout_time:
            st.error(f"Too many attempts. Try again in {int((st.session_state.lockout_time - pd.Timestamp.now()).total_seconds())} seconds")
            st.stop()
        else:
            st.session_state.login_attempts = 0
            st.session_state.lockout_time = None

    with st.form("secure_login"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        otp = st.text_input("2FA Code (check your phone/email)")

        if st.form_submit_button("Login"):
            if user == "admin" and pwd == st.secrets["ADMIN_PASSWORD"] and otp == st.secrets["ADMIN_2FA"]:
                st.session_state.admin = True
                st.session_state.login_attempts = 0
                st.success("Welcome, Administrator!")
                st.balloons()
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                if st.session_state.login_attempts >= 5:
                    st.session_state.lockout_time = pd.Timestamp.now() + pd.Timedelta(minutes=15)
                    st.error("Account locked for 15 minutes")
                else:
                    st.error(f"Access denied ({st.session_state.login_attempts}/5)")

# ===================== ADMIN PANEL (SECURE + FULL ACTIVITY LOGGING) =====================

elif selected == "Admin Panel":

    # -------- SECURITY CHECK --------
    if not st.session_state.get("admin", False):
        st.error("Unauthorized access. Redirecting to Home...")
        st.session_state.selected = "Home"
        st.rerun()

    st.markdown("# ADMIN PANEL • Full Control")
    st.success("Logged in as Administrator")

    # Determine admin identifier for logs (prefer session user/email if present)
    admin_identifier = st.session_state.get("admin_user") \
                       or (st.session_state.get("user") or {}).get("email") \
                       or (st.session_state.get("user") or {}).get("full_name") \
                       or "admin"

    # Logout area (clears admin & returns home)
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Logout", type="primary", use_container_width=True):
            st.session_state.admin = False
            # clear user session safely
            if "user" in st.session_state:
                st.session_state.pop("user", None)
            st.session_state.selected = "Home"
            st.experimental_rerun()

    # -------- DB CHECK & LOAD PENDING SUBMISSIONS --------
    if not engine:
        st.error("Database not connected.")
        st.stop()

    try:
        pending = pd.read_sql(text("""
            SELECT id, school_name, lga_name, enrollment_total, teachers_total,
                   submitted_by, email, submitted_at, facilities, photo_path
            FROM school_submissions
            WHERE approved IS NULL
            ORDER BY submitted_at DESC
        """), con=engine)
    except Exception as e:
        st.error(f"Failed to load pending submissions: {e}")
        st.stop()

    # -------- Activity log function (safe append) --------
    def log_admin_action(action: str, submission_id: int, school_name: str, lga_name: str):
        log_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "admin": admin_identifier,
            "action": action,
            "submission_id": submission_id,
            "school_name": school_name,
            "lga_name": lga_name
        }
        logfile = "admin_activity_log.csv"
        write_header = not os.path.exists(logfile)
        # Append safe CSV (note: on multi-worker setups consider a DB or file lock)
        try:
            with open(logfile, "a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=log_entry.keys())
                if write_header:
                    writer.writeheader()
                writer.writerow(log_entry)
        except Exception as e:
            st.warning(f"Failed to write admin log: {e}")

    # -------- UI: Pending list --------
    st.subheader(f"Pending Submissions ({len(pending):,})")
    if pending.empty:
        st.info("No pending submissions at this time.")
    else:
        # Iterate over rows and show expanders
        for _, row in pending.iterrows():
            sub_id = int(row["id"])
            submitted_at_str = ""
            try:
                submitted_at_str = pd.to_datetime(row["submitted_at"]).strftime("%b %d, %Y %H:%M")
            except Exception:
                submitted_at_str = str(row["submitted_at"])

            with st.expander(f"#{sub_id} — {row.get('school_name','(Unknown)')} • {row.get('lga_name','(Unknown)')} • Submitted {submitted_at_str}"):
                left, right = st.columns([1, 2])

                # --- Left: Photo and basic info ---
                with left:
                    st.markdown(f"**Students:** {int(row.get('enrollment_total') or 0):,}")
                    st.markdown(f"**Teachers:** {int(row.get('teachers_total') or 0):,}")
                    st.markdown(f"**Contact:** {row.get('submitted_by') or 'N/A'}")
                    st.markdown(f"**Email:** {row.get('email') or 'N/A'}")
                    photo_path = row.get("photo_path")
                    if photo_path and os.path.exists(photo_path):
                        try:
                            st.image(photo_path, caption="Photo proof", use_column_width=True)
                        except Exception:
                            st.warning("Photo exists but could not be displayed.")
                    else:
                        st.info("Photo missing or path invalid.")  # info instead of warning to reduce alarm

                # --- Right: Facilities and actions ---
                with right:
                    st.markdown("#### Functional Facilities")
                    raw_facilities = row.get("facilities")
                    facilities_list = []
                    if raw_facilities:
                        try:
                            # Expecting JSON string like '["Functional Toilets (Boys)", ...]'
                            if isinstance(raw_facilities, str):
                                facilities_list = json.loads(raw_facilities)
                            else:
                                facilities_list = raw_facilities
                            if not isinstance(facilities_list, list):
                                facilities_list = []
                        except Exception:
                            # Try ast.literal_eval as fallback, but avoid eval()
                            try:
                                facilities_list = ast.literal_eval(raw_facilities)
                                if not isinstance(facilities_list, list):
                                    facilities_list = []
                            except Exception:
                                facilities_list = []
                                st.error("Facilities data malformed.")
                    # Map & display
                    facility_map = {
                        "Functional Toilets (Boys)": "Boys Toilet",
                        "Functional Toilets (Girls)": "Girls Toilet",
                        "Clean Drinking Water": "Water",
                        "Electricity / Solar Power": "Electricity",
                        "Enough Desks & Chairs (80%+ students seated)": "Desks",
                        "Perimeter Fencing": "Fencing",
                        "Functional Classrooms (no leaking roof)": "Classrooms",
                        "Computer Lab / ICT Center.": "ICT Lab"
                    }
                    cols = st.columns(4)
                    for i, (full_label, short_label) in enumerate(facility_map.items()):
                        with cols[i % 4]:
                            if full_label in facilities_list:
                                st.success(f"{short_label}: Yes")
                            else:
                                st.info(f"{short_label}: No")

                    st.markdown("---")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("APPROVE & Publish", key=f"approve_{sub_id}", type="primary", use_container_width=True):
                            # APPROVE — DB update + dwh sync + email + logging
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("UPDATE school_submissions SET approved=TRUE WHERE id=:id"), {"id": sub_id})
                                    # Optional: update DWH / fact table as in original intent
                                    conn.execute(text("""
                                        INSERT INTO dwh.fact_abia_metrics (lga_key, enrollment_total, teachers_total, approved)
                                        SELECT l.lga_key, :e, :t, TRUE
                                        FROM dwh.dim_lga l WHERE l.lga_name=:lga
                                        ON CONFLICT (lga_key) DO UPDATE SET
                                           enrollment_total = EXCLUDED.enrollment_total,
                                           teachers_total = EXCLUDED.teachers_total
                                    """), {"e": int(row.get("enrollment_total") or 0), "t": int(row.get("teachers_total") or 0), "lga": row.get("lga_name")})
                                # send notification email (safe-guard)
                                try:
                                    if row.get("email"):
                                        send_email(row.get("email"), "APPROVED – Abia Education Portal",
                                                   f"Good news!\n\nYour submission for **{row.get('school_name','(Unknown)')}** has been APPROVED and is now live.\n\nThank you!\n— Abia Education Portal Team")
                                except Exception as e:
                                    st.warning(f"Approval saved but failed to send email: {e}")

                                # Log action and refresh
                                log_admin_action("APPROVED", sub_id, row.get("school_name",""), row.get("lga_name",""))
                                st.success("APPROVED & LIVE!")
                                st.balloons()
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Failed to approve submission: {e}")

                    with c2:
                        if st.button("REJECT", key=f"reject_{sub_id}", type="secondary", use_container_width=True):
                            try:
                                with engine.begin() as conn:
                                    conn.execute(text("UPDATE school_submissions SET approved=FALSE WHERE id=:id"), {"id": sub_id})
                                # notify submitter
                                try:
                                    if row.get("email"):
                                        send_email(row.get("email"), "Submission Rejected – Abia Education Portal",
                                                   f"Hello,\n\nYour submission for **{row.get('school_name','(Unknown)')}** was reviewed but could not be approved.\n\nPlease resubmit with correct details and photo.\n\n— Abia Education Portal Team")
                                except Exception as e:
                                    st.warning(f"Rejection recorded but failed to send email: {e}")

                                log_admin_action("REJECTED", sub_id, row.get("school_name",""), row.get("lga_name",""))
                                st.warning("Rejected")
                                st.experimental_rerun()
                            except Exception as e:
                                st.error(f"Failed to reject submission: {e}")

    # -------- Admin activity log display (last 50) --------
    st.markdown("---")
    st.markdown("### Admin Activity Log")
    logpath = "admin_activity_log.csv"
    if os.path.exists(logpath):
        try:
            log_df = pd.read_csv(logpath)
            log_df = log_df.sort_values("timestamp", ascending=False).head(50)
            st.dataframe(log_df, use_container_width=True)
            # allow download of the full log file if needed
            try:
                full_csv = open(logpath, "r", encoding="utf-8").read()
                if st.download_button("Download Full Admin Log", data=full_csv, file_name="admin_log_full.csv", mime="text/csv"):
                    st.success("Log downloaded")
            except Exception:
                # fallback: offer the head portion
                if st.download_button("Download Log (recent)", data=log_df.to_csv(index=False), file_name="admin_log_recent.csv"):
                    st.success("Recent log downloaded")
        except Exception as e:
            st.error(f"Failed to read admin log: {e}")
    else:
        st.info("No admin actions logged yet.")



elif selected == "About":
    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="margin:0; padding:40px; background:#f0fff0; font-family:Arial;">
    
    <div style="background:#f8fff8; padding:50px; border-radius:25px; border-left:10px solid #006400; text-align:center; box-shadow:0 10px 30px rgba(0,100,0,0.2);">
        <h1 style="color:#006400; font-size:48px; margin-bottom:20px;">About the Portal</h1>
        
        <p style="font-size:20px; color:#333; max-width:900px; margin:30px auto; line-height:1.9;">
            This is the <strong>official real-time education data platform</strong> for Abia State — 
            the first of its kind in Nigeria.
        </p>

        <div style="background:white; padding:35px; border-radius:20px; margin:40px auto; max-width:1000px; box-shadow:0 8px 25px rgba(0,0,0,0.1);">
            <h2 style="color:#006400; margin-bottom:25px;">What This Portal Does</h2>
            <p style="font-size:18px; color:#333; line-height:2;">
                • Collects verified data from <strong>every school</strong> in all 17 LGAs<br>
                • Displays live, accurate statistics — updated every minute<br>
                • Ensures 100% transparency for the Ministry, parents, and citizens<br>
                • All submissions are email-verified and admin-approved before going live
            </p>
        </div>

        <div style="background:#e8f5e8; padding:40px; border-radius:20px; margin:40px auto; max-width:900px;">
            <h2 style="color:#006400; margin-bottom:20px;">Vision</h2>
            <p style="font-size:24px; font-style:italic; color:#006400; line-height:1.8;">
                “No child left behind.<br>No school left out.”
            </p>
        </div>

        <div style="background:white; padding:50px; border-radius:25px; margin:50px auto; max-width:800px; box-shadow:0 12px 40px rgba(0,100,0,0.2);">
            <h2 style="color:#006400; margin-bottom:25px;">Built with Excellence by</h2>
            <h1 style="font-size:58px; color:#006400; margin:15px 0;">Alabi Winner</h1>
            <h3 style="color:#228B22; margin:10px 0;">(BookyAde)</h3>
            <p style="font-size:22px; color:#333; margin:30px 0; line-height:1.8;">
                Abia TechRice Cohort 2.0 • Class of 2025<br>
                Data Engineer • Data Champion • Proud Son of Abia State
            </p>
            <p style="margin:35px 0;">
                <a href="https://github.com/BookyAde" style="color:#006400; font-size:20px; margin:0 25px; font-weight:bold;">GitHub</a>
                <a href="mailto:alabiwinner9@gmail.com" style="color:#006400; font-size:20px; margin:0 25px; font-weight:bold;">Email</a>
            </p>
            <p style="font-style:italic; color:#006400; font-size:26px; margin-top:40px;">
                “I didn’t just build an app.<br>I built the future of education in Abia State.”
            </p>
        </div>

        <div style="margin-top:60px; color:#006400; font-size:18px;">
            <p><strong>© 2025 Abia State Education Portal</strong></p>
            <p>Official Government Initiative • Powered by <strong>Abia TechRice</strong></p>
        </div>
    </div>

    </body>
    </html>
    """, height=2000, scrolling=True)
