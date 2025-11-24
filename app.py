# ===================== ABIA EDUCATION PORTAL - FINAL WORKING VERSION =====================
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import pandas as pd
from sqlalchemy import create_engine, text
from passlib.context import CryptContext
import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from streamlit_autorefresh import st_autorefresh

# ===================== PASSWORD HASHING =====================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ===================== DATABASE CONNECTION =====================
engine = create_engine(
    f"postgresql+pg8000://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ===================== PAGE CONFIG & HEADER =====================
st.set_page_config(page_title="Abia Education Portal", layout="wide")
logo = Image.open("assets/Abia_logo.jpeg")
st.image(logo, width=120)

st.markdown(
    """
    <div style='text-align: center;'>
        <img src='assets/Abia_logo.jpeg' width='140'>
        <h1 style='margin-top: -5px;'>Abia State Education Data Portal</h1>
        <p style='margin-top:-15px; font-size:15px;'>Powered by Abia TechRice Cohort 2.0</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ===================== CSS STYLING =====================
st.markdown("""
<style>
.header {background: linear-gradient(90deg, #006400, #98FB98); padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;}
.card {background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1.5rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="header"><h1>Abia State Real-Time Education Portal</h1>'
    '<p>Live • Transparent • Government-Ready • Built by BookyAde</p></div>',
    unsafe_allow_html=True
)

# ===================== SIDEBAR NAVIGATION =====================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Seal_of_Abia_State.svg", width=180)
    selected = option_menu(
        "Navigation",
        ["Home", "Live Dashboard", "Register/Login", "Request Data", "Submit Data", "Admin Panel", "About Creator"],
        icons=["house", "bar-chart", "person-check", "cloud-download", "upload", "shield-lock", "person-circle"],
        menu_icon="cast",
        default_index=0,
    )

# ===================== HELPER FUNCTIONS =====================
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = st.secrets['EMAIL']['EMAIL_USER']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP_SSL(st.secrets['EMAIL']['SMTP_SERVER'], int(st.secrets['EMAIL']['SMTP_PORT']))
        server.login(st.secrets['EMAIL']['EMAIL_USER'], st.secrets['EMAIL']['EMAIL_PASS'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

@st.cache_data(ttl=60)
def load_dashboard_data():
    query = text("""
        SELECT l.lga_name,
               COALESCE(SUM(f.enrollment_total), 0) AS students,
               COALESCE(SUM(f.teachers_total), 0) AS teachers,
               ROUND(COALESCE(SUM(f.enrollment_total)::NUMERIC / NULLIF(SUM(f.teachers_total), 0), 0), 1) AS pupil_teacher_ratio
        FROM dwh.fact_abia_metrics f
        JOIN dwh.dim_lga l ON f.lga_key = l.lga_key
        WHERE f.approved = TRUE
        GROUP BY l.lga_name
        ORDER BY students DESC
    """)
    return pd.read_sql(query, engine)

def generate_excel_from_db():
    try:
        df = pd.read_sql("SELECT * FROM school_submissions WHERE approved = TRUE ORDER BY submitted_at DESC", engine)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Approved Submissions')
        output.seek(0)
        return output
    except Exception as e:
        st.error(f"Excel generation failed: {e}")
        return None

# ===================== SAVE SUBMISSION (WORKS WITH YOUR CURRENT TABLE) =====================
def save_school_submission(school_name, lga_name, enrollment_total, teachers_total, submitted_by):
    query = text("""
        INSERT INTO school_submissions
        (school_name, lga_name, enrollment_total, teachers_total, submitted_by, submitted_at, approved)
        VALUES (:school_name, :lga_name, :enrollment_total, :teachers_total, :submitted_by, NOW(), NULL)
    """)
    params = {
        'school_name': school_name,
        'lga_name': lga_name,
        'enrollment_total': int(enrollment_total),
        'teachers_total': int(teachers_total),
        'submitted_by': submitted_by
    }
    try:
        with engine.begin() as conn:
            conn.execute(query, params)
        return True
    except Exception as e:
        st.error(f"Submission failed: {e}")
        return False

# ===================== PAGES =====================
if selected == "Home":
    st.markdown("<div class='card'><h2>Welcome to Abia State Education Revolution</h2>"
                "<p>Real-time monitoring of schools across all 17 LGAs.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("LGAs", "17")
    c2.metric("Schools Connected", "250+")
    c3.metric("Status", "LIVE")

elif selected == "Live Dashboard":
    st.markdown("<div class='card'><h2>Live Statistics - Abia State 2024</h2></div>", unsafe_allow_html=True)
    st_autorefresh(interval=60000, key="refresh")
    df = load_dashboard_data()
    if df.empty:
        st.info("No approved data yet. Submit and approve entries to see live stats.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Total Students by LGA")
            st.bar_chart(df.set_index("lga_name")["students"])
        with col2:
            st.subheader("Pupil-Teacher Ratio")
            st.bar_chart(df.set_index("lga_name")["pupil_teacher_ratio"])
        st.dataframe(df.style.format({"students": "{:,}", "teachers": "{:,}"}))

elif selected == "Register/Login":
    st.markdown("<div class='card'><h2>Register or Login</h2></div>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", key="login_btn"):
            if not username or not password:
                st.error("Fill both fields")
            else:
                try:
                    result = pd.read_sql("SELECT password_hash, is_admin FROM users WHERE username = :u", engine, params={"u": username})
                    if not result.empty and pwd_context.verify(password, result.iloc[0]['password_hash']):
                        st.session_state.logged_in = True
                        st.session_state.user = username
                        st.session_state.is_admin = result.iloc[0]['is_admin']
                        st.success(f"Welcome, {username}!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Invalid credentials")
                except:
                    st.error("Login failed")

    with tab2:
        st.subheader("Register New Account")
        new_user = st.text_input("Username", key="reg_user")
        new_email = st.text_input("Email", key="reg_email")
        new_pass = st.text_input("Password", type="password", key="reg_pass")
        confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        if st.button("Register", key="reg_btn"):
            if new_pass != confirm:
                st.error("Passwords don't match")
            elif len(new_pass) < 6:
                st.error("Password too short")
            else:
                hashed = pwd_context.hash(new_pass)
                try:
                    with engine.begin() as conn:
                        conn.execute(text("INSERT INTO users (username, password_hash, email) VALUES (:u, :p, :e)"),
                                   {"u": new_user, "p": hashed, "e": new_email})
                    st.success("Account created! Now login.")
                    st.balloons()
                except:
                    st.error("Username or email taken")

    if st.session_state.get("logged_in"):
        st.success(f"Logged in as: {st.session_state.user}")
        if st.button("Logout"):
            for k in ["logged_in", "user", "is_admin"]:
                st.session_state.pop(k, None)
            st.rerun()

elif selected == "Submit Data":
    st.markdown("<div class='card'><h2>Submit School Data</h2></div>", unsafe_allow_html=True)
    lgas = pd.read_sql("SELECT lga_name FROM dwh.dim_lga ORDER BY lga_name", engine)['lga_name'].tolist()
    with st.form("submit_form"):
        school_name = st.text_input("School Name *")
        lga_name = st.selectbox("LGA *", lgas)
        enrollment_total = st.number_input("Total Students *", min_value=0, step=1)
        teachers_total = st.number_input("Total Teachers *", min_value=0, step=1)
        submitted_by = st.text_input("Your Name *")
        submitted = st.form_submit_button("Submit for Approval")
        if submitted:
            if save_school_submission(school_name, lga_name, enrollment_total, teachers_total, submitted_by):
                st.success("Submitted! Awaiting approval.")
                st.balloons()

elif selected == "Request Data":
    st.markdown("<div class='card'><h2>Download Approved Data</h2></div>", unsafe_allow_html=True)
    if st.button("Generate Excel File"):
        file = generate_excel_from_db()
        if file:
            st.download_button("Download Abia_Education_Data.xlsx", file, "Abia_Education_Data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            st.success("Ready!")
        else:
            st.error("No approved data")

elif selected == "Admin Panel":
    if not st.session_state.get("logged_in") or not st.session_state.get("is_admin"):
        st.warning("Login as admin first")
        st.stop()

    st.markdown("<div class='card'><h2>Admin Panel</h2></div>", unsafe_allow_html=True)
    pending = pd.read_sql("SELECT * FROM school_submissions WHERE approved IS NULL ORDER BY submitted_at DESC", engine)
    if pending.empty:
        st.info("No pending submissions")
    else:
        for _, row in pending.iterrows():
            with st.expander(f"{row['school_name']} - {row['lga_name']}"):
                st.write(f"**By:** {row['submitted_by']} | **Students:** {row['enrollment_total']:,} | **Teachers:** {row['teachers_total']:,}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Approve", key=f"app_{row['id']}"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE school_submissions SET approved=TRUE WHERE id=:id"), {"id": row['id']})
                            conn.execute(text("""
                                INSERT INTO dwh.fact_abia_metrics (lga_key, enrollment_total, teachers_total, approved)
                                SELECT l.lga_key, :e, :t, TRUE FROM dwh.dim_lga l WHERE l.lga_name = :lga
                            """), {"e": row['enrollment_total'], "t": row['teachers_total'], "lga": row['lga_name']})
                        st.success("Approved & Published!")
                        st.rerun()
                with c2:
                    if st.button("Reject", key=f"rej_{row['id']}"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE school_submissions SET approved=FALSE WHERE id=:id"), {"id": row['id']})
                        st.warning("Rejected")
                        st.rerun()

elif selected == "About Creator":
    st.markdown(
        "<div class='card'><h2>Creator: Alabi Winner (BookyAde)</h2>"
        "<p>Abia TechRice Cohort 2.0<br>"
        "<a href='https://github.com/BookyAde'>github.com/BookyAde</a><br>"
        "<a href='mailto:alabiwinner9@gmail.com'>alabiwinner9@gmail.com</a></p></div>",
        unsafe_allow_html=True
    )
    st.balloons()