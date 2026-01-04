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
    return f"₹{int(price):,}"

def get_arrow(value):
    if value > 0: return "🔺"
    if value < 0: return "🔻"
    return "➖"

def create_ascii_bar(value, min_val=0, max_val=100, length=20):
    if max_val == min_val: 
        normalized_len = 0
    else:
        normalized_len = int((value - min_val) / (max_val - min_val) * length)
    
    normalized_len = max(0, min(length, normalized_len))
    return f"{'█' * normalized_len}{'░' * (length - normalized_len)}"

def generate_advanced_charts(history):
    dates = history.get('dates', [])
    prices_10g = history.get('prices', [])
    
    if not dates or not prices_10g: return

    # CHART PRIORITY: 1g (Retail)
    prices_1g = [p / 10 for p in prices_10g]
    date_objs = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
    
    if not os.path.exists("assets"):
        os.makedirs("assets")

    # --- CHART 1: Technical Landscape (1g) ---
    plt.figure(figsize=(10, 5))
    plt.plot(date_objs, prices_1g, label='Retail Price (1g)', color='#FFD700', linewidth=2)
    
    max_p = max(prices_1g)
    min_p = min(prices_1g)
    
    plt.axhline(max_p, color='#e74c3c', linestyle='--', alpha=0.5, label=f'Resist: ₹{int(max_p):,}')
    plt.axhline(min_p, color='#2ecc71', linestyle='--', alpha=0.5, label=f'Support: ₹{int(min_p):,}')
    plt.fill_between(date_objs, min_p, max_p, color='#FFD700', alpha=0.05)
    
    plt.title("Technical Landscape: Retail Price (1 Gram)", fontsize=14, fontweight='bold', color='#ecf0f1')
    plt.legend(loc='upper left')
    plt.grid(True, linestyle=':', alpha=0.3)
    
    # Dark Mode Styling
    plt.gca().set_facecolor('#2c3e50')
    plt.gcf().patch.set_facecolor('#2c3e50')
    plt.tick_params(colors='white')
    for spine in plt.gca().spines.values(): spine.set_color('white')
    plt.gca().xaxis.label.set_color('white')
    plt.gca().yaxis.label.set_color('white')
    plt.gca().title.set_color('white')
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("assets/trend_chart.png", dpi=100)
    plt.close()

    # --- CHART 2: Volatility (1g) ---
    plt.figure(figsize=(10, 4))
    changes = [0] + [prices_1g[i] - prices_1g[i-1] for i in range(1, len(prices_1g))]
    colors = ['#2ecc71' if c >= 0 else '#e74c3c' for c in changes] 
    
    plt.bar(date_objs, changes, color=colors, alpha=0.8)
    plt.axhline(0, color='white', linewidth=0.8)
    
    plt.title("Daily Movement (₹ per Gram)", fontsize=14, fontweight='bold', color='#ecf0f1')
    plt.grid(True, axis='y', linestyle=':', alpha=0.3)
    
    plt.gca().set_facecolor('#2c3e50')
    plt.gcf().patch.set_facecolor('#2c3e50')
    plt.tick_params(colors='white')
    for spine in plt.gca().spines.values(): spine.set_color('white')
    plt.gca().title.set_color('white')
    
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("assets/volatility_chart.png", dpi=100)
    plt.close()

