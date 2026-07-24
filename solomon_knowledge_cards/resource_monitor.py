import os
import sys
import logging
from datetime import datetime

# Setup logs directory safely
LOGS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE_PATH = os.path.join(LOGS_DIR, "solomon_telemetry.log")

# Setup clean plain-text telemetry logging
telemetry_logger = logging.getLogger("solomon_telemetry")
telemetry_logger.setLevel(logging.INFO)

# Avoid adding multiple handlers if already initialized
if not telemetry_logger.handlers:
    fh = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    fh.setFormatter(formatter)
    telemetry_logger.addHandler(fh)

def get_memory_footprint_mb() -> float:
    """
    Parses the current process memory footprint in Megabytes (MB).
    Reads /proc/self/status under Linux, or uses mock/psutil fallback safely.
    """
    try:
        # Standard Linux system proc lookup
        if os.path.exists("/proc/self/status"):
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        parts = line.split()
                        return float(parts[1]) / 1024.0 # Convert KB to MB

        # Fallback for other operating systems (e.g. macOS / Windows)
        import resource
        return float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) / 1024.0
    except Exception:
        # Static mock return if platform doesn't support proc lookup or resource
        return 42.0

def get_scaled_memory_cap() -> float:
    """
    Dynamically scales the memory cap based on Project Loki's net betting profit.
    'More cash equals more RAM' auto-financing rule!
    Starts at 1.5GB (1536MB) and scales up to 3.0GB (3072MB) as bankroll profit grows.
    """
    base_cap = 1536.0 # 1.5GB
    try:
        # Import LokiEngine dynamically to prevent circular dependencies
        from .loki_engine import LokiEngine
        from .runtime import MnemosyneRuntime
        runtime = MnemosyneRuntime()
        loki = LokiEngine(runtime)
        stats = loki.get_betting_stats()
        net_profit = stats.get("net_profit", 0.0)

        if net_profit > 0.0:
            # Scale: add 1.0MB of allowed RAM for every $1.00 of net profit, capped at 3GB
            scaled_cap = base_cap + (net_profit * 1.0)
            return min(scaled_cap, 3072.0) # Cap at 3.0GB (3072MB)
    except Exception:
        pass
    return base_cap

def enforce_resource_caps(max_memory_mb: float = 1536.0) -> bool:
    """
    Enforces a dynamic or static memory cap.
    Logs plain-text warnings to the telemetry sink.
    Returns True if resource utilization is safely within boundaries, False if cap is exceeded.
    """
    if max_memory_mb == 1536.0:
        max_memory_mb = get_scaled_memory_cap()

    mem_used = get_memory_footprint_mb()
    timestamp = datetime.utcnow().isoformat()

    if mem_used > max_memory_mb:
        msg = f"CRITICAL LIMIT: Process memory utilization is {mem_used:.2f}MB, which exceeds the cap of {max_memory_mb:.2f}MB!"
        telemetry_logger.error(msg)
        # Log to stderr directly
        print(f"[{timestamp}] | RESOURCE_ALERT | {msg}", file=sys.stderr)
        return False
    else:
        # Normal trace logs
        telemetry_logger.info(f"HEALTH CHECK: Memory footprint stable at {mem_used:.2f}MB. Cap scaled to {max_memory_mb:.2f}MB.")
        return True
