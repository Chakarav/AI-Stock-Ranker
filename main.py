# src/main.py
from config import US_TICKERS, INDIA_TICKERS
from data_engine import DataEngine
from model_engine import ModelEngine
from backtest import run_backtest 

# ==========================================
# USER SETTINGS
CHOSEN_MARKET = 'IN'  # Change to 'US' or 'IN'
# ==========================================

def run_pipeline():
    # --- PHASE 1: DATA ---
    print(f"=== STEP 1: PROCESSING {CHOSEN_MARKET} DATA ===")
    
    if CHOSEN_MARKET == 'US':
        my_tickers = US_TICKERS
    else:
        my_tickers = INDIA_TICKERS

    data_eng = DataEngine(CHOSEN_MARKET)
    raw_data = data_eng.fetch_data(my_tickers)
    clean_data = data_eng.add_technical_indicators(raw_data, my_tickers)
    
    if clean_data.empty:
        print("Data processing failed.")
        return

    clean_data.to_csv(f"data/{CHOSEN_MARKET}_processed_data.csv")
    print("Data Ready.")

    # --- PHASE 2: MODEL & RANKING ---
    print(f"\n=== STEP 2: TRAINING MODEL ===")
    
    model_eng = ModelEngine(CHOSEN_MARKET)
    df = model_eng.load_data()
    
    if df is not None:
        model_eng.train_model(df)
        rankings = model_eng.generate_rankings(df)
        
        print("\n=== TOP 5 STOCK PICKS FOR TODAY ===")
        print(rankings.head(5))
        rankings.to_csv(f"data/{CHOSEN_MARKET}_rankings.csv")

    # --- PHASE 3: BACKTEST ---
    print(f"\n=== STEP 3: VERIFYING PERFORMANCE ===")
    run_backtest(CHOSEN_MARKET)

if __name__ == "__main__":
    run_pipeline()