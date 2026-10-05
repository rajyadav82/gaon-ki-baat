import json, html, os, re, urllib.request, urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

QUERIES = {
    "emotional": ["इंसानियत मदद गरीब", "मदद जरूरतमंद परिवार"],
    "funny": ["मजेदार वीडियो वायरल", "funny viral India"],
    "farming": ["खेती किसान कृषि India", "किसान खेती मंडी"],
    "schemes": ["सरकारी योजना भारत", "government scheme India"],
    "entertainment": ["मनोरंजन फिल्म गाना वायरल", "Bollywood entertainment India"]
}

def clean(s):
    s = html.unescape(s or "")
    s = re.sub(r"<[^>]*>", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def feed_url(query):
    q = urllib.parse.quote_plus(query)
    return f"https://news.google.com/rss/search?q={q}&hl=hi&gl=IN&ceid=IN:hi"

def get(url):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (compatible; GaonKiBaat/1.0)"
            }
        )
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.read()
    except Exception as e:
        print("Feed error:", url, e)
        return b""

def parse(data, category):
    out = []
    if not data:
        return out
    try:
        root = ET.fromstring(data)
        for item in root.findall(".//item"):
            title = clean(item.findtext("title", ""))
            link = clean(item.findtext("link", ""))
            desc = clean(item.findtext("description", ""))
            date = clean(item.findtext("pubDate", ""))
            if title and link:
                out.append({
                    "title": title,
                    "description": desc[:300],
                    "url": link,
                    "date": date,
                    "category": category
                })
    except Exception as e:
        print("XML error:", e)
    return out

def build(category, queries):
    unique = {}
    for query in queries:
        for item in parse(get(feed_url(query)), category):
            unique[item["url"]] = item
    return list(unique.values())[:18]

def main():
    os.makedirs("data", exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()

    for category, queries in QUERIES.items():
        articles = build(category, queries)
        print(category, "articles:", len(articles))
        with open(f"data/{category}.json", "w", encoding="utf-8") as f:
            json.dump(
                {"updated": now, "articles": articles},
                f, ensure_ascii=False, indent=2
            )

    # Deals are kept separate until a real product/affiliate feed is connected.
    with open("data/deals.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "updated": now,
                "articles": [],
                "note": "Deals will be connected to an affiliate/product feed later."
            },
            f, ensure_ascii=False, indent=2
        )

if __name__ == "__main__":
    main()
