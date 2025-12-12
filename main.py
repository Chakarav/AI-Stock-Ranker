import yfinance as yf
import pandas as pd
import time

def get_stock_data(tickers):
    """
    Robust download function that handles:
    1. YFTzMissingError (Timezone crash)
    2. Multi-Index Columns (New yfinance format)
    3. Empty Data (Network fails)
    """
    print(f"📥 Downloading data for {len(tickers)} stocks...")
    
    data = pd.DataFrame()
    
    # RETRY LOGIC: Try 3 times if Yahoo blocks us
    for attempt in range(3):
        try:
            # auto_adjust=False fixes some data alignment bugs
            data = yf.download(tickers, period="1y", interval="1d", auto_adjust=False, progress=False)
            
            if not data.empty:
                break
            else:
                print(f"   ⚠️ Attempt {attempt+1}: Downloaded empty data. Retrying...")
                time.sleep(2)
        except Exception as e:
            print(f"   ⚠️ Attempt {attempt+1} Failed: {e}")
            time.sleep(2)
    
    # CRITICAL CHECK: Did we actually get data?
    if data.empty:
        print("❌ CRITICAL ERROR: All download attempts failed. Using old data if available.")
        return None

    # FIX: Handle Multi-Index (Recent yfinance update changed columns to (Price, Ticker))
    # We only want 'Adj Close' or 'Close'
    try:
        if 'Adj Close' in data.columns:
            data = data['Adj Close']
        elif 'Close' in data.columns:
            data = data['Close']
        else:
            # Fallback for weird formats
            data = data.xs('Close', level=0, axis=1, drop_level=False)
    except Exception as e:
        print(f"   ⚠️ Column cleanup warning: {e}")
        
    # Drop tickers that failed completely (all NaNs)
    data = data.dropna(axis=1, how='all')
    
    print(f"✅ Successfully loaded data for {len(data.columns)} tickers.")
    return data

