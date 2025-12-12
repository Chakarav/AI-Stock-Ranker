import smtplib
import pandas as pd
import os
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# CONFIGURATION
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465  # <-- CHANGED TO SSL (More reliable)
SENDER = "vishwajeetchakaravarthi@gmail.com"
RECEIVERS = ["vishwajeetchakaravarthi@gmail.com"]

def send_email():
    print("--- 🔍 DEBUG LOG START ---")
    
    # 1. CHECK PASSWORD
    raw_password = os.environ.get("EMAIL_PASSWORD")
    if not raw_password:
        print("❌ CRITICAL FAILURE: Password Secret is EMPTY.")
        print("   -> Go to GitHub Settings -> Secrets -> Ensure APP_PASSWORD exists.")
        exit(1) # FORCE CRASH
    
    # CLEAN PASSWORD (Remove spaces and newlines)
    password = raw_password.replace(" ", "").strip()
    print(f"✅ Password found (Length: {len(password)})")

    # 2. FIND DATA
    files = glob.glob("*.csv")
    if not files:
        print("❌ CRITICAL FAILURE: No CSV file found in repository.")
        exit(1) # FORCE CRASH
    
    filename = files[0]
    print(f"✅ Found Data File: {filename}")

    # 3. PREPARE EMAIL
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"AlphaQuant Alert: {datetime.now().strftime('%H:%M:%S')}"
        msg["From"] = SENDER
        msg["To"] = ", ".join(RECEIVERS)
        
        # Simple body to avoid spam filters
        html_body = f"""
        <h3>AlphaQuant Pipeline Success</h3>
        <p>The workflow ran successfully at {datetime.now()}.</p>
        <p><b>Data Source:</b> {filename}</p>
        """
        msg.attach(MIMEText(html_body, "html"))
    except Exception as e:
        print(f"❌ Error preparing email: {e}")
        exit(1)

    # 4. SEND EMAIL (SSL MODE)
    try:
        print(f"⏳ Connecting to Gmail (SSL Port 465)...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        
        print(f"⏳ Logging in as {SENDER}...")
        server.login(SENDER, password)
        print("✅ Login Successful!")
        
        print(f"⏳ Sending email...")
        server.sendmail(SENDER, RECEIVERS, msg.as_string())
        server.quit()
        print("✅ EMAIL SENT SUCCESSFULLY! (Check Spam/Promotions)")
        
    except Exception as e:
        print(f"❌ FATAL CONNECTION ERROR: {e}")
        print("   -> If this is a 'Login' error, your APP_PASSWORD is invalid.")
        exit(1) # FORCE CRASH

if __name__ == "__main__":
    send_email()
