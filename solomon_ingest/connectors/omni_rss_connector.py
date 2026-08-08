import json
import logging
import os
from typing import Any

import feedparser
import requests

from solomon_ingest.core.connector import SourceConnector

logger = logging.getLogger(__name__)

class OmniRSSConnector(SourceConnector):
    """
    A single massive ingestion engine that scrapes dozens of global feeds simultaneously.
    Bypasses all API keys, rate limits, and authentication.
    """
    source_id = "omni_rss"

    def __init__(self, target_categories: list[str] = None):
        """
        :param target_categories: e.g. ["sports", "finance"]. If None, pulls EVERYTHING.
        """
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "omni_feeds.json")
        try:
            with open(self.config_path, "r") as f:
                self.FEED_MATRIX = json.load(f)
        except Exception as e: # noqa: BLE001
            logger.error(f"[OMNI] Failed to load omni_feeds.json: {e}")
            self.FEED_MATRIX = {}

        self.target_categories = target_categories if target_categories else list(self.FEED_MATRIX.keys())
        self.active_urls = []
        for cat in self.target_categories:
            if cat in self.FEED_MATRIX:
                self.active_urls.extend(self.FEED_MATRIX[cat])

    def healthcheck(self) -> dict:
        if not self.active_urls:
            return {"status": "error", "source": self.source_id, "error": "No active URLs configured."}
        try:
            res = requests.get(self.active_urls[0], timeout=5)
            return {"status": "ok", "source": self.source_id, "http_code": res.status_code}
        except Exception as e: # noqa: BLE001
            return {"status": "error", "source": self.source_id, "error": str(e)}

    def discover(self, cursor: str | None = None) -> list[dict[str, Any]]:
        all_entries = []
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
        
        for url in self.active_urls:
            try:
                logger.info(f"[OMNI] Fetching RSS feed: {url}")
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
                logger.error(f"[OMNI] Error fetching {url}: {e}")
                
        return all_entries

    def fetch(self, native_id: str) -> dict:
        return {}

    def normalize(self, raw: dict) -> list[dict]:
        return []

    def next_cursor(self, response: dict) -> str | None:
        return None
