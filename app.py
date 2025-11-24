# ===================== ABIA EDUCATION PORTAL - PROFESSIONAL & SECURE =====================
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


st.set_page_config(page_title="Abia State Education Portal", layout="wide", page_icon="")

# ===================== DATABASE CONNECTION =====================
engine = create_engine(
    f"postgresql+pg8000://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ===================== PROFESSIONAL EMAIL SETUP =====================
def send_professional_email(to_email, subject, body_html):
    try:
        msg = MIMEMultipart("alternative")
        msg['From'] = st.secrets['EMAIL']['EMAIL_USER']
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body_html, 'html'))

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(st.secrets['EMAIL']['EMAIL_USER'], st.secrets['EMAIL']['EMAIL_PASS'])
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# ===================== VERIFICATION & SUBMISSION =====================
def send_verification_code(email):
    code = random.randint(100000, 999999)
    st.session_state.verification_code = code
    st.session_state.pending_email = email

    html = f"""
    <div style="font-family:Arial,sans-serif; max-width:600px; margin:auto; border:2px solid #006400; border-radius:10px; padding:20px;">
        <h2 style="color:#006400; text-align:center;">Abia State Education Portal</h2>
        <p>Dear School Administrator,</p>
        <p>Your school is submitting data to the official Abia State Education Portal.</p>
        <p><strong>Verification Code: <h1 style="display:inline; color:#006400;">{code}</h1></strong></p>
        <p>This code expires in 10 minutes.</p>
        <hr>
        <p style="color:#666; font-size:12px;">Abia State Ministry of Education • Real-Time Data Initiative</p>
    </div>
    """
    send_professional_email(email, "Verify Your School Submission", html)

def save_submission_with_email(school_name, lga_name, enrollment, teachers, name, email):
    query = text("""
        INSERT INTO school_submissions 
        (school_name, lga_name, enrollment_total, teachers_total, submitted_by, email, submitted_at, approved)
        VALUES (:s, :l, :e, :t, :n, :em, NOW(), NULL)
    """)
    try:
        with engine.begin() as conn:
            conn.execute(query, {"s": school_name, "l": lga_name, "e": int(enrollment), 
                               "t": int(teachers), "n": name, "em": email})
        # Success email
        success_html = f"""
        <div style="font-family:Arial; max-width:600px; margin:auto; border:2px solid #006400; padding:20px; border-radius:10px;">
            <h2 style="color:#006400; text-align:center;">Submission Received ✓</h2>
            <p>Dear {name},</p>
            <p>Thank you for submitting data for <strong>{school_name}</strong>, {lga_name} LGA.</p>
            <p>Your submission has been received and is awaiting verification by the Ministry.</p>
            <p>You will receive another email once your data is approved and goes live on the portal.</p>
            <br>
            <p>Best regards,<br><strong>Abia State Ministry of Education</strong></p>
        </div>
        """
        send_professional_email(email, "School Data Received – Abia Education Portal", success_html)
        return True
    except Exception as e:
        st.error("Database error. Contact admin.")
        return False

# ===================== PAGE LAYOUT =====================
st.set_page_config(page_title="Abia Education Portal", layout="centered")
logo = Image.open("assets/Abia_logo.jpeg")
st.image(logo, width=130)
st.markdown("<h1 style='text-align:center; color:#006400;'>Abia State Education Data Portal</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Official • Verified • Real-Time</p>", unsafe_allow_html=True)

