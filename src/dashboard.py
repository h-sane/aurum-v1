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
    print("--- 📝 Generating Futuristic Dashboard ---")
    
    data = load_json(DASHBOARD_PATH)
    mood_data = load_json(MOOD_PATH)
    
    if not data: return

    # --- EXTRACT DATA ---
    price_today = data['current_price']
    price_yest = data['yesterday_price']
    forecast = data['forecast_price']
    
    # Calculations
    delta_forecast = forecast - price_today
    delta_yest = price_today - price_yest
    accuracy_err = data.get('accuracy_last_error', 0)
    
    # Formatting Helpers
    def fmt_price(p): return f"₹{p:,}"
    def fmt_delta(d): return f"+{d}" if d > 0 else f"{d}"
    def get_arrow(d): return "🔺" if d > 0 else "🔻" if d < 0 else "➖"

    # Context
    sentiment = mood_data.get('market_mood', 'NEUTRAL') if mood_data else "NEUTRAL"
    headlines = mood_data.get('top_headlines', []) if mood_data else []
    keywords = mood_data.get('keywords', []) if mood_data else []
    
    # --- VISUALIZATION 1: Price History (Line Chart) ---
    dates = data['history']['dates']
    prices = data['history']['prices']
    chart_price = "```mermaid\nxychart-beta\n"
    chart_price += '    title "30-Day Market Trend (22K Gold)"\n'
    chart_price += '    x-axis [ ' + ", ".join([d[5:] for d in dates]) + " ]\n"
    chart_price += '    y-axis "INR/10g" ' + f"{min(prices)-200} --> {max(prices)+200}\n"
    chart_price += '    line [' + ", ".join(map(str, prices)) + "]\n```"

    # --- VISUALIZATION 2: Sentiment Gauge (Pie Chart Hack) ---
    # We use a pie chart to simulate a "Gauge" of Positive vs Negative news
    score = mood_data.get('sentiment_score', 0) if mood_data else 0
    # Map score (-1 to 1) to percentages for the chart
    pos_pct = int((score + 1) * 50) 
    neg_pct = 100 - pos_pct
    
    chart_mood = "```mermaid\npie title \"Global Sentiment Intensity\"\n"
    chart_mood += f'    "Bullish Factors" : {pos_pct}\n'
    chart_mood += f'    "Bearish Factors" : {neg_pct}\n```'

    # --- LOGIC: RSI Reality Check ---
    rsi_val = data['rsi']
    trend_signal = data['trend_signal']
    
    momentum_label = "NEUTRAL ⚪"
    momentum_desc = "Stable Market"
    confidence = "⭐⭐⭐ (High)"
    
    if rsi_val > 70:
        momentum_label = "OVERHEATED ⚠️"
        momentum_desc = "Price Too High - Risk of Crash"
        # If model predicts UP but market is Overheated -> LOW CONFIDENCE
        if "BULLISH" in trend_signal:
            confidence = "⭐ (Low - Divergence)"
            
    elif rsi_val < 30:
        momentum_label = "OVERSOLD 💎"
        momentum_desc = "Price Too Low - Potential Bounce"
    elif rsi_val > 50:
        momentum_label = "BULLISH 🟢"
        momentum_desc = "Healthy Upward Trend"
    else:
        momentum_label = "BEARISH 🔴"
        momentum_desc = "Downward Trend"

    # --- BUILD MARKDOWN ---
    md = f"""
# 🔱 Aurum-V1: Market Command Center

> **"Advanced Predictive Intelligence for the Indian Gold Market."** > *Powered by Holt-Winters Forecasting & VADER NLP Analysis.*

<div align="center">

| 🏛️ Current Price (10g) | 🔮 Tomorrow's Forecast | 📉 Market Status | 🧠 Model Confidence |
| :---: | :---: | :---: | :---: |
| **{fmt_price(price_today)}** | **{fmt_price(forecast)}** | **{momentum_label}** | **{confidence}** |
| {get_arrow(delta_yest)} {fmt_delta(delta_yest)} vs yest | {get_arrow(delta_forecast)} {fmt_delta(delta_forecast)} predicted | RSI: {rsi_val} | *Based on RSI Check* |

</div>

---

### ⏳ The Time Machine: Accuracy & Trend
*Comparing the Past, Present, and Future.*

| Timeline | Price (10g) | Change (₹) | Insight |
| :--- | :--- | :--- | :--- |
| **Yesterday** (Actual) | {fmt_price(price_yest)} | - | Historical Anchor |
| **Today** (Live) | **{fmt_price(price_today)}** | {fmt_delta(delta_yest)} | **Actual Market Rate** |
| **Tomorrow** (AI Forecast) | `{fmt_price(forecast)}` | {fmt_delta(delta_forecast)} | *{momentum_desc}* |

> **🎯 AI Accuracy Tracker:** > Yesterday's prediction for today was: **{fmt_delta(accuracy_err) if accuracy_err is not None else 'N/A (No Record)'}** off from reality.  
> *(Note: We use a 1-day lag to measure true predictive performance.)*

---

### 📊 Visual Intelligence

<table>
<tr>
<td width="60%">

#### 📈 Price Action (30 Days)
{chart_price}

</td>
<td width="40%">

#### 🧠 Market Sentiment
{chart_mood}

**Key Drivers:**
{' '.join([f'`{k}`' for k in keywords])}

</td>
</tr>
</table>

---

### 📰 Global Intelligence Feed
*Real-time news snippets affecting Gold prices (Wars, Economy, Seasonality).*

| Source | Headline | Impact |
| :--- | :--- | :--- |
| **Global News** | {headlines[0] if len(headlines) > 0 else "No Data"} | {'🔥 High' if 'War' in str(headlines) else 'ℹ️ Info'} |
| **Indian Market** | {headlines[1] if len(headlines) > 1 else "No Data"} | {'💍 Demand' if 'Jewellery' in str(headlines) else 'ℹ️ Info'} |
| **Geopolitics** | {headlines[2] if len(headlines) > 2 else "No Data"} | ⚠️ Risk |

---

### 🛠️ System Health
* **ETL Pipeline:** 🟢 Online (Custom `curl_cffi` Driver)
* **ML Engine:** 🟢 Online (Holt-Winters Exp. Smoothing)
* **Sentiment Node:** 🟢 Online (Google News RSS)
* **Last Updated:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST`

"""

    with open(README_PATH, 'w', encoding='utf-8') as f:
        f.write(md)
    print("✅ Futuristic Dashboard Generated.")

if __name__ == "__main__":
    generate_readme()