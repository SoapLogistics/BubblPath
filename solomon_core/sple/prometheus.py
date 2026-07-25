import logging
from typing import Dict, Any, List
from solomon_core.event_bus import CognitiveEventBus

logger = logging.getLogger(__name__)

class PrometheusEngine:
    """
    Curiosity Engine and Missing-Piece Queue manager.
    Listens for friction signals and curiosity pulses to generate automated experiments.
    """
    def __init__(self, bus: CognitiveEventBus):
        self.bus = bus
        self.missing_piece_queue: List[Dict[str, Any]] = []

        # Subscribe to relevant events
        self.bus.subscribe("sple.curiosity.pulse", self._on_curiosity_pulse)
        self.bus.subscribe("metrics.friction", self._on_friction_signal)

    def _on_curiosity_pulse(self, event: Any):
        """Triggered periodically by the Scheduler."""
        logger.info("Prometheus: Curiosity pulse received.")
        self._evaluate_queue()

    def _on_friction_signal(self, event: Any):
        """Triggered when an error or inefficient workflow is detected."""
        payload = event.payload
        logger.info(f"Prometheus: Friction signal received: {payload}")

        # Normalize and diagnose (Stage 2/3 of SPLE Pipeline)
        entry = {
            "source": payload.get("source", "unknown"),
            "error": payload.get("error", "none"),
            "context": payload.get("context", {}),
            "status": "pending_analysis"
        }
        self.missing_piece_queue.append(entry)

    def _evaluate_queue(self):
        """Scans the missing piece queue and initiates experiments if resources permit."""
        if not self.missing_piece_queue:
            return

        # Take the top priority item
        item = self.missing_piece_queue.pop(0)
        logger.info(f"Prometheus: Proposing experiment for friction source: {item['source']}")

        # Emit an event for Gabriel to pick up and solve
        self.bus.publish("gabriel.task.propose", {
            "task": f"Resolve friction in {item['source']}",
            "details": item
        })
