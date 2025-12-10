# src/data_engine.py
import yfinance as yf
import pandas as pd
import numpy as np
import os

class DataEngine:
    def __init__(self, market_name):
        # This remembers if we are doing 'US' or 'IN' (India)
        self.market = market_name
        self.file_path = f"data/{market_name}_raw_data.csv"

    def fetch_data(self, ticker_list):
        """
        Step 1: Go to the internet and download price history.
        """
        print(f"--- Downloading data for {self.market} market ---")
        
        # 'group_by=ticker' keeps the data organized by company name
        df = yf.download(ticker_list, period="2y", group_by='ticker', auto_adjust=True, threads=True)
        
        # Save this raw data just in case we need it later
        df.to_csv(self.file_path)
        print("Download complete.")
        return df

    def add_technical_indicators(self, big_dataframe, ticker_list):
        """
        Step 2: Do the math. Calculate RSI, Moving Averages, etc.
        """
        print("Calculating technical indicators (Math stuff)...")
        all_stocks_list = []

        for ticker in ticker_list:
            try:
                # 1. Grab the data for just THIS one stock
                # We use .copy() to make sure we don't mess up the original
                if ticker not in big_dataframe.columns.levels[0]:
                    print(f"Skipping {ticker} (No data found)")
                    continue
                    
                stock_df = big_dataframe[ticker].copy()
                stock_df = stock_df.dropna() # Remove empty rows

                if stock_df.empty:
                    continue

                # 2. Calculate RSI (Relative Strength Index)
                # This measures if a stock is 'overbought' or 'oversold'
                delta = stock_df['Close'].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                stock_df['RSI'] = 100 - (100 / (1 + rs))

                # 3. Calculate Momentum (How fast is it rising?)
                # Return over the last 1 month (21 trading days)
                stock_df['Return_1M'] = stock_df['Close'].pct_change(21)
                
                # 4. Moving Averages (Trend)
                stock_df['SMA_50'] = stock_df['Close'].rolling(50).mean()
                stock_df['SMA_200'] = stock_df['Close'].rolling(200).mean()

                # 5. Create the "Target" for Machine Learning
                # We want to predict: Will the price be higher in 10 days?
                # 1 = Yes, 0 = No
                future_price = stock_df['Close'].shift(-10)
                current_price = stock_df['Close']
                stock_df['Target'] = (future_price > current_price).astype(int)

                # Add the ticker name so we know who this belongs to
                stock_df['Ticker'] = ticker

                # Add to our list
                all_stocks_list.append(stock_df)

            except Exception as e:
                print(f"Error with {ticker}: {e}")

        # Combine all the individual stock tables into one giant table
        if len(all_stocks_list) > 0:
            final_df = pd.concat(all_stocks_list)
            # Remove the first 200 rows because moving averages need 200 days of data to start working
            final_df = final_df.dropna() 
            return final_df
        else:
            return pd.DataFrame()