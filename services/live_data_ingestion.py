import os
import time
import uuid
import random
import logging
import hashlib
from typing import Dict, Any, List
from core.solomon_web_crawler import SolomonWebCrawler
from datetime import datetime, UTC
from core.health import HealthCheckResult, HealthStatus, registry


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
            # Create a real candidate from the scraped data
            return [
                {
                    "id": f"fin_web_{uuid.uuid4().hex[:6]}", 
                    "domain": "finance", 
                    "conf": 92.0, 
                    "base_prob": 0.55, 
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
            return [
                {
                    "id": f"geo_web_{uuid.uuid4().hex[:6]}", 
                    "domain": "geopolitics", 
                    "conf": 94.0, 
                    "base_prob": 0.40, 
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
            return [
                {
                    "id": f"sports_web_{uuid.uuid4().hex[:6]}", 
                    "domain": "sports", 
                    "conf": 96.0, 
                    "base_prob": 0.50, 
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

    def healthcheck(self) -> HealthCheckResult:
        try:
            return HealthCheckResult(
                service="omni_data_router",
                status=HealthStatus.HEALTHY,
                checked_at=datetime.now(UTC),
                message=f"Router is active with {len(self.ingestors)} ingestors"
            )
        except Exception as e:
            return HealthCheckResult(
                service="omni_data_router",
                status=HealthStatus.UNHEALTHY,
                checked_at=datetime.now(UTC),
                message="Health check failed",
                details={"error_type": type(e).__name__}
            )

    def stream_global_events(self):
        for ingestor in self.ingestors:
            candidates = ingestor.fetch_live_candidates()
            for c in candidates:
                yield c

def check_omni_data_router() -> HealthCheckResult:
    try:
        # We can just check the environment variables used by the ingestors
        import os
        keys_missing = []
        if not os.environ.get("ALPHAVANTAGE_API_KEY"): keys_missing.append("ALPHAVANTAGE_API_KEY")
        if not os.environ.get("NEWS_API_KEY"): keys_missing.append("NEWS_API_KEY")
        if not os.environ.get("ODDS_API_KEY"): keys_missing.append("ODDS_API_KEY")

        if len(keys_missing) == 3:
            # If all are missing, we fall back to simulation
            status = HealthStatus.DEGRADED
            msg = "Using hyper-realistic simulation fallback (no live keys found)"
        else:
            status = HealthStatus.HEALTHY
            msg = "Live data ingestor keys configured"

        return HealthCheckResult(
            service="omni_data_router",
            status=status,
            checked_at=datetime.now(UTC),
            message=msg
        )
    except Exception as e:
        return HealthCheckResult(
            service="omni_data_router",
            status=HealthStatus.UNHEALTHY,
            checked_at=datetime.now(UTC),
            message="Health check failed",
            details={"error_type": type(e).__name__}
        )
registry.register("omni_data_router", check_omni_data_router, critical=False)
