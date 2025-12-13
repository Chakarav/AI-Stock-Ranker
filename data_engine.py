import yfinance as yf
import pandas as pd
import requests
import io
import datetime

class DataEngine:
    def __init__(self):
        print("⚙️ Initializing Dynamic Data Engine...")

    # --- DYNAMIC TICKER FETCHING ---
    def get_sp500_tickers(self):
        print("🔍 Scanning US Market (S&P 500)...")
        try:
            # Scrape Wikipedia for the live list
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            df = tables[0]
            tickers = df['Symbol'].tolist()
            # Clean tickers (Wikipedia uses '.' where Yahoo uses '-')
            tickers = [t.replace('.', '-') for t in tickers]
            print(f"✅ Found {len(tickers)} US Tickers.")
            return tickers
        except Exception as e:
            print(f"❌ Error fetching S&P 500: {e}")
            # Fallback if Wikipedia is down (Safety Net)
            return ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

    def get_nifty50_tickers(self):
        print("🔍 Scanning India Market (Nifty 50)...")
        try:
            # Official NSE CSV Source
            url = "https://archives.nseindia.com/content/indices/ind_nifty50list.csv"
            # Headers to mimic a real browser so NSE doesn't block us
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
            
            s = requests.get(url, headers=headers).content
            df = pd.read_csv(io.StringIO(s.decode('utf-8')))
            
            # Extract symbols and add .NS suffix
            tickers = [f"{x}.NS" for x in df['Symbol'].tolist()]
            print(f"✅ Found {len(tickers)} Indian Tickers.")
            return tickers
        except Exception as e:
            print(f"❌ Error fetching Nifty 50: {e}")
            # Fallback (Just in case NSE website is down)
            return ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS"]

    # --- LIVE DATA DOWNLOADER ---
    def fetch_data(self, tickers, region="US"):
        print(f"\n📥 Downloading Data for {len(tickers)} tickers ({region})...")
        
        # Limit to first 30 tickers for speed during testing
        # (Remove '[:30]' later if you want the FULL 500 stocks)
        tickers = tickers[:30] 

        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=365)

        try:
            # Batch download from Yahoo Finance
            data = yf.download(tickers, start=start_date, end=end_date, group_by='ticker', progress=False)
            
            processed_list = []

            for t in tickers:
                try:
                    # Handle data structure (Single vs Multi-Index)
                    if len(tickers) > 1:
                        df = data[t].copy()
                    else:
                        df = data.copy()

                    df = df.dropna()
                    if df.empty: continue

                    # Grab Live Price
                    latest_price = float(df['Close'].iloc[-1])
                    
                    # Structure Data
                    df['Ticker'] = t.replace(".NS", "") 
                    df['Region'] = region
                    df = df.reset_index()
                    
                    if 'Date' not in df.columns and 'Datetime' in df.columns:
                        df.rename(columns={'Datetime': 'Date'}, inplace=True)
                    
                    processed_list.append(df)
                except:
                    continue

            if not processed_list: return pd.DataFrame()

            return pd.concat(processed_list)

        except Exception as e:
            print(f"❌ Download Error: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    eng = DataEngine()
    sp500 = eng.get_sp500_tickers()
    print(f"Sample US: {sp500[:5]}")
    nifty = eng.get_nifty50_tickers()
    print(f"Sample IN: {nifty[:5]}")
