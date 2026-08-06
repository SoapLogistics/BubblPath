import urllib.parse

import requests

from solomon_ingest.core.connector import SourceConnector


class GDELTConnector(SourceConnector):
    source_id = "gdelt"
    base_url = "https://api.gdeltproject.org/api/v2/doc/doc"

    def healthcheck(self) -> dict:
        try:
            # Query for something highly generic just to test the endpoint
            res = requests.get(f"{self.base_url}?query=test&mode=artlist&format=json&maxrecords=1", timeout=5)
            if res.status_code == 200:
                return {"status": "ok", "source": self.source_id, "http_code": res.status_code}
            return {"status": "degraded", "source": self.source_id, "http_code": res.status_code}
        except Exception as e:
            return {"status": "error", "source": self.source_id, "error": str(e)}

    def discover(self, cursor: str | None = None) -> list[dict]:
        # A basic discovery query: global news matching a generic filter
        # In a real scenario, this would be highly configurable based on Solomon's current focus
        # For this test, let's query for recent major global events
        query = urllib.parse.quote("sourcelang:eng")
        url = f"{self.base_url}?query={query}&mode=artlist&format=json&maxrecords=5"
        
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()
            articles = data.get("articles", [])
            return self.normalize(articles)
        except Exception as e:
            print(f"[GDELT] Discover error: {e}")
            return []

    def fetch(self, native_id: str) -> dict:
        # GDELT Doc API doesn't easily fetch by single article ID,
        # it returns arrays of articles based on search queries.
        # But we implement the interface.
        return {}

    def normalize(self, raw_list: list) -> list[dict]:
        normalized = []
        for item in raw_list:
            normalized.append({
                "source_id": self.source_id,
                "source_native_id": item.get("url"),
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "published_at": item.get("seendate", ""),
                "domain": item.get("domain", ""),
                "language": item.get("language", "")
            })
        return normalized

    def next_cursor(self, response: dict) -> str | None:
        # GDELT doesn't provide standard pagination cursors in the basic artlist JSON
        return None