# ===================== ULTRA BEAUTIFUL & ANIMATED SIDEBAR =====================
with st.sidebar:
    # Logo at the top
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Seal_of_Abia_State.svg", width=180)
    st.markdown("<h2 style='text-align:center; color:#006400; margin-top:-10px;'>Abia Education Portal</h2>", unsafe_allow_html=True)
    
    # Custom CSS for the sidebar (smooth hover, modern look)
    st.markdown("""
    <style>
        /* Smooth transition when opening/closing */
        .css-1d391kg {transition: all 0.4s ease;}
        
        /* Beautiful menu items */
        .css-1v0mbdj a {
            border-radius: 15px !important;
            margin: 8px 10px !important;
            padding: 15px 12px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            border-left: 5px solid transparent;
        }
        
        /* Hover effect */
        .css-1v0mbdj a:hover {
            background-color: rgba(50, 205, 50, 0.2) !important;
            border-left: 5px solid #32CD32 !important;
            transform: translateX(8px);
        }
        
        /* Active selected item */
        .css-1v0mbdj a[data-baseweb="menu-item"][aria-current="page"],
        .css-1v0mbdj a[data-baseweb="menu-item"]:focus {
            background: linear-gradient(90deg, #006400, #228B22) !important;
            color: white !important;
            border-left: 5px solid #32CD32 !important;
            box-shadow: 0 4px 15px rgba(0,100,0,0.3);
        }
        
        /* Icon styling */
        .css-1v0mbdj i {
            font-size: 22px !important;
            margin-right: 12px;
        }
    </style>
    """, unsafe_allow_html=True)

    # The actual menu — now looks AMAZING
    selected = option_menu(
        menu_title=None,
        options=["Home", "Live Dashboard", "Submit Data", "Request Data", "Admin Login", "About"],
        icons=["house-fill", "graph-up-arrow", "cloud-upload-fill", "cloud-download-fill", "shield-lock-fill", "person-circle"],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0px", "background-color": "#f8fff8"},
            "nav-link": {
                "font-size": "18px",
                "text-align": "left",
                "margin": "5px",
                "padding": "14px",
                "border-radius": "15px",
            },
            "nav-link-selected": {
                "background": "linear-gradient(90deg, #006400, #228B22)",
                "color": "white",
                "font-weight": "bold"
            },
        }
    )

# ===================== PAGES =====================
if selected == "Home" or selected is None:  # ← Critical fix: shows on first load!
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    # HERO BANNER — Presidential feel
    st.markdown("""
    <div style="background:linear-gradient(135deg, #006400, #32CD32); padding:60px 20px; border-radius:25px; text-align:center; color:white; box-shadow:0 15px 40px rgba(0,100,0,0.4); margin-bottom:40px;">
        <h1 style="font-size:56px; margin:0; font-weight:900;">Abia State Education Portal</h1>
        <p style="font-size:28px; margin:20px 0 0; opacity:0.95;">Real-Time • Verified • Transparent</p>
        <p style="font-size:20px; margin-top:10px;">1,900+ Schools • 17 LGAs • Live Data • Built for Excellence</p>
    </div>
    """, unsafe_allow_html=True)

    # LIVE STATS — Auto-updating from your real data
    try:
        total_schools = pd.read_sql("SELECT COUNT(*) FROM school_submissions WHERE approved=TRUE", engine).iloc[0,0]
        total_students = pd.read_sql("SELECT COALESCE(SUM(enrollment_total),0) FROM school_submissions WHERE approved=TRUE", engine).iloc[0,0]
        total_teachers = pd.read_sql("SELECT COALESCE(SUM(teachers_total),0) FROM school_submissions WHERE approved=TRUE", engine).iloc[0,0]
        total_lgas = pd.read_sql("SELECT COUNT(DISTINCT lga_name) FROM school_submissions WHERE approved=TRUE", engine).iloc[0,0]
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
            “No child left behind. No school left out.”
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

