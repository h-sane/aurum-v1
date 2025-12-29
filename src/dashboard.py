import json
import os
import matplotlib.pyplot as plt
from datetime import datetime

DATA_FILE = "data/dashboard_data.json"
MOOD_FILE = "data/market_mood.json"
README_FILE = "README.md"

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}

def fmt_price(price):
    return f"₹{price:,}"

def get_arrow(value):
    if value > 0: return "🔺"
    if value < 0: return "🔻"
    return "➖"

def generate_plot(history):
    dates = history.get('dates', [])
    prices = history.get('prices', [])
    if not dates or not prices: return

    if not os.path.exists("assets"): os.makedirs("assets")
        
    plt.figure(figsize=(10, 5))
    plt.plot(dates, prices, marker='o', linestyle='-', color='#d4af37', linewidth=2.5, markersize=5, label='Gold Price (10g)')
    plt.title(f"Gold Price Trend (Last {len(dates)} Days)", fontsize=14, fontweight='bold', color='#333333')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=9)
    plt.legend()
    plt.tight_layout()
    plt.savefig("assets/trend_chart.png", dpi=100)
    plt.close()

def generate_readme():
    print("--- 📝 Generating Performance Dashboard ---")
    data = load_json(DATA_FILE)
    mood = load_json(MOOD_FILE)
    
    if not data: return

    # Prices
    price_today_10g = data.get('current_price', 0)
    price_today_1g  = data.get('current_price_1g', int(price_today_10g / 10))
    price_yest_10g = data.get('yesterday_price', 0)
    price_yest_1g  = int(price_yest_10g / 10)
    forecast_10g = data.get('forecast_price', 0)
    forecast_1g  = data.get('forecast_price_1g', int(forecast_10g / 10))
    
    # Deltas
    delta_10g = price_today_10g - price_yest_10g
    delta_1g  = price_today_1g - price_yest_1g
    delta_forecast_10g = forecast_10g - price_today_10g
    delta_forecast_1g  = forecast_1g - price_today_1g
    
    # Scorecard
    scorecard = data.get('scorecard', {})
    mape = scorecard.get('mape', 'N/A')
    win_rate = scorecard.get('win_rate', 'N/A')
    mae = scorecard.get('mae', 'N/A')
    samples = scorecard.get('samples', 0)

    # Status
    trend = data.get('trend_signal', 'NEUTRAL')
    volatility = data.get('volatility_status', 'Stable')
    rsi = data.get('rsi', 0)
    sentiment_score = mood.get('sentiment_score', 0)
    headlines = mood.get('headlines', [])
    accuracy_display = f"₹{abs(data.get('accuracy_last_error'))}" if data.get('accuracy_last_error') is not None else "N/A"

    if 'history' in data: generate_plot(data['history'])

    md = f"""
# 🔱 Aurum-V1: Market Command Center

> **"Professional Intelligence for the Indian Gold Market."** > *Engine: Random Forest Regressor (Multivariate) | Signals: USD/INR, News, RSI.*

<div align="center">

| 🏛️ Metric | 💰 10 Grams (Standard) | 💎 1 Gram (Retail) | 📉 Status |
| :--- | :---: | :---: | :---: |
| **Current Price** | **{fmt_price(price_today_10g)}** | **{fmt_price(price_today_1g)}** | {trend} |
| **Tomorrow's Forecast** | `{fmt_price(forecast_10g)}` | `{fmt_price(forecast_1g)}` | {volatility} |
| **Change (vs Yest)** | {get_arrow(delta_10g)} {fmt_price(abs(delta_10g))} | {get_arrow(delta_1g)} {fmt_price(abs(delta_1g))} | RSI: {rsi} |

</div>

---

### 📊 Performance Scorecard
*How accurate is this AI? Metrics based on the last {samples} logged predictions.*

| Metric | Score | Description |
| :--- | :--- | :--- |
| **Directional Accuracy** | **{win_rate}%** | How often did we guess UP/DOWN correctly? (Target: >55%) |
| **Error Margin (MAPE)** | **{mape}%** | Average percentage error per prediction. (Lower is better) |
| **Avg Price Error (MAE)** | **₹{mae}** | On average, how far off is the price in Rupees? |

---

### ⏳ The Time Machine: Accuracy & Trend
| Timeline | Price (10g) | Price (1g) | Change (10g) | Insight |
| :--- | :---: | :---: | :---: | :--- |
| **Yesterday** | {fmt_price(price_yest_10g)} | {fmt_price(price_yest_1g)} | - | Historical Anchor |
| **Today** | **{fmt_price(price_today_10g)}** | **{fmt_price(price_today_1g)}** | {get_arrow(delta_10g)} {fmt_price(abs(delta_10g))} | **Actual Market Rate** |
| **Tomorrow** | `{fmt_price(forecast_10g)}` | `{fmt_price(forecast_1g)}` | {get_arrow(delta_forecast_10g)} {fmt_price(abs(delta_forecast_10g))} | *{volatility}* |

> **🎯 Daily Grading:** Yesterday's prediction error was **{accuracy_display}**.

---

### 🧠 The Oracle's Report
* **Prediction:** The model expects prices to move **{get_arrow(delta_forecast_10g)} {fmt_price(abs(delta_forecast_10g))} (10g)** / **{fmt_price(abs(delta_forecast_1g))} (1g)** tomorrow.
* **Confidence Check:** Market volatility is **{volatility}**. RSI is at **{rsi}**.

---

### 📰 Sentinel Intelligence
* **Market Mood:** **{mood.get('market_status', 'NEUTRAL')}** (Score: {sentiment_score})
* **Key Headlines:**
"""
    
    if headlines:
        for news in headlines[:3]:
            title = news.get('title', 'No Title')
            source = news.get('source', 'Google News')
            md += f"* Found in {source}: *\"{title}\"*\n"
    else:
        md += "* *No significant market news detected today.*\n"

    md += f"\n---\n*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST*"

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(md)
    print("✅ Dashboard Updated with Performance Metrics.")

if __name__ == "__main__":
    generate_readme()