import smtplib
import pandas as pd
import os
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# CONFIG
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 
SENDER = "vishwajeetchakaravarthi@gmail.com"
RECEIVERS = ["vishwajeetchakaravarthi@gmail.com"]

def send_email():
    print("📧 Generating Daily Report...")
    
    # 1. AUTH
    password = os.environ["EMAIL_PASSWORD"].replace(" ", "").strip()

    # 2. DATA
    files = glob.glob("*.csv")
    filename = files[0] # Grab the first CSV found
    df = pd.read_csv(filename)
    
    # 3. SELECT TOP PICKS
    # Safe column selection to avoid crashes
    cols = [c for c in ['Ticker', 'Close', 'Alpha_Score', 'RSI', 'Data_Source'] if c in df.columns]
    top_picks = df[cols].head(10)

    # 4. COMPOSE
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🚀 Daily AlphaQuant: {datetime.now().strftime('%d-%b %H:%M')}"
    msg["From"] = SENDER
    msg["To"] = ", ".join(RECEIVERS)
    
    html = f"""
    <html>
      <body style="font-family: sans-serif;">
        <h2 style="color: #2E86C1;">Daily Market Intelligence</h2>
        <p>Top 10 High-Conviction Setups:</p>
        {top_picks.to_html(index=False, border=1, justify="center")}
        <p style="color: gray; font-size: 12px;">Automated by GitHub Actions</p>
      </body>
    </html>
    """
    msg.attach(MIMEText(html, "html"))

    # 5. SEND
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(SENDER, password)
    server.sendmail(SENDER, RECEIVERS, msg.as_string())
    server.quit()
    print("✅ Report Sent!")

if __name__ == "__main__":
    send_email()
