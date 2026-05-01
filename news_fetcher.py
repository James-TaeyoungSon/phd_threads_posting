import feedparser

def fetch_latest_news(limit=10, query="AI"):
    """
    Fetches the latest news matching a query from Google News Korea RSS feed.
    """
    import urllib.parse
    if query:
        encoded_query = urllib.parse.quote(query)
        url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ko&gl=KR&ceid=KR:ko"
    else:
        url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    
    news_items = []
    
    # Iterate over entries and pick the top `limit` items
    for entry in feed.entries[:limit]:
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.published if hasattr(entry, 'published') else 'Unknown'
        })
        
    return news_items

if __name__ == "__main__":
    # Test the news fetcher
    news = fetch_latest_news(3)
    for n in news:
        print(f"Title: {n['title']}\nLink: {n['link']}\n")
