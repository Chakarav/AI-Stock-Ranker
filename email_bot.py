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
    print("📧 Starting Email Bot...")
    
    # --- FIX 1: CHECK BOTH PASSWORD NAMES ---
    # We try 'EMAIL_PASSWORD' first. If missing, we try 'APP_PASSWORD'.
    raw_pass = os.environ.get("EMAIL_PASSWORD")
    if not raw_pass:
        raw_pass = os.environ.get("APP_PASSWORD")
        
    if not raw_pass:
        print("❌ CRITICAL: Could not find password in environment variables.")
        exit(1)
        
    # Clean the password (remove spaces)
    password = raw_pass.replace(" ", "").strip()
    print("✅ Password found.")

    # --- FIX 2: TARGET THE RIGHT FILE ---
    # We ONLY look for files ending in "_rankings.csv"
    # This prevents it from reading the backtest history file.
    files = glob.glob("*_rankings.csv")
    
    if not files:
        print("❌ No '_rankings.csv' file found. Checking folder...")
        print(os.listdir(".")) # Print all files to debug
        return
            
    filename = files[0]
    print(f"✅ Reading Correct Data from: {filename}")
    
    try:
        # 3. READ & SELECT DATA
        df = pd.read_csv(filename)
        
        # Smart column selection (Prevents crashing if a column is missing)
        # We assume 'Close' is the price.
        desired_cols = ['Ticker', 'Close', 'Alpha_Score', 'RSI', 'Data_Source']
        cols = [c for c in desired_cols if c in df.columns]
        
        # Get top 10 rows
        top_picks = df[cols].head(10)

        # 4. COMPOSE HTML EMAIL
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"🚀 Daily AlphaQuant: {datetime.now().strftime('%d-%b')}"
        msg["From"] = SENDER
        msg["To"] = ", ".join(RECEIVERS)
        
        html = f"""
        <html>
          <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2E86C1;">Daily Market Intelligence</h2>
            <p>Top 10 High-Conviction Setups:</p>
            {top_picks.to_html(index=False, border=1, justify="center")}
            <p style="color: gray; font-size: 12px; margin-top: 20px;">
               Automated by GitHub Actions | Data Source: {filename}
            </p>
          </body>
        </html>
        """
        msg.attach(MIMEText(html, "html"))

        # 5. SEND (Using SSL Connection)
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SENDER, password)
        server.sendmail(SENDER, RECEIVERS, msg.as_string())
        server.quit()
        print("✅ Professional Report Sent!")
        
    except Exception as e:
        print(f"❌ Error during processing: {e}")
        exit(1)

if __name__ == "__main__":
    send_email()
