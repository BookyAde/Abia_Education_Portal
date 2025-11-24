# ===================== ABIA STATE EDUCATION PORTAL - GRAND FINAL EDITION =====================
# Created with pride by Alabi Winner (BookyAde) — Abia TechRice Cohort 2.0
# Default Admin → Username: admin | Password: Booky123

import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import pandas as pd
from sqlalchemy import create_engine, text
import io
import os
from streamlit_autorefresh import st_autorefresh

# ===================== DATABASE CONNECTION =====================
engine = create_engine(
    f"postgresql+pg8000://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ===================== PAGE CONFIG & LUXURY HEADER =====================
st.set_page_config(page_title="Abia Education Portal • BookyAde", layout="wide", page_icon="🇳🇬")

# Logo & Hero Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    logo = Image.open("assets/Abia_logo.jpeg")
    st.image(logo, width=140)
    st.markdown(
        "<h1 style='text-align:center; color:#006400; margin-top:-10px;'>Abia State Education Portal</h1>"
        "<p style='text-align:center; font-size:18px; color:#333;'>Powered by Abia TechRice Cohort 2.0 • Built by BookyAde</p>",
        unsafe_allow_html=True
    )

# Grand Header Banner
st.markdown("""
<style>
.grand-header {
    background: linear-gradient(90deg, #006400, #228B22, #32CD32);
    padding: 2.5rem;
    border-radius: 20px;
    text-align: center;
    color: white;
    box-shadow: 0 10px 30px rgba(0,100,0,0.3);
    margin-bottom: 2rem;
}
.card {background: white; padding: 2rem; border-radius: 18px; box-shadow: 0 6px 20px rgba(0,0,0,0.1); margin: 1.5rem 0;}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="grand-header">'
    '<h1>Abia State Real-Time Education Portal</h1>'
    '<p>Live • Transparent • Government-Ready • Built with Excellence by BookyAde</p>'
    '</div>', 
    unsafe_allow_html=True
)

# ===================== SIDEBAR WITH ELEGANCE =====================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Seal_of_Abia_State.svg", width=200)
    st.markdown("<h2 style='text-align:center; color:#006400;'>Navigation</h2>", unsafe_allow_html=True)
    
    selected = option_menu(
        None,
        ["Home", "Live Dashboard", "Register/Login", "Request Data", "Submit Data", "Admin Panel", "About Creator"],
        icons=["house-fill", "graph-up", "person-lock", "cloud-download", "upload", "shield-lock-fill", "star-fill"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#f0f2f6"},
            "icon": {"color": "#006400", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px"},
            "nav-link-selected": {"background-color": "#006400"},
        }
    )

# ===================== AUTO-REFRESH DASHBOARD =====================
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

def generate_excel():
    df = pd.read_sql("SELECT * FROM school_submissions WHERE approved = TRUE ORDER BY submitted_at DESC", engine)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Approved Submissions')
    output.seek(0)
    return output

# ===================== SUBMISSION FUNCTION =====================
def save_submission(school_name, lga_name, enrollment, teachers, name):
    query = text("""
        INSERT INTO school_submissions 
        (school_name, lga_name, enrollment_total, teachers_total, submitted_by, submitted_at, approved)
        VALUES (:s, :l, :e, :t, :n, NOW(), NULL)
    """)
    try:
        with engine.begin() as conn:
            conn.execute(query, {"s": school_name, "l": lga_name, "e": int(enrollment), "t": int(teachers), "n": name})
        return True
    except Exception as e:
        st.error(f"Submission failed: {e}")
        return False

# ===================== PAGES =====================
if selected == "Home":
    st.markdown("<div class='card'><h2>Welcome to the Future of Education in Abia State</h2>"
                "<p>Real-time, transparent, and government-ready data collection across all 17 LGAs.</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Local Government Areas", "17")
    with c2: st.metric("Schools Connected", "250+")
    with c3: st.metric("System Status", "LIVE", delta="Real-time")

elif selected == "Live Dashboard":
    st.markdown("<div class='card'><h2>Live Education Statistics • 2024/2025</h2></div>", unsafe_allow_html=True)
    st_autorefresh(interval=60000, key="auto")
    df = load_dashboard_data()
    if df.empty:
        st.info("No approved data yet. Submit and approve school records to see live statistics.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Total Students by LGA")
            st.bar_chart(df.set_index("lga_name")["students"], height=500)
        with col2:
            st.subheader("Pupil-Teacher Ratio")
            st.bar_chart(df.set_index("lga_name")["pupil_teacher_ratio"], height=500)
        st.dataframe(df.style.format({"students": "{:,}", "teachers": "{:,}", "pupil_teacher_ratio": "{:.1f}"}))

elif selected == "Register/Login":
    st.markdown("<div class='card'><h2>Administrator Login</h2></div>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        st.write("**Default Admin Account**")
        st.write("Username: `admin` • Password: `Booky123`")
        username = st.text_input("Username", value="admin")
        password = st.text_input("Password", type="password", value="Booky123")
        login = st.form_submit_button("Login as Administrator")

        if login:
            if username == "admin" and password == "Booky123":
                st.session_state.logged_in = True
                st.session_state.is_admin = True
                st.session_state.user = "BookyAde"
                st.success("Welcome back, BookyAde! You are now in full control.")
                st.balloons()
                st.rerun()
            else:
                st.error("Incorrect credentials")

    if st.session_state.get("logged_in"):
        st.success(f"Logged in as **{st.session_state.user}**")
        if st.button("Logout"):
            st.session_state.clear()
            st.rerun()

elif selected == "Submit Data":
    st.markdown("<div class='card'><h2>Submit School Data</h2></div>", unsafe_allow_html=True)
    lgas = pd.read_sql("SELECT lga_name FROM dwh.dim_lga ORDER BY lga_name", engine)['lga_name'].tolist()
    
    with st.form("submission_form"):
        st.markdown("### Enter Accurate School Information")
        school_name = st.text_input("School Name")
        lga_name = st.selectbox("LGA", lgas)
        enrollment = st.number_input("Total Students", min_value=1, step=1)
        teachers = st.number_input("Total Teachers", min_value=1, step=1)
        submitted_by = st.text_input("Your Full Name")
        submitted = st.form_submit_button("Submit for Approval")

        if submitted:
            if save_submission(school_name, lga_name, enrollment, teachers, submitted_by):
                st.success("Thank you! Your submission has been received and is awaiting approval.")
                st.balloons()

elif selected == "Request Data":
    st.markdown("<div class='card'><h2>Download Approved Dataset</h2></div>", unsafe_allow_html=True)
    if st.button("Generate & Download Excel Report", type="primary"):
        file = generate_excel()
        st.download_button(
            label="Download Abia_Education_Data.xlsx",
            data=file,
            file_name="Abia_Education_Data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        st.success("Report ready for download!")

elif selected == "Admin Panel":
    if not st.session_state.get("logged_in"):
        st.warning("Please login as admin from the Register/Login page")
        st.stop()

    st.markdown("<div class='card'><h2>Administrator Control Panel</h2></div>", unsafe_allow_html=True)
    st.success(f"Welcome, **{st.session_state.user}** — Full access granted")

    pending = pd.read_sql("SELECT * FROM school_submissions WHERE approved IS NULL ORDER BY submitted_at DESC", engine)
    if pending.empty:
        st.info("No pending submissions at this time.")
    else:
        for _, row in pending.iterrows():
            with st.expander(f"{row['school_name']} • {row['lga_name']} • Submitted by {row['submitted_by']}"):
                st.write(f"**Students:** {row['enrollment_total']:,} | **Teachers:** {row['teachers_total']:,}")
                st.write(f"**Date:** {row['submitted_at']}")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Approve & Publish", key=f"app_{row['id']}"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE school_submissions SET approved=TRUE WHERE id=:id"), {"id": row['id']})
                            conn.execute(text("""
                                INSERT INTO dwh.fact_abia_metrics (lga_key, enrollment_total, teachers_total, approved)
                                SELECT l.lga_key, :e, :t, TRUE FROM dwh.dim_lga l WHERE l.lga_name = :lga
                            """), {"e": row['enrollment_total'], "t": row['teachers_total'], "lga": row['lga_name']})
                        st.success("Approved and now LIVE on dashboard!")
                        st.rerun()
                with c2:
                    if st.button("Reject", key=f"rej_{row['id']}"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE school_submissions SET approved=FALSE WHERE id=:id"), {"id": row['id']})
                        st.warning("Submission rejected")
                        st.rerun()

elif selected == "About Creator":
    st.markdown(
        "<div class='card'>"
        "<h2>Creator: Alabi Winner (BookyAde)</h2>"
        "<p style='font-size:18px;'>Abia TechRice Cohort 2.0 • Full-Stack Developer</p>"
        "<p>GitHub: <a href='https://github.com/BookyAde'>github.com/BookyAde</a><br>"
        "Email: <a href='mailto:alabiwinner9@gmail.com'>alabiwinner9@gmail.com</a></p>"
        "<p style='font-style:italic; color:#006400;'>“Building the future of education, one line of code at a time.”</p>"
        "</div>",
        unsafe_allow_html=True
    )
    st.balloons()

# ===================== FOOTER =====================
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#666;'>© 2025 Abia State Education Portal • Built with ❤️ by BookyAde</p>",
    unsafe_allow_html=True
)