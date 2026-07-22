import json
import pytest
from unittest.mock import MagicMock, patch
from app import app, SYSTEM_INSTRUCTIONS
from openai import RateLimitError, APIConnectionError, APIError

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_health_endpoint(client):
    """Verify that the health route returns telemetry metrics and is healthy."""
    response = client.get("/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["status"] == "healthy"
    assert "uptime_seconds" in data
    assert "memory_footprint" in data
    assert "openai_client_state" in data

def test_chat_non_json_payload(client):
    """Verify that /chat endpoint rejects non-JSON content types."""
    response = client.post("/chat", data="Not JSON", content_type="text/plain")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "Content-Type must be application/json" in data["error"]

def test_chat_empty_json(client):
    """Verify that /chat endpoint handles empty JSON gracefully."""
    response = client.post("/chat", json={}, content_type="application/json")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_chat_missing_message(client):
    """Verify that /chat endpoint rejects requests missing the 'message' field."""
    response = client.post("/chat", json={"other_key": "val"}, content_type="application/json")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "Missing or empty 'message'" in data["error"]

def test_chat_empty_message_string(client):
    """Verify that /chat endpoint rejects empty message string."""
    response = client.post("/chat", json={"message": "   "}, content_type="application/json")
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

@patch("app.openai_client")
def test_chat_success(mock_openai, client):
    """Verify that a successful chat transaction processes correctly and invokes system instructions."""
    # Build nested mock structure simulating modern openai client's response
    mock_completion = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = (
        "Hello, from the architect foundation.\n\n"
        "### **<span style='color:#ff0055;'>RECOMMENDED NEXT STEP</span>**\n"
        "Integrate additional metrics handlers."
    )
    mock_completion.choices = [mock_choice]
    mock_openai.chat.completions.create.return_value = mock_completion

    response = client.post("/chat", json={"message": "System check"}, content_type="application/json")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "reply" in data
    assert "RECOMMENDED NEXT STEP" in data["reply"]

    # Assert client was called with correct arguments
    mock_openai.chat.completions.create.assert_called_once()
    kwargs = mock_openai.chat.completions.create.call_args[1]
    assert kwargs["model"] == "gpt-3.5-turbo"
    assert kwargs["messages"][0]["role"] == "system"
    assert kwargs["messages"][0]["content"] == SYSTEM_INSTRUCTIONS
    assert kwargs["messages"][1]["role"] == "user"
    assert kwargs["messages"][1]["content"] == "System check"

@patch("app.openai_client")
def test_chat_rate_limit_error(mock_openai, client):
    """Verify that RateLimitError is captured and custom error status is returned."""
    # Simulate standard OpenAI RateLimitError
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {}

    mock_openai.chat.completions.create.side_effect = RateLimitError(
        message="Too many requests",
        response=mock_response,
        body=None
    )

    response = client.post("/chat", json={"message": "Test limit"}, content_type="application/json")
    assert response.status_code == 429
    data = json.loads(response.data)
    assert "error" in data
    assert "Rate limit exceeded" in data["error"]

@patch("app.openai_client")
def test_chat_connection_error(mock_openai, client):
    """Verify that APIConnectionError returns a custom network failure error status."""
    mock_openai.chat.completions.create.side_effect = APIConnectionError(
        message="Network unreachability",
        request=MagicMock()
    )

    response = client.post("/chat", json={"message": "Test connection"}, content_type="application/json")
    assert response.status_code == 503
    data = json.loads(response.data)
    assert "error" in data
    assert "Failed to connect to the model provider" in data["error"]

@patch("app.openai_client")
def test_chat_api_error(mock_openai, client):
    """Verify that standard APIError returns model provider error status."""
    mock_openai.chat.completions.create.side_effect = APIError(
        message="Internal Provider Error",
        request=MagicMock(),
        body=None
    )

    response = client.post("/chat", json={"message": "Test api error"}, content_type="application/json")
    assert response.status_code == 502
    data = json.loads(response.data)
    assert "error" in data
    assert "Model provider API error" in data["error"]

@patch("app.openai_client")
def test_chat_unexpected_exception(mock_openai, client):
    """Verify that unexpected exceptions are handled gracefully with a 500 error status."""
    mock_openai.chat.completions.create.side_effect = ValueError("Fatal execution anomaly")

    response = client.post("/chat", json={"message": "Test generic error"}, content_type="application/json")
    assert response.status_code == 500
    data = json.loads(response.data)
    assert "error" in data
    assert "An unexpected system error occurred" in data["error"]

def test_chat_uninitialized_client(client):
    """Verify that when the OpenAI client is uninitialized, /chat returns a 500 error status."""
    with patch("app.openai_client", None):
        response = client.post("/chat", json={"message": "No client"}, content_type="application/json")
        assert response.status_code == 500
        data = json.loads(response.data)
        assert "error" in data
        assert "OpenAI client is not configured" in data["error"]

def test_get_memory_footprint_with_proc_mock(client):
    """Verify memory footprint parsing when mock proc filesystem is present."""
    from unittest.mock import mock_open
    mock_data = "VmRSS:     10240 kB\n"
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=mock_data)):
            from app import get_memory_footprint
            res = get_memory_footprint()
            assert res == "10.00 MB"

def test_get_memory_footprint_exception_fallback(client):
    """Verify fallback behavior of get_memory_footprint when exception occurs."""
    with patch("os.path.exists", side_effect=Exception("mocked os error")):
        with patch("resource.getrusage", side_effect=Exception("mocked resource error")):
            from app import get_memory_footprint
            res = get_memory_footprint()
            assert res == "N/A"
