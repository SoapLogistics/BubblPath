import feedparser
import requests

from solomon_ingest.core.connector import SourceConnector


class OfficialRSSConnector(SourceConnector):
    source_id = "official_rss"
    
    # In a real environment, this would be loaded from domain_allowlist.yaml
    allowed_feeds = [
        "http://feeds.bbci.co.uk/news/world/rss.xml",
        "https://www.nasa.gov/news-release/feed/",
        "http://export.arxiv.org/rss/cs.AI",
        "http://export.arxiv.org/rss/cs.AR"
    ]

    def healthcheck(self) -> dict:
        try:
            # Just check if we can parse one feed
            res = requests.get(self.allowed_feeds[0], timeout=5)
            feed = feedparser.parse(res.content)
            if feed.bozo == 0 or len(feed.entries) > 0:
                return {"status": "ok", "source": self.source_id, "entries": len(feed.entries)}
            return {"status": "degraded", "source": self.source_id, "error": "Feed parsed but bozo flag set or empty"}
        except Exception as e: # noqa: BLE001
            return {"status": "error", "source": self.source_id, "error": str(e)}

    def discover(self, cursor: str | None = None) -> list[dict]:
        all_items = []
        for feed_url in self.allowed_feeds:
            try:
                res = requests.get(feed_url, timeout=10)
                feed = feedparser.parse(res.content)
                # Take top 5 entries from each feed for discovery
                entries = feed.entries[:5]
                all_items.extend(self.normalize(entries))
            except Exception as e: # noqa: BLE001
                print(f"[RSS] Failed to fetch {feed_url}: {e}")
        return all_items

    def fetch(self, native_id: str) -> dict:
        # RSS is typically a bulk stream, we extract items during discover
        return {}

    def normalize(self, raw_list: list) -> list[dict]:
        normalized = []
        for item in raw_list:
            normalized.append({
                "source_id": self.source_id,
                "source_native_id": item.get("link", ""),
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "published_at": item.get("published", ""),
                "summary": item.get("summary", ""),
            })
        return normalized

    def next_cursor(self, response: dict) -> str | None:
        return None
