import streamlit as st
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import streamlit as st
import smtplib
from email.mime.text import MIMEText

# Function to send email using SMTP_SSL
def send_email(to_email, subject, body):
    try:
        smtp_server = st.secrets["EMAIL"]["SMTP_SERVER"]
        smtp_port = st.secrets["EMAIL"]["SMTP_PORT"]
        email_user = st.secrets["EMAIL"]["EMAIL_USER"]
        email_pass = st.secrets["EMAIL"]["EMAIL_PASS"]

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = email_user
        msg["To"] = to_email

        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_user, email_pass)
            server.sendmail(email_user, to_email, msg.as_string())
        print("✅ Email sent successfully!")
        return True
    except Exception as e:
        print("❌ Failed to send email:", e)
        return False

# ---------------------- TEST ----------------------
if __name__ == "__main__":
    to_email = input("Enter recipient email: ")
    subject = "Test Email from Abia Portal"
    body = "Hello! This is a test email from your Streamlit dashboard."
    
    send_email(to_email, subject, body)