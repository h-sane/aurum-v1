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

    # Create Asset Folder
    if not os.path.exists("assets"):
        os.makedirs("assets")
        
    plt.figure(figsize=(10, 5))
    # Plot Line
    plt.plot(dates, prices, marker='o', linestyle='-', color='#d4af37', linewidth=2.5, markersize=5, label='Gold Price (10g)')
    
    # Add Title & Grid
    plt.title(f"Gold Price Trend (Last {len(dates)} Days)", fontsize=14, fontweight='bold', color='#333333')
    plt.grid(True, linestyle='--', alpha=0.3)
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=9)
    plt.legend()
    plt.tight_layout()
    
    # Save
    img_path = "assets/trend_chart.png"
    plt.savefig(img_path, dpi=100)
    plt.close()

def generate_readme():
    print("--- 📝 Generating Hybrid Dashboard (Visuals + Intelligence) ---")
    
    data = load_json(DATA_FILE)
    mood = load_json(MOOD_FILE)
    
    if not data:
        print("⚠️ No data found. Run main.py first.")
        return

    # Extract Data
    price_today_10g = data.get('current_price', 0)
    price_today_1g = data.get('current_price_1g', int(price_today_10g / 10))
    
    forecast_10g = data.get('forecast_price', 0)
    forecast_1g = data.get('forecast_price_1g', int(forecast_10g / 10))
    
    price_yest_10g = data.get('yesterday_price', 0)
    
    # Deltas
    delta_10g = price_today_10g - price_yest_10g
    delta_forecast = forecast_10g - price_today_10g
    
    # Status
    trend = data.get('trend_signal', 'NEUTRAL')
    volatility = data.get('volatility_status', 'Stable')
    rsi = data.get('rsi', 0)
    
    sentiment_score = mood.get('sentiment_score', 0)
    sentiment_label = mood.get('market_status', 'NEUTRAL')
    
    # Accuracy Logic
    last_error = data.get('accuracy_last_error')
    accuracy_display = f"₹{abs(last_error)}" if last_error is not None else "N/A (Calibrating)"

    # Generate Chart
    if 'history' in data:
        generate_plot(data['history'])

    # --- MARKDOWN TEMPLATE ---
    md = f"""
# 🔱 Aurum-V1: Market Command Center

> **"Professional Intelligence for the Indian Gold Market."** > *Engine: Random Forest Regressor (Multivariate) | Signals: USD/INR, News, RSI.*

<div align="center">

| 🏛️ Metric | 💰 10 Grams (Standard) | 💎 1 Gram (Retail) | 📉 Status |
| :--- | :---: | :---: | :---: |
| **Current Price** | **{fmt_price(price_today_10g)}** | **{fmt_price(price_today_1g)}** | {trend} |
| **Tomorrow's Forecast** | `{fmt_price(forecast_10g)}` | `{fmt_price(forecast_1g)}` | {volatility} |
| **Change (vs Yest)** | {get_arrow(delta_10g)} {fmt_price(abs(delta_10g))} | {get_arrow(delta_10g/10)} {fmt_price(int(abs(delta_10g)/10))} | RSI: {rsi} |

</div>

---

### 📊 Market Trend Analysis
*Visualizing the price action over the last 30 days.*

![Gold Trend Chart](assets/trend_chart.png)

---

### ⏳ The Time Machine: Accuracy & Trend
*Comparing the Past, Present, and Future.*

| Timeline | Price (10g) | Change (₹) | Insight |
| :--- | :--- | :--- | :--- |
| **Yesterday** (Actual) | {fmt_price(price_yest_10g)} | - | Historical Anchor |
| **Today** (Live) | **{fmt_price(price_today_10g)}** | {get_arrow(delta_10g)} {fmt_price(abs(delta_10g))} | **Actual Market Rate** |
| **Tomorrow** (AI Forecast) | `{fmt_price(forecast_10g)}` | {get_arrow(delta_forecast)} {fmt_price(abs(delta_forecast))} | *{volatility}* |

> **🎯 AI Accuracy Tracker:** > Yesterday's prediction error was **{accuracy_display}**.  
> *The model learns from this error to improve future forecasts.*

---

### 🧠 The Oracle's Report
* **Prediction:** The model expects prices to move **{get_arrow(delta_forecast)} {fmt_price(abs(delta_forecast))}** tomorrow.
* **Confidence Check:** Market volatility is **{volatility}**. RSI is at **{rsi}**.
* **Key Drivers:** Predictions are now weighted by **USD/INR Exchange Rates** and **Global News Sentiment**.

---

### 📰 Sentinel Intelligence
* **Market Mood:** **{sentiment_label}** (Score: {sentiment_score})
* **Key Headlines:**
"""
    
    # Add News
    for news in mood.get('headlines', [])[:3]:
        title = news['title']
        source = news.get('source', 'Unknown')
        md += f"* Found in {source}: *\"{title}\"*\n"

    md += f"\n---\n*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST*"

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print("✅ Hybrid Dashboard Generated (Charts + Analytics Restored).")

if __name__ == "__main__":
    generate_readme()