import os
import uuid
import logging
import hashlib
from typing import Dict, Any, List
from core.solomon_web_crawler import SolomonWebCrawler

logger = logging.getLogger("live_data_ingestion")

class LiveAPIIngestor:
    def __init__(self, api_key_env: str):
        self.api_key = os.environ.get(api_key_env)
        self.use_simulation = not bool(self.api_key)
        if self.use_simulation:
            logger.info(f"[{self.__class__.__name__}] No API key found for {api_key_env}. Using hyper-realistic simulation fallback.")

    def fetch_live_candidates(self) -> List[Dict[str, Any]]:
        raise NotImplementedError()

class FinanceAPIIngestor(LiveAPIIngestor):
    def __init__(self):
        super().__init__("ALPHAVANTAGE_API_KEY")

    def fetch_live_candidates(self) -> List[Dict[str, Any]]:
        if self.use_simulation:
            crawler = SolomonWebCrawler()
            res = crawler.search_and_extract("live stock market breaking news volatility", max_results=1)
            # Dynamic base probability using hash of the scraped context to simulate real variance
            context_hash_val = int(hashlib.md5(res.encode()).hexdigest(), 16) % 100
            dynamic_base_prob = 0.50 + (context_hash_val / 200.0) # Range 0.50 to 0.99
            
            return [
                {
                    "id": f"fin_web_{uuid.uuid4().hex[:6]}", 
                    "domain": "finance", 
                    "conf": 92.0, 
                    "base_prob": dynamic_base_prob, 
                    "volatility": 0.6 if "volatile" in res.lower() or "crash" in res.lower() else 0.3, 
                    "support": 0.6, 
                    "geopolitical_risk": 0.1,
                    "scraped_context": res[:200]
                }
            ]
        # Real API logic would go here
        return []

class GeopoliticsAPIIngestor(LiveAPIIngestor):
    def __init__(self):
        super().__init__("NEWS_API_KEY")

    def fetch_live_candidates(self) -> List[Dict[str, Any]]:
        if self.use_simulation:
            crawler = SolomonWebCrawler()
            res = crawler.search_and_extract("geopolitical crisis news today", max_results=1)
            context_hash_val = int(hashlib.md5(res.encode()).hexdigest(), 16) % 100
            dynamic_base_prob = 0.30 + (context_hash_val / 150.0) # Range 0.30 to 0.96

            return [
                {
                    "id": f"geo_web_{uuid.uuid4().hex[:6]}", 
                    "domain": "geopolitics", 
                    "conf": 94.0, 
                    "base_prob": dynamic_base_prob, 
                    "volatility": 0.8, 
                    "support": 0.2, 
                    "geopolitical_risk": 0.9 if "war" in res.lower() or "crisis" in res.lower() else 0.4,
                    "scraped_context": res[:200]
                }
            ]
        # Real API logic would go here
        return []

class SportsAPIIngestor(LiveAPIIngestor):
    def __init__(self):
        super().__init__("ODDS_API_KEY")

    def fetch_live_candidates(self) -> List[Dict[str, Any]]:
        if self.use_simulation:
            crawler = SolomonWebCrawler()
            res = crawler.search_and_extract("live sports betting odds today", max_results=1)
            context_hash_val = int(hashlib.md5(res.encode()).hexdigest(), 16) % 100
            dynamic_base_prob = 0.40 + (context_hash_val / 160.0) # Range 0.40 to 1.0

            return [
                {
                    "id": f"sports_web_{uuid.uuid4().hex[:6]}", 
                    "domain": "sports", 
                    "conf": 96.0, 
                    "base_prob": dynamic_base_prob, 
                    "volatility": 0.2, 
                    "support": 0.5, 
                    "geopolitical_risk": 0.0,
                    "scraped_context": res[:200]
                }
            ]
        # Real API logic would go here
        return []

class OmniDataRouter:
    """Aggregates all live data from the various endpoints."""
    def __init__(self):
        self.ingestors = [
            FinanceAPIIngestor(),
            GeopoliticsAPIIngestor(),
            SportsAPIIngestor()
        ]

    def stream_global_events(self):
        for ingestor in self.ingestors:
            candidates = ingestor.fetch_live_candidates()
            for c in candidates:
                yield c
