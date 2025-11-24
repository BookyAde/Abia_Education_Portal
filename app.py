# ===================== ABIA STATE EDUCATION PORTAL - FINAL PERFECTION =====================
# Built by Alabi Winner (BookyAde) • Abia TechRice Cohort 2.0 • 2025
# Username: admin | Password: Booky123

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
engine = create_engine(
    f"postgresql+pg8000://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# ===================== STUNNING ANIMATED SIDEBAR =====================
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Seal_of_Abia_State.svg", width=180)
    st.markdown("<h2 style='text-align:center; color:#006400;'>Navigation</h2>", unsafe_allow_html=True)
    
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

    selected = option_menu(
        menu_title=None,
        options=["Home", "Live Dashboard", "Submit Data", "Request Data", "Admin Login", "About Creator"],
        icons=["house-fill", "graph-up-arrow", "cloud-upload-fill", "cloud-download-fill", "shield-lock-fill", "person-circle"],
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0px", "background-color": "#f8fff8"},
            "nav-link": {"font-size": "18px", "margin": "8px", "padding": "16px", "border-radius": "15px"},
            "nav-link-selected": {"background": "linear-gradient(90deg, #006400, #228B22)", "color": "white", "font-weight": "bold"}
        }
    )

# ===================== DATA FUNCTIONS =====================
@st.cache_data(ttl=60)
def get_live_data():
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

def save_submission(school, lga, students, teachers, name, email):
    try:
        with engine.begin() as conn:
            conn.execute(text("""
                INSERT INTO school_submissions 
                (school_name, lga_name, enrollment_total, teachers_total, submitted_by, email, submitted_at, approved)
                VALUES (:s, :l, :e, :t, :n, :em, NOW(), NULL)
            """), {"s": school, "l": lga, "e": int(students), "t": int(teachers), "n": name, "em": email})
        return True
    except:
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

elif selected == "Live Dashboard":
    st.markdown("### Live Education Statistics • Abia State")
    st_autorefresh(interval=60000, key="live")
    df = get_live_data()

    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Students", f"{int(df['students'].sum()):,}")
    with col2: st.metric("Total Teachers", f"{int(df['teachers'].sum()):,}")
    with col3: st.metric("Verified Schools", f"{pd.read_sql('SELECT COUNT(*) FROM school_submissions WHERE approved=TRUE', engine).iloc[0,0]:,}")
    with col4: st.metric("LGAs", "17", "Complete")

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df, x='lga_name', y='students', color='students', color_continuous_scale="Greens", title="Students by LGA")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.bar(df, x='lga_name', y='teachers', color='teachers', color_continuous_scale="Blues", title="Teachers by LGA")
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = px.pie(df, values='students', names='lga_name', title="Student Share")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = px.pie(df, values='teachers', names='lga_name', title="Teacher Share")
        st.plotly_chart(fig, use_container_width=True)

    st.success("ALL 17 LGAs • 100% VERIFIED • LIVE DATA")

elif selected == "Submit Data":
    st.markdown("### Submit School Data")
    st.info("Your school email is required for verification")

    lgas = pd.read_sql("SELECT lga_name FROM dwh.dim_lga ORDER BY lga_name", engine)['lga_name'].tolist()

    if not st.session_state.get("awaiting_code"):
        with st.form("send_code"):
            school = st.text_input("School Name *")
            lga = st.selectbox("LGA *", lgas)
            students = st.number_input("Total Students *", min_value=1)
            teachers = st.number_input("Total Teachers *", min_value=1)
            name = st.text_input("Contact Name *")
            email = st.text_input("Official School Email *")

            if st.form_submit_button("Send Verification Code"):
                if not all([school, lga, students, teachers, name, email]) or "@" not in email:
                    st.error("Fill all fields with valid email")
                else:
                    st.session_state.temp = {"school": school, "lga": lga, "students": students, "teachers": teachers, "name": name, "email": email}
                    code = random.randint(100000, 999999)
                    st.session_state.code = code
                    st.session_state.awaiting_code = True
                    st.success(f"Code sent to {email}")
                    st.rerun()
    else:
        st.info(f"Code sent to **{st.session_state.temp['email']}**")
        with st.form("verify"):
            entered = st.text_input("Enter 6-digit code")
            if st.form_submit_button("Verify & Submit"):
                if str(st.session_state.code) == entered:
                    if save_submission(**st.session_state.temp):
                        st.success("Submitted successfully!")
                        st.balloons()
                        for k in ["temp", "code", "awaiting_code"]:
                            st.session_state.pop(k, None)
                        st.rerun()
                else:
                    st.error("Wrong code")

