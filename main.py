import yfinance as yf
import pandas as pd
import requests
import time
from datetime import datetime

# --- CONFIGURATION ---
def get_stock_data(tickers):
    """
    Stealth Mode Download: Uses a fake 'User-Agent' to trick Yahoo 
    into thinking we are a real browser, preventing blocks/stale data.
    """
    print(f"📥 Downloading data for {len(tickers)} stocks in Stealth Mode...")
    
    # 1. Create a "Fake Browser" Session
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    })

    data = pd.DataFrame()
    
    # 2. Retry Logic with Session
    for attempt in range(3):
        try:
            # Pass the fake session to yfinance
            data = yf.download(
                tickers, 
                period="1y", 
                interval="1d", 
                auto_adjust=False, 
                progress=False,
                session=session  # <--- The Key Fix
            )
            
            if not data.empty:
                break
            else:
                print(f"   ⚠️ Attempt {attempt+1}: Yahoo sent empty data. Retrying...")
                time.sleep(2)
        except Exception as e:
            print(f"   ⚠️ Attempt {attempt+1} Failed: {e}")
            time.sleep(2)
    
    # 3. Final Check
    if data.empty:
        print("❌ CRITICAL ERROR: Yahoo blocked all attempts. Using backup data.")
        return None

    # 4. Clean Columns (Handle Multi-Index)
    try:
        if 'Adj Close' in data.columns:
            data = data['Adj Close']
        elif 'Close' in data.columns:
            data = data['Close']
        else:
            # Fallback for weird formats (New yfinance)
            data = data.xs('Close', level=0, axis=1, drop_level=False)
    except Exception as e:
        print(f"   ⚠️ Column cleanup warning: {e}")
        
    data = data.dropna(axis=1, how='all')
    
    # --- DATE VERIFICATION (The "Is it Today?" Test) ---
    if not data.empty:
        last_date = data.index[-1]
        today_date = pd.Timestamp.now().date()
        
        print(f"\n📅 DATA CHECK:")
        print(f"   Latest Date in File: {last_date.date()}")
        print(f"   Today's Date: {today_date}")
        
        if last_date.date() < today_date:
            print("⚠️ WARNING: Data is NOT from today yet. (Likely 15-min delay).")
        else:
            print("✅ SUCCESS: We have TODAY'S fresh data!")
            
    return data

# --- MAIN EXECUTION BLOCK (Placeholders for your logic) ---
# Paste your existing main logic below this function, 
# but make sure it calls THIS get_stock_data() function.
