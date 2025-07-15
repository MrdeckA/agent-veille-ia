import os
import time
from datetime import datetime
from dotenv import load_dotenv
import feedparser
from pyairtable import Table
import schedule

load_dotenv()

# Configuration
RSS_FEEDS = [
    "https://news.google.com/rss/search?q=intelligence+artificielle&hl=fr&gl=FR&ceid=FR:fr",
    "https://blogs.microsoft.com/ai/feed/",
    "https://medium.com/feed/tag/artificial-intelligence",
    "https://techcrunch.com/category/artificial-intelligence/feed/"
]

TOPIC = "intelligence artificielle"
KEYWORDS = [
    "ai",
    "artificial intelligence",
    "intelligence artificielle",
    "deep learning",
    "machine learning"
]

AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)

def already_exists(url):
    """Vérifie si l'URL existe déjà dans Airtable via filterByFormula"""
    formula = f"{{URL}}='{url}'"
    records = table.all(formula=formula)
    return len(records) > 0

def article_matches_keywords(title, summary):
    text = f"{title} {summary}".lower()
    return any(keyword in text for keyword in KEYWORDS)

def fetch_and_store():
    print(f"[{datetime.now()}] Début de la collecte…")
    new_articles = 0

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.title
            link = entry.link
            summary = getattr(entry, 'summary', '')
            published_real = getattr(entry, 'published', '')
            collected_at = datetime.now().isoformat()

            if not article_matches_keywords(title, summary):
                continue

            if already_exists(link):
                continue

            table.create({
                "Collected At": collected_at,
                "Published At": published_real,
                "Source": feed_url,
                "Title": title,
                "URL": link,
                "Summary": summary
            })
            new_articles += 1
            print(f"✅ Ajouté : {title}")

    print(f"[{datetime.now()}] Collecte terminée. {new_articles} nouveaux articles ajoutés.\n")

schedule.every(1).hours.do(fetch_and_store)

print(f"Agent de veille sur le topic : {TOPIC}")
fetch_and_store()

while True:
    schedule.run_pending()
    time.sleep(60)
