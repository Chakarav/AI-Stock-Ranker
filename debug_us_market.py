import yfinance as yf

print("--- 🔍 CHECKING REAL-TIME PRICES ---")

tickers = ["AAPL", "TSLA", "MSFT", "GOOGL"]
data = yf.download(tickers, period="1d", group_by='ticker')

for t in tickers:
    try:
        # Get the 'Close' price from the most recent available data point
        price = data[t]['Close'].iloc[-1]
        print(f"🇺🇸 {t}: {price:.2f}")
    except:
        print(f"❌ Failed to get {t}")

print("--- END CHECK ---")
