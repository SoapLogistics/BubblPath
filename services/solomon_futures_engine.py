import json
import time

route_key = "solomon_futures_engine"

class FuturesEngine:
    def __init__(self):
        self.log_file = "fact_memory.log"

    def evaluate_threshold(self, value, threshold):
        """
        Evaluate 80/90 threshold metrics.
        Returns true if value crosses or meets threshold.
        """
        if threshold not in [80.0, 90.0]:
            raise ValueError("Only 80.0 and 90.0 thresholds are supported")

        result = value >= threshold

        # Log threshold crossed
        if result:
            self._write_fact_memory(f"Threshold {threshold} crossed with value {value}")

        return result

    def generate_projection(self, target_id, confidence, data_payload):
        """
        Generates a future projection conforming to the strictly mandated data_health shape.
        """
        is_80 = self.evaluate_threshold(confidence, 80.0)
        is_90 = self.evaluate_threshold(confidence, 90.0)

        # Strict data health shape
        return {
            "target_id": target_id,
            "confidence": float(confidence),
            "threshold_80_met": is_80,
            "threshold_90_met": is_90,
            "data_health": "verified" if (is_80 or is_90) else "marginal",
            "payload": data_payload,
            "timestamp": time.time()
        }

    def _write_fact_memory(self, message):
        """
        Trace every time an 80/90 threshold is crossed or calculated in fact_memory logs.
        """
        with open(self.log_file, "a") as f:
            f.write(f"[{time.time()}] {message}\n")
