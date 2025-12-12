import smtplib
import os
from email.mime.text import MIMEText
import socket

# 1. SETUP
SENDER = "vishwajeetchakaravarthi@gmail.com"
RECEIVER = "vishwajeetchakaravarthi@gmail.com"
PASSWORD = os.environ.get("EMAIL_PASSWORD")

print("🔍 DEBUG MODE: Port 465 SSL Test")

if not PASSWORD:
    print("❌ FATAL: Secret 'EMAIL_PASSWORD' is missing.")
    exit(1)

try:
    print("   1. Connecting to Gmail (Port 465)...")
    # FIX: Use SMTP_SSL directly (Port 465) instead of .starttls()
    # FIX: Added timeout=30 so it doesn't hang for an hour
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
    
    print(f"   2. Logging in as {SENDER}...")
    server.login(SENDER, PASSWORD)
    print("   ✅ Login Successful!")
    
    msg = MIMEText("If you see this, Port 465 worked perfectly.")
    msg["Subject"] = "🚨 TEST: Port 465 Success"
    msg["From"] = SENDER
    msg["To"] = RECEIVER
    
    server.sendmail(SENDER, RECEIVER, msg.as_string())
    print("   ✅ Email Sent!")
    server.quit()

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")
    exit(1)
