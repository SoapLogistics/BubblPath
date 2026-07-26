import time
from flask import request, g
from core.solomon_telemetry import telemetry
import hashlib

def before_request_telemetry():
    g.start_time = time.time()

def after_request_telemetry(response):
    if not hasattr(g, 'start_time'):
        return response

    duration_ms = (time.time() - g.start_time) * 1000
    success = 200 <= response.status_code < 400

    path = request.path
    if request.query_string:
        path += "?" + request.query_string.decode('utf-8')

    # Generate quick correlation hash based on IP and time if no header
    corr_id = request.headers.get("X-Correlation-ID", str(time.time()) + request.remote_addr)

    # Context could just be the endpoint and method
    context = f"{request.method} {path}"

    telemetry.record_event(
        component="api",
        event_type=1, # 1 for HTTP Request
        severity="info" if success else "error",
        duration_ms=duration_ms,
        success=success,
        corr_id=corr_id,
        context=context
    )
    return response

def register_telemetry_middleware(app):
    app.before_request(before_request_telemetry)
    app.after_request(after_request_telemetry)
