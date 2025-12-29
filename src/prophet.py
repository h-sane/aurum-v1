import pandas as pd
import numpy as np
import json
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
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

def calculate_metrics(df, pred_log):
    """
    Compares historical predictions (from log) vs Actuals (from CSV).
    Returns a dictionary of 'Scorecard' metrics.
    """
    actuals = []
    preds = []
    directions_correct = 0
    total_direction_checks = 0

    # We need to pair up "Prediction made for Date X" with "Actual Price on Date X"
    # pred_log keys are Dates (Strings)
    
    # Create a lookup for actual prices
    price_map = dict(zip(df['Date'].dt.strftime('%Y-%m-%d'), df['Gold_Price_22k']))
    prev_actual = None

    sorted_dates = sorted(pred_log.keys())
    
    for date_str in sorted_dates:
        if date_str in price_map:
            actual = price_map[date_str]
            pred = pred_log[date_str]
            
            actuals.append(actual)
            preds.append(pred)

            # Directional Accuracy Logic
            # We need the day BEFORE this date to know if it actually went up or down
            # Finding "Yesterday" relative to date_str
            dt_obj = datetime.strptime(date_str, '%Y-%m-%d')
            yest_str = (dt_obj - timedelta(days=1)).strftime('%Y-%m-%d')
            
            if yest_str in price_map:
                prev_price = price_map[yest_str]
                
                # Did it actually go up?
                actual_move = "UP" if actual > prev_price else "DOWN"
                # Did we predict up?
                pred_move = "UP" if pred > prev_price else "DOWN"
                
                if actual_move == pred_move:
                    directions_correct += 1
                total_direction_checks += 1

    if not actuals:
        return {
            "mae": 0, "mape": 0, "rmse": 0, "win_rate": 0, "samples": 0
        }

    # Calculate Math Metrics
    mae = mean_absolute_error(actuals, preds)
    rmse = np.sqrt(mean_squared_error(actuals, preds))
    
    # MAPE (Mean Absolute Percentage Error)
    mape = np.mean(np.abs((np.array(actuals) - np.array(preds)) / np.array(actuals))) * 100
    
    # Win Rate
    win_rate = (directions_correct / total_direction_checks * 100) if total_direction_checks > 0 else 0

    return {
        "mae": int(mae),
        "rmse": int(rmse),
        "mape": round(mape, 2),
        "win_rate": round(win_rate, 1),
        "samples": len(actuals)
    }

def prepare_features(df, sentiment_score):
    df['Prev_Close'] = df['Gold_Price_22k'].shift(1)
    df['SMA_5'] = df['Gold_Price_22k'].rolling(window=5).mean()
    df['SMA_15'] = df['Gold_Price_22k'].rolling(window=15).mean()
    
    delta = df['Gold_Price_22k'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    df['Sentiment'] = 0.0 
    df.iloc[-1, df.columns.get_loc('Sentiment')] = sentiment_score
    
    if 'USD_INR' not in df.columns:
        df['USD_INR'] = 83.0

    df = df.dropna()
    return df

def run_oracle():
    print("--- 🧠 Starting Random Forest Oracle (With Self-Grading) ---")
    
    if not os.path.exists(DATA_FILE):
        print("❌ Error: No data found.")
        return

    df = pd.read_csv(DATA_FILE)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    mood_data = load_json(MOOD_FILE)
    current_sentiment = mood_data.get('sentiment_score', 0)

    # 1. Feature Engineering
    df_features = prepare_features(df.copy(), current_sentiment)
    
    if len(df_features) < 50:
        print("⚠️ Not enough data.")
        return

    # 2. Train Model
    feature_cols = ['Prev_Close', 'USD_INR', 'SMA_5', 'SMA_15', 'RSI', 'Sentiment']
    X = df_features[feature_cols].values
    y = df_features['Gold_Price_22k'].values
    
    X_train = X[:-1] 
    y_train = y[1:]  
    
    model = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train, y_train)
    
    # 3. Predict Tomorrow
    X_today = X[-1].reshape(1, -1)
    prediction = int(model.predict(X_today)[0])
    print(f"🌲 Prediction: ₹{prediction}")

    # 4. Accuracy Logging & Scorecard Calculation
    pred_log = load_json(PREDICTION_LOG)
    
    # A. Check Yesterday's Accuracy
    today_str = datetime.now().strftime('%Y-%m-%d')
    yest_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    tom_str = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    last_error = None
    if yest_str in pred_log:
        pred_yest = pred_log[yest_str]
        actual_today = df['Gold_Price_22k'].iloc[-1]
        last_error = actual_today - pred_yest

    # B. Generate Full Scorecard (The New Feature)
    scorecard = calculate_metrics(df, pred_log)
    print(f"📊 Live Scorecard: Win Rate {scorecard['win_rate']}% | MAPE {scorecard['mape']}%")

    # C. Save Tomorrow's prediction
    pred_log[tom_str] = prediction
    save_json(PREDICTION_LOG, pred_log)

    # 5. Output for Dashboard
    last_row = df_features.iloc[-1]
    
    dashboard_data = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "current_price": int(last_row['Gold_Price_22k']),
        "current_price_1g": int(last_row['Gold_Price_22k'] / 10),
        "yesterday_price": int(df_features.iloc[-2]['Gold_Price_22k']),
        "forecast_price": prediction,
        "forecast_price_1g": int(prediction / 10),
        "accuracy_last_error": last_error,
        "scorecard": scorecard,  # <--- Passing the metrics to dashboard
        "volatility_status": "High ⚡" if last_row['RSI'] > 70 or last_row['RSI'] < 30 else "Stable 🌊",
        "trend_signal": "BULLISH 🟢" if last_row['SMA_5'] > last_row['SMA_15'] else "BEARISH 🔴",
        "rsi": round(last_row['RSI'], 2),
        "history": {
            "dates": df['Date'].dt.strftime('%Y-%m-%d').tolist()[-30:],
            "prices": df['Gold_Price_22k'].tolist()[-30:]
        }
    }
    
    save_json(OUTPUT_FILE, dashboard_data)
    print("✅ Analysis Complete.")

if __name__ == "__main__":
    run_oracle()