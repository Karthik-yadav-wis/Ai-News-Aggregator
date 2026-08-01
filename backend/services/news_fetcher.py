import requests
import os
from dotenv import load_dotenv
 
load_dotenv()
 
CURRENTS_API_KEY   = os.getenv("CURRENT_NEWS_API_KEY")
FREENEWS_API_KEY   = os.getenv("FREE_NEWS_API_KEY")
NEWSDATA_API_KEY   = os.getenv("NEWS_DATA_API_KEY")
 
#currentNews
def _fetch_currents(keyword):
    try:
        response = requests.get(
            "https://api.currentsapi.services/v1/search",
            headers={"Authorization": CURRENTS_API_KEY},
            params={"keywords": keyword, "language": "en"},
            timeout=10
        )
        response.raise_for_status()
        articles = response.json().get("news", [])
 
        return [
            {
                "title":        a.get("title", ""),
                "description":  a.get("description", ""),
                "url":          a.get("url", ""),
                "source":       a.get("author", "Currents"),
                "published_at": a.get("published", ""),
            }
            for a in articles
        ]
 
    except Exception as e:
        print("[Currents API] Error: ", e)
        return []
 
#freeNews
def _fetch_freenews(keyword: str, country: str = "IN") -> list[dict]:
    headers = {
        "x-api-key": FREENEWS_API_KEY,
        "Accept":    "application/json",
    }
    normalized = []
 
    try:
        response = requests.get(
            "https://api.freenewsapi.io/v1/news",
            headers=headers,
            params={
                "in_title":        keyword,
                "language": "en",
                "order_by": "recent",
                "offset":   0,
            },
            timeout=10
        )
        response.raise_for_status()
        articles = response.json().get("data", [])
 
    except Exception as e:
        print("[FreeNews API] List error: ", e)
        return []
 
    for article in articles:
        uuid = article.get("uuid")
        body = ""
 
        # Fetch full article body
        if uuid:
            try:
                details_resp = requests.get(
                    "https://api.freenewsapi.io/v1/details",
                    headers=headers,
                    params={"uuid": uuid},
                    timeout=10
                )
                details_resp.raise_for_status()
                full = details_resp.json().get("data", {})
                body = full.get("body", "")
            except Exception as e:
                print("[FreeNews API] Details error for ", uuid, ": ", e)
 
        normalized.append({
            "title":        article.get("title", ""),
            # Use body if available, fall back to snippet/description
            "description":  body or article.get("description", ""),
            "url":          article.get("url", ""),
            "source":       article.get("publisher", "FreeNews"),
            "published_at": article.get("published_at", ""),
        })
 
    return normalized
 
 
#NewsData
def _fetch_newsdata(keyword: str) -> list[dict]:
    try:
        response = requests.get(
            "https://newsdata.io/api/1/latest",
            params={
                "apikey":   NEWSDATA_API_KEY,
                "q":        keyword,
                "language": "en",
            },
            timeout=10
        )
        response.raise_for_status()
        results = response.json().get("results", [])
 
        return [
            {
                "title":        a.get("title", ""),
                "description":  a.get("description", ""),
                "url":          a.get("link", ""),
                "source":       a.get("source_name", "NewsData"),
                "published_at": a.get("pubDate", ""),
            }
            for a in results
        ]
 
    except Exception as e:
        print("[NewsData API] Error: ", e)
        return []

def fetch_news(keyword):
    print("[fetch_news] Fetching '", keyword, "' from all sources...")
 
    all_articles = (
        _fetch_currents(keyword)
        + _fetch_freenews(keyword)
        + _fetch_newsdata(keyword)
    )
 
    # Deduplicate by URL
    seen_urls = set()
    unique = []
    for article in all_articles:
        url = article.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique.append(article)
 
    print("[fetch_news] ", len(unique), " unique articles collected "
          f"({len(all_articles) - len(unique)} duplicates removed)")
 
    return unique
 