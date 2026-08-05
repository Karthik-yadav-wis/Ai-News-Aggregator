from apscheduler.schedulers.background import BackgroundScheduler
from database import SessionLocal
from models import Interest
from services.news_fetcher import fetch_news
from services.rag_pipeline import process_and_store_articles

# How often to refresh every saved interest, in hours.
# Adjust to taste — shorter = fresher news, more external API calls.
REFRESH_INTERVAL_HOURS = 2


def refresh_all_interests():
    """
    Re-fetches news for every distinct interest saved by any user.
    Runs once per REFRESH_INTERVAL_HOURS, independent of anyone being
    logged in. Relies on the dedup check in process_and_store_articles
    so repeated runs don't keep re-embedding the same articles.
    """
    db = SessionLocal()
    try:
        interests = db.query(Interest).all()
        print(f"[Scheduler] Refreshing {len(interests)} saved interest(s)...")

        total_new_chunks = 0
        for interest in interests:
            try:
                articles = fetch_news(interest.name)
                new_chunks = process_and_store_articles(articles, db,interest.name)
                total_new_chunks += new_chunks
                print(f"[Scheduler] '{interest.name}': {new_chunks} new chunks stored")
            except Exception as e:
                # One interest failing shouldn't stop the rest from refreshing
                print(f"[Scheduler] Error refreshing '{interest.name}': {e}")

        print(f"[Scheduler] Refresh complete — {total_new_chunks} new chunks total")
    finally:
        db.close()


scheduler = BackgroundScheduler()
scheduler.add_job(
    refresh_all_interests,
    trigger="interval",
    hours=REFRESH_INTERVAL_HOURS,
    id="refresh_all_interests",
    replace_existing=True,
)
