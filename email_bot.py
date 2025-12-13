import smtplib
import pandas as pd
import os
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# CONFIGURATION
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 
SENDER = "vishwajeetchakaravarthi@gmail.com"
RECEIVERS = ["vishwajeetchakaravarthi@gmail.com"]

def send_email():
    print("📧 Starting Multi-Market Email Bot...")
    
    # 1. AUTH
    # Check both potential secret names
    raw_pass = os.environ.get("EMAIL_PASSWORD")
    if not raw_pass:
        raw_pass = os.environ.get("APP_PASSWORD")
        
    if not raw_pass:
        print("❌ CRITICAL: Password missing.")
        exit(1)
        
    password = raw_pass.replace(" ", "").strip()

    # 2. FIND ALL RANKING FILES
    # This will find both 'IN_rankings.csv' AND 'US_rankings.csv'
    files = glob.glob("*_rankings.csv")
    
    if not files:
        print("❌ No ranking files found.")
        return

    print(f"✅ Found files: {files}")

    # 3. BUILD EMAIL CONTENT
    email_html_body = ""
    
    # Loop through EVERY file found (India AND US)
    for filename in files:
        print(f"   Processing: {filename}...")
        try:
            df = pd.read_csv(filename)
            
            # Determine Region Name from filename (e.g., "IN_rankings.csv" -> "IN")
            region_name = filename.split("_")[0] 
            
            # Smart Column Selection
            desired_cols = ['Ticker', 'Close', 'Alpha_Score', 'RSI', 'Data_Source']
            cols = [c for c in desired_cols if c in df.columns]
            
            # Top 10 for this region
            top_picks = df[cols].head(10)
            
            # Add a Header and Table for this region
            email_html_body += f"""
            <h3 style="color: #2E86C1; margin-top: 20px;">📍 Region: {region_name} Market</h3>
            {top_picks.to_html(index=False, border=1, justify="center")}
            <p style="font-size: 10px; color: gray;">Source: {filename}</p>
            <hr>
            """
            
        except Exception as e:
            print(f"⚠️ Error processing {filename}: {e}")

    # 4. COMPOSE FINAL EMAIL
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🌍 Global AlphaQuant Report: {datetime.now().strftime('%d-%b')}"
    msg["From"] = SENDER
    msg["To"] = ", ".join(RECEIVERS)
    
    final_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #17202A;">🚀 Global Market Intelligence</h2>
        <p>Fresh high-conviction setups for all tracked markets:</p>
        
        {email_html_body}
        
        <p style="color: gray; font-size: 12px; margin-top: 30px;">
           Automated by GitHub Actions
        </p>
      </body>
    </html>
    """
    msg.attach(MIMEText(final_html, "html"))

    # 5. SEND
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(SENDER, password)
    server.sendmail(SENDER, RECEIVERS, msg.as_string())
    server.quit()
    print("✅ Global Report Sent!")

if __name__ == "__main__":
    send_email()
