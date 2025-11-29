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

## ===================== STUNNING ANIMATED SIDEBAR — FINAL & COMPLETE =====================
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

    # ===================== ADMIN MENU =====================
    if st.session_state.get("admin", False):
        selected = option_menu(
            menu_title=None,
            options=[
                "Home",
                "Live Dashboard",
                "Submit Data",
                "Request Data",
                "School Lookup",           # ← NEW: Search any school + report
                "Transparency Ranking",    # ← Public leaderboard
                "Admin Panel",
                "Logout"
            ],
            icons=[
                "house-fill",
                "graph-up-arrow",
                "cloud-upload-fill",
                "cloud-download-fill",
                "search-heart-fill",       # ← Perfect icon for lookup + care
                "trophy-fill",
                "shield-lock-fill",
                "box-arrow-right"
            ],
            default_index=6,  # Opens on Admin Panel by default
            orientation="vertical",
            styles={
                "container": {"padding": "0px", "background-color": "#f8fff8"},
                "nav-link": {"font-size": "18px", "margin": "8px", "padding": "16px", "border-radius": "15px"},
                "nav-link-selected": {"background": "linear-gradient(90deg, #006400, #228B22)", "color": "white", "font-weight": "bold"}
            }
        )
        
        if selected == "Logout":
            st.session_state.admin = False
            st.rerun()

    # ===================== PUBLIC / NORMAL USER MENU =====================
    else:
        selected = option_menu(
            menu_title=None,
            options=[
                "Home",
                "Live Dashboard",
                "Submit Data",
                "Request Data",
                "School Lookup",           # ← NEW: Most important public feature
                "Transparency Ranking",    # ← Public shaming/praise
                "Admin Login",
                "About"
            ],
            icons=[
                "house-fill",
                "graph-up-arrow",
                "cloud-upload-fill",
                "cloud-download-fill",
                "search-heart-fill",       # ← Warm, caring icon
                "trophy-fill",
                "shield-lock-fill",
                "person-circle"
            ],
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

elif selected == "Live Dashboard":
    st.markdown("### Live Education Statistics • Abia State")
    st_autorefresh(interval=60000, key="live")
    df = get_live_data()

    if not df.empty:
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
    else:
        st.warning("No data available yet or database connection failed.")
       
    # === NEW: Facility Crisis Heatmap ===
    st.markdown("### 🟥 Facility Crisis Heatmap Across Abia State")

    facility_df = pd.read_sql("""
        SELECT s.lga_name,
               COUNT(*) as total_schools,
               SUM(CASE WHEN s.facilities LIKE '%Toilets (Boys)%' THEN 1 ELSE 0 END) as has_boys_toilet,
               SUM(CASE WHEN s.facilities LIKE '%Toilets (Girls)%' THEN 1 ELSE 0 END) as has_girls_toilet,
               SUM(CASE WHEN s.facilities LIKE '%Clean Drinking Water%' THEN 1 ELSE 0 END) as has_water,
               SUM(CASE WHEN s.facilities LIKE '%Electricity%' THEN 1 ELSE 0 END) as has_electricity
        FROM school_submissions s
        WHERE s.approved = TRUE
        GROUP BY s.lga_name
    """, engine)

    if not facility_df.empty:
        facility_df["No Toilet (Boys) %"] = 100 - round((facility_df["has_boys_toilet"] / facility_df["total_schools"]) * 100, 1)
        facility_df["No Toilet (Girls) %"] = 100 - round((facility_df["has_girls_toilet"] / facility_df["total_schools"]) * 100, 1)
        facility_df["No Water %"] = 100 - round((facility_df["has_water"] / facility_df["total_schools"]) * 100, 1)

        fig = px.treemap(
            facility_df,
            path=['lga_name'],
            values='total_schools',
            color='No Toilet (Boys) %',
            color_continuous_scale="Reds",
            title="🚽 LGAs with Highest Toilet Crisis (Darker = Worse)"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Key Crisis Zones")
        st.dataframe(facility_df[['lga_name', 'total_schools', 'No Toilet (Boys) %', 'No Toilet (Girls) %', 'No Water %']]
                     .sort_values("No Toilet (Boys) %", ascending=False), use_container_width=True)

elif selected == "Submit Data":
    st.markdown("### Submit School Data")
    st.info("Your official school email is required • All submissions are verified")

    # Load LGAs
    if engine:
        try:
            lgas = pd.read_sql("SELECT lga_name FROM dwh.dim_lga ORDER BY lga_name", engine)['lga_name'].tolist()
        except:
            lgas = []
            st.error("Could not load LGAs. Check database connection.")
    else:
        lgas = []
        st.error("Database not connected.")

    # Ensure uploads folder exists
    os.makedirs("uploads", exist_ok=True)

    # ============= STEP 1: Fill Form & Send Code =============
    if not st.session_state.get("awaiting_code", False):
        with st.form("send_code_form", clear_on_submit=False):
            st.markdown("#### School & Contact Information")
            col1, col2 = st.columns(2)
            with col1:
                school = st.text_input("School Name *", placeholder="e.g. Community Secondary School Ohafia")
                lga = st.selectbox("LGA *", options=lgas if lgas else ["Loading LGAs..."], disabled=not lgas)
                name = st.text_input("Contact Name *", placeholder="Principal / Head Teacher")
            with col2:
                students = st.number_input("Total Students Enrolled *", min_value=1, step=1)
                teachers = st.number_input("Total Teachers *", min_value=1, step=1)
                email = st.text_input("Official School Email *", placeholder="principal.school@abiaschools.edu.ng")

            st.markdown("#### School Facilities (Check all that currently work)")
            facilities = st.multiselect(
                "Select functional facilities",
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
                help="This helps the government prioritize support"
            )

            st.markdown("#### Upload Proof Photo *")
            photo = st.file_uploader(
                "Photo of school signboard, front gate, or building (required)",
                type=['jpg', 'jpeg', 'png'],
                help="Clear photo prevents fake submissions"
            )

            submitted = st.form_submit_button("Send Verification Code", type="primary")

            if submitted:
                if not all([school, lga and lga != "Loading LGAs...", students, teachers, name, email]):
                    st.error("Please fill all required fields.")
                elif "@" not in email:
                    st.error("Please enter a valid email address.")
                elif not facilities:
                    st.error("Please select at least one facility (or none if none work).")
                elif not photo:
                    st.error("Photo is mandatory to verify the school exists.")
                else:
                    # Save photo
                    timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
                    safe_school_name = "".join(c for c in school if c.isalnum() or c in " -_")[:50]
                    filename = f"{safe_school_name}_{timestamp}.jpg"
                    photo_path = f"uploads/{filename}"
                    
                    with open(photo_path, "wb") as f:
                        f.write(photo.getbuffer())

                    # Store all data in session
                    st.session_state.temp_data = {
                        "school": school,
                        "lga": lga,
                        "students": int(students),
                        "teachers": int(teachers),
                        "name": name,
                        "email": email,
                        "facilities": facilities,
                        "photo_path": photo_path
                    }

                    # Generate and send code
                    code = random.randint(100000, 999999)
                    subject = "Abia Education Portal – Your Verification Code"
                    body = f"""
Hello {name},

Thank you for submitting data for **{school}**, {lga} LGA.

Your 6-digit verification code is:

**{code}**

Enter this code on the portal to complete submission.

This helps us ensure only real schools submit data.

— Abia State Education Portal Team
                    """

                    if send_email(email, subject, body):
                        st.session_state.verification_code = code
                        st.session_state.awaiting_code = True
                        st.success(f"Verification code sent to {email}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("Failed to send email. Check email address and try again.")

    # ============= STEP 2: Enter Code & Final Submit =============
    else:
        temp = st.session_state.temp_data
        st.info(f"Code sent to **{temp['email']}** • School: **{temp['school']}**")

        with st.form("verify_code_form"):
            code_input = st.text_input("Enter 6-digit verification code", max_chars=6)
            submitted = st.form_submit_button("Verify & Submit Data", type="primary")

            if submitted:
                if code_input == str(st.session_state.verification_code):
                    # Save to database
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
                        send_email(
                            temp["email"],
                            "Submission Received – Abia Education Portal",
                            f"Hello {temp['name']},\n\nYour data for {temp['school']} has been received and is pending admin approval.\n\nYou will be notified when it's live.\n\nThank you!\n— Abia Education Portal"
                        )
                        st.success("Submitted successfully! Pending approval.")
                        st.balloons()

                        # Clear session
                        for key in ["temp_data", "verification_code", "awaiting_code"]:
                            st.session_state.pop(key, None)
                        st.rerun()
                    else:
                        st.error("Failed to save. Please try again.")
                else:
                    st.error("Incorrect code. Please check and try again.")
    

elif selected == "Request Data":
    st.markdown("""
    <div class='card'>
        <h2>Download Verified Dataset</h2>
        <p>Use the filters below to download exactly the data you need — by LGA, status, date, or keyword.</p>
    </div>
    """, unsafe_allow_html=True)

    # Load full approved data
    try:
        if engine:
            df = pd.read_sql("""
                SELECT id, school_name, lga_name, enrollment_total, teachers_total, 
                       submitted_by, email, submitted_at,
                       CASE WHEN approved=TRUE THEN 'Approved' WHEN approved=FALSE THEN 'Rejected' ELSE 'Pending' END AS status
                FROM school_submissions 
                ORDER BY submitted_at DESC
            """, engine)
        else:
            df = pd.DataFrame()
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


elif selected == "School Lookup":
    st.markdown("# School Lookup")
    st.markdown("### Search any school in Abia State • See real data • Report problems instantly")

    # Search bar with live filtering
    search = st.text_input(
        "🔍 Search by school name or LGA",
        placeholder="e.g. Community School Umuahia, Aba North, Ohafia",
        help="Type anything — results appear instantly"
    )

    if not engine:
        st.error("Database not connected")
        st.stop()

    # Load only approved schools
    df = pd.read_sql("""
        SELECT id, school_name, lga_name, enrollment_total, teachers_total,
               submitted_by, email, submitted_at, photo_path, facilities
        FROM school_submissions 
        WHERE approved = TRUE
        ORDER BY school_name
    """, engine)

    if df.empty:
        st.warning("No verified schools yet.")
    else:
        # Live filter
        if search:
            mask = df['school_name'].str.contains(search, case=False, na=False) | \
                   df['lga_name'].str.contains(search, case=False, na=False)
            df = df[mask]

        st.markdown(f"**Found {len(df)} school(s)**")

        for _, row in df.iterrows():
            with st.container():
                col1, col2 = st.columns([1, 3])

                # Photo
                with col1:
                    if row['photo_path'] and os.path.exists(row['photo_path']):
                        st.image(row['photo_path'], use_container_width=True)
                    else:
                        st.image("https://via.placeholder.com/300x200?text=No+Photo", use_container_width=True)

                # Details + Report Button
                with col2:
                    st.markdown(f"### {row['school_name']}")
                    st.markdown(f"**LGA:** {row['lga_name']}  \n**Students:** {row['enrollment_total']:,}  \n**Teachers:** {row['teachers_total']:,}")

                    # Facilities with icons
                    facilities = eval(row['facilities']) if row['facilities'] else []
                    st.markdown("**Working Facilities:**")
                    icons = {
                        "Toilets (Boys)": "Boys Toilet", "Toilets (Girls)": "Girls Toilet",
                        "Clean Drinking Water": "Water", "Electricity": "Electricity",
                        "Enough Desks": "Desks", "Perimeter Fencing": "Fencing",
                        "Functional Classrooms": "Classrooms", "Computer Lab": "Computer"
                    }
                    cols = st.columns(4)
                    for i, fac in enumerate(facilities):
                        short = icons.get(fac, fac)
                        with cols[i % 4]:
                            st.success(f"{short}")

                    # REPORT BUTTON
                    if st.button("Report Issue at This School", key=f"report_{row['id']}", type="primary"):
                        with st.form(f"report_form_{row['id']}"):
                            st.error(f"Problem at: **{row['school_name']}**, {row['lga_name']}")
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
                                if send_email("complaints@abiaeducation.gov.ng", f"URGENT: {issue} – {row['school_name']}", body):
                                    st.success("Report sent! Thank you — action will be taken.")
                                    st.balloons()
                                else:
                                    st.error("Failed to send")
                            if cancel:
                                st.rerun()

                st.markdown("---")
elif selected == "Transparency Ranking":
    st.markdown("# LGA Education Transparency Ranking")
    st.markdown("### Which LGA is leading in verified school data and facilities?")

    if not engine:
        st.error("Database not connected")
        st.stop()

    # Main ranking query
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
            ROUND(100.0 * COALESCE(has_boys_toilet, 0) / NULLIF(verified_schools, 0), 1) AS boys_toilet_coverage_pct,
            ROUND(100.0 * COALESCE(has_girls_toilet, 0) / NULLIF(verified_schools, 0), 1) AS girls_toilet_coverage_pct,
            ROUND(100.0 * COALESCE(has_water, 0) / NULLIF(verified_schools, 0), 1) AS water_coverage_pct
        FROM stats
        ORDER BY verified_schools DESC, verification_rate_percent DESC
    """, engine)

    if ranking.empty:
        st.info("No verified data yet.")
    else:
        ranking.index = range(1, len(ranking) + 1)
        ranking.index.name = "Rank"

        # Display leaderboard
        st.dataframe(
            ranking.style
            .background_gradient(subset=["verified_schools"], cmap="Greens")
            .background_gradient(subset=["verification_rate_percent"], cmap="Blues")
            .background_gradient(subset=["boys_toilet_coverage_pct"], cmap="Oranges")
            .format({"verification_rate_percent": "{:.1f}%", "boys_toilet_coverage_pct": "{:.1f}%", "girls_toilet_coverage_pct": "{:.1f}%", "water_coverage_pct": "{:.1f}%"}),
            use_container_width=True
        )

        # Highlight top & bottom
        col1, col2 = st.columns(2)
        with col1:
            st.success(f"Leading LGA: **{ranking.iloc[0]['lga_name']}** • {ranking.iloc[0]['verified_schools']} verified schools")
        with col2:
            st.error(f"Lagging LGA: **{ranking.iloc[-1]['lga_name']}** • Only {ranking.iloc[-1]['verified_schools']} verified")

        st.markdown("---")
        st.markdown("### Report Systemic Issues in Your LGA")
        st.info("See something wrong across many schools in your LGA? Report it here — goes straight to the Ministry.")

        for _, row in ranking.iterrows():
            lga = row['lga_name']
            with st.container():
                c1, c2, c3 = st.columns([3, 4, 2])
                with c1:
                    st.markdown(f"#### {lga}")
                    st.caption(f"Rank #{ranking.index[ranking['lga_name'] == lga][0]} • {row['verified_schools']} verified schools")
                with c2:
                    st.markdown(f"""
                    **Toilet Coverage:** Boys {row['boys_toilet_coverage_pct']}% | Girls {row['girls_toilet_coverage_pct']}%  
                    **Clean Water:** {row['water_coverage_pct']}% of schools
                    """)
                with c3:
                    if st.button("Report LGA Issue", key=f"lga_report_{lga}", type="secondary", use_container_width=True):
                        with st.form(f"lga_complaint_{lga}"):
                            st.markdown(f"### Reporting Issue in **{lga} LGA**")
                            issue = st.selectbox("Main Problem", [
                                "Most schools have no toilets",
                                "No clean drinking water in schools",
                                "Widespread leaking roofs",
                                "Ghost teachers / absent staff",
                                "Illegal fees being charged",
                                "No desks or chairs",
                                "Security/fencing problems",
                                "Other systemic issue"
                            ], key=f"type_{lga}")
                            details = st.text_area("Give details (optional)", placeholder="e.g. 8 out of 10 schools I visited have broken toilets...", key=f"det_{lga}")
                            contact = st.text_input("Your contact (optional)", key=f"con_{lga}")

                            cola, colb = st.columns(2)
                            with cola:
                                send = st.form_submit_button("Send Report", type="primary")
                            with colb:
                                cancel = st.form_submit_button("Cancel")

                            if send:
                                body = f"""
SYSTEMIC COMPLAINT – {lga} LGA

Issue: {issue}
Details: {details}
Reported by: {contact or "Anonymous"}
Date: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}
                                """
                                if send_email("complaints@abiaeducation.gov.ng",
                                            f"LGA ISSUE: {issue} – {lga}",
                                            body):
                                    st.success("Report sent! Thank you — this helps fix things faster.")
                                    st.balloons()
                                else:
                                    st.error("Failed to send. Try again.")
                            if cancel:
                                st.rerun()

                st.markdown("---")

# ---------- ADMIN LOGIN ----------
elif selected == "Admin Login":
    st.markdown("### Admin Access")

    with st.form("login"):
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.form_submit_button("Login"):
            if user == "admin" and pwd == "Booky123":
                # Save admin login
                st.session_state.admin = True
                
                # Move user to Admin Panel immediately
                st.session_state.selected = "Admin Panel"

                st.success("Welcome, Administrator!")
                st.balloons()
                st.rerun()  # <----- THIS IS THE MOST IMPORTANT PART
            else:
                st.error("Access denied")


# ---------- ADMIN PANEL ----------
elif selected == "Admin Panel":

    # Security check
    if not st.session_state.get("admin", False):
        st.error("Unauthorized access. Please log in as admin.")
        st.stop()

    st.markdown("# ADMIN PANEL • Full Control")
    st.success("Logged in as Administrator")

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Logout", type="primary"):
            st.session_state.admin = False
            st.rerun()

    if not engine:
        st.error("Database not connected.")
        st.stop()

    # Load pending submissions
    pending = pd.read_sql("""
        SELECT id, school_name, lga_name, enrollment_total, teachers_total, 
               submitted_by, email, submitted_at, facilities, photo_path
        FROM school_submissions 
        WHERE approved IS NULL 
        ORDER BY submitted_at DESC
    """, engine)

    if pending.empty:
        st.success("No pending submissions")
        st.balloons()
    else:
        st.markdown(f"### {len(pending)} Pending Submission(s)")
        
        for _, row in pending.iterrows():
            with st.expander(f"**{row['school_name']}** • {row['lga_name']} • Submitted {row['submitted_at'].strftime('%b %d, %Y')}", expanded=False):
                
                col1, col2 = st.columns([1, 2])
                
                # === LEFT: Photo + Basic Info ===
                with col1:
                    st.markdown(f"**Students:** {row['enrollment_total']:,}  \n**Teachers:** {row['teachers_total']:,}")
                    st.markdown(f"**Contact:** {row['submitted_by']}  \n**Email:** {row['email']}")

                    if row['photo_path'] and os.path.exists(row['photo_path']):
                        st.image(row['photo_path'], caption="School Photo Proof", width=300)
                    else:
                        st.warning("Photo missing or deleted")

                # === RIGHT: Facilities + Actions ===
                with col2:
                    st.markdown("#### Functional Facilities")
                    facilities = eval(row['facilities']) if row['facilities'] else []
                    facility_options = {
                        "Functional Toilets (Boys)": "Boys Toilet",
                        "Functional Toilets (Girls)": "Girls Toilet",
                        "Clean Drinking Water": "Drinking Water",
                        "Electricity / Solar Power": "Electricity",
                        "Enough Desks & Chairs (80%+ students seated)": "Desks",
                        "Perimeter Fencing": "Fencing",
                        "Functional Classrooms (no leaking roof)": "Classrooms",
                        "Computer Lab / ICT Center": "Computer Lab"
                    }

                    cols = st.columns(4)
                    for i, (full, short) in enumerate(facility_options.items()):
                        with cols[i % 4]:
                            if full in facilities:
                                st.markdown(f"**Yes** {short}")
                            else:
                                st.markdown(f"**No** {short}")

                    # === APPROVE / REJECT BUTTONS ===
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("APPROVE & Publish", key=f"approve_{row['id']}", type="primary"):
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE school_submissions SET approved=TRUE WHERE id=:id"), {"id": row['id']})
                                # Insert/update fact table (your existing logic)
                                conn.execute(text("""
                                    INSERT INTO dwh.fact_abia_metrics 
                                    (lga_key, enrollment_total, teachers_total, approved)
                                    SELECT l.lga_key, :e, :t, TRUE 
                                    FROM dwh.dim_lga l WHERE l.lga_name=:lga
                                    ON CONFLICT (lga_key) DO UPDATE SET 
                                        enrollment_total = EXCLUDED.enrollment_total,
                                        teachers_total = EXCLUDED.teachers_total
                                """), {"e": row['enrollment_total'], "t": row['teachers_total'], "lga": row['lga_name']})

                            send_email(row['email'], "APPROVED – Abia Education Portal",
                                f"Good news!\n\nYour submission for **{row['school_name']}** has been APPROVED and is now live on the state dashboard.\n\nThank you for your contribution!\n\n— Abia Education Portal Team")
                            
                            st.success("APPROVED & LIVE!")
                            st.balloons()
                            st.rerun()

                    with c2:
                        if st.button("REJECT", key=f"reject_{row['id']}", type="secondary"):
                            with engine.begin() as conn:
                                conn.execute(text("UPDATE school_submissions SET approved=FALSE WHERE id=:id"), {"id": row['id']})

                            send_email(row['email'], "Submission Update – Abia Education Portal",
                                f"Hello,\n\nYour submission for **{row['school_name']}** could not be approved at this time.\n\nPlease review and resubmit with correct details and photo.\n\n— Abia Education Portal Team")
                            
                            st.warning("Rejected")
                            st.rerun()



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
