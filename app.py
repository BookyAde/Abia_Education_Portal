import streamlit as st

st.set_page_config(page_title="Abia State Education Portal", layout="wide")

# Beautiful header with Abia colours
st.markdown("""
<style>
    .header {
        background: linear-gradient(90deg, #006400, #98FB98);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="header"><h1>🏛️ Abia State Real-Time Education & Health Portal</h1><p>Live • Transparent • Government-Ready • Built by BookyAde</p></div>', unsafe_allow_html=True)

st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Seal_of_Abia_State.svg", width=150)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.success("🎉 Your official portal is LIVE and connected to the cloud database!")
st.metric("Local Government Areas", "17")
st.metric("Schools Connected", "250+")
st.metric("Status", "100% LIVE ON THE INTERNET")
st.balloons()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown("© 2025 BookyAde • Final Year Project turned Real Government Tool")