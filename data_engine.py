# src/data_engine.py
import yfinance as yf
import pandas as pd
import requests
from textblob import TextBlob

# ==========================================
# PASTE YOUR NEWSAPI KEY HERE
NEWS_API_KEY = "5f63e4cd71e04979836f15c58469710b"
# ==========================================

class DataEngine:
    def __init__(self, market_name):
        self.market = market_name

    def get_sentiment(self, ticker):
        query = ticker.replace('.NS', '')
        url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}&language=en&sortBy=publishedAt&pageSize=5"
        try:
            response = requests.get(url).json()
            articles = response.get('articles', [])
            if not articles: return 0.0
            
            score = 0
            for article in articles:
                title = article['title']
                if title: score += TextBlob(title).sentiment.polarity
            return score / len(articles)
        except:
            return 0.0

    def fetch_data(self, ticker_list):
        print(f"---  Initializing Institutional Data Scan ({self.market}) ---")
        all_data = []

        for ticker in ticker_list:
            print(f"Processing: {ticker}...")
            try:
                stock = yf.Ticker(ticker)
                
                # 1. Get Price History (Technical)
                hist = stock.history(period="6mo")
                if hist.empty: continue
                
                # 2. Get Deep Fundamentals
                info = stock.info
                
                # --- The "Hedge Fund" Metrics ---
                pe = info.get('trailingPE', 0)
                pb = info.get('priceToBook', 0)              # Value: < 1 is cheap
                ev_ebitda = info.get('enterpriseToEbitda', 0) # Better than P/E for debt-heavy firms
                debt_equity = info.get('debtToEquity', 0)    # Safety: > 200 is risky
                margins = info.get('profitMargins', 0)       # Quality: Higher is better
                roe = info.get('returnOnEquity', 0)          # Efficiency
                
                # 3. Sentiment
                sentiment = self.get_sentiment(ticker)
                
                # 4. Technical Indicators
                close_price = hist['Close'].iloc[-1]
                # Simple RSI Calculation
                delta = hist['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1]

                # 5. Composite Scoring Model (0-100)
                # We reward: Low Valuations (PE/EV), High Quality (Margins/ROE), Safe Debt, Positive Sentiment
                score = 0
                
                # Value Score (30%)
                if 0 < pe < 25: score += 15
                if 0 < ev_ebitda < 15: score += 15
                
                # Quality Score (30%)
                if margins > 0.15: score += 15  # >15% margin is healthy
                if roe > 0.15: score += 15      # >15% ROE is strong
                
                # Safety Score (20%)
                if debt_equity < 100: score += 20 # Low debt
                
                # Momentum/Sentiment (20%)
                if sentiment > 0.1: score += 10
                if 30 < current_rsi < 70: score += 10 # Not overbought
                
                # Append Data
                all_data.append({
                    'Ticker': ticker,
                    'Close': close_price,
                    'Alpha_Score': score,
                    'PE_Ratio': pe,
                    'EV_EBITDA': ev_ebitda,
                    'PB_Ratio': pb,
                    'Margins': margins * 100, # Percent
                    'ROE': roe * 100,         # Percent
                    'Debt_Equity': debt_equity,
                    'Sentiment': sentiment,
                    'RSI': current_rsi
                })
                
            except Exception as e:
                print(f"Failed on {ticker}")

        df = pd.DataFrame(all_data)
        return df.sort_values(by='Alpha_Score', ascending=False)