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
    price = data['current_price']
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
    
    # Mermaid xychart syntax (GitHub supports this!)
    chart = "```mermaid\n"
    chart += "xychart-beta\n"
    chart += '    title "Gold Price Trend (30 Days)"\n'
    chart += '    x-axis [ ' + ", ".join([d.split("-")[2] for d in dates]) + " ]\n" # Just Show Days
    chart += '    y-axis "Price (INR)" ' + f"{min(prices)-500} --> {max(prices)+500}\n"
    chart += '    line [' + ", ".join(map(str, prices)) + "]\n"
    chart += "```"

    # --- BUILD THE MARKDOWN ---
    md = f"""
# 🏆 Aurum-V1: Autonomous Gold Intelligence

> **"A robust, self-correcting ETL pipeline that tracks, predicts, and analyzes the Indian Gold Market (22K) using Holt-Winters Exponential Smoothing and VADER Sentiment Analysis."**

### ⚡ Live Market Intelligence
| Metric | Status | Value |
| :--- | :--- | :--- |
| **Current Price (10g)** | {trend_symbol} | **₹{price:,}** |
| **Tomorrow's Forecast** | 🔮 | **₹{prediction:,}** |
| **Market Trend** | 📊 | **{trend}** |
| **RSI Strength** | 📉 | **{rsi}** (0-100) |
| **News Sentiment** | 🌍 | **{sentiment}** ({score}) |

---

### 📈 Price Action (Last 30 Days)
{chart}

### 🧠 The Oracle's Analysis
* **Technical View:** The market is currently **{trend}**. The Relative Strength Index (RSI) is **{rsi}**, suggesting the asset is {'Overbought (Risk of Pullback)' if rsi > 70 else 'Oversold (Buy Opportunity)' if rsi < 30 else 'Stable'}.
* **Fundamental View:** Sentinel analysis of global news feeds indicates a **{sentiment}** environment.
    * *Top Headline:* "{headlines[0] if headlines else 'No Major News'}"

---

### 🏗️ Architecture
* **Ingestion:** Custom `curl_cffi` driver to bypass WAFs on Indian financial sites.
* **Persistence:** Atomic CSV ledger with idempotent checks to prevent data corruption.
* **Prediction:** Holt-Winters Exponential Smoothing (Additive Trend) trained on a 64-day sliding window.
* **Context:** NLP Sentiment Analysis (VADER) on Google News RSS feeds to detect Geopolitical Risk ("War Premium").

---
*Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST | Automated by GitHub Actions*
"""

    # Overwrite README
    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(md)
    
    print("✅ README.md updated successfully.")

if __name__ == "__main__":
    generate_readme()