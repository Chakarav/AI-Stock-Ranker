import smtplib
import os
from email.mime.text import MIMEText

print("--- 🚀 STARTING RAW EMAIL TEST ---")

# 1. Force-Get Password (This will CRASH if the secret is missing)
# We do not use .get() so it errors out immediately if empty
password = os.environ["EMAIL_PASSWORD"] 

# 2. Clean Password (Remove spaces automatically)
password = password.replace(" ", "").strip()
print(f"✅ Password loaded (Length: {len(password)})")

# 3. Setup Email
sender = "vishwajeetchakaravarthi@gmail.com"
# Sending to yourself often triggers Spam filters, but we must try.
receiver = "vishwajeetchakaravarthi@gmail.com" 

msg = MIMEText("If you are reading this, the pipeline is PERFECT.")
msg['Subject'] = "🚨 FINAL TEST: GitHub Actions"
msg['From'] = sender
msg['To'] = receiver

# 4. Connect SSL (Standard Port 465)
print("⏳ Connecting to Google...")
server = smtplib.SMTP_SSL("smtp.gmail.com", 465)

# 5. Login (This will CRASH if password is wrong)
print("⏳ Logging in...")
server.login(sender, password)
print("✅ Login Success!")

# 6. Send
print("⏳ Sending email...")
server.sendmail(sender, receiver, msg.as_string())
server.quit()

print("✅ EMAIL SENT. CHECK SPAM FOLDER NOW.")
