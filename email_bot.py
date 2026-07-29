import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 
SENDER = "vishwajeetchakaravarthi@gmail.com"

# Load Subscribers
try:
    subs = pd.read_csv("subscribers.csv")
    RECEIVERS = subs['email'].dropna().unique().tolist()
except Exception:
    RECEIVERS = ["vishwajeetchakaravarthi@gmail.com"]

DASHBOARD_URL = "https://ai-stock-ranker-jmt6zuxodyrhsbrbgo7dck.streamlit.app"

def send_email():
    print("📠 Generating Report...")
    
    # 1. Fetch password safely and strip spaces/newlines
    raw_pass = os.environ.get("EMAIL_PASSWORD")
    if not raw_pass: 
        print("❌ Error: EMAIL_PASSWORD environment variable is missing or empty.")
        return

    raw_pass = raw_pass.strip()
    email_body = ""
    has_data = False

    # Process Market Data
    for region in ["US", "IN", "UK"]:
        filename = f"{region}_Market_Data.csv" 
        
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                if df.empty: 
                    continue
                
                df = df[['Ticker', 'Close', 'Blend_Score', 'SARIMA_Forecast_5D', 'PE_Ratio']].head(5)
                
                table_html = df.to_html(index=False, border=0)
                table_html = table_html.replace('class="dataframe"', 'style="width:100%; border-collapse:collapse; font-family:monospace; font-size:12px; margin-bottom:20px;"')
                table_html = table_html.replace('<th>', '<th style="text-align:right; background:#eee; padding:5px; border-bottom:2px solid black;">')
                table_html = table_html.replace('<td>', '<td style="text-align:right; padding:5px; border-bottom:1px solid #ddd;">')
                
                email_body += f"<h3 style='border-left:5px solid black; padding-left:10px;'>{region} MARKET</h3>{table_html}"
                has_data = True
            except Exception as e:
                print(f"⚠️ Error processing {filename}: {e}")
    
    if not has_data:
        print("⚠️ No new data to send.")
        return

    # 2. Build MIME Email
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"IRONGATE BRIEF: {datetime.now().strftime('%d %b')}"
    msg["From"] = f"IronGate Research <{SENDER}>"
    msg["To"] = ", ".join(RECEIVERS)
    
    final_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h2>IRONGATE <span style="color:#666">GLOBAL</span></h2>
        <hr>
        {email_body}
        <br>
        <a href="{DASHBOARD_URL}" style="background:black; color:white; padding:10px 20px; text-decoration:none; font-weight:bold;">OPEN TERMINAL</a>
    </body>
    </html>
    """
    msg.attach(MIMEText(final_html, "html"))

    # 3. SMTP SSL Authentication
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(SENDER, raw_pass)
            server.sendmail(SENDER, RECEIVERS, msg.as_string())
        print("✅ Email Sent successfully.")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication Failed: Check your EMAIL_PASSWORD in GitHub Secrets.")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

if __name__ == "__main__":
    send_email()
