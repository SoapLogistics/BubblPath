from solomon_ingest.core.connector import SourceConnector

class APISportsConnector(SourceConnector):
    source_id = "api_sports"

    def healthcheck(self) -> dict:
        return {"status": "ok", "source": self.source_id}

    def discover(self, cursor: str | None = None) -> list[dict]:
        return []

    def fetch(self, native_id: str) -> dict:
        return {}

    def normalize(self, raw: dict) -> list[dict]:
        return []

    def next_cursor(self, response: dict) -> str | None:
        return None
