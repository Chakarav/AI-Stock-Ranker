import yfinance as yf
import pandas as pd
import datetime

class DataEngine:
    def __init__(self):
        print("⚙️ Initializing Live Data Engine...")

    def fetch_data(self, tickers, region="US"):
        print(f"\n📥 STARTING DOWNLOAD: {region} Market ({len(tickers)} tickers)")
        
        # 1. PREPARE TICKERS
        # India needs '.NS' suffix for Yahoo Finance
        clean_tickers = []
        for t in tickers:
            t = t.strip()
            if region == "IN" and not t.endswith(".NS"):
                t = f"{t}.NS"
            clean_tickers.append(t)

        print(f"📋 Requesting: {clean_tickers}")

        # 2. DEFINE DATE RANGE (Last 1 Year for RSI/MA calculations)
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=365)

        # 3. DOWNLOAD DATA
        try:
            # group_by='ticker' ensures consistent format regardless of number of tickers
            data = yf.download(clean_tickers, start=start_date, end=end_date, group_by='ticker', progress=False)
            
            if data.empty:
                print(f"❌ CRITICAL: No data received for {region}.")
                return pd.DataFrame()

            processed_list = []

            # 4. PROCESS EACH TICKER
            for t in clean_tickers:
                try:
                    # Handle Multi-Index (If multiple tickers) or Single Index (If 1 ticker)
                    if len(clean_tickers) > 1:
                        df = data[t].copy()
                    else:
                        df = data.copy()

                    # Remove empty rows
                    df = df.dropna()

                    if df.empty:
                        print(f"⚠️ No data for {t}")
                        continue

                    # --- KEY STEP: VALIDATE LIVE PRICE ---
                    latest_price = df['Close'].iloc[-1]
                    # Convert to float to handle potential Series formatting
                    latest_price = float(latest_price)
                    print(f"✅ {t}: {latest_price:.2f}")

                    # Structure for Main Pipeline
                    df['Ticker'] = t.replace(".NS", "") # Clean name for CSV
                    df['Region'] = region
                    df = df.reset_index() # Ensure Date is a column

                    # Standardize Date Column Name
                    if 'Date' not in df.columns and 'Datetime' in df.columns:
                        df.rename(columns={'Datetime': 'Date'}, inplace=True)
                    
                    processed_list.append(df)

                except Exception as e:
                    print(f"⚠️ Error extracting {t}: {e}")

            if not processed_list:
                print("❌ All tickers failed processing.")
                return pd.DataFrame()

            # Combine
            final_df = pd.concat(processed_list)
            print(f"✅ SUCCESS: {len(final_df)} rows loaded for {region}.")
            return final_df

        except Exception as e:
            print(f"❌ FATAL DOWNLOAD ERROR: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Quick Test if run directly
    eng = DataEngine()
    eng.fetch_data(["AAPL", "TSLA"], region="US")
