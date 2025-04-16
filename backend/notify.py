import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env

# ✅ Send Email Notification
def send_email_notification(subject, message, to_email):
    sender_email = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEText(message)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, msg.as_string())
        print("✅ Email sent successfully!")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

# ✅ Main Notify Function (for Accident & Crime Detection)
def notify_all(accident=False, theft=False):
    if accident and theft:
        subject = "Accident & Crime Alert"
        message = "🚨 Accident and 🔫 Crime Detected together! Immediate attention required!"
    elif accident:
        subject = "Accident Alert"
        message = "🚨 Accident Detected. Immediate attention required!"
    elif theft:
        subject = "Crime Alert"
        message = "🔫 Crime Detected (Theft/Robbery/Violence)!"
    else:
        return  # No notification needed

    receiver_email = os.getenv("EMAIL_RECEIVER")
    send_email_notification(subject, message, receiver_email)