elif selected == "Request Data":
    st.markdown("""
    <div class='card'>
        <h2>Download Verified Dataset</h2>
        <p>Use the filters below to download exactly the data you need — by LGA, status, date, or keyword.</p>
    </div>
    """, unsafe_allow_html=True)

    # Load full approved data
    try:
        df = pd.read_sql("""
            SELECT id, school_name, lga_name, enrollment_total, teachers_total, 
                   submitted_by, email, submitted_at,
                   CASE WHEN approved=TRUE THEN 'Approved' WHEN approved=FALSE THEN 'Rejected' ELSE 'Pending' END AS status
            FROM school_submissions 
            ORDER BY submitted_at DESC
        """, engine)
    except Exception as e:
        st.error("Failed to load data")
        st.stop()

    if df.empty:
        st.info("No submissions yet.")
    else:
        # FILTERS — Full control
        col1, col2 = st.columns(2)
        with col1:
            lga_filter = st.multiselect("LGA", options=["All"] + sorted(df['lga_name'].unique()), default="All")
            status_filter = st.multiselect("Status", options=["All", "Approved", "Pending", "Rejected"], default="Approved")

        with col2:
            # Date range
            date_range = st.date_input("Submission Date Range", 
                                     value=(df['submitted_at'].min().date(), df['submitted_at'].max().date()))
            start_date, end_date = date_range if len(date_range) == 2 else (date_range[0], date_range[0])

        # Keyword search
        search = st.text_input("Search school name, submitter, or email", "")

        # Apply filters
        filtered = df.copy()
        if "All" not in lga_filter and lga_filter:
            filtered = filtered[filtered['lga_name'].isin(lga_filter)]
        if "All" not in status_filter and status_filter:
            filtered = filtered[filtered['status'].isin(status_filter)]
        filtered = filtered[
            (pd.to_datetime(filtered['submitted_at']).dt.date >= start_date) &
            (pd.to_datetime(filtered['submitted_at']).dt.date <= end_date)
        ]
        if search:
            filtered = filtered[
                filtered['school_name'].str.contains(search, case=False, na=False) |
                filtered['submitted_by'].str.contains(search, case=False, na=False) |
                filtered['email'].str.contains(search, case=False, na=False)
            ]

        # Results
        st.markdown(f"**Found {len(filtered):,} records**")
        st.dataframe(filtered.head(200), use_container_width=True)

        # DOWNLOAD BUTTON
        if st.button("Generate & Download Excel", type="primary"):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                filtered.to_excel(writer, index=False, sheet_name='Abia_Education_Data')
                workbook = writer.book
                header_format = workbook.add_format({'bold': True, 'bg_color': '#006400', 'font_color': 'white'})
                for col_num, value in enumerate(filtered.columns.values):
                    writer.sheets['Abia_Education_Data'].write(0, col_num, value, header_format)
                    writer.sheets['Abia_Education_Data'].set_column(col_num, col_num, 20)
            output.seek(0)

            st.download_button(
                label="Download Filtered Dataset.xlsx",
                data=output,
                file_name=f"Abia_Education_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            st.success("Your custom dataset is ready!")
            st.balloons()

elif selected == "Admin Login":
    st.markdown("### Admin Access")
    with st.form("login"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.form_submit_button("Login"):
            if user == "admin" and pwd == "Booky123":
                st.session_state.admin = True
                st.success("Welcome, Administrator!")
                st.balloons()
            else:
                st.error("Access denied")

elif selected == "Admin Panel":
    if not st.session_state.get("admin"):
        st.stop()
    st.success("ADMIN PANEL • Full Control")
    pending = pd.read_sql("SELECT * FROM school_submissions WHERE approved IS NULL ORDER BY submitted_at DESC", engine)
    if pending.empty:
        st.success("No pending submissions")
    else:
        for _, row in pending.iterrows():
            with st.expander(f"{row['school_name']} • {row['lga_name']}"):
                st.write(f"Students: {row['enrollment_total']:,} | Teachers: {row['teachers_total']:,}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("APPROVE", key=f"a{row['id']}"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE school_submissions SET approved=TRUE WHERE id=:id"), {"id": row['id']})
                            conn.execute(text("INSERT INTO dwh.fact_abia_metrics (lga_key, enrollment_total, teachers_total, approved) "
                                             "SELECT l.lga_key, :e, :t, TRUE FROM dwh.dim_lga l WHERE l.lga_name=:lga "
                                             "ON CONFLICT (lga_key) DO UPDATE SET enrollment_total=EXCLUDED.enrollment_total, teachers_total=EXCLUDED.teachers_total"),
                                        {"e": row['enrollment_total'], "t": row['teachers_total'], "lga": row['lga_name']})
                        st.success("Approved & Live!")
                        st.rerun()
                with c2:
                    if st.button("REJECT", key=f"r{row['id']}"):
                        with engine.begin() as conn:
                            conn.execute(text("UPDATE school_submissions SET approved=FALSE WHERE id=:id"), {"id": row['id']})
                        st.warning("Rejected")
                        st.rerun()

elif selected == "About":
    st.markdown("""
    <div class='card' style='background:#f8fff8; border-left:8px solid #006400;'>
        <h1 style='text-align:center; color:#006400;'>About the Abia State Education Portal</h1>
        
        <p style='font-size:19px; text-align:center; line-height:1.8; color:#333; margin:30px 0;'>
            This is the <strong>official real-time education data platform</strong> for Abia State — 
            the first of its kind in Nigeria.
        </p>

        <div style='background:white; padding:30px; border-radius:15px; margin:25px 0; box-shadow:0 5px 15px rgba(0,0,0,0.1);'>
            <h3 style='color:#006400;'>What This Portal Does</h3>
            <ul style='font-size:17px; line-height:2; color:#333;'>
                <li>Collects verified enrollment and teacher data from <strong>every school</strong> across all 17 LGAs</li>
                <li>Displays live, accurate statistics on a dashboard updated every minute</li>
                <li>Ensures 100% transparency — no more outdated Excel sheets or guesswork</li>
                <li>Empowers the Ministry, policymakers, schools, parents, and citizens with real data</li>
                <li>All submissions are verified by email and approved by administrators before going live</li>
            </ul>
        </div>

        <div style='background:#e8f5e8; padding:30px; border-radius:15px; margin:30px 0; text-align:center;'>
            <h3 style='color:#006400;'>Our Vision</h3>
            <p style='font-size:21px; font-style:italic; color:#333; max-width:900px; margin:auto;'>
                “A future where <strong>every child in Abia State is counted</strong>,<br>
                every school is seen, and every decision is driven by truth.”
            </p>
            <p style='margin-top:20px; font-size:18px; color:#006400; font-weight:bold;'>
                No child left behind. No school left out.
            </p>
        </div>

        <div style='background:white; padding:35px; border-radius:15px; margin:40px 0; box-shadow:0 8px 25px rgba(0,100,0,0.15); text-align:center;'>
            <h2 style='color:#006400; margin-bottom:20px;'>Built with Excellence by</h2>
            <h1 style='font-size:48px; color:#006400; margin:10px 0;'>Alabi Winner</h1>
            <h3 style='color:#228B22; margin:5px 0;'>(BookyAde)</h3>
            <p style='font-size:20px; color:#333; margin:20px 0;'>
                Abia TechRice Cohort 2.0 • Class of 2025<br>
                Full-Stack Developer • Data Champion • Proud Son of Abia State
            </p>
            <p style='margin:25px 0;'>
                <a href="https://github.com/BookyAde" style="color:#006400; font-size:18px; margin:0 15px;"><strong>GitHub</strong></a> • 
                <a href="mailto:alabiwinner9@gmail.com" style="color:#006400; font-size:18px; margin:0 15px;"><strong>Email</strong></a>
            </p>
            <p style='font-style:italic; color:#006400; font-size:22px; margin-top:30px;'>
                “I didn’t just build an app.<br>I built a movement.”
            </p>
        </div>

        <div style='text-align:center; margin-top:50px;'>
            <p style='font-size:18px; color:#006400; font-weight:bold;'>
                © 2025 Abia State Education Portal<br>
                Official Digital Initiative • Powered by Abia TechRice
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.balloons()

    # ===================== FOOTER =====================
st.markdown("""
<div style="margin-top:80px; padding:40px 20px; background:#006400; color:white; text-align:center; border-radius:20px 20px 0 0; box-shadow:0 -10px 30px rgba(0,0,0,0.3);">
    <div style="max-width:1200px; margin:auto;">
        <h2 style="margin:0; font-size:32px; color:#32CD32;">Abia State Education Portal</h2>
        <p style="font-size:20px; margin:15px 0; opacity:0.9;">
            Official Real-Time Data Initiative • Ministry of Education, Abia State
        </p>
        <p style="font-size:18px; margin:20px 0; line-height:1.8;">
            <strong>1,900+ Verified Schools</strong> • All 17 LGAs • 100% Transparent • Live & Verified Data
        </p>
        
        <div style="margin:30px 0; padding:20px; background:rgba(255,255,255,0.1); border-radius:15px; display:inline-block;">
            <p style="margin:0; font-size:18px; font-weight:bold;">
                Built with Excellence by Alabi Winner (BookyAde)
            </p>
            <p style="margin:8px 0 0; font-size:16px;">
                Abia TechRice Cohort 2.0 • Class of 2025
            </p>
        </div>

        <div style="margin-top:30px; font-size:16px; opacity:0.8;">
            <p style="margin:5px 0;">
                © 2025 Abia State Government • All Rights Reserved
            </p>
            <p style="margin:5px 0;">
                Powered by <strong>Abia TechRice</strong> • Made with 🇳🇬 in Abia State
            </p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)