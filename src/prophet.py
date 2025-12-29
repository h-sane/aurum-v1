import pandas as pd
import numpy as np
import json
import os
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import warnings

warnings.filterwarnings("ignore")

DATA_FILE = "data/gold_prices.csv"
MOOD_FILE = "data/market_mood.json"
OUTPUT_FILE = "data/dashboard_data.json"
PREDICTION_LOG = "data/prediction_log.json"

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def prepare_features(df, sentiment_score):
    """
    Feature Engineering: Converts raw data into "Signals" for the AI.
    """
    # 1. Price Signals
    df['Prev_Close'] = df['Gold_Price_22k'].shift(1)
    
    # 2. Trend Signals (Moving Averages)
    df['SMA_5'] = df['Gold_Price_22k'].rolling(window=5).mean()
    df['SMA_15'] = df['Gold_Price_22k'].rolling(window=15).mean()
    
    # 3. Momentum Signal (RSI)
    delta = df['Gold_Price_22k'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # 4. External Signals (News & Currency)
    # We broadcast the *current* sentiment to the latest row for prediction
    df['Sentiment'] = 0.0 
    df.iloc[-1, df.columns.get_loc('Sentiment')] = sentiment_score
    
    # Currency Check: Ensure USD_INR exists (It should from your backfill)
    if 'USD_INR' not in df.columns:
        print("⚠️ Warning: USD_INR not found. Using dummy values (Legacy Mode).")
        df['USD_INR'] = 83.0 # Fallback

    # Drop NaNs created by lag/rolling features
    df = df.dropna()
    return df

def run_oracle():
    print("--- 🧠 Starting Random Forest Oracle (Multivariate) ---")
    
    if not os.path.exists(DATA_FILE):
        print("❌ Error: No data found.")
        return

    # 1. Load Data
    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    mood_data = load_json(MOOD_FILE)
    current_sentiment = mood_data.get('sentiment_score', 0)

    # 2. Feature Engineering
    df_features = prepare_features(df.copy(), current_sentiment)
    
    if len(df_features) < 50:
        print("⚠️ Not enough data for Random Forest. (Run backfill.py first)")
        return

    # 3. Train the Model
    # Features: [Prev_Close, USD_INR, SMA_5, SMA_15, RSI, Sentiment]
    feature_cols = ['Prev_Close', 'USD_INR', 'SMA_5', 'SMA_15', 'RSI', 'Sentiment']
    
    X = df_features[feature_cols].values
    y = df_features['Gold_Price_22k'].values
    
    # Train on T-1 to predict T (Standard Time Series Supervised Learning)
    X_train = X[:-1] 
    y_train = y[1:]  
    
    # The Random Forest Config (100 Trees, limited depth to prevent overfitting)
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # 4. Predict Tomorrow
    # Use Today's features to predict Tomorrow
    X_today = X[-1].reshape(1, -1)
    prediction = int(model.predict(X_today)[0])
    
    print(f"🌲 Random Forest Prediction: ₹{prediction} (10g)")

    # --- ACCURACY LOGGING (Fixed Logic) ---
    pred_log = load_json(PREDICTION_LOG)
    today_str = datetime.now().strftime('%Y-%m-%d')
    yest_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    tom_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    accuracy_msg = "N/A (Tracking)"
    last_error = None
    
    # Compare ACTUAL TODAY vs PREDICTED YESTERDAY
    if yest_str in pred_log:
        pred_yest = pred_log[yest_str]
        actual_today = df['Gold_Price_22k'].iloc[-1]
        last_error = actual_today - pred_yest
        accuracy_msg = f"₹{abs(last_error)}"
        print(f"🎯 Accuracy Check: Pred (Yest) ₹{pred_yest} vs Actual ₹{actual_today} (Diff: {last_error})")

    # Save Tomorrow's prediction
    pred_log[tom_str] = prediction
    save_json(PREDICTION_LOG, pred_log)

    # --- OUTPUT FOR DASHBOARD ---
    last_row = df_features.iloc[-1]
    
    # Determine Status
    rsi = last_row['RSI']
    volatility_status = "High ⚡" if rsi > 70 or rsi < 30 else "Stable 🌊"
    trend_signal = "BULLISH 🟢" if last_row['SMA_5'] > last_row['SMA_15'] else "BEARISH 🔴"
    
    dashboard_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_price": int(last_row['Gold_Price_22k']),
        "current_price_1g": int(last_row['Gold_Price_22k'] / 10), # Explicit 1g Calculation
        "yesterday_price": int(df_features.iloc[-2]['Gold_Price_22k']),
        "forecast_price": prediction,
        "forecast_price_1g": int(prediction / 10), # Explicit 1g Forecast
        "accuracy_last_error": last_error,
        "volatility_status": volatility_status,
        "trend_signal": trend_signal,
        "rsi": round(rsi, 2),
        "history": {
            "dates": df['Date'].dt.strftime('%Y-%m-%d').tolist()[-30:],
            "prices": df['Gold_Price_22k'].tolist()[-30:]
        }
    }
    
    save_json(OUTPUT_FILE, dashboard_data)
    print("✅ Advanced Analysis Complete.")

if __name__ == "__main__":
    run_oracle()