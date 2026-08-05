import os
import requests
from dotenv import load_dotenv

load_dotenv()

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"
PEXELS_SEARCH_URL = "https://api.pexels.com/v1/search"
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")


def fetch_wikipedia_image(topic: str) -> str | None:
    """
    Look up a topic on Wikipedia and return its thumbnail image URL, if any.
    Returns None on any failure (no page found, no image, network error, etc.)
    """
    try:
        response = requests.get(
            WIKI_SUMMARY_URL.format(topic.strip().replace(" ", "_")),
            headers={"User-Agent": "AI-News-Aggregator/1.0 (student project)"},
            timeout=8,
        )
        if response.status_code != 200:
            return None

        data = response.json()

        # Disambiguation pages have no single useful image
        if data.get("type") == "disambiguation":
            return None

        thumbnail = data.get("thumbnail", {})
        return thumbnail.get("source")

    except Exception as e:
        print(f"[Wikipedia Image] Error fetching image for '{topic}': {e}")
        return None


def fetch_pexels_image(topic: str) -> str | None:
    """
    Fallback image source for topics with no Wikipedia page — e.g. general
    concepts, niche interests. Returns a stock photo related to the topic,
    NOT a real photo of a specific named person (Pexels is a stock photo
    library, not a search engine — treat this as a generic-but-relevant
    visual, not an accurate likeness).
    """
    if not PEXELS_API_KEY:
        print("[Pexels Image] No PEXELS_API_KEY set — skipping fallback")
        return None

    try:
        response = requests.get(
            PEXELS_SEARCH_URL,
            headers={"Authorization": PEXELS_API_KEY},
            params={"query": topic, "per_page": 1},
            timeout=8,
        )
        if response.status_code != 200:
            return None

        data = response.json()
        photos = data.get("photos", [])
        if not photos:
            return None

        return photos[0].get("src", {}).get("medium")

    except Exception as e:
        print(f"[Pexels Image] Error fetching image for '{topic}': {e}")
        return None


def fetch_topic_image(topic: str) -> str | None:
    """
    Primary entrypoint — tries Wikipedia first (accurate for named people,
    places, well-known things), falls back to Pexels stock photos for
    anything Wikipedia doesn't have a page for.
    """
    image = fetch_wikipedia_image(topic)
    if image:
        return image

    print(f"[Image Lookup] No Wikipedia image for '{topic}', trying Pexels fallback...")
    return fetch_pexels_image(topic)