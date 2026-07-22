import requests
API_KEY='BadgKksuf6hRE3f2qTcDg71usyqypgxc2kGcOo90hf0nfgYg'


BASE_URL = "https://api.currentsapi.services/v1/search"

headers = {
    "Authorization": API_KEY
}

params = {
    "keywords": "hyderabad",
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