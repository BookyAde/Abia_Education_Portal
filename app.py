# ===================== APP.PY - FINAL VERSION =====================
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import pandas as pd
from sqlalchemy import create_engine
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
from sqlalchemy import create_engine

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
    '<div class="header"><h1>🏛️ Abia State Real-Time Education Portal</h1>'
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
            msg.add_attachment(
                attachment.read(),
                maintype='application',
                subtype='vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                filename=attachment_name
            )

        smtp_server = st.secrets['EMAIL']['SMTP_SERVER']
        smtp_port = st.secrets['EMAIL']['SMTP_PORT']
        user = st.secrets['EMAIL']['EMAIL_USER']
        password = st.secrets['EMAIL']['EMAIL_PASS']

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()

        server.login(user, password)
        server.send_message(msg)
        server.quit()
        return True

    except Exception as e:
        st.error(f"Failed to send email: {e}")
        return False


# ===================== LOAD DASHBOARD DATA =====================
@st.cache_data(ttl=30)
def load_dashboard_data():
    query = """
        SELECT l.lga_name,
               COALESCE(SUM(f.enrollment_total),0) AS students,
               COALESCE(SUM(f.teachers_total),0) AS teachers,
               ROUND(
                    COALESCE(SUM(f.enrollment_total)::NUMERIC / NULLIF(SUM(f.teachers_total),0),0),
                    1
               ) AS pupil_teacher_ratio
        FROM dwh.fact_abia_metrics f
        JOIN dwh.dim_lga l ON f.lga_key = l.lga_key
        WHERE f.approved = TRUE
        GROUP BY l.lga_name
        ORDER BY students DESC
    """
    return pd.read_sql(query, engine)


# ===================== SAVE SCHOOL SUBMISSION =====================
def save_school_submission(school_name, lga_name, enrollment_total, teachers_total, submitted_by, email):
    query = """
        INSERT INTO school_submissions
        (school_name, lga_name, enrollment_total, teachers_total, submitted_by, email, submitted_at, approved)
        VALUES (:school_name, :lga_name, :enrollment_total, :teachers_total, :submitted_by, :email, NOW(), NULL)
    """

    params = {
        'school_name': school_name,
        'lga_name': lga_name,
        'enrollment_total': enrollment_total,
        'teachers_total': teachers_total,
        'submitted_by': submitted_by,
        'email': email
    }

    try:
        with engine.connect() as conn:
            conn.execute(query, params)
        return True
    except Exception as e:
        st.error(f"Failed to submit data: {e}")
        return False


# ===================== GENERATE EXCEL FILE =====================
def generate_excel_from_db():
    try:
        df = pd.read_sql("SELECT * FROM school_submissions WHERE approved = TRUE ORDER BY submitted_at ASC", engine)
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name="Approved Submissions")
            writer.save()

        output.seek(0)
        return output

    except Exception as e:
        st.error(f"Failed to generate Excel: {e}")
        return None


