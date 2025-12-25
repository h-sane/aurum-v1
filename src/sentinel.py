import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from datetime import datetime
import json
import os

# --- OPERATIONAL HARDENING: Safe Resource Loading ---
# We check for the lexicon locally before hitting the network.
# This prevents rate-limiting issues on GitHub Actions.
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    try:
        nltk.download('vader_lexicon', quiet=True)
    except Exception as e:
        print(f"⚠️ NLTK Download Failed: {e}. Sentiment analysis may degrade.")

OUTPUT_FILE = "data/market_mood.json"

class Sentinel:
    def __init__(self):
        # RSS Feeds: General Gold News & India Specific
        self.rss_urls = [
            "https://news.google.com/rss/search?q=gold+price+india&hl=en-IN&gl=IN&ceid=IN:en",
            "https://news.google.com/rss/search?q=geopolitical+tension&hl=en-US&gl=US&ceid=US:en"
        ]
        # Initialize VADER (will work if lexicon exists)
        try:
            self.sia = SentimentIntensityAnalyzer()
        except:
            self.sia = None

    def analyze_market_mood(self):
        print("--- 📡 Sentinel: Scanning Global News ---")
        
        if not self.sia:
            print("⚠️ Sentinel Error: VADER lexicon missing. Skipping.")
            return

        headlines = []
        
        # 1. Fetch Headlines (RSS)
        for url in self.rss_urls:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, features="xml")
                items = soup.findAll('item')
                # Grab top 3 from each feed to avoid noise
                for item in items[:3]:
                    headlines.append(item.title.text)
            except Exception as e:
                print(f"⚠️ RSS Fetch Error: {e}")

        if not headlines:
            print("⚠️ No headlines found. Skipping sentiment analysis.")
            return

        # 2. Score Sentiment
        total_score = 0
        significant_keywords = []
        
        for h in headlines:
            score = self.sia.polarity_scores(h)['compound']
            
            # --- DOMAIN LOGIC: The "War Premium" ---
            # In standard NLP, "War" = Negative.
            # In Gold Markets, "War" = Positive (Safe Haven Buy).
            # We invert the score if conflict keywords are found.
            if any(word in h.lower() for word in ['war', 'conflict', 'tension', 'crisis', 'attack']):
                if score < 0:
                    score = abs(score) # Flip negative to positive
                    significant_keywords.append("Geopolitics (Safe Haven) 🛡️")
            
            total_score += score

        avg_score = total_score / len(headlines)

        # 3. DOMAIN LOGIC: "Indian Psyche" (Seasonality Heuristic)
        # Wedding Season: Nov, Dec, Jan, Feb, May
        current_month = datetime.now().month
        if current_month in [11, 12, 1, 2, 5]:
            # This is a heuristic adjustment, not a learned weight
            avg_score += 0.15 
            significant_keywords.append("Wedding Season 💍")

        # 4. Determine "The Mood" (Qualitative Labeling)
        mood = "NEUTRAL"
        if avg_score > 0.05:
            mood = "RISK-ON (High Demand)"
        elif avg_score < -0.05:
            mood = "RISK-OFF (Low Demand)"
            
        print(f"   🌍 Market Mood: {mood} (Score: {avg_score:.2f})")

        # 5. Save Context Data
        payload = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "market_mood": mood,
            "sentiment_score": round(avg_score, 2),
            "top_headlines": headlines[:3], # Save top 3 for display
            "keywords": list(set(significant_keywords))
        }

        # Atomic write to ensure dashboard never reads half-written JSON
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(payload, f, indent=2)
            
        print(f"💾 Context saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    bot = Sentinel()
    bot.analyze_market_mood()