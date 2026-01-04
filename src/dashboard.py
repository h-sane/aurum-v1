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

def create_ascii_bar(value, min_val=0, max_val=100, length=20):
    """Creates a visual progress bar for text (e.g., [|||||||......])"""
    normalized = int((value - min_val) / (max_val - min_val) * length)
    normalized = max(0, min(length, normalized)) # Clamp
    return f"[{'|' * normalized}{'.' * (length - normalized)}]"

def generate_advanced_charts(history):
    dates = history.get('dates', [])
    prices = history.get('prices', [])
    
    if not dates or not prices: return

    date_objs = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # --- CHART 1: Technical Analysis (Price + Support/Resistance) ---
    plt.figure(figsize=(10, 5))
    plt.plot(date_objs, prices, label='Gold Price', color='#FFD700', linewidth=2)
    
    # Dynamic Support/Resistance Lines
    max_p = max(prices)
    min_p = min(prices)
    plt.axhline(max_p, color='#e74c3c', linestyle='--', alpha=0.5, label=f'Resistance (₹{max_p:,})')
    plt.axhline(min_p, color='#2ecc71', linestyle='--', alpha=0.5, label=f'Support (₹{min_p:,})')
    
    plt.fill_between(date_objs, min_p, max_p, color='#FFD700', alpha=0.05) # Shading
    
    plt.title("Technical Landscape: Price vs Key Levels", fontsize=14, fontweight='bold', color='#ecf0f1')
    plt.legend(loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.3)
    
    # Dark Mode Style for Chart
    plt.gca().set_facecolor('#2c3e50')
    plt.gcf().patch.set_facecolor('#2c3e50')
    plt.tick_params(colors='white')
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['left'].set_color('white')
    plt.gca().xaxis.label.set_color('white')
    plt.gca().yaxis.label.set_color('white')
    plt.gca().title.set_color('white')
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("assets/trend_chart.png", dpi=100)
    plt.close()

def generate_readme():
    print("--- 📝 Generating Aurum-V3 Intelligence Dashboard ---")
    data = load_json(DATA_FILE)
    mood = load_json(MOOD_FILE)
    
    if not data: return

    # --- 1. DATA PROCESSING ---
    price_10g = data.get('current_price', 0)
    price_1g  = data.get('current_price_1g', int(price_10g / 10))
    forecast_10g = data.get('forecast_price', 0)
    
    # History Analysis (The Smart Part)
    history_prices = data.get('history', {}).get('prices', [])
    if history_prices:
        support_level = min(history_prices)
        resistance_level = max(history_prices)
        avg_price = sum(history_prices) / len(history_prices)
        
        # Position in Range (0% = at Support, 100% = at Resistance)
        if resistance_level != support_level:
            range_pos = (price_10g - support_level) / (resistance_level - support_level) * 100
        else:
            range_pos = 50
    else:
        support_level = resistance_level = price_10g
        range_pos = 50

    # Indicators
    rsi = data.get('rsi', 50)
    sentiment_score = mood.get('sentiment_score', 0)
    trend_signal = data.get('trend_signal', 'NEUTRAL')
    
    # --- 2. THE AI VERDICT GENERATOR ---
    # Synthesizing Technicals + Fundamentals into a Strategy
    verdict = ""
    strategy = ""
    
    if price_10g >= resistance_level * 0.99:
        verdict = "⚠️ CRITICAL: Testing Resistance."
        strategy = "Price is at the 30-day ceiling. Breakout above this level signals a massive rally. Rejection here could lead to a drop back to average."
    elif price_10g <= support_level * 1.01:
        verdict = "✅ OPPORTUNITY: Testing Support."
        strategy = "Price is at the 30-day floor. Historically a strong buying zone. Low downside risk."
    elif trend_signal == "BULLISH 🟢":
        verdict = "🚀 MOMENTUM: Strong Uptrend."
        strategy = f"Trend is healthy. Buy on dips. Next target is ₹{resistance_level:,}."
    else:
        verdict = "⚖️ CONSOLIDATION: Market Uncertain."
        strategy = "Price is ranging sideways. Wait for a clearer signal or trade small."

    # --- 3. DASHBOARD CONSTRUCTION ---
    if 'history' in data:
        generate_advanced_charts(data['history'])

    md = f"""
# 🔱 Aurum-V3: Strategic Market Intelligence

> **"The Analyst's View."**
> *Current Strategy: {verdict}*

<div align="center">

| 🏛️ Live Ticker | 💰 10 Grams | 💎 1 Gram | 🎯 T+1 Forecast |
| :--- | :---: | :---: | :---: |
| **Price** | **{fmt_price(price_10g)}** | **{fmt_price(price_1g)}** | `{fmt_price(forecast_10g)}` |
| **Trend** | {trend_signal} | RSI: {rsi} | {get_arrow(forecast_10g - price_10g)} {fmt_price(abs(forecast_10g - price_10g))} |

</div>

---

### 🧠 The AI Analyst's Verdict
**{verdict}**
> "{strategy}"

**Key Levels Watchlist:**
* 🔴 **Ceiling (Resistance):** **{fmt_price(resistance_level)}** *— Selling pressure likely here.*
* 🟢 **Floor (Support):** **{fmt_price(support_level)}** *— Buying interest likely here.*
* 📍 **Current Position:** Price is **{int(range_pos)}%** of the way to the top of its monthly range.

---

### 📊 Technical Landscape
*Visualizing the battle between Buyers (Support) and Sellers (Resistance).*

![Technical Chart](assets/trend_chart.png)

---

### 🌡️ Market Thermometer
*A quick gauge of market psychology.*

| Indicator | Status | Meter | Interpretation |
| :--- | :--- | :--- | :--- |
| **RSI (Momentum)** | **{rsi}** | `{create_ascii_bar(rsi, 0, 100)}` | { "Oversold (Cheap)" if rsi < 30 else "Overbought (Expensive)" if rsi > 70 else "Balanced" } |
| **Sentiment (News)** | **{sentiment_score}** | `{create_ascii_bar(sentiment_score, -0.5, 0.5)}` | { "Fear/Negative" if sentiment_score < -0.1 else "Greed/Positive" if sentiment_score > 0.1 else "Neutral" } |
| **Volatility** | **{data.get('volatility_status')}** | `------` | Market Energy |

---

### 📰 Sentinel Intelligence
* **Market Mood:** **{mood.get('market_status', 'NEUTRAL')}**
"""
    
    # News Section
    headlines = mood.get('headlines', [])
    if headlines:
        for news in headlines[:3]:
            source = news.get('source', 'Google News')
            title = news.get('title', 'No Title')
            md += f"* **{source}:** *\"{title}\"*\n"
    else:
        md += "* *No significant global drivers detected.*\n"

    md += f"\n---\n*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST*"

    with open(README_FILE, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print("✅ Aurum-V3 Dashboard Generated.")

if __name__ == "__main__":
    generate_readme()