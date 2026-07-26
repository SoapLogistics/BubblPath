"""
Worker registry for Gabriel, Mnemosyne, Prometheus, Loki.
"""
route_key = "/api/command-center/workers"
readiness_key = "soss_worker_registry"

def get_workers():
    return ["Gabriel", "Mnemosyne", "Prometheus", "Loki"]
