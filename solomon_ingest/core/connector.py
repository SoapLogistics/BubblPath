class SourceConnector:
    source_id: str

    def healthcheck(self) -> dict:
        pass

    def discover(self, cursor: str | None = None) -> list[dict]:
        pass

    def fetch(self, native_id: str) -> dict:
        pass

    def normalize(self, raw: dict) -> list[dict]:
        pass

    def next_cursor(self, response: dict) -> str | None:
        pass
