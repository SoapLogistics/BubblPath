from solomon_os.kernel import SolomonModule
import threading
import time
import logging

logger = logging.getLogger("SchedulingModule")

class SchedulingModule(SolomonModule):
    def __init__(self):
        super().__init__()
        self.cron_jobs = []
        self._lock = threading.RLock()

    def start(self):
        super().start()
        self.kernel.register_rpc('add_cron_job', self.add_cron_job)
        self.kernel.register_rpc('list_cron_jobs', self.list_cron_jobs)

        # Start a background tick thread
        self.tick_thread = threading.Thread(target=self._tick_loop, daemon=True)
        self.tick_thread.start()

    def add_cron_job(self, name: str, event_topic: str, interval_seconds: int, payload: dict = None) -> bool:
        with self._lock:
            self.cron_jobs.append({
                "name": name,
                "topic": event_topic,
                "interval": interval_seconds,
                "payload": payload or {},
                "last_run": time.time()
            })
            logger.info(f"Added cron job {name} for event {event_topic} every {interval_seconds}s")
            return True

    def list_cron_jobs(self) -> list:
        with self._lock:
            return self.cron_jobs.copy()

    def _tick_loop(self):
        while self.state == "RUNNING":
            current_time = time.time()
            if self.kernel:
                self.kernel.publish('TICK_1S', self.name, {"timestamp": current_time})

                # Check cron jobs
                with self._lock:
                    for job in self.cron_jobs:
                        if current_time - job["last_run"] >= job["interval"]:
                            job["last_run"] = current_time
                            self.kernel.publish(job["topic"], self.name, job["payload"])
                            logger.info(f"Cron fired: {job['name']} -> {job['topic']}")

            time.sleep(1)
