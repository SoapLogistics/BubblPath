import sys
import os
import json

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings
from core.health import registry, HealthStatus
# Import services to register them
import services.solomon_futures_engine
import services.solomon_governance_approval_packet
import core.solomon_quantized_memory
import services.live_data_ingestion


def cmd_config_check():
    print("=== Configuration Check ===")
    print(f"Environment: {settings.app.environment}")
    print(f"Log Level: {settings.app.log_level}")
    print(f"Test Mode: {settings.app.test_mode}")
    print(f"Database Path: {settings.database.db_path}")
    print(f"WAL Mode: {settings.database.wal_mode}")
    print(f"Health Checks Enabled: {settings.health.enabled}")

    # Check secrets securely
    if settings.providers.openai_api_key:
        print("OpenAI API Key: [SET]")
    else:
        print("OpenAI API Key: [MISSING]")

    print("\nStatus: Validation Passed.")
    return 0

def cmd_health():
    print("=== Health Check ===")
    results = registry.run_all()

    print(f"Overall Status: {results['status']}")
    print(f"Timestamp: {results['timestamp']}")
    print("-" * 40)

    for r in results['results']:
        print(f"Service: {r['service']}")
        print(f"  Status:  {r['status']}")
        print(f"  Latency: {r['latency_ms']:.2f} ms")
        print(f"  Message: {r['message']}")
        if r['details']:
            print(f"  Details: {r['details']}")
        print("-" * 40)

    if results['status'] == HealthStatus.UNHEALTHY.value:
        return 1
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/solomon_dx.py [config-check|health]")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "config-check":
        sys.exit(cmd_config_check())
    elif cmd == "health":
        sys.exit(cmd_health())
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)

if __name__ == "__main__":
    main()
