import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_payload_limit(client):
    # Trying to send a >1MB payload
    huge_payload = b"A" * (2 * 1024 * 1024)
    response = client.post("/chat", data=huge_payload, content_type="application/json")
    # Flask MAX_CONTENT_LENGTH drops it with 413 Request Entity Too Large
    assert response.status_code in (400, 413)

def test_gzip_and_headers(client):
    response = client.get("/api/system/health", headers={"Accept-Encoding": "gzip"})

    assert response.status_code == 200
    assert response.headers.get("Content-Encoding") == "gzip"
    assert "X-Response-Time-Ms" in response.headers
    assert response.headers.get("Access-Control-Allow-Origin") == "chrome-extension://solomon-uuid"

def test_telemetry_rss(client):
    response = client.get("/api/system/health")
    data = response.get_json()
    assert "process_rss_mb" in data["telemetry"]
    assert data["telemetry"]["process_rss_mb"] > 0

if __name__ == "__main__":
    pytest.main(["-v", "test_flask_opts_41_50.py"])
