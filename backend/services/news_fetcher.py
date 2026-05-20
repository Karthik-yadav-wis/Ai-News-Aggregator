import requests
import os

from dotenv import load_dotenv

load_dotenv()

CURRENT_NEWS_API_KEY = os.getenv(
    "CURRENT_NEWS_API_KEY"
)

BASE_URL = "https://api.currentsapi.services/v1/search"

def fetch_news(keyword: str):

    headers = {
        "Authorization": CURRENT_NEWS_API_KEY
    }

    params = {
        "keywords": keyword,
        "language": "en"
    }

    response = requests.get(
        BASE_URL,
        headers=headers,
        params=params
    )

    data = response.json()
    return data.get("news", [])