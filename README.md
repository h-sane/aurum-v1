
# 🏆 Aurum-V1: Autonomous Gold Intelligence

> **"A robust, self-correcting ETL pipeline that tracks, predicts, and analyzes the Indian Gold Market using Machine Learning and NLP."**

### ⚡ Live Market Intelligence
| Metric | Status | Value | Description |
| :--- | :--- | :--- | :--- |
| **Price (10g)** | 🟢 | **₹127,650** | Standard Jewellery Unit (22K) |
| **Price (1g)** | 🔹 | **₹12,765** | Per Gram Unit |
| **Forecast** | 🔮 | **₹128,191** | Predicted price for tomorrow |
| **Momentum** | 📉 | **RSI 86.73** | 0-30=Cheap, 70-100=Expensive |
| **Mood** | 🌍 | **RISK-ON (High Demand)** | Analysis of Global News Feeds |

---

### 📈 Price Action (Last 30 Days)
```mermaid
xychart-beta
    title "Gold Price Trend (30 Days - 10g 22K)"
    x-axis [ 11-13, 11-14, 11-17, 11-18, 11-19, 11-20, 11-21, 11-24, 11-25, 11-26, 11-28, 12-01, 12-02, 12-03, 12-04, 12-05, 12-08, 12-09, 12-10, 12-11, 12-12, 12-15, 12-16, 12-17, 12-18, 12-19, 12-22, 12-23, 12-24, 12-25 ]
    y-axis "Price (INR)" 115067 --> 128212
    line [119282, 116453, 115903, 115704, 116171, 115567, 116143, 116576, 117923, 118664, 120177, 120775, 119274, 119635, 119992, 120023, 119291, 119846, 119553, 122091, 122507, 122695, 122632, 123858, 123630, 124254, 126624, 127712, 127650, 127650]
```

---

### 🧠 The Oracle's Report
* **Technical Analysis:** The market is currently **BULLISH (Up Trend) 🟢**. The RSI is **86.73**.
    * *What this means:* The price is rising aggressively. Be cautious of a sudden drop.
* **Fundamental Analysis:** Our Sentinel Bot scanned global news and detected a **RISK-ON (High Demand)** environment (Score: 0.43).
    * *Top Headline:* "Gold Price Surges Rs 2,650 To Record Rs 1.4 Lakh Per 10 Gram - NDTV"

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
*Last Updated: 2025-12-25 15:00:57 IST | Automated by GitHub Actions*
