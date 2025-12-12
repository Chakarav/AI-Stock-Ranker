import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

# ==================================================
# 🔐 CONFIGURATION
# ==================================================
EMAIL_SENDER = "vishwajeetchakaravarthi@gmail.com"
EMAIL_PASSWORD = "cxpu bbnm rqus mkva"
# Add all subscribers here (for now, hardcode them to ensure delivery)
SUBSCRIBERS = ["vishwajeetchakaravarthi@gmail.com"] 
DASHBOARD_URL = "https://ai-stock-ranker-jmt6zuxodyrhsbrbgo7dck.streamlit.app/"
# ==================================================

def load_data(market):
    """Loads the ranking data safely."""
    try:
        if os.path.exists(f"data/{market}_rankings.csv"):
            return pd.read_csv(f"data/{market}_rankings.csv")
        elif os.path.exists(f"{market}_rankings.csv"):
            return pd.read_csv(f"{market}_rankings.csv")
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

def generate_html_table(df, title, color):
    if df.empty:
        return f"<p style='color: #666;'><i>No data available for {title} today.</i></p>"
    
    # Select & Rename Columns for Email
    cols = ['Ticker', 'Alpha_Score', 'Close', 'PE_Ratio', 'EV_EBITDA']
    df = df[cols].head(5)
    df.columns = ['Ticker', 'Score', 'Price', 'P/E', 'EV/EBITDA']
    
    # Create HTML Table
    table_html = df.to_html(index=False, border=0, justify='left')
    
    # Apply Professional CSS Styles inline
    table_html = table_html.replace('<table border="0" class="dataframe">', 
        '<table style="width: 100%; border-collapse: collapse; font-family: Arial, sans-serif; font-size: 14px; margin-bottom: 20px;">')
    table_html = table_html.replace('<thead>', f'<thead style="background-color: {color}; color: white;">')
    table_html = table_html.replace('<th>', '<th style="padding: 10px; text-align: left;">')
    table_html = table_html.replace('<td>', '<td style="padding: 10px; border-bottom: 1px solid #ddd; color: #333;">')
    table_html = table_html.replace('tr style="text-align: left;"', 'tr')
    
    return f"<h3 style='color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px; margin-top: 20px;'>{title}</h3>" + table_html

def send_daily_briefing():
    print(f"📧 Generating Report for {len(SUBSCRIBERS)} subscribers...")
    
    df_in = load_data('IN')
    df_us = load_data('US')
    date_str = datetime.now().strftime('%d %b %Y')

    # Build the Email Body
    html_content = f"""
    <html>
        <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                
                <div style="background-color: #111; padding: 20px; text-align: center;">
                    <h1 style="color: #fff; margin: 0; font-size: 24px;">AlphaQuant <span style="color: #4caf50;">Daily</span></h1>
                    <p style="color: #aaa; margin: 5px 0 0; font-size: 12px;">INSTITUTIONAL GRADE ANALYTICS • {date_str}</p>
                </div>

                <div style="padding: 20px;">
                    <p style="color: #555; font-size: 14px; line-height: 1.5;">
                        Good morning. Our AI models have processed 500+ assets this morning. 
                        Below are the highest conviction opportunities based on valuation, momentum, and sentiment.
                    </p>
                    
                    {generate_html_table(df_in, "🇮🇳 Top India Opportunities", "#e67e22")}
                    {generate_html_table(df_us, "🇺🇸 Top US Opportunities", "#2980b9")}
                    
                    <div style="text-align: center; margin-top: 30px; margin-bottom: 20px;">
                        <a href="{DASHBOARD_URL}" style="background-color: #4caf50; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; font-size: 16px;">
                            🚀 Open Live Dashboard
                        </a>
                    </div>
                </div>

                <div style="background-color: #eee; padding: 15px; text-align: center; font-size: 11px; color: #777;">
                    <p>Alpha Score (0-100) combines Technicals, Fundamentals & News Sentiment.</p>
                    <p>Calculated automatically by AlphaQuant AI Engine.</p>
                </div>
            </div>
        </body>
    </html>
    """

    # Send to All Subscribers
    for email in SUBSCRIBERS:
        try:
            msg = MIMEMultipart()
            msg['From'] = f"AlphaQuant AI <{EMAIL_SENDER}>"
            msg['To'] = email
            msg['Subject'] = f"📈 Market Intel: Top Picks for {date_str}"
            msg.attach(MIMEText(html_content, 'html'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            print(f"✅ Sent to {email}")
        except Exception as e:
            print(f"❌ Failed to send to {email}: {e}")

if __name__ == "__main__":

    send_daily_briefing()

