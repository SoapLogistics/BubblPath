import time
import json
import os

class GabrielMetricsTracker:
    """
    Implements Roadmap Item 1: Measure everything.
    Tracks latency, cost, success rate, and learning events.
    """
    def __init__(self, log_file="metrics_log.json"):
        self.log_file = log_file
        self.metrics = {
            "total_tasks": 0,
            "successful_tasks": 0,
            "total_latency_ms": 0,
            "learning_events": 0,
            "compressions_performed": 0
        }
        self._load_metrics()

    def _load_metrics(self):
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, "r") as f:
                    self.metrics = json.load(f)
            except:
                pass

    def _save_metrics(self):
        with open(self.log_file, "w") as f:
            json.dump(self.metrics, f, indent=4)

    def record_task(self, latency_ms, success=True):
        self.metrics["total_tasks"] += 1
        self.metrics["total_latency_ms"] += latency_ms
        if success:
            self.metrics["successful_tasks"] += 1
        self._save_metrics()

    def record_learning_event(self):
        self.metrics["learning_events"] += 1
        self._save_metrics()

    def record_compression(self):
        self.metrics["compressions_performed"] += 1
        self._save_metrics()

    def get_stats(self):
        avg_latency = 0
        if self.metrics["total_tasks"] > 0:
            avg_latency = self.metrics["total_latency_ms"] / self.metrics["total_tasks"]

        success_rate = 0
        if self.metrics["total_tasks"] > 0:
            success_rate = (self.metrics["successful_tasks"] / self.metrics["total_tasks"]) * 100

        return {
            "total_tasks": self.metrics["total_tasks"],
            "avg_latency_ms": round(avg_latency, 2),
            "success_rate_percent": round(success_rate, 2),
            "learning_events": self.metrics["learning_events"],
            "compressions_performed": self.metrics["compressions_performed"]
        }

metrics_tracker = GabrielMetricsTracker()
