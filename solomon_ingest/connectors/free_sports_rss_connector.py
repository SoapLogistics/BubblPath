import logging
from typing import Any

import feedparser
import requests

from solomon_ingest.core.connector import SourceConnector

logger = logging.getLogger(__name__)

class FreeSportsRSSConnector(SourceConnector):
    """
    Scrapes free sports RSS feeds (WNBA, Soccer, NBA, NFL) to bypass API keys.
    """
    source_id = "free_sports_rss"

    def __init__(self):
        self.feed_urls = [
            "https://sports.yahoo.com/wnba/rss/",
            "https://sports.yahoo.com/soccer/rss/",
            "https://sports.yahoo.com/nba/rss/",
            "https://sports.yahoo.com/nfl/rss/",
        ]

    def healthcheck(self) -> dict:
        try:
            res = requests.get(self.feed_urls[0], timeout=5)
            return {"status": "ok", "source": self.source_id, "http_code": res.status_code}
        except Exception as e: # noqa: BLE001
            return {"status": "error", "source": self.source_id, "error": str(e)}

    def discover(self, cursor: str | None = None) -> list[dict[str, Any]]:
        all_entries = []
        for url in self.feed_urls:
            try:
                logger.info(f"Fetching RSS feed: {url}")
                # Use requests with a browser User-Agent to bypass 403 Forbidden
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
                res = requests.get(url, headers=headers, timeout=10)
                if res.status_code == 200:
                    feed = feedparser.parse(res.content)
                    for entry in feed.entries:
                        all_entries.append({
                            "title": entry.get("title", ""),
                            "summary": entry.get("summary", ""),
                            "link": entry.get("link", ""),
                            "feed_source": url
                        })
            except Exception as e: # noqa: BLE001
                logger.error(f"Error fetching {url}: {e}")
        return all_entries

    def fetch(self, native_id: str) -> dict:
        return {}

    def normalize(self, raw: dict) -> list[dict]:
        return []

    def next_cursor(self, response: dict) -> str | None:
        return None
