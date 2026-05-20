import requests

API_KEY = "86fcb4b4ef90ee7f14ffa1599fe5c07341b1f8eb9b5288f95489dfda19806ed2"



url = "https://api.freenewsapi.io/v1/news"

headers = {
    "x-api-key": API_KEY,
    "Accept": "application/json"
}

# STEP 1: Get news list
news_url = "https://api.freenewsapi.io/v1/news"

params = {
    "q": "osmania",
    "language": "en",
    "country": "IN",
    "order_by": "recent",
    "offset": 0
}

response = requests.get(news_url, headers=headers, params=params)

data = response.json()

articles = data.get("data", [])

print("\n=== ARTICLES ===\n")

# STEP 2: Fetch details for each article
for article in articles:

    print("Title:", article.get("title"))
    print("Publisher:", article.get("publisher"))
    print("Published:", article.get("published_at"))

    article_uuid = article.get("uuid")

    # Details endpoint
    details_url = "https://api.freenewsapi.io/v1/details"

    details_response = requests.get(
        details_url,
        headers=headers,
        params={"uuid": article_uuid}
    )

    details_data = details_response.json()

    full_article = details_data.get("data", {})

    body = full_article.get("body", "")

    print("\nFirst 5 lines of content:\n")

    # Split into lines/sentences
    lines = body.split(". ")

    for line in lines[:5]:
        print(line.strip())

    print("\n" + "-" * 60 + "\n")