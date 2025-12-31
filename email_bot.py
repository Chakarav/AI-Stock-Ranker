import smtplib
import pandas as pd
import os
import glob
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# CONFIG (Same as before)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465 
SENDER = "vishwajeetchakaravarthi@gmail.com"
# LOAD SUBSCRIBERS
try:
    subs_df = pd.read_csv("subscribers.csv")
    RECEIVERS = subs_df['email'].dropna().unique().tolist()
except:
    RECEIVERS = ["vishwajeetchakaravarthi@gmail.com"]

DASHBOARD_URL = "https://ai-stock-ranker-jmt6zuxodyrhsbrbgo7dck.streamlit.app"

def send_email():
    print("📠 Generating Global Brief...")
    
    raw_pass = os.environ.get("EMAIL_PASSWORD") or os.environ.get("APP_PASSWORD")
    if not raw_pass: exit(1)
    password = raw_pass.replace(" ", "").strip()

    email_html_body = ""
    
    # Process all 3 regions
    for region in ["US", "IN", "UK"]:
        filename = f"{region}_rankings.csv"
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                
                # Format Table
                cols = ['Ticker', 'Close', 'Blend_Score', 'SARIMA_Forecast_5D', 'PE_Ratio']
                display_df = df[cols].head(10) # TOP 10
                
                table_html = display_df.to_html(index=False, border=0)
                # Institutional Styling
                table_html = table_html.replace('class="dataframe"', 'style="width: 100%; border-collapse: collapse; font-family: \'Courier New\', monospace; font-size: 12px;"')
                table_html = table_html.replace('<th>', '<th style="text-align: right; padding: 4px; border-bottom: 2px solid #000; background: #f0f0f0;">')
                table_html = table_html.replace('<td>', '<td style="text-align: right; padding: 4px; border-bottom: 1px solid #ddd;">')
                
                email_html_body += f"""
                <div style="margin-bottom: 25px;">
                    <h3 style="font-family: Arial; border-left: 4px solid #000; padding-left: 10px;">
                        {region} MARKET / TOP 10
                    </h3>
                    {table_html}
                </div>
                """
            except: continue

    # EMAIL TEMPLATE
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"IRONGATE GLOBAL: {datetime.now().strftime('%d %b')}"
    msg["From"] = "IronGate Research"
    msg["To"] = ", ".join(RECEIVERS)
    
    final_html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #000; max-width: 800px;">
        <h2 style="letter-spacing: -1px;">IRONGATE <span style="color:#666">GLOBAL</span></h2>
        <p>STRATEGY: BLEND (Value+Growth) | MODEL: SARIMA (5-Day Forecast)</p>
        <hr style="border: 1px solid #000;">
        {email_html_body}
        <br>
        <a href="{DASHBOARD_URL}" style="background:#000; color:#fff; padding:10px 20px; text-decoration:none;">OPEN TERMINAL</a>
      </body>
    </html>
    """
    msg.attach(MIMEText(final_html, "html"))

    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
    server.login(SENDER, password)
    server.sendmail(SENDER, RECEIVERS, msg.as_string())
    server.quit()

if __name__ == "__main__":
    send_email()
