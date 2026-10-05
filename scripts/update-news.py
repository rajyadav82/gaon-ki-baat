import json
import os
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

RSS_FEEDS = [
    "https://news.google.com/rss/search?q=India&hl=hi&gl=IN&ceid=IN:hi",
    "https://news.google.com/rss/search?q=Uttar+Pradesh&hl=hi&gl=IN&ceid=IN:hi",
]

OUTPUT_FILE = "data/news.json"

def clean_text(text):
    if not text:
        return ""

    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def get_feed(url):
    try:
        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read()

    except Exception as e:
        print("Feed error:", e)
        return None


def parse_feed(data):
    articles = []

    if not data:
        return articles

    try:
        root = ET.fromstring(data)

        for item in root.findall(".//item"):

            title = item.findtext("title", "")
            link = item.findtext("link", "")
            description = item.findtext("description", "")
            pub_date = item.findtext("pubDate", "")

            title = clean_text(title)
            description = clean_text(description)

            if not title or not link:
                continue

            articles.append({
                "title": title,
                "description": description[:300],
                "url": link,
                "date": pub_date
            })

    except Exception as e:
        print("XML error:", e)

    return articles


def main():

    all_articles = []

    for feed in RSS_FEEDS:
        data = get_feed(feed)

        articles = parse_feed(data)

        all_articles.extend(articles)

    # Remove duplicate URLs
    unique = {}

    for article in all_articles:
        unique[article["url"]] = article

    articles = list(unique.values())

    # Keep latest 20
    articles = articles[:20]

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "articles": articles
    }

    os.makedirs("data", exist_ok=True)

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("Updated articles:", len(articles))


if __name__ == "__main__":
    main()
