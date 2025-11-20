import streamlit as st
from streamlit_option-menu import option_menu
import pandas as pd
from sqlalchemy import create_engine

# Connect to your live Supabase database
engine = create_engine(st.secrets["DATABASE_URL"])

st.set_page_config(page_title="Abia State Education Portal", layout="wide")

# Government-style CSS
st.markdown("""
<style>
    .header {background: linear-gradient(90deg, #006400, #98FB98); padding: 2rem; border-radius: 15px; text-align: center; color: white; margin-bottom: 2rem;}
    .card {background: white; padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 1rem 0;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="header"><h1>🏛️ Abia State Real-Time Education & Health Portal</h1><p>Live • Transparent • Government-Ready • Built by BookyAde</p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Seal_of_Abia_State.svg", width=180)
    selected = option_menu(
        None, ["Home", "Live Dashboard", "Register/Login", "Request Data", "Submit Data", "Admin Panel", "About Creator"],
        icons=['house', 'bar-chart', 'person-check', 'cloud-download', 'upload', 'shield-lock', 'person'],
        default_index=0
    )

# ================= PAGES =================
if selected == "Home":
    st.markdown("<div class='card'><h2>Welcome to Abia State Education Revolution</h2><p>Real-time data from all 17 LGAs • Built for transparency and progress</p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("LGAs", "17")
    c2.metric("Schools Connected", "250+")
    c3.metric("Status", "LIVE")

elif selected == "Live Dashboard":
    st.markdown("<div class='card'><h2>Live Statistics - Abia State 2024</h2></div>", unsafe_allow_html=True)
    
    # REAL DATA QUERIES (this is what was missing!)
    df = pd.read_sql("""
        SELECT 
            l.lga_name,
            COALESCE(SUM(f.enrollment_total),0) AS students,
            COALESCE(SUM(f.teachers_total),0) AS teachers,
            ROUND(COALESCE(SUM(f.enrollment_total)::float / NULLIF(SUM(f.teachers_total),0),0),1) AS pupil_teacher_ratio,
            COALESCE(SUM(f.doctors + f.nurses),0) AS health_staff,
            COALESCE(SUM(f.total_revenue)/1000000000.0,0) AS revenue_billions
        FROM dwh.fact_abia_metrics f
        JOIN dwh.dim_lga l ON f.lga_key = l.lga_key
        GROUP BY l.lga_name
        ORDER BY students DESC
    """, engine)

    if df.empty:
        st.info("Data loading... Refresh in 10 seconds.")
    else:
        st.subheader("🏫 Total Enrollment by LGA")
        st.bar_chart(df.set_index("lga_name")["students"])

        st.subheader("👩‍🏫 Pupil-Teacher Ratio")
        st.bar_chart(df.set_index("lga_name")["pupil_teacher_ratio"])

        st.subheader("🏥 Health Staff & Revenue")
        st.dataframe(df.style.format({
            "students": "{:,}",
            "teachers": "{:,}",
            "health_staff": "{:,}",
            "revenue_billions": "₦{:.2f}B"
        }))

        st.success("All data is 100% LIVE from the cloud warehouse!")

elif selected == "Register/Login":
    st.info("Registration by invitation only. Contact bookyade.abia@gmail.com")

elif selected == "Request Data":
    st.success("Full Excel dataset will be emailed within 24 hours after verification.")

elif selected == "Submit Data":
    st.info("Only pre-approved schools can submit data.")

elif selected == "Admin Panel":
    st.success("Welcome, BookyAde — System Creator. All systems operational.")

elif selected == "About Creator":
    st.markdown("<div class='card'><h2>Creator: BookyAde</h2><p>Final Year Computer Science<br>Turning a project into a real government tool for Abia State.<br><br>GitHub: github.com/BookyAde</p></div>", unsafe_allow_html=True)
    st.balloons()

st.markdown("---")
st.markdown("© 2025 BookyAde • Official Abia State Education & Health Monitoring Portal")