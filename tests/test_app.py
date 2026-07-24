import os
import pytest
from unittest.mock import MagicMock, patch
from openai import RateLimitError, APIConnectionError, APIStatusError
from httpx import Request, Response

# Ensure environment variable is set before importing the app
os.environ["OPENAI_API_KEY"] = "test-key-12345"

from app import app, client, limiter

@pytest.fixture
def test_client():
    app.config["TESTING"] = True
    # Disable rate limiting for standard tests to prevent cross-contamination,
    # unless specifically testing rate limiting.
    limiter.enabled = False
    with app.test_client() as flask_client:
        yield flask_client

def test_health_check_healthy(test_client):
    """Tests health check endpoint when API key is configured."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-12345"}):
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "healthy"
        assert data["environment"]["openai_api_key_configured"] is True

def test_health_check_unhealthy(test_client):
    """Tests health check endpoint when API key is missing."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": ""}):
        response = test_client.get("/health")
        assert response.status_code == 503
        data = response.get_json()
        assert data["status"] == "unhealthy"
        assert data["environment"]["openai_api_key_configured"] is False
        assert "Service misconfigured" in data["message"]

def test_chat_success(test_client):
    """Tests successful chat completion with mock OpenAI response."""
    # Create mock structure for client.chat.completions.create response
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a wonderful mock reply!"

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch.object(client.chat.completions, "create", return_value=mock_response) as mock_create:
        response = test_client.post("/chat", json={"message": "Hello!"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["reply"] == "This is a wonderful mock reply!"

        # Verify call was correct
        mock_create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello!"}],
            max_tokens=1000
        )

def test_chat_non_json_payload(test_client):
    """Tests payload validation for non-JSON content type."""
    response = test_client.post("/chat", data="just a plain string")
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "Content-Type must be application/json" in data["message"]

def test_chat_malformed_or_none_json(test_client):
    """Tests payload validation when get_json() raises BadRequest on malformed JSON."""
    response = test_client.post(
        "/chat",
        data="malformed-json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "could not understand" in data["message"]

def test_chat_null_json(test_client):
    """Tests payload validation when get_json() successfully parses but is None."""
    response = test_client.post(
        "/chat",
        data="null",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "Invalid JSON body" in data["message"]

def test_chat_empty_json(test_client):
    """Tests payload validation for missing fields."""
    response = test_client.post("/chat", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "Missing required field: 'message'" in data["message"]

def test_chat_non_string_message(test_client):
    """Tests payload validation when message is not a string."""
    response = test_client.post("/chat", json={"message": 12345})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "The 'message' field must be a string" in data["message"]

def test_chat_empty_string_message(test_client):
    """Tests payload validation when message is empty or whitespace only."""
    response = test_client.post("/chat", json={"message": "   "})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "cannot be empty or whitespace" in data["message"]

def test_chat_message_too_long(test_client):
    """Tests payload validation when message exceeds characters threshold."""
    long_message = "A" * 4001
    response = test_client.post("/chat", json={"message": long_message})
    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "Bad Request"
    assert "exceeds the maximum allowed length" in data["message"]

def test_chat_openai_rate_limit(test_client):
    """Tests error handling for RateLimitError from OpenAI API."""
    # Instantiate RateLimitError with a mock response and request
    req = Request("POST", "https://api.openai.com/v1/chat/completions")
    res = Response(429, request=req)
    rate_limit_err = RateLimitError("Rate limit exceeded.", response=res, body={})

    with patch.object(client.chat.completions, "create", side_effect=rate_limit_err):
        response = test_client.post("/chat", json={"message": "Trigger Rate Limit"})
        assert response.status_code == 429
        data = response.get_json()
        assert data["error"] == "Service Unavailable"
        assert "OpenAI API rate limit exceeded" in data["message"]

def test_chat_openai_connection_error(test_client):
    """Tests error handling for APIConnectionError from OpenAI SDK."""
    req = Request("POST", "https://api.openai.com/v1/chat/completions")
    connection_err = APIConnectionError(request=req, message="Connection timed out.")

    with patch.object(client.chat.completions, "create", side_effect=connection_err):
        response = test_client.post("/chat", json={"message": "Trigger Connection Error"})
        assert response.status_code == 503
        data = response.get_json()
        assert data["error"] == "Service Unavailable"
        assert "Could not connect to OpenAI API servers" in data["message"]

def test_chat_openai_status_error(test_client):
    """Tests error handling for general APIStatusError from OpenAI SDK."""
    req = Request("POST", "https://api.openai.com/v1/chat/completions")
    res = Response(401, request=req)
    status_err = APIStatusError("Unauthorized access.", response=res, body={})

    with patch.object(client.chat.completions, "create", side_effect=status_err):
        response = test_client.post("/chat", json={"message": "Trigger Status Error"})
        assert response.status_code == 401
        data = response.get_json()
        assert data["error"] == "OpenAI API Error (401)"
        assert "OpenAI returned an error" in data["message"]

def test_chat_unexpected_exception(test_client):
    """Tests error handling for general unexpected server errors."""
    with patch.object(client.chat.completions, "create", side_effect=ValueError("Unexpected database disconnect")):
        response = test_client.post("/chat", json={"message": "Trigger generic error"})
        assert response.status_code == 500
        data = response.get_json()
        assert data["error"] == "Internal Server Error"
        assert "An unexpected error occurred" in data["message"]

def test_not_found(test_client):
    """Tests customized 404 handler."""
    response = test_client.get("/this-route-does-not-exist")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Not Found"
    assert "resource was not found" in data["message"]

def test_method_not_allowed(test_client):
    """Tests customized 405 handler."""
    response = test_client.get("/chat")  # /chat only allows POST
    assert response.status_code == 405
    data = response.get_json()
    assert data["error"] == "Method Not Allowed"
    assert "method is not allowed" in data["message"]

def test_chat_rate_limiting():
    """Tests custom rate limiter throttling endpoint when enabled."""
    app.config["TESTING"] = True
    limiter.enabled = True

    # We create a temporary client instance to test rate-limiting behavior
    with app.test_client() as local_client:
        # Our limit is 30 per minute. We will mock the OpenAI API calls to always succeed
        mock_choice = MagicMock()
        mock_choice.message.content = "Mocked Response"
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        with patch.object(client.chat.completions, "create", return_value=mock_response):
            # Fire 31 requests to trip the limiter limit of 30 per minute
            for i in range(30):
                resp = local_client.post("/chat", json={"message": f"Hello {i}"})
                assert resp.status_code == 200

            # The 31st request should be rate limited
            limited_resp = local_client.post("/chat", json={"message": "Limit breaker"})
            assert limited_resp.status_code == 429
            data = limited_resp.get_json()
            assert data["error"] == "Rate limit exceeded"
            assert "Too many requests" in data["message"]

    # Clean up state: disable rate limiter for any other subsequent test runner context
    limiter.enabled = False
