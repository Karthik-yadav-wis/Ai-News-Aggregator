import requests

API_KEY = "pub_640312d4855f4727bd0ac5cc2178b636"

url = "https://newsdata.io/api/1/latest"

params = {
    "apikey": API_KEY,
    "q": "osmania",
    "language": "en"
}

response = requests.get(url, params=params)

print("Status:", response.status_code)

data = response.json()

results = data.get("results", [])

print("Total Articles:", len(results))

for article in results[:5]:

    print("\nTitle:", article.get("title"))

    print("Source:", article.get("source_name"))

    print("Published:", article.get("pubDate"))

    print("\nDescription:")

    description = article.get("description", "")

    print(description)

    print("\nURL:", article.get("link"))

    print("\n" + "=" * 60)