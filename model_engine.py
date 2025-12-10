# src/model_engine.py
import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class ModelEngine:
    def __init__(self, market_name):
        self.market = market_name
        self.data_path = f"data/{market_name}_processed_data.csv"
        self.model = None

    def load_data(self):
        """Load the processed data we created earlier."""
        try:
            df = pd.read_csv(self.data_path)
            # Remove any rows that still have missing values
            df = df.dropna()
            return df
        except FileNotFoundError:
            print(f"Error: Could not find {self.data_path}. Did you run main.py first?")
            return None

    def train_model(self, df):
        """
        Train the XGBoost Machine Learning model.
        It learns: Given RSI, Momentum, SMA -> Will the stock go up?
        """
        print(f"--- Training ML Model for {self.market} ---")
        
        # 1. Define the features (Inputs)
        features = ['RSI', 'Return_1M', 'SMA_50', 'SMA_200']
        target = 'Target' # 1 = Up, 0 = Down

        X = df[features]
        y = df[target]

        # 2. Split data: 80% for training, 20% for testing
        # shuffle=False is CRITICAL for time-series (don't peek into the future)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

        # 3. Create and Train the Brain (XGBoost)
        self.model = xgb.XGBClassifier(
            n_estimators=100,    # Number of trees
            learning_rate=0.05,  # Speed of learning
            max_depth=3,         # How complex the trees can be
            random_state=42
        )
        
        self.model.fit(X_train, y_train)

        # 4. Check how smart it is
        predictions = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)
        print(f"Model Accuracy on Test Data: {accuracy:.2%}")
        
        return self.model

    def generate_rankings(self, df):
        """
        This combines traditional scores with ML predictions.
        """
        print("Generating Daily Rankings...")
        
        # Get the LATEST available data for each ticker (the most recent day)
        latest_data = df.groupby('Ticker').last().copy()
        
        # 1. Traditional Score (0 to 100)
        # Higher Momentum + Lower RSI (dip buying) is good
        latest_data['Factor_Score'] = (
            (latest_data['Return_1M'] * 100) +  # Momentum weight
            (100 - latest_data['RSI'])          # Mean reversion weight
        )

        # 2. ML Prediction (Probability)
        features = ['RSI', 'Return_1M', 'SMA_50', 'SMA_200']
        
        # Predict probability of going UP (Class 1)
        probs = self.model.predict_proba(latest_data[features])[:, 1]
        latest_data['ML_Confidence'] = probs

        # 3. Final Rank
        # Sort by ML Confidence first, then Factor Score
        ranked_stocks = latest_data.sort_values(by='ML_Confidence', ascending=False)
        
        return ranked_stocks[['ML_Confidence', 'Factor_Score', 'Close', 'RSI']]