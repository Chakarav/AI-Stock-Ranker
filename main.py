import pandas as pd
from data_engine import DataEngine

def run_pipeline():
    engine = DataEngine()
    
    # --------------------
    # 1. INDIA PIPELINE
    # --------------------
    print("\n🇮🇳 FETCHING NIFTY 50 DATA...")
    nifty_tickers = engine.get_nifty50_tickers()
    in_data = engine.fetch_data(nifty_tickers, region="IN")
    
    if not in_data.empty:
        # Sort by Alpha Score (Best Opportunities First)
        in_data = in_data.sort_values(by="Alpha_Score", ascending=False)
        in_data.to_csv("IN_rankings.csv", index=False)
        print("✅ SAVED: IN_rankings.csv")

    # --------------------
    # 2. US PIPELINE
    # --------------------
    print("\n🇺🇸 FETCHING S&P 500 DATA...")
    sp500_tickers = engine.get_sp500_tickers()
    us_data = engine.fetch_data(sp500_tickers, region="US")
    
    if not us_data.empty:
        # Sort by Alpha Score
        us_data = us_data.sort_values(by="Alpha_Score", ascending=False)
        us_data.to_csv("US_rankings.csv", index=False)
        print("✅ SAVED: US_rankings.csv")

if __name__ == "__main__":
    run_pipeline()
