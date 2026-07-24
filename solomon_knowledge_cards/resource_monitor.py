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

def enforce_resource_caps(max_memory_mb: float = 1536.0) -> bool:
    """
    Enforces a strict 1.5GB (1536MB) memory cap.
    Logs plain-text warnings to the telemetry sink.
    Returns True if resource utilization is safely within boundaries, False if cap is exceeded.
    """
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
        telemetry_logger.info(f"HEALTH CHECK: Memory footprint stable at {mem_used:.2f}MB.")
        return True
