import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY=os.getenv("CURRENT_NEWS_API_KEY")

print("API Key:", API_KEY)
print(os.getcwd())


BASE_URL = "https://api.currentsapi.services/v1/search"

headers = {
    "Authorization": API_KEY
}

params = {
    "keywords": "India",
    "language": "en"
}

response = requests.get(
    BASE_URL,
    headers=headers,
    params=params
)

print("Status:", response.status_code)

data = response.json()

news = data.get("news", [])

print("Total Articles:", len(news))

for article in news:

    print("\nTitle:", article.get("title"))

    print("Author:", article.get("author"))

    print("Published:", article.get("published"))

    print("\nFirst 5 lines:\n")

    description = article.get("description", "")

    lines = description.split(". ")

    for line in lines[:5]:
        print(line.strip())

    print("\nArticle URL:", article.get("url"))

    print("\n" + "=" * 60)