elif selected == "Live Dashboard":
    st.markdown("""
    <div style="text-align:center; padding:30px; background:linear-gradient(135deg,#006400,#228B22); border-radius:20px; color:white; box-shadow:0 10px 30px rgba(0,100,0,0.3);">
        <h1>Abia State Education • Live Dashboard</h1>
        <p style="font-size:22px; opacity:0.95;">Real-Time • Verified • All 17 LGAs • Powered by 1,900+ Schools</p>
    </div>
    """, unsafe_allow_html=True)

    st_autorefresh(interval=60000, key="auto")

    # Load data with ALL 17 LGAs guaranteed
    df = pd.read_sql("""
        SELECT 
            l.lga_name,
            COALESCE(SUM(s.enrollment_total),0) AS students,
            COALESCE(SUM(s.teachers_total),0) AS teachers,
            ROUND(COALESCE(SUM(s.enrollment_total)::NUMERIC / NULLIF(SUM(s.teachers_total),0),999),1) AS ratio
        FROM dwh.dim_lga l
        LEFT JOIN school_submissions s ON TRIM(UPPER(l.lga_name)) = TRIM(UPPER(s.lga_name)) AND s.approved=TRUE
        GROUP BY l.lga_key, l.lga_name
        ORDER BY students DESC
    """, engine)

    # LIVE METRICS — Big & Bold
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Students", f"{int(df['students'].sum()):,}", "Across Abia")
    with col2: st.metric("Total Teachers", f"{int(df['teachers'].sum()):,}")
    with col3: st.metric("Verified Schools", f"{pd.read_sql('SELECT COUNT(*) FROM school_submissions WHERE approved=TRUE', engine).iloc[0,0]:,}")
    with col4: st.metric("LGAs Covered", "17", "100%")

    st.markdown("---")

    # STUNNING PLOTLY CHARTS
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # 2x2 Grid of Beauty
    fig = make_subplots(rows=2, cols=2,
                        subplot_titles=("Students by LGA", "Teachers by LGA", "Student Share", "Teacher Share"),
                        specs=[[{"type": "bar"}, {"type": "bar"}],
                               [{"type": "pie"}, {"type": "pie"}]])

    # Bar Charts
    fig.add_trace(go.Bar(x=df['lga_name'], y=df['students'], name="Students", marker_color="#006400"), row=1, col=1)
    fig.add_trace(go.Bar(x=df['lga_name'], y=df['teachers'], name="Teachers", marker_color="#1f77b4"), row=1, col=2)

    # Pie Charts
    fig.add_trace(go.Pie(labels=df['lga_name'], values=df['students'], name="Students", marker_colors=px.colors.sequential.Greens), row=2, col=1)
    fig.add_trace(go.Pie(labels=df['lga_name'], values=df['teachers'], name="Teachers", marker_colors=px.colors.sequential.Blues), row=2, col=2)

    fig.update_layout(height=900, showlegend=False, title_text="Abia State Education Overview", title_x=0.5)
    st.plotly_chart(fig, use_container_width=True)

    # Rankings
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Top 5 LGAs by Enrollment")
        top5 = df.nlargest(5, 'students')[['lga_name', 'students']]
        st.dataframe(top5.style.format({"students": "{:,}"}), use_container_width=True)
    with col2:
        st.subheader("Best Pupil-Teacher Ratio")
        best = df[df['teachers'] > 0].nsmallest(5, 'ratio')[['lga_name', 'ratio']]
        st.dataframe(best, use_container_width=True)

    # Final Seal of Excellence
    st.markdown("""
    <div style="text-align:center; padding:30px; background:#e8f5e8; border-radius:20px; margin-top:40px;">
        <h2 style="color:#006400;">ALL 17 LGAs • 100% VERIFIED • LIVE DATA</h2>
        <p style="font-size:18px;">This dashboard is updated every minute from verified school submissions across Abia State.</p>
        <p><strong>Abia State Ministry of Education • 2025 Digital Initiative</strong></p>
    </div>
    """, unsafe_allow_html=True)

    st.success("All 17 LGAs • 100% Verified • Real-Time • Government-Ready")

