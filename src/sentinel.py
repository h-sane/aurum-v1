from curl_cffi import requests
from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
import os
from datetime import datetime

# CONFIG: We switch from the 'Web URL' to the 'RSS Feed URL'
# This is the dedicated feed for "Gold Price India"
RSS_FEED_URL = "https://news.google.com/rss/search?q=gold+price+india&hl=en-IN&gl=IN&ceid=IN:en"
MOOD_FILE = "data/market_mood.json"

class Sentinel:
    def __init__(self):
        print("--- 📡 Sentinel: Initializing Neural Net ---")
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
            
        self.sia = SentimentIntensityAnalyzer()

    def fetch_news(self):
        print(f"   🕵️  Fetching News via RSS Feed (Stable)...")
        
        try:
            # We still use curl_cffi to be polite, but pointing to the RSS endpoint
            response = requests.get(
                RSS_FEED_URL, 
                impersonate="chrome110", 
                timeout=20
            )
        except Exception as e:
            print(f"   ❌ Connection Failed: {e}")
            return []

        # Parse XML instead of HTML
        soup = BeautifulSoup(response.content, "xml")
        
        # In RSS, every news story is inside an <item> tag
        items = soup.find_all("item")
        
        headlines = []
        for item in items[:8]: # Analyze top 8 stories
            title = item.title.text
            # Filter out non-relevant titles if necessary
            if len(title) > 10: 
                headlines.append(title)

        print(f"   ✅ Found {len(headlines)} headlines.")
        return headlines

    def analyze_market_mood(self):
        headlines = self.fetch_news()
        
        if not headlines:
            print("   ⚠️ No headlines found. (RSS might be down)")
            # Save neutral state so Dashboard doesn't crash
            self.save_mood(0, "NEUTRAL", [])
            return

        compound_score = 0
        analyzed_news = []
        
        print("   🧠 Analyzing Sentiment...")
        for h in headlines:
            # FILTER: Ignore meta-news to avoid circular logic
            if any(w in h.lower() for w in ["prediction", "forecast", "outlook", "opinion"]):
                continue 

            score = self.sia.polarity_scores(h)['compound']
            compound_score += score
            
            # Google RSS often puts the source name at the end of the title
            # e.g., "Gold Price Jumps - Times of India"
            source = "Google News"
            if "-" in h:
                source = h.split("-")[-1].strip()

            analyzed_news.append({
                "title": h,
                "source": source,
                "score": score
            })

        # Average the score
        if analyzed_news:
            avg_score = compound_score / len(analyzed_news)
        else:
            avg_score = 0

        # Determine Label
        if avg_score > 0.05:
            status = "RISK-ON (High Demand) 🟢"
        elif avg_score < -0.05:
            status = "FEAR (Low Demand) 🔴"
        else:
            status = "NEUTRAL ⚪"

        print(f"   📊 Final Score: {avg_score:.2f} ({status})")
        self.save_mood(avg_score, status, analyzed_news)

    def save_mood(self, score, status, headlines):
        data = {
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sentiment_score": round(score, 2),
            "market_status": status,
            "headlines": headlines
        }
        
        os.makedirs(os.path.dirname(MOOD_FILE), exist_ok=True)
        
        with open(MOOD_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("   💾 Market Mood Saved.")

if __name__ == "__main__":
    s = Sentinel()
    s.analyze_market_mood()