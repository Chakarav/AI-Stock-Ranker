import smtplib
import pandas as pd
import os
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# CONFIG (SSL MODE)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 
SENDER = "vishwajeetchakaravarthi@gmail.com"
RECEIVERS = ["vishwajeetchakaravarthi@gmail.com"] 

def send_email():
    print("📧 DEBUG: Starting Email Bot...")
    
    # 1. CHECK PASSWORD
    password = os.environ.get("EMAIL_PASSWORD")
    if not password:
        print("❌ FATAL: Secret is missing.")
        return
    # Remove spaces just in case, though Google handles it
    password = password.replace(" ", "")

    # 2. FIND DATA
    files = glob.glob("*_rankings.csv")
    if not files:
        print("❌ FATAL: No CSV found.")
        return
    filename = files[0]
    
    try:
        df = pd.read_csv(filename)
        # SAFE COLUMNS ONLY
        cols = [c for c in ['Ticker', 'Close', 'Alpha_Score', 'Last_Updated'] if c in df.columns]
        top_picks = df[cols].head(5)
        
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"AlphaQuant LIVE: {datetime.now().strftime('%H:%M')}"
        msg["From"] = SENDER
        msg["To"] = ", ".join(RECEIVERS)
        
        html = f"<h3>Top Picks</h3>{top_picks.to_html(index=False, border=1)}"
        msg.attach(MIMEText(html, "html"))

        # SSL CONNECTION (No .starttls needed)
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER, password)
        server.sendmail(SENDER, RECEIVERS, msg.as_string())
        server.quit()
        print("✅ EMAIL SENT SUCCESSFULLY!")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    send_email()
