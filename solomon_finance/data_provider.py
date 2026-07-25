import time
import random
import logging
from typing import Dict, Any, Generator
from solomon_core.interfaces import IDataProvider

logger = logging.getLogger("LokiDataProvider")

class LightweightMarketStream(IDataProvider):
    """
    Zero-IO, generator-based streaming data feed for Loki.
    Avoids heavy requests overhead by yielding synthetic/cached market ticks.
    """
    def fetch_data(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetches a single synthetic market snapshot."""
        asset = query_params.get("asset", "UNKNOWN")
        return {
            "asset": asset,
            "price": round(random.uniform(100.0, 500.0), 2),
            "timestamp": int(time.time())
        }

    def stream_data(self, callback: callable) -> None:
        """
        Simulates an infinite stream of market ticks without blocking the main thread.
        In production, this wraps a WebSocket.
        """
        logger.info("Starting lightweight market stream...")
        # A simple synthetic generator for extreme efficiency testing
        def synthetic_tick_generator() -> Generator[Dict[str, Any], None, None]:
            base_price = 150.0
            while True:
                base_price += random.uniform(-1.0, 1.0)
                yield {"asset": "SYNTH_SPX", "price": round(base_price, 2), "timestamp": int(time.time())}

        # In a real async scenario, this would yield to an event loop
        # Here we just generate 5 ticks to prove the interface
        gen = synthetic_tick_generator()
        for _ in range(5):
            callback(next(gen))