# ===================== PAGE: HOME =====================
if selected == "Home":
    st.markdown("<div class='card'><h2>Welcome to Abia State Education Revolution</h2>"
                "<p>Real-time monitoring of education and teacher distribution across all 17 LGAs.</p></div>",
                unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("LGAs", "17")
    c2.metric("Schools Connected", "250+")
    c3.metric("Status", "LIVE")


# ===================== PAGE: LIVE DASHBOARD =====================
elif selected == "Live Dashboard":
    st.markdown("<div class='card'><h2>Live Statistics - Abia State 2024</h2></div>", unsafe_allow_html=True)
    st_autorefresh(interval=60000, key="dashboard_refresh")

    try:
        df = load_dashboard_data()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🏫 Total Enrollment by LGA")
            st.bar_chart(df.set_index("lga_name")["students"])
        with col2:
            st.subheader("👩‍🏫 Pupil-Teacher Ratio")
            st.bar_chart(df.set_index("lga_name")["pupil_teacher_ratio"])

        st.dataframe(df)

    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")


# ===================== PAGE: SUBMIT DATA =====================
elif selected == "Submit Data":
    st.markdown("<div class='card'><h2>Submit School Data</h2></div>", unsafe_allow_html=True)

    lga_df = pd.read_sql("SELECT lga_name FROM dwh.dim_lga ORDER BY lga_name", engine)
    lga_options = lga_df['lga_name'].tolist()

    with st.form("school_submission_form"):
        school_name = st.text_input("School Name")
        lga_name = st.selectbox("LGA", lga_options)
        enrollment_total = st.number_input("Total Students", min_value=0)
        teachers_total = st.number_input("Total Teachers", min_value=0)
        submitted_by = st.text_input("Your Name")
        email = st.text_input("Email Address")

        submitted = st.form_submit_button("Submit")

        if submitted:
            if not all([school_name, lga_name, submitted_by, email]):
                st.error("Fill all fields.")
            else:
                save_school_submission(school_name, lga_name, enrollment_total, teachers_total, submitted_by, email)
                st.success("✔️ Submission received. Await admin approval.")


# ===================== PAGE: REQUEST DATA =====================
elif selected == "Request Data":
    st.markdown("<div class='card'><h2>Request Full Dataset</h2></div>", unsafe_allow_html=True)

    with st.form("request_form"):
        name = st.text_input("Your Name")
        email = st.text_input("Your Email")
        purpose = st.text_input("Purpose")

        submitted = st.form_submit_button("Submit Request")

        if submitted:
            excel_file = generate_excel_from_db()

            if excel_file:
                send_email(
                    email,
                    "Abia State Education Dataset",
                    f"Hello {name},\n\nYour request has been received.\n\nPurpose: {purpose}",
                    attachment=excel_file,
                    attachment_name="Abia_State_Dataset.xlsx"
                )
                st.success("✔️ Dataset sent successfully")


# ===================== PAGE: ADMIN PANEL =====================
elif selected == "Admin Panel":
    st.markdown("<div class='card'><h2>Administrator Review Panel</h2></div>", unsafe_allow_html=True)

    password = st.text_input("Enter Admin Password", type="password")

    if password != "abia_admin_2025":
        st.warning("Enter correct admin password.")
        st.stop()

    st.success("Admin Access Granted")

    st.subheader("Pending Submissions")

    try:
        pending_df = pd.read_sql(
            "SELECT * FROM school_submissions WHERE approved IS NULL ORDER BY submitted_at ASC",
            engine
        )

        if pending_df.empty:
            st.info("No pending submissions.")
        else:
            for idx, row in pending_df.iterrows():
                st.markdown(f"### {row['school_name']} ({row['lga_name']})")
                st.write(f"📅 {row['submitted_at']}")
                st.write(f"👤 {row['submitted_by']} | 📧 {row['email']}")
                st.write(f"Students: {row['enrollment_total']} | Teachers: {row['teachers_total']}")

                col1, col2 = st.columns(2)

                # APPROVE
                with col1:
                    if st.button(f"Approve {row['id']}", key=f"a{row['id']}"):
                        engine.execute("UPDATE school_submissions SET approved=TRUE WHERE id=%s", (row['id'],))
                        
                        # NEW CODE: Insert approved data into fact_abia_metrics
                        insert_query = """
                            INSERT INTO dwh.fact_abia_metrics (lga_key, enrollment_total, teachers_total, approved)
                            SELECT l.lga_key, %s, %s, TRUE
                            FROM dwh.dim_lga l
                            WHERE l.lga_name = %s
                        """
                        with engine.connect() as conn:
                            conn.execute(insert_query, (row['enrollment_total'], row['teachers_total'], row['lga_name']))
                        
                        send_email(
                            row['email'],
                            "Submission Approved",
                            f"Hello {row['submitted_by']},\n\nYour submission has been approved."
                        )
                        st.success("Approved and email sent.")
                        st.rerun()

                # REJECT
                with col2:
                    if st.button(f"Reject {row['id']}", key=f"r{row['id']}"):
                        engine.execute("UPDATE school_submissions SET approved=FALSE WHERE id=%s", (row['id'],))
                        send_email(
                            row['email'],
                            "Submission Rejected",
                            f"Hello {row['submitted_by']},\n\nYour submission has been rejected."
                        )
                        st.warning("Rejected and email sent.")
                        st.rerun()

    except Exception as e:
        st.error(f"Error loading admin data: {e}")


# ===================== PAGE: ABOUT CREATOR =====================
elif selected == "About Creator":
    st.markdown(
        "<div class='card'><h2>Creator: Alabi Winner (BookyAde)</h2>"
        "<p>Beneficiary of Abia TechRice Cohort 2.0<br>"
        "GitHub: <a href='https://github.com/BookyAde'>github.com/BookyAde</a><br>"
        "Email: <a href='mailto:alabiwinner9@gmail.com'>alabiwinner9@gmail.com</a></p></div>",
        unsafe_allow_html=True
    )
    st.balloons()