def generate_readme():
    print("--- 📝 Generating Aurum-V5 Hybrid Dashboard ---")
    data = load_json(DATA_FILE)
    mood = load_json(MOOD_FILE)
    
    if not data: return

    # Data Processing
    price_10g = data.get('current_price', 0)
    price_1g  = int(price_10g / 10)
    
    yest_10g = data.get('yesterday_price', 0)
    yest_1g = int(yest_10g / 10)
    
    forecast_10g = data.get('forecast_price', 0)
    forecast_1g  = int(forecast_10g / 10)
    
    delta_1g = price_1g - yest_1g
    delta_forecast_1g = forecast_1g - price_1g

    # History Analysis (1g Basis)
    history_prices_10g = data.get('history', {}).get('prices', [])
    if history_prices_10g:
        history_1g = [p / 10 for p in history_prices_10g]
        support_level = min(history_1g)
        resistance_level = max(history_1g)
        if resistance_level != support_level:
            range_pos = (price_1g - support_level) / (resistance_level - support_level) * 100
        else:
            range_pos = 50
    else:
        support_level = resistance_level = price_1g
        range_pos = 50

    # Indicators
    rsi = data.get('rsi', 50)
    sentiment_score = mood.get('sentiment_score', 0)
    trend_signal = data.get('trend_signal', 'NEUTRAL')
    
    # Strategy (1g Priority)
    verdict = ""
    strategy = ""
    if price_1g >= resistance_level * 0.99:
        verdict = "⚠️ CRITICAL: Resistance Test"
        strategy = f"Price is hitting the ceiling (₹{int(resistance_level):,}). Breakout or Rejection imminent."
    elif price_1g <= support_level * 1.01:
        verdict = "✅ OPPORTUNITY: Support Test"
        strategy = f"Price is at the floor (₹{int(support_level):,}). Good entry point for buyers."
    elif trend_signal == "BULLISH 🟢":
        verdict = "🚀 MOMENTUM: Uptrend"
        strategy = f"Trend is healthy. Target: ₹{int(resistance_level):,}."
    else:
        verdict = "⚖️ CONSOLIDATION"
        strategy = "Market is sideways. Wait for clear direction."

    if 'history' in data:
        generate_advanced_charts(data['history'])

    md = f"""
# 🔱 Aurum-V5: Market Command Center

> **"Retail Focus. Industry Context."**
> *Strategy: {verdict}*

<div align="center">

| 💎 Retail (1g) | 🎯 Forecast (1g) | 🏛️ Industry (10g) |
| :---: | :---: | :---: |
| **{fmt_price(price_1g)}** | `{fmt_price(forecast_1g)}` | **{fmt_price(price_10g)}** |
| {get_arrow(delta_1g)} {fmt_price(abs(delta_1g))} | {get_arrow(delta_forecast_1g)} {fmt_price(abs(delta_forecast_1g))} | {trend_signal} |

</div>

---

### ⏳ The Time Machine (Side-by-Side Comparison)
*Comprehensive breakdown of price action across units.*

| Timeline | 💎 Price (1g) | 🏛️ Price (10g) | Change (1g) | Status |
| :--- | :---: | :---: | :---: | :--- |
| **Yesterday** | {fmt_price(yest_1g)} | {fmt_price(yest_10g)} | - | Historical |
| **Today** | **{fmt_price(price_1g)}** | **{fmt_price(price_10g)}** | {get_arrow(delta_1g)} {fmt_price(abs(delta_1g))} | **Actual** |
| **Tomorrow** | `{fmt_price(forecast_1g)}` | `{fmt_price(forecast_10g)}` | {get_arrow(delta_forecast_1g)} {fmt_price(abs(delta_forecast_1g))} | *Forecast* |

---

### 🧠 Analyst Verdict (Retail View)
**{verdict}**
> "{strategy}"

* 🔴 **Ceiling:** **{fmt_price(resistance_level)}** (1g)
* 🟢 **Floor:** **{fmt_price(support_level)}** (1g)
* 📍 **Range:** Price is **{int(range_pos)}%** of the way to the top.

---

### 📊 Visual Intelligence (1g)
**1. Technical Landscape:** *Support & Resistance Levels.*
![Technical Chart](assets/trend_chart.png)

**2. Volatility Scanner:** *Daily Price Change.*
![Volatility Chart](assets/volatility_chart.png)

---

### 🌡️ Market Thermometer

| Indicator | Status | Meter | Interpretation |
| :--- | :--- | :--- | :--- |
| **RSI** | **{rsi}** | `{create_ascii_bar(rsi, 0, 100)}` | { "Buy" if rsi < 30 else "Sell" if rsi > 70 else "Hold" } |
| **Sentiment** | **{sentiment_score}** | `{create_ascii_bar(sentiment_score, -0.5, 0.5)}` | { "Fear" if sentiment_score < -0.1 else "Greed" if sentiment_score > 0.1 else "Neutral" } |
| **Volatility** | **{data.get('volatility_status')}** | `------` | Market Energy |

---

### 📰 Sentinel Intelligence
* **Market Mood:** **{mood.get('market_status', 'NEUTRAL')}**
"""
    
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
    
    print("✅ Aurum-V5 Hybrid Dashboard Generated.")

if __name__ == "__main__":
    generate_readme()