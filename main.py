# src/main.py
from config import US_TICKERS, INDIA_TICKERS
from data_engine import DataEngine

# =================================
CHOSEN_MARKET = 'US'
# =================================

def run_pipeline():
    print(f"--- 🚀 STARTING PIPELINE FOR {CHOSEN_MARKET} ---")
    
    # 1. DEFINE TICKERS
    if CHOSEN_MARKET == 'US':
        # FALLBACK: If US_TICKERS is empty or fails, use this hardcoded list
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'AMD', 'NFLX', 'INTC']
        print(f"Using Hardcoded US List: {tickers}")
    else:
        tickers = INDIA_TICKERS[:15]

    # 2. RUN ENGINE
    engine = DataEngine(CHOSEN_MARKET)
    df = engine.fetch_data(tickers)
    
    # 3. SAVE RESULTS
    if not df.empty:
        filename = f"data/{CHOSEN_MARKET}_rankings.csv"
        df.to_csv(filename, index=False)
        print(f"\n✅ SUCCESS: Data saved to {filename}")
        print(df[['Ticker', 'Alpha_Score', 'EV_EBITDA', 'Margins']].head(3))
    else:
        print("❌ ERROR: No data found. Frame is empty.")

if __name__ == "__main__":
    run_pipeline()