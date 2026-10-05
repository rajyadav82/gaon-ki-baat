import json, html, os, re, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

FEEDS = {
"news":["https://news.google.com/rss/search?q=India&hl=hi&gl=IN&ceid=IN:hi","https://news.google.com/rss/search?q=Uttar+Pradesh&hl=hi&gl=IN&ceid=IN:hi"],
"emotional":["https://news.google.com/rss/search?q=इंसानियत+मदद+गरीब&hl=hi&gl=IN&ceid=IN:hi"],
"funny":["https://news.google.com/rss/search?q=मजेदार+वीडियो+वायरल&hl=hi&gl=IN&ceid=IN:hi"],
"farming":["https://news.google.com/rss/search?q=खेती+किसान+कृषि+India&hl=hi&gl=IN&ceid=IN:hi"],
"schemes":["https://news.google.com/rss/search?q=सरकारी+योजना+भारत+site:gov.in&hl=hi&gl=IN&ceid=IN:hi"],
"entertainment":["https://news.google.com/rss/search?q=मनोरंजन+फिल्म+गाना+वायरल&hl=hi&gl=IN&ceid=IN:hi"]
}

def clean(s):
    s=html.unescape(s or "")
    s=re.sub(r"<[^>]*>"," ",s)
    s=re.sub(r"&nbsp;?"," ",s,flags=re.I)
    return re.sub(r"\s+"," ",s).strip()

def get(url):
    try:
        req=urllib.request.Request(url,headers={"User-Agent":"GaonKiBaatBot/1.0"})
        with urllib.request.urlopen(req,timeout=20) as r:return r.read()
    except Exception as e:
        print("Feed error:",e); return b""

def parse(data,cat):
    out=[]
    try:
        root=ET.fromstring(data)
        for item in root.findall(".//item"):
            t=clean(item.findtext("title","")); u=clean(item.findtext("link",""))
            d=clean(item.findtext("description","")); dt=clean(item.findtext("pubDate",""))
            if t and u: out.append({"title":t,"description":d[:280],"url":u,"date":dt,"category":cat})
    except Exception as e: print("XML error:",e)
    return out

def build(cat,urls):
    unique={}
    for url in urls:
        for x in parse(get(url),cat): unique[x["url"]]=x
    return list(unique.values())[:18]

def main():
    os.makedirs("data",exist_ok=True)
    now=datetime.now(timezone.utc).isoformat()
    for cat,urls in FEEDS.items():
        with open(f"data/{cat}.json","w",encoding="utf-8") as f:
            json.dump({"updated":now,"articles":build(cat,urls)},f,ensure_ascii=False,indent=2)
    with open("data/deals.json","w",encoding="utf-8") as f:
        json.dump({"updated":now,"articles":[],"note":"Deals will be connected to an affiliate/product feed later."},f,ensure_ascii=False,indent=2)

if __name__=="__main__": main()
