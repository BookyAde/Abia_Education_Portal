# ===================== APP.PY - FINAL WORKING VERSION =====================
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import pandas as pd
from sqlalchemy import create_engine, text
import io
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from streamlit_autorefresh import st_autorefresh


# ----------------- PORTAL HEADER LOGO -----------------
logo = Image.open("assets/Abia_logo.jpeg")
st.image(logo, width=120)


# ----------------- HTML HEADER -----------------
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


# ===================== DATABASE CONNECTION =====================
engine = create_engine(
    f"postgresql+pg8000://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


# ===================== CSS =====================
st.markdown("""
<style>
.header {background: linear-gradient(90deg, #006400, #98FB98); padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;}
.card {background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1rem 0;}
</style>
""", unsafe_allow_html=True)


# ===================== TOP HEADER =====================
st.markdown(
    '<div class="header"><h1>Abia State Real-Time Education Portal</h1>'
    '<p>Live • Transparent • Government-Ready • Built by BookyAde</p></div>',
    unsafe_allow_html=True
)


# ===================== SIDEBAR =====================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Seal_of_Abia_State.svg", width=180)
    selected = option_menu(
        "Navigation",
        ["Home", "Live Dashboard", "Register/Login", "Request Data", "Submit Data", "Admin Panel", "About Creator"],
        icons=["house", "bar-chart", "person-check", "cloud-download", "upload", "shield-lock", "person-circle"],
        menu_icon="cast",
        default_index=0,
    )


# ===================== EMAIL FUNCTION =====================
def send_email(to_email, subject, body, attachment=None, attachment_name=None):
    try:
        msg = MIMEMultipart()
        msg['Subject'] = subject
        msg['From'] = st.secrets['EMAIL']['EMAIL_USER']
        msg['To'] = to_email
        msg.attach(MIMEText(body, 'plain'))

        if attachment and attachment_name:
            part = MIMEText(attachment.read(), 'base64', 'utf-8')
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment_name}'
            )
            msg.attach(part)

        smtp_server = st.secrets['EMAIL']['SMTP_SERVER']
        smtp_port = int(st.secrets['EMAIL']['SMTP_PORT'])
        user = st.secrets['EMAIL']['EMAIL_USER']
        password = st.secrets['EMAIL']['EMAIL_PASS']

        server = smtplib.SMTP_SSL(smtp_server, smtp_port) if smtp_port == 465 else smtplib.SMTP(smtp_server, smtp_port)
        if smtp_port != 465:
            server.starttls()
        server.login(user, password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False


# ===================== LOAD DASHBOARD DATA =====================
@st.cache_data(ttl=60)
def load_dashboard_data():
    query = """
        SELECT l.lga_name,
               COALESCE(SUM(f.enrollment_total), 0) AS students,
               COALESCE(SUM(f.teachers_total), 0) AS teachers,
               ROUND(
                   COALESCE(SUM(f.enrollment_total)::NUMERIC / NULLIF(SUM(f.teachers_total), 0), 0), 1
               ) AS pupil_teacher_ratio
        FROM dwh.fact_abia_metrics f
        JOIN dwh.dim_lga l ON f.lga_key = l.lga_key
        WHERE f.approved = TRUE
        GROUP BY l.lga_name
        ORDER BY students DESC
    """
    return pd.read_sql(query, engine)


# ===================== SAVE SCHOOL SUBMISSION - FIXED =====================
def save_school_submission(school_name, lga_name, enrollment_total, teachers_total, submitted_by, email):
    query = text("""
        INSERT INTO school_submissions
        (school_name, lga_name, enrollment_total, teachers_total, submitted_by, email, submitted_at, approved)
        VALUES (:school_name, :lga_name, :enrollment_total, :teachers_total, :submitted_by, :email, NOW(), NULL)
    """)

    params = {
        'school_name': school_name,
        'lga_name': lga_name,
        'enrollment_total': int(enrollment_total),
        'teachers_total': int(teachers_total),
        'submitted_by': submitted_by,
        'email': email
    }

    try:
        with engine.begin() as conn:  # Automatically commits on success
            conn.execute(query, params)
        return True
    except Exception as e:
        st.error(f"Failed to submit data: {e}")
        return False


# ===================== GENERATE EXCEL FILE =====================
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
    st_autorefresh(interval=60000, key="data_refresh")

    df = load_dashboard_data()
    if df.empty:
        st.info("No approved data yet. Submit and approve school data to see live stats.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Total Enrollment by LGA")
            st.bar_chart(df.set_index("lga_name")["students"])
        with col2:
            st.subheader("Pupil-Teacher Ratio")
            st.bar_chart(df.set_index("lga_name")["pupil_teacher_ratio"])
        st.dataframe(df.style.format({"students": "{:,}", "teachers": "{:,}"}))

elif selected == "Submit Data":
    st.markdown("<div class='card'><h2>Submit School Data</h2></div>", unsafe_allow_html=True)

    lga_df = pd.read_sql("SELECT lga_name FROM dwh.dim_lga ORDER BY lga_name", engine)
    lga_options = lga_df['lga_name'].tolist()

    with st.form("school_submission_form"):
        school_name = st.text_input("School Name *")
        lga_name = st.selectbox("LGA *", lga_options)
        enrollment_total = st.number_input("Total Students *", min_value=0, step=1)
        teachers_total = st.number_input("Total Teachers *", min_value=0, step=1)
        submitted_by = st.text_input("Your Name *")
        email = st.text_input("Your Email *")

        submitted = st.form_submit_button("Submit for Approval")

        if submitted:
            if not all([school_name, lga_name, enrollment_total, teachers_total, submitted_by, email]):
                st.error("Please fill all required fields.")
            else:
                if save_school_submission(school_name, lga_name, enrollment_total, teachers_total, submitted_by, email):
                    st.success("Submission received! Awaiting admin approval.")
                    st.balloons()

elif selected == "Request Data":
    st.markdown("<div class='card'><h2>Request Full Dataset</h2></div>", unsafe_allow_html=True)
    with st.form("request_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        purpose = st.text_area("Purpose of Request")
        sent = st.form_submit_button("Send Dataset")
        if sent:
            excel = generate_excel_from_db()
            if excel and send_email(email, "Abia Education Dataset", f"Hi {name},\n\nAttached is the approved dataset.\nPurpose: {purpose}", excel, "Abia_Education_Data.xlsx"):
                st.success("Dataset sent to your email!")

elif selected == "Admin Panel":
    st.markdown("<div class='card'><h2>Administrator Panel</h2></div>", unsafe_allow_html=True)
    password = st.text_input("Admin Password", type="password")
    if password != "abia_admin_2025":
        st.warning("Incorrect password.")
        st.stop()

    st.success("Access Granted")

    pending = pd.read_sql("SELECT * FROM school_submissions WHERE approved IS NULL ORDER BY submitted_at DESC", engine)
    if pending.empty:
        st.info("No pending submissions.")
    else:
        for _, row in pending.iterrows():
            with st.expander(f"{row['school_name']} - {row['lga_name']} | Submitted by {row['submitted_by']}"):
                st.write(f"Students: {row['enrollment_total']:,} | Teachers: {row['teachers_total']:,}")
                st.write(f"Email: {row['email']} | Date: {row['submitted_at']}")

                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Approve", key=f"approve_{row['id']}"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE school_submissions SET approved=TRUE WHERE id=:id"), {"id": row['id']})
                            conn.execute(text("""
                                INSERT INTO dwh.fact_abia_metrics (lga_key, enrollment_total, teachers_total, approved)
                                SELECT l.lga_key, :enrollment, :teachers, TRUE
                                FROM dwh.dim_lga l WHERE l.lga_name = :lga
                            """), {
                                "enrollment": row['enrollment_total'],
                                "teachers": row['teachers_total'],
                                "lga": row['lga_name']
                            })
                        send_email(row['email'], "Submission Approved!", f"Dear {row['submitted_by']},\n\nYour data has been approved and is now live on the portal.")
                        st.success("Approved & Live!")
                        st.rerun()
                with c2:
                    if st.button("Reject", key=f"reject_{row['id']}"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE school_submissions SET approved=FALSE WHERE id=:id"), {"id": row['id']})
                        send_email(row['email'], "Submission Rejected", f"Dear {row['submitted_by']},\n\nYour submission was not approved.")
                        st.warning("Rejected")
                        st.rerun()

elif selected == "About Creator":
    st.markdown(
        "<div class='card'><h2>Creator: Alabi Winner (BookyAde)</h2>"
        "<p>Abia TechRice Cohort 2.0 Beneficiary<br>"
        "<a href='https://github.com/BookyAde'>github.com/BookyAde</a><br>"
        "<a href='mailto:alabiwinner9@gmail.com, winalabi@yahoo.com'>alabiwinner9@gmail.com</a></p></div>",
        unsafe_allow_html=True
    )
    st.balloons()