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

# 🔗 YOUR DASHBOARD LINK
DASHBOARD_URL = "https://ai-stock-ranker-jmt6zuxodyrhsbrbgo7dck.streamlit.app"

def send_email():
    print("📧 Starting Email Bot...")
    
    # Auth
    raw_pass = os.environ.get("EMAIL_PASSWORD") or os.environ.get("APP_PASSWORD")
    if not raw_pass: exit(1)
    password = raw_pass.replace(" ", "").strip()

    # Find Files
    files = glob.glob("*_rankings.csv")
    if not files: return

    # Build Email Body
    email_html_body = ""
    for filename in files:
        try:
            df = pd.read_csv(filename)
            region_name = filename.split("_")[0] 
            
            # Select columns for EMAIL (Keep it simple for the inbox)
            # The Dashboard has the full details (PE, Margins, etc.)
            cols = [c for c in ['Ticker', 'Close', 'Alpha_Score', 'RSI'] if c in df.columns]
            top_picks = df[cols].head(5) 
            
            email_html_body += f"""
            <h3 style="color: #2E86C1; margin-top: 20px;">📍 {region_name} Top Picks</h3>
            {top_picks.to_html(index=False, border=1, justify="center")}
            """
        except: continue

    # COMPOSE FINAL EMAIL
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🌍 AlphaQuant Alert: {datetime.now().strftime('%d-%b')}"
    msg["From"] = SENDER
    msg["To"] = ", ".join(RECEIVERS)
    
    final_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #17202A;">🚀 Daily Market Intelligence</h2>
        
        {email_html_body}
        
        <br>
        <div style="text-align: center; margin-top: 30px;">
            <a href="{DASHBOARD_URL}" 
               style="background-color: #28B463; color: white; padding: 14px 25px; 
                      text-align: center; text-decoration: none; display: inline-block; 
                      font-size: 16px; border-radius: 5px; font-weight: bold;">
               📊 VIEW FULL DASHBOARD
            </a>
            <p style="color: gray; font-size: 12px; margin-top: 10px;">
               Click above to see PE Ratios, Valuation Maps, and Deep Analytics.
            </p>
        </div>
      </body>
    </html>
    """
    msg.attach(MIMEText(final_html, "html"))

    # SEND
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(SENDER, password)
    server.sendmail(SENDER, RECEIVERS, msg.as_string())
    server.quit()
    print("✅ Report Sent with Dashboard Link!")

if __name__ == "__main__":
    send_email()
