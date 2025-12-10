# src/config.py
import pandas as pd
import requests
from niftystocks import ns

# ==========================================
# HELPER: THE STEALTH DOWNLOADER
# ==========================================
def get_table_from_web(url):
    """
    Downloads a webpage pretending to be a real browser (Chrome)
    to avoid HTTP 403 Forbidden errors.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            return pd.read_html(r.text)
        else:
            print(f"Failed to access {url} (Status: {r.status_code})")
            return []
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return []

# ==========================================
# INDIA: NIFTY 50 (Using Library or Fallback)
# ==========================================
def get_india_tickers():
    print("Fetching India (Nifty 50) list...")
    try:
        # Correct function is get_nifty50()
        tickers = ns.get_nifty50()
        # Add .NS for Yahoo Finance
        formatted = [t + '.NS' for t in tickers]
        print(f"Successfully fetched {len(formatted)} Indian stocks.")
        return formatted
    except Exception as e:
        print(f"Library failed ({e}). Using manual backup list.")
        # Backup list of top Indian stocks
        return [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'ICICIBANK.NS', 'INFY.NS',
            'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS', 'KOTAKBANK.NS', 'LICI.NS',
            'HINDUNILVR.NS', 'LT.NS', 'AXISBANK.NS', 'BAJFINANCE.NS', 'MARUTI.NS',
            'ASIANPAINT.NS', 'HCLTECH.NS', 'TITAN.NS', 'SUNPHARMA.NS', 'TATASTEEL.NS'
        ]

# ==========================================
# USA: S&P 500 (Scraping Wikipedia with Headers)
# ==========================================
def get_us_tickers():
    print("Fetching US (S&P 500) list...")
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    
    tables = get_table_from_web(url)
    
    if len(tables) > 0:
        # Table 0 is usually the S&P 500 list
        df = tables[0]
        tickers = df['Symbol'].tolist()
        # Fix: Yahoo uses '-' instead of '.' (e.g., BRK-B)
        clean_tickers = [t.replace('.', '-') for t in tickers]
        print(f"Successfully fetched {len(clean_tickers)} US stocks.")
        return clean_tickers
    else:
        print("Scraping failed. Using manual US backup.")
        return ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B', 'JPM']

# ==========================================
# EXPORT
# ==========================================
INDIA_TICKERS = get_india_tickers()
US_TICKERS = get_us_tickers()