elif selected == "Submit Data":
    st.markdown("### Submit Your School Data")
    st.info("Your school email is required for verification")

    with st.form("verified_submission"):
        school_name = st.text_input("School Name")
        lga_name = st.selectbox("LGA", pd.read_sql("SELECT lga_name FROM dwh.dim_lga", engine)['lga_name'])
        enrollment = st.number_input("Total Students", min_value=1)
        teachers = st.number_input("Total Teachers", min_value=1)
        contact_name = st.text_input("Contact Person Name")
        school_email = st.text_input("Official School Email (required)")

        if st.form_submit_button("Send Verification Code"):
            if "@" not in school_email:
                st.error("Please enter a valid email")
            else:
                send_verification_code(school_email)
                st.success(f"Verification code sent to {school_email}")
                st.session_state.awaiting_code = True

        if st.session_state.get("awaiting_code"):
            code = st.text_input("Enter 6-digit code")
            if st.button("Verify & Submit"):
                if str(st.session_state.verification_code) == code:
                    if save_submission_with_email(school_name, lga_name, enrollment, teachers, contact_name, school_email):
                        st.success("Verified & Submitted Successfully!")
                        st.balloons()
                        for k in ["awaiting_code", "verification_code", "pending_email"]:
                            st.session_state.pop(k, None)
                else:
                    st.error("Wrong code")

elif selected == "Request Data":
    st.markdown("### Download Approved Dataset")
    if st.button("Generate Excel"):
        df = pd.read_sql("SELECT * FROM school_submissions WHERE approved=TRUE", engine)
        bio = io.BytesIO()
        df.to_excel(bio, index=False)
        bio.seek(0)
        st.download_button("Download Now", bio, "Abia_Education_Data.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

elif selected == "Admin Login":
    st.markdown("### Administrator Access")
    with st.form("login"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user == "admin" and pwd == "Booky123":
                st.session_state.admin = True
                st.success("Welcome, Administrator")
                st.balloons()
            else:
                st.error("Access denied")

elif selected == "Admin Panel":
    if not st.session_state.get("admin"):
        st.stop()

    st.success("ADMIN PANEL • Full Control")
    pending = pd.read_sql("SELECT * FROM school_submissions WHERE approved IS NULL", engine)
    for _, row in pending.iterrows():
        with st.expander(f"{row['school_name']} • {row['lga_name']}"):
            st.write(f"Contact: {row['submitted_by']} • Email: {row['email']}")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("APPROVE", key=f"a{row['id']}"):
                    with engine.begin() as conn:
                        conn.execute(text("UPDATE school_submissions SET approved=TRUE WHERE id=:id"), {"id": row['id']})
                        conn.execute(text("INSERT INTO dwh.fact_abia_metrics (lga_key, enrollment_total, teachers_total, approved) "
                                         "SELECT l.lga_key, :e, :t, TRUE FROM dwh.dim_lga l WHERE l.lga_name=:lga"),
                                    {"e": row['enrollment_total'], "t": row['teachers_total'], "lga": row['lga_name']})
                    # Approval email
                    approval_html = f"""
                    <h2 style="color:green">Your School Data is Now LIVE!</h2>
                    <p>Dear {row['submitted_by']},</p>
                    <p>The data for <strong>{row['school_name']}</strong> has been officially approved and is now visible on the Abia State Education Portal.</p>
                    <p>Thank you for your contribution.</p>
                    <p><strong>Abia State Ministry of Education</strong></p>
                    """
                    send_professional_email(row['email'], "Your School Data is Live!", approval_html)
                    st.success("Published!")
                    st.rerun()
            with c2:
                if st.button("Reject", key=f"r{row['id']}"):
                    with engine.begin() as conn:
                        conn.execute(text("UPDATE school_submissions SET approved=FALSE WHERE id=:id"), {"id": row['id']})
                    st.warning("Rejected")
                    st.rerun()

elif selected == "About":
    st.markdown("### Creator: Alabi Winner (BookyAde)")
    st.write("Abia TechRice Cohort 2.0 • Building the future of education data in Abia State")
    st.write("GitHub: [BookyAde](https://github.com/BookyAde) • Email: alabiwinner9@gmail.com")

st.markdown("---")
st.caption("© 2025 Abia State Education Portal • Official Government Initiative")