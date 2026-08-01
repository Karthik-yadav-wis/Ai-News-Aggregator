import requests

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{}"


def fetch_wikipedia_image(topic: str) -> str | None:
    """
    Look up a topic on Wikipedia and return its thumbnail image URL, if any.
    Returns None on any failure (no page found, no image, network error, etc.)
    so callers can fall back to a placeholder without special-casing errors.
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

        # Wikipedia disambiguation pages have no useful single image
        if data.get("type") == "disambiguation":
            return None

        thumbnail = data.get("thumbnail", {})
        return thumbnail.get("source")

    except Exception as e:
        print(f"[Wikipedia Image] Error fetching image for '{topic}': {e}")
        return None