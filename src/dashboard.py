import json
import os
from datetime import datetime

DASHBOARD_PATH = "data/dashboard_data.json"
MOOD_PATH = "data/market_mood.json"
README_PATH = "README.md"

def load_json(path):
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def generate_readme():
    print("--- 📝 Generating Dashboard (README.md) ---")
    
    data = load_json(DASHBOARD_PATH)
    mood_data = load_json(MOOD_PATH)
    
    if not data:
        print("⚠️ No dashboard data found. Skipping README update.")
        return

    # Extract Stats
    price_10g = data['current_price']
    price_1g = int(price_10g / 10)  # Calculate 1 gram price
    prediction = data['forecast_price']
    trend = data['trend_signal']
    rsi = data['rsi']
    
    # Extract Context (News)
    sentiment = mood_data.get('market_mood', 'NEUTRAL') if mood_data else "NEUTRAL"
    score = mood_data.get('sentiment_score', 0) if mood_data else 0
    headlines = mood_data.get('top_headlines', []) if mood_data else []
    
    # Format Symbols
    trend_symbol = "🟢" if "BULLISH" in trend else "🔴" if "BEARISH" in trend else "⚪"
    
    # Generate Mermaid Chart (Last 30 Days)
    dates = data['history']['dates']
    prices = data['history']['prices']
    
    # Mermaid xychart syntax
    chart = "```mermaid\n"
    chart += "xychart-beta\n"
    chart += '    title "Gold Price Trend (30 Days - 10g 22K)"\n'
    chart += '    x-axis [ ' + ", ".join([d.split("-")[2] for d in dates]) + " ]\n" 
    chart += '    y-axis "Price (INR)" ' + f"{min(prices)-500} --> {max(prices)+500}\n"
    chart += '    line [' + ", ".join(map(str, prices)) + "]\n"
    chart += "```"

    # --- BUILD THE MARKDOWN ---
    md = f"""
# 🏆 Aurum-V1: Autonomous Gold Intelligence

> **"A robust, self-correcting ETL pipeline that tracks, predicts, and analyzes the Indian Gold Market using Machine Learning and NLP."**

### ⚡ Live Market Intelligence
| Metric | Status | Value | Description |
| :--- | :--- | :--- | :--- |
| **Price (10g)** | {trend_symbol} | **₹{price_10g:,}** | Standard Jewellery Unit (22K) |
| **Price (1g)** | 🔹 | **₹{price_1g:,}** | Per Gram Unit |
| **Forecast** | 🔮 | **₹{prediction:,}** | Predicted price for tomorrow |
| **Momentum** | 📉 | **RSI {rsi}** | 0-30=Cheap, 70-100=Expensive |
| **Mood** | 🌍 | **{sentiment}** | Analysis of Global News Feeds |

---

### 📈 Price Action (Last 30 Days)
{chart}

---

### 🧠 The Oracle's Report
* **Technical Analysis:** The market is currently **{trend}**. The RSI is **{rsi}**.
    * *What this means:* {'The price is rising aggressively. Be cautious of a sudden drop.' if rsi > 70 else 'The price has dropped significantly. It might be a good time to buy.' if rsi < 30 else 'The market is stable with no extreme buying or selling pressure.'}
* **Fundamental Analysis:** Our Sentinel Bot scanned global news and detected a **{sentiment}** environment (Score: {score}).
    * *Top Headline:* "{headlines[0] if headlines else 'No Major News'}"

---

### 📚 How to Read This Dashboard
**1. What is RSI (Relative Strength Index)?**
Think of RSI as a speedometer for the price (0 to 100).
* **> 70 (Overbought):** The price went up too fast. It usually crashes soon after.
* **< 30 (Oversold):** The price dropped too fast. It usually bounces back up.

**2. Why Analyze News Sentiment?**
Gold is a "Fear Asset." 
* When the world is **scared** (War, Pandemic, Recession), people buy Gold -> **Price Goes UP.**
* When the world is **happy** (Peace, Strong Economy), people sell Gold -> **Price Goes DOWN.**
* *Our Sentinel Bot reads the news to see if the world is scared or happy.*

**3. What is Bullish vs. Bearish?**
* **🟢 Bullish:** The trend is UP (Like a Bull attacking with horns up).
* **🔴 Bearish:** The trend is DOWN (Like a Bear swiping with paws down).

---

### 🏗️ Technical Architecture
* **Ingestion:** Custom `curl_cffi` driver (mimics Chrome 120) to bypass WAFs.
* **Storage:** Atomic CSV ledger to prevent data corruption.
* **Prediction:** Holt-Winters Exponential Smoothing (Statistical ML).
* **Context:** VADER Sentiment Analysis on Google News RSS feeds.

---
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST | Automated by GitHub Actions*
"""

    # Overwrite README
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print("✅ README.md updated with Educational Sections.")

if __name__ == "__main__":
    generate_readme()