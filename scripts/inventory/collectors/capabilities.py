import json
import os

def collect():
    results = []
    evidence = []

    if os.path.exists("/app/solomon_api/engine_registry.json"):
        with open("/app/solomon_api/engine_registry.json") as f:
            data = json.load(f)
            for eng in data.get("engines", []):
                results.append({
                    "capability_ID": eng.get("engine_id"),
                    "name": eng.get("display_name"),
                    "path": eng.get("source_path"),
                    "status": eng.get("status_class"),
                })

        evidence.append({
            "claim": "Capabilities loaded from registry",
            "confidence": "VERIFIED",
            "collector": "capabilities.py",
            "command": "read solomon_api/engine_registry.json",
            "stdout": f"Loaded {len(results)} capabilities"
        })
    else:
        evidence.append({
            "claim": "Registry not found",
            "confidence": "CONTRADICTED",
            "collector": "capabilities.py",
            "command": "read solomon_api/engine_registry.json",
            "stdout": ""
        })

    return results, evidence
