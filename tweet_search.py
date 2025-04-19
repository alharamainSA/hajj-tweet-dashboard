import tweepy
import sqlite3
import time
from transformers import pipeline

# ✅ Twitter API Token
BEARER_TOKEN = "AAAAAAAAAAAAAAAAAAAAAGcW0AEAAAAArxSDoOSNFlquw49lfq5UExYio1E=6sXKQgyypUsVgr4y5Yb8lVzJ08yOFrXILKXiPJ0tjUvLSEcFaH"

# ✅ Twitter client setup
client = tweepy.Client(bearer_token=BEARER_TOKEN, wait_on_rate_limit=True)

# ✅ Keywords (Arabic + English)
keywords = [
    "الحج", "حج", "مكة", "المدينة", "هيئة العناية بالحرمين",
    "Hajj", "Mecca", "pilgrims", "Islam", "Muslim", "Arafat"
]
query = " OR ".join(keywords) + " -is:retweet"
print("🔍 Search query:", query)

# ✅ Load sentiment pipeline for Arabic
classifier = pipeline("sentiment-analysis", model="CAMeL-Lab/bert-base-arabic-camelbert-da-sentiment")

# ✅ SQLite database setup
conn = sqlite3.connect("hajj_tweets.db")
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS tweets (
    id TEXT PRIMARY KEY,
    text TEXT,
    lang TEXT,
    sentiment TEXT,
    created_at TEXT
)
''')
conn.commit()
print("📦 Database ready.")

# ✅ Main tweet fetch loop
while True:
    try:
        tweets = client.search_recent_tweets(
            query=query,
            tweet_fields=["lang", "created_at"],
            max_results=50
        )

        if not tweets.data:
            print("🕓 No tweets found...")
            time.sleep(30)
            continue

        print(f"✅ {len(tweets.data)} tweets fetched.")

        for tweet in tweets.data:
            tweet_id = tweet.id
            text = tweet.text.strip()
            lang = tweet.lang
            created_at = tweet.created_at

            print(f"📥 [{lang}] {text[:60]}...")

            # Only support Arabic and English
            if lang not in ["ar", "en"]:
                print("⏭️ Skipping unsupported language")
                continue

            try:
                result = classifier(text)
                sentiment = result[0]['label']
            except Exception as e:
                print(f"⚠️ Sentiment error: {e}")
                continue

            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO tweets (id, text, lang, sentiment, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (str(tweet_id), text, lang, sentiment, str(created_at)))
                conn.commit()
                print(f"💾 Saved → {sentiment}")
            except Exception as e:
                print(f"❌ DB save error: {e}")

        time.sleep(30)

    except Exception as e:
        print(f"💥 API Error: {e}")
        time.sleep(60)
