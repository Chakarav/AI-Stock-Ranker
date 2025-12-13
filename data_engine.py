import yfinance as yf
import pandas as pd
import datetime
import time

class DataEngine:
    def __init__(self):
        print("⚙️ Initializing Live Data Engine...")

    def fetch_data(self, tickers, region="US"):
        print(f"\n📥 STARTING DOWNLOAD: {region} Market ({len(tickers)} tickers)")
        
        # 1. CLEAN TICKERS
        # India needs '.NS', US needs nothing.
        clean_tickers = []
        for t in tickers:
            t = t.strip()
            if region == "IN" and not t.endswith(".NS"):
                t = f"{t}.NS"
            clean_tickers.append(t)

        print(f"📋 Ticker List: {clean_tickers}")

        # 2. DEFINE DATES (Last 1 year to ensure we have enough for RSI)
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=365)

        # 3. DOWNLOAD (FORCE YFINANCE)
        try:
            print(f"⏳ Contacting Yahoo Finance...")
            # group_by='ticker' ensures we get a structure we can loop through easily
            data = yf.download(clean_tickers, start=start_date, end=end_date, group_by='ticker', progress=False)
            
            if data.empty:
                print("❌ CRITICAL: Download returned EMPTY data.")
                return pd.DataFrame()

            processed_data = []

            # 4. PROCESS EACH TICKER
            for t in clean_tickers:
                try:
                    # Extract single ticker DF
                    if len(clean_tickers) == 1:
                        df = data.copy()
                    else:
                        df = data[t].copy()

                    # Drop empty rows
                    df = df.dropna()

                    if df.empty:
                        print(f"⚠️ No data found for {t} (Skipping)")
                        continue

                    # Get the LATEST price (Live Data)
                    latest_price = df['Close'].iloc[-1]
                    print(f"✅ {t}: {latest_price:.2f}")

                    # Structure it for the pipeline
                    df['Ticker'] = t.replace(".NS", "") # Remove .NS for cleaner display
                    df['Region'] = region
                    df = df.reset_index() # Make Date a column
                    
                    # Rename Date col if needed
                    if 'Date' not in df.columns and 'Datetime' in df.columns:
                        df.rename(columns={'Datetime': 'Date'}, inplace=True)

                    processed_data.append(df)

                except Exception as e:
                    print(f"⚠️ Error processing ticker {t}: {e}")

            if not processed_data:
                print("❌ ALL tickers failed processing.")
                return pd.DataFrame()

            # Combine all into one big table
            final_df = pd.concat(processed_data)
            print(f"✅ FINAL DATASET: {len(final_df)} rows.")
            return final_df

        except Exception as e:
            print(f"❌ FATAL DOWNLOAD ERROR: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Test Block
    engine = DataEngine()
    print("Testing US...")
    engine.fetch_data(["AAPL", "TSLA", "GOOGL"], region="US")
