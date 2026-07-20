import os
import sys
import time
import datetime
import threading
import sqlite3
import json
import urllib.request
from typing import Dict, Any

class SolomonAutonomousDaemon:
    def __init__(self, db_path: str, interval_seconds: int = 60):
        self.db_path = db_path
        self.interval_seconds = interval_seconds
        self.is_running = False
        self._thread = None
        self._lock = threading.Lock()
        self.health_log_path = "solomon_daemon_health.json"

    def start(self):
        """Starts the daemon in a background thread."""
        with self._lock:
            if not self.is_running:
                self.is_running = True
                self._thread = threading.Thread(target=self._loop, name="SolomonDaemonThread", daemon=True)
                self._thread.start()
                print("Solomon 24/7 Autonomous Optimization Daemon successfully started!")

    def stop(self):
        """Stops the background loop gracefully."""
        with self._lock:
            self.is_running = False

    def _loop(self):
        """Infinite loop running optimizations periodically."""
        while self.is_running:
            try:
                self.execute_optimization_cycle()
            except Exception as e:
                print(f"Error in daemon optimization cycle: {e}", file=sys.stderr)

            # Sleep in tiny steps to check for stop requests fast
            for _ in range(self.interval_seconds):
                if not self.is_running:
                    break
                time.sleep(1)

    def execute_optimization_cycle(self) -> Dict[str, Any]:
        """Runs a complete suite of optimization, cleaning, and connection health hardening."""
        metrics = {
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "database_vacuumed": False,
            "bytecode_pruned": 0,
            "ram_info": {},
            "connections_healthy": False
        }

        # 1. Database Housekeeping (Hardening and Time Efficiency)
        # Run VACUUM and ANALYZE to optimize SQLite indices and keep queries fast
        try:
            if os.path.exists(self.db_path):
                conn = sqlite3.connect(self.db_path)
                # Ensure write-ahead log is on for max concurrency and speed
                conn.execute("PRAGMA journal_mode = WAL;")
                conn.execute("PRAGMA synchronous = NORMAL;")
                # Clean up fragmented pages
                conn.execute("VACUUM;")
                # Optimize query planner statistics
                conn.execute("ANALYZE;")
                conn.close()
                metrics["database_vacuumed"] = True
        except Exception as e:
            print(f"Daemon database optimization failed: {e}", file=sys.stderr)

        # 2. Automated File and Bytecode Cleanups (Memory & Disk Efficiency)
        try:
            pruned_count = 0
            for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__))):
                for file in files:
                    if file.endswith(".pyc") or file.endswith(".pyo") or file.endswith(".pyd"):
                        full_path = os.path.join(root, file)
                        try:
                            os.remove(full_path)
                            pruned_count += 1
                        except OSError:
                            pass
            metrics["bytecode_pruned"] = pruned_count
        except Exception as e:
            print(f"Daemon directory cleanup failed: {e}", file=sys.stderr)

        # 3. Connection Health Verification (Strengthening Connections)
        connections = {}
        try:
            # Probe OpenAI gateway and Flask gateway health
            for service_name, url in [("local_gateway", "http://127.0.0.1:10000/cards")]:
                try:
                    req = urllib.request.Request(url, method="HEAD")
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        connections[service_name] = resp.status == 200
                except Exception:
                    connections[service_name] = False

            # Simple check if any gateway connects successfully
            metrics["connections_healthy"] = any(connections.values()) if connections else True
            metrics["connection_details"] = connections
        except Exception as e:
            print(f"Daemon connection validation failed: {e}", file=sys.stderr)

        # 4. RAM / Memory Footprint Monitoring (RAM Efficiency)
        try:
            # Read from Linux /proc/meminfo or /proc/self/status for zero-dependency overhead
            pid = os.getpid()
            status_path = f"/proc/{pid}/status"
            if os.path.exists(status_path):
                ram_metrics = {}
                with open(status_path, "r") as f:
                    for line in f:
                        if line.startswith("VmRSS:"): # Resident Set Size (actual RAM used)
                            parts = line.split()
                            ram_metrics["rss_kb"] = int(parts[1])
                        elif line.startswith("VmSize:"): # Virtual Memory Size
                            parts = line.split()
                            ram_metrics["vms_kb"] = int(parts[1])
                metrics["ram_info"] = ram_metrics
        except Exception as e:
            print(f"Daemon RAM tracking failed: {e}", file=sys.stderr)

        # Save health metrics log
        try:
            with open(self.health_log_path, "w") as f:
                json.dump(metrics, f, indent=2)
        except Exception as e:
            print(f"Daemon metrics save failed: {e}", file=sys.stderr)

        return metrics

if __name__ == "__main__":
    # If run standalone, run a single cycle as standard check
    daemon = SolomonAutonomousDaemon("solomon_mnemosyne.db")
    res = daemon.execute_optimization_cycle()
    print("Optimization cycle executed successfully:")
    print(json.dumps(res, indent=2))
