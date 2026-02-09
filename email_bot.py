import smtplib
import pandas as pd
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 
SENDER = "vishwajeetchakaravarthi@gmail.com"

# Load Subscribers
try:
    subs = pd.read_csv("subscribers.csv")
    RECEIVERS = subs['email'].dropna().unique().tolist()
except:
    RECEIVERS = ["vishwajeetchakaravarthi@gmail.com"]

DASHBOARD_URL = "https://ai-stock-ranker-jmt6zuxodyrhsbrbgo7dck.streamlit.app"

def send_email():
    print("📠 Generating Report...")
    raw_pass = os.environ.get("EMAIL_PASSWORD")
    if not raw_pass: 
        print("❌ No Password Found")
        return

    email_body = ""
    has_data = False

    # UPDATED FILENAMES HERE
    for region in ["US", "IN", "UK"]:
        filename = f"{region}_Market_Data.csv" 
        
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                if df.empty: continue
                
                df = df[['Ticker', 'Close', 'Blend_Score', 'SARIMA_Forecast_5D', 'PE_Ratio']].head(5)
                
                table_html = df.to_html(index=False, border=0)
                table_html = table_html.replace('class="dataframe"', 'style="width:100%; border-collapse:collapse; font-family:monospace; font-size:12px; margin-bottom:20px;"')
                table_html = table_html.replace('<th>', '<th style="text-align:right; background:#eee; padding:5px; border-bottom:2px solid black;">')
                table_html = table_html.replace('<td>', '<td style="text-align:right; padding:5px; border-bottom:1px solid #ddd;">')
                
                email_body += f"<h3 style='border-left:5px solid black; padding-left:10px;'>{region} MARKET</h3>{table_html}"
                has_data = True
            except: pass
    
    if not has_data:
        print("⚠️ No new data to send.")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"IRONGATE BRIEF: {datetime.now().strftime('%d %b')}"
    msg["From"] = "IronGate Research"
    msg["To"] = ", ".join(RECEIVERS)
    
    final_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>IRONGATE <span style="color:#666">GLOBAL</span></h2>
        <p style="font-size:12px; color:#555;">STRATEGY: VALUE/GROWTH STOCK FORECAST</p>
        <hr>
        {email_body}
        <br>
        <a href="{DASHBOARD_URL}" style="background:black; color:white; padding:10px 20px; text-decoration:none; font-weight:bold;">OPEN TERMINAL</a>
    </body>
    </html>
    """
    msg.attach(MIMEText(final_html, "html"))

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(SENDER, raw_pass)
        server.sendmail(SENDER, RECEIVERS, msg.as_string())
    
    print("✅ Email Sent.")

if __name__ == "__main__":
    send_email()

