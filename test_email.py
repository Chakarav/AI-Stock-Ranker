import smtplib
import os
from email.mime.text import MIMEText

# 1. SETUP
SENDER = "vishwajeetchakaravarthi@gmail.com"
RECEIVER = "vishwajeetchakaravarthi@gmail.com"
PASSWORD = os.environ.get("EMAIL_PASSWORD") # We will check if this is finding the secret

print("🔍 DEBUG MODE: Started.")

# 2. CHECK PASSWORD
if not PASSWORD:
    print("❌ FATAL ERROR: The robot cannot find your 'EMAIL_PASSWORD' secret.")
    print("   Fix: Go to Settings -> Secrets. make sure the name is EXACTLY 'APP_PASSWORD' or 'EMAIL_PASSWORD'.")
    exit(1)
else:
    print(f"✅ Password found (Length: {len(PASSWORD)} chars).")

# 3. TRY TO CONNECT
try:
    print(f"   Connecting to Gmail...")
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    
    print(f"   Logging in as {SENDER}...")
    server.login(SENDER, PASSWORD)
    print("   ✅ Login Successful!")
    
    # 4. SEND TEST EMAIL
    msg = MIMEText("If you are reading this, the pipeline is PERFECT. The issue was just the CSV file path.")
    msg["Subject"] = "🚨 TEST: The Robot is Alive"
    msg["From"] = SENDER
    msg["To"] = RECEIVER
    
    server.sendmail(SENDER, RECEIVER, msg.as_string())
    print("   ✅ Email Sent!")
    server.quit()

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")
    exit(1)
