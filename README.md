
# 🏆 Aurum-V1: Autonomous Gold Intelligence

> **"A robust, self-correcting ETL pipeline that tracks, predicts, and analyzes the Indian Gold Market (22K) using Holt-Winters Exponential Smoothing and VADER Sentiment Analysis."**

### ⚡ Live Market Intelligence
| Metric | Status | Value |
| :--- | :--- | :--- |
| **Current Price (10g)** | 🟢 | **₹127,650** |
| **Tomorrow's Forecast** | 🔮 | **₹128,191** |
| **Market Trend** | 📊 | **BULLISH (Up Trend) 🟢** |
| **RSI Strength** | 📉 | **86.73** (0-100) |
| **News Sentiment** | 🌍 | **RISK-ON (High Demand)** (0.43) |

---

### 📈 Price Action (Last 30 Days)
```mermaid
xychart-beta
    title "Gold Price Trend (30 Days)"
    x-axis [ 13, 14, 17, 18, 19, 20, 21, 24, 25, 26, 28, 01, 02, 03, 04, 05, 08, 09, 10, 11, 12, 15, 16, 17, 18, 19, 22, 23, 24, 25 ]
    y-axis "Price (INR)" 115067 --> 128212
    line [119282, 116453, 115903, 115704, 116171, 115567, 116143, 116576, 117923, 118664, 120177, 120775, 119274, 119635, 119992, 120023, 119291, 119846, 119553, 122091, 122507, 122695, 122632, 123858, 123630, 124254, 126624, 127712, 127650, 127650]
```

### 🧠 The Oracle's Analysis
* **Technical View:** The market is currently **BULLISH (Up Trend) 🟢**. The Relative Strength Index (RSI) is **86.73**, suggesting the asset is Overbought (Risk of Pullback).
* **Fundamental View:** Sentinel analysis of global news feeds indicates a **RISK-ON (High Demand)** environment.
    * *Top Headline:* "Gold Price Surges Rs 2,650 To Record Rs 1.4 Lakh Per 10 Gram - NDTV"

---

### 🏗️ Architecture
* **Ingestion:** Custom `curl_cffi` driver to bypass WAFs on Indian financial sites.
* **Persistence:** Atomic CSV ledger with idempotent checks to prevent data corruption.
* **Prediction:** Holt-Winters Exponential Smoothing (Additive Trend) trained on a 64-day sliding window.
* **Context:** NLP Sentiment Analysis (VADER) on Google News RSS feeds to detect Geopolitical Risk ("War Premium").

---
*Last Updated: 2025-12-25 14:42:20 IST | Automated by GitHub Actions*
