import json
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

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

def generate_advanced_charts(history):
    dates = history.get('dates', [])
    prices = history.get('prices', [])
    
    if not dates or not prices: return

    # Convert strings to datetime objects for better plotting
    date_objs = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    
    # Ensure assets folder exists
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # --- CHART 1: Price vs Moving Average (Trend) ---
    plt.figure(figsize=(10, 5))
    # Plot Price
    plt.plot(date_objs, prices, label='Gold Price (10g)', color='#d4af37', linewidth=2.5, marker='o', markersize=4)
    
    # Calculate & Plot 5-Day SMA (Simple Moving Average)
    if len(prices) >= 5:
        sma_5 = np.convolve(prices, np.ones(5)/5, mode='valid')
        # Adjust dates to match SMA length
        plt.plot(date_objs[4:], sma_5, label='5-Day Trend', color='#2c3e50', linestyle='--', linewidth=1.5)

    plt.title("Price Trend vs Short-Term Average", fontsize=14, fontweight='bold', color='#333333')
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend()
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("assets/trend_chart.png", dpi=100)
    plt.close()

    # --- CHART 2: Daily Volatility (Gains vs Losses) ---
    plt.figure(figsize=(10, 4))
    
    # Calculate daily changes
    changes = [0] + [prices[i] - prices[i-1] for i in range(1, len(prices))]
    colors = ['green' if c >= 0 else 'red' for c in changes]
    
    plt.bar(date_objs, changes, color=colors, alpha=0.7)
    plt.axhline(0, color='black', linewidth=0.8)
    plt.title("Daily Market Volatility (Net Change in ₹)", fontsize=14, fontweight='bold', color='#333333')
    plt.grid(True, axis='y', linestyle=':', alpha=0.6)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("assets/volatility_chart.png", dpi=100)
    plt.close()

def generate_readme():
    print("--- 📝 Generating Advanced Analytics Dashboard ---")
    data = load_json(DATA_FILE)
    mood = load_json(MOOD_FILE)
    
    if not data:
        print("⚠️ No data found. Run main.py first.")
        return

    # --- 1. DATA EXTRACTION ---
    price_10g = data.get('current_price', 0)
    price_1g  = data.get('current_price_1g', int(price_10g / 10))
    
    yest_10g = data.get('yesterday_price', 0)
    delta_10g = price_10g - yest_10g
    
    forecast_10g = data.get('forecast_price', 0)
    forecast_1g  = int(forecast_10g / 10)
    delta_forecast = forecast_10g - price_10g
    
    # Insights
    history_prices = data.get('history', {}).get('prices', [])
    if history_prices:
        high_30d = max(history_prices)
        low_30d = min(history_prices)
        avg_30d = int(sum(history_prices) / len(history_prices))
    else:
        high_30d = low_30d = avg_30d = price_10g

    # Signals
    trend = data.get('trend_signal', 'NEUTRAL')
    rsi = data.get('rsi', 50)
    
    # Strategic Advice Logic
    if rsi < 30:
        advice = "✅ BUY SIGNAL (Oversold)"
    elif rsi > 70:
        advice = "⚠️ WAIT / SELL (Overbought)"
    elif trend == "BULLISH 🟢":
        advice = "✅ ACCUMULATE (Trend Up)"
    else:
        advice = "⏳ HOLD (Market Uncertain)"

    # Scorecard
    scorecard = data.get('scorecard', {})
    
    # Generate Charts
    if 'history' in data:
        generate_advanced_charts(data['history'])

    # --- 2. MARKDOWN GENERATION ---
    md = f"""
# 🔱 Aurum-V2: Executive Analytics Suite

> **"Data-Driven Intelligence for the Indian Gold Market."** > *Engine: Random Forest Regressor | Strategy: {advice}*

<div align="center">

| 🏛️ Core Metric | 💰 10 Grams | 💎 1 Gram | 📉 Market Pulse |
| :--- | :---: | :---: | :---: |
| **Live Price** | **{fmt_price(price_10g)}** | **{fmt_price(price_1g)}** | **{trend}** |
| **Forecast (T+1)** | `{fmt_price(forecast_10g)}` | `{fmt_price(forecast_1g)}` | RSI: **{rsi}** |
| **Daily Move** | {get_arrow(delta_10g)} {fmt_price(abs(delta_10g))} | {get_arrow(delta_10g/10)} {fmt_price(int(abs(delta_10g)/10))} | Volatility: {data.get('volatility_status')} |

</div>

---

### 📊 Visual Intelligence
**1. Trend Confirmation:** *Is the price moving above the 5-Day average?* ![Trend Chart](assets/trend_chart.png)

**2. Volatility Scanner:** *Green bars indicate gains, Red bars indicate losses.* ![Volatility Chart](assets/volatility_chart.png)

---

### 🧠 Deep Dive Analytics
*Contextualizing today's price against the last 30 days.*

| 🔎 Insight | Value (10g) | Interpretation |
| :--- | :--- | :--- |
| **30-Day High** | {fmt_price(high_30d)} | Resistance Level |
| **30-Day Low** | {fmt_price(low_30d)} | Strong Support |
| **Monthly Avg** | {fmt_price(avg_30d)} | Baseline Price |
| **AI Confidence** | {scorecard.get('win_rate', 'N/A')}% | Directional Accuracy |

> **💡 Strategic Advice:** {advice}.  
> *Based on RSI of {rsi} and current trend momentum.*

---

### ⏳ The Time Machine (Forecast Accuracy)
| Timeline | Price (10g) | Price (1g) | Variance |
| :--- | :---: | :---: | :---: |
| **Yesterday** | {fmt_price(yest_10g)} | {fmt_price(int(yest_10g/10))} | - |
| **Today** | **{fmt_price(price_10g)}** | **{fmt_price(price_1g)}** | {get_arrow(delta_10g)} {fmt_price(abs(delta_10g))} |
| **Tomorrow (AI)** | `{fmt_price(forecast_10g)}` | `{fmt_price(forecast_1g)}` | {get_arrow(delta_forecast)} {fmt_price(abs(delta_forecast))} |

---

### 📰 Sentinel Intelligence
* **Market Mood:** **{load_json(MOOD_FILE).get('market_status', 'N/A')}**
"""
    
    # Add News
    headlines = load_json(MOOD_FILE).get('headlines', [])
    if headlines:
        for news in headlines[:3]:
            title = news.get('title', 'No Title')
            source = news.get('source', 'Google News')
            md += f"* **{source}:** *\"{title}\"*\n"
    else:
        md += "* *No significant market news detected today.*\n"

    md += f"\n---\n*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST*"

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print("✅ Advanced Dashboard Generated.")

if __name__ == "__main__":
    generate_readme()