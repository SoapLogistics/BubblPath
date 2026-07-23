import json
import pytest
from unittest.mock import MagicMock, patch
from openai import OpenAIError, RateLimitError
from flask import Request
from app import app, client

@pytest.fixture
def flask_client():
    app.config["TESTING"] = True
    with app.test_client() as client_fixture:
        yield client_fixture

def test_chat_success(flask_client):
    """Test successful chat invocation with mocked OpenAI completion response."""
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a mocked response."

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    with patch.object(client.chat.completions, "create", return_value=mock_response) as mock_create:
        response = flask_client.post(
            "/chat",
            json={"message": "Hello, how are you?"}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data == {"reply": "This is a mocked response."}

        # Verify call arguments
        mock_create.assert_called_once()
        kwargs = mock_create.call_args[1]
        assert kwargs["messages"] == [{"role": "user", "content": "Hello, how are you?"}]

def test_chat_non_json_request(flask_client):
    """Test response when payload is not JSON."""
    response = flask_client.post(
        "/chat",
        data="plain text data",
        headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Content-Type must be application/json" in data["error"]

def test_chat_malformed_json_request(flask_client):
    """Test response with malformed JSON string."""
    response = flask_client.post(
        "/chat",
        data="{'invalid_json': }",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Invalid or malformed JSON payload" in data["error"] or "Missing JSON payload" in data["error"]

def test_chat_json_parse_exception(flask_client):
    """Test response when get_json raises an exception (e.g., parsing error inside Flask)."""
    with patch("flask.Request.get_json", side_effect=Exception("Severe parse error")):
        response = flask_client.post(
            "/chat",
            json={"message": "test"}
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Invalid or malformed JSON payload" in data["error"]

def test_chat_missing_message_key(flask_client):
    """Test missing required 'message' key."""
    response = flask_client.post(
        "/chat",
        json={"different_key": "some value"}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Missing 'message' field in payload" in data["error"]

def test_chat_invalid_message_type(flask_client):
    """Test non-string value for the 'message' field."""
    response = flask_client.post(
        "/chat",
        json={"message": 12345}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "must be a string" in data["error"]

def test_chat_empty_message(flask_client):
    """Test message parameter that is empty."""
    response = flask_client.post(
        "/chat",
        json={"message": ""}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "cannot be empty or whitespace-only" in data["error"]

def test_chat_whitespace_only_message(flask_client):
    """Test message parameter containing only spaces and tabs."""
    response = flask_client.post(
        "/chat",
        json={"message": "   \n\t   "}
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "cannot be empty or whitespace-only" in data["error"]

def test_chat_openai_api_error(flask_client):
    """Test scenario where OpenAI API raises OpenAIError."""
    # Create realistic error mock
    openai_error = OpenAIError("API quota exceeded")

    with patch.object(client.chat.completions, "create", side_effect=openai_error) as mock_create:
        response = flask_client.post(
            "/chat",
            json={"message": "Can you hear me?"}
        )
        assert response.status_code == 502
        data = response.get_json()
        assert "error" in data
        assert "Failed to communicate with OpenAI service" in data["error"]
        assert "API quota exceeded" in data["details"]

def test_chat_unexpected_exception(flask_client):
    """Test generic unexpected internal exception handling."""
    with patch.object(client.chat.completions, "create", side_effect=RuntimeError("Database full!")) as mock_create:
        response = flask_client.post(
            "/chat",
            json={"message": "Hello?"}
        )
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "An unexpected error occurred internally" in data["error"]
