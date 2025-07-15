import os
import time
import re
from datetime import datetime
from dotenv import load_dotenv
import feedparser
from pyairtable import Api
import schedule
import html

load_dotenv()

# Configuration des flux RSS à surveiller
RSS_FEEDS = [
    {
        "name": "Google News IA",
        "url": "https://news.google.com/rss/search?q=intelligence+artificielle&hl=fr&gl=FR&ceid=FR:fr"
    },
    {
        "name": "ActuIA",
        "url": "https://www.actuia.com/feed"
    },
    {
        "name": "Euronews IA",
        "url": "https://fr.euronews.com/rss?level=tag&name=intelligence-artificielle"
    }
]

TOPIC = "intelligence artificielle"

# Variables d'environnement Airtable
AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

print(f"Configuration chargée:")
print(f"   - API Key: {'OK' if AIRTABLE_API_KEY else 'MANQUANT'}")
print(f"   - Base ID: {'OK' if BASE_ID else 'MANQUANT'}")
print(f"   - Table: {TABLE_NAME}")

# Initialisation de la connexion Airtable
api = Api(AIRTABLE_API_KEY)
table = api.table(BASE_ID, TABLE_NAME)

def already_exists(url):
    """Vérifie si un article existe déjà dans Airtable via son URL"""
    try:
        formula = f"{{URL}}='{url}'"
        records = table.all(formula=formula)
        return len(records) > 0
    except Exception as e:
        print(f"ERREUR lors de la vérification d'existence : {e}")
        return False

def clean_html_text(text):
    """Nettoie le texte HTML en supprimant les balises et en décodant les entités"""
    if not text:
        return ""
    
    # Décodage des entités HTML (&amp;, &lt;, etc.)
    cleaned = html.unescape(text)
    # Suppression des balises HTML
    cleaned = re.sub(r'<[^>]+>', '', cleaned)
    # Normalisation des espaces multiples
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    return cleaned





def fetch_and_store():
    """Fonction principale : collecte les articles RSS et les stocke dans Airtable"""
    print(f"\n[{datetime.now()}] Début de la collecte - {len(RSS_FEEDS)} flux")
    
    new_articles = 0
    total_articles_processed = 0
    total_articles_duplicates = 0

    for i, feed in enumerate(RSS_FEEDS, 1):
        feed_name = feed["name"]
        feed_url = feed["url"]
        print(f"\n[{i}/{len(RSS_FEEDS)}] {feed_name}")
        
        try:
            # Parsing du flux RSS
            feed_data = feedparser.parse(feed_url)
            print(f"   Articles trouvés: {len(feed_data.entries)}")
            
            feed_articles_processed = 0
            feed_articles_duplicates = 0
            feed_articles_added = 0

            for j, entry in enumerate(feed_data.entries, 1):
                # Extraction et nettoyage des données de l'article
                title = clean_html_text(entry.title)
                link = entry.link
                summary = clean_html_text(getattr(entry, 'summary', ''))
                published_raw = getattr(entry, 'published', '')
                
                # Parsing de la date de publication (format RSS standard)
                try:
                    published_dt = datetime.strptime(published_raw, '%a, %d %b %Y %H:%M:%S %z')
                    published_real = published_dt.strftime('%Y-%m-%d')
                except:
                    published_real = published_raw
                
                collected_at = datetime.now().strftime('%Y-%m-%d')

                feed_articles_processed += 1
                total_articles_processed += 1

                # Vérification des doublons avant ajout
                if already_exists(link):
                    feed_articles_duplicates += 1
                    total_articles_duplicates += 1
                    continue

                # Préparation des données pour Airtable
                record_data = {
                    "URL": link,
                    "Title": title,
                    "Summary": summary,
                    "Source": feed_name,
                    "Published": published_real,
                    "Collected": collected_at
                }

                # Ajout dans Airtable
                try:
                    table.create(record_data)
                    new_articles += 1
                    feed_articles_added += 1
                    print(f"      AJOUTE [{j}] {title[:50]}...")
                except Exception as e:
                    print(f"      ERREUR [{j}] {title[:50]}... - {e}")

            print(f"   Traités: {feed_articles_processed} | Doublons: {feed_articles_duplicates} | Ajoutés: {feed_articles_added}")

        except Exception as e:
            print(f"   ERREUR lors du traitement du flux {feed_name}: {e}")

    print(f"\n[{datetime.now()}] Collecte terminée - {new_articles} nouveaux articles ajoutés\n")

def scheduled_fetch_and_store():
    """Wrapper pour la collecte planifiée avec gestion d'erreurs"""
    try:
        print(f"\n⏰ [{datetime.now()}] Exécution de la collecte planifiée")
        fetch_and_store()
        print(f"✅ [{datetime.now()}] Collecte planifiée terminée avec succès")
    except Exception as e:
        print(f"❌ [{datetime.now()}] Erreur lors de la collecte planifiée: {e}")
        print("🔄 La prochaine collecte aura lieu demain à 09:00")

# Configuration de la planification quotidienne
schedule.every().day.at("09:00").do(scheduled_fetch_and_store)

print(f"Agent de veille IA - Collecte quotidienne à 09:00")
print(f"Démarrage...\n")

# Première collecte immédiate
fetch_and_store()

print(f"Agent en veille - prochaine collecte demain à 09:00\n")

# Boucle principale de planification avec gestion d'erreurs
while True:
    try:
        schedule.run_pending()
        time.sleep(60)
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'agent demandé par l'utilisateur")
        break
    except Exception as e:
        print(f"\n❌ Erreur dans la boucle de planification: {e}")
        print("🔄 Redémarrage de la boucle dans 60 secondes...")
        time.sleep(60)
