# src/main.py
from config import US_TICKERS, INDIA_TICKERS
from data_engine import DataEngine

# =================================
CHOSEN_MARKET = 'IN'  # Change to 'US' when needed
# =================================

def run_pipeline():
    # Use top 15 tickers for speed testing (Increase this later)
    if CHOSEN_MARKET == 'US': tickers = US_TICKERS[:15]
    else: tickers = INDIA_TICKERS[:15]

    engine = DataEngine(CHOSEN_MARKET)
    df = engine.fetch_data(tickers)
    
    if not df.empty:
        filename = f"data/{CHOSEN_MARKET}_rankings.csv"
        df.to_csv(filename, index=False)
        print(f"\nSUCCESS: Data saved to {filename}")
        print(df[['Ticker', 'Alpha_Score', 'EV_EBITDA', 'Margins']].head(3))
    else:
        print("No data found.")

if __name__ == "__main__":
    run_pipeline()