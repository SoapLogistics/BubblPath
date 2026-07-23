import os
import json
import importlib
from unittest.mock import MagicMock, patch
import pytest
import openai
from openai import (
    APITimeoutError,
    RateLimitError,
    AuthenticationError,
    APIConnectionError,
    APIError,
)

# Ensure the mock request and response objects are available
mock_req = MagicMock()
mock_resp = MagicMock()
mock_resp.status_code = 400
mock_resp.headers = {}


@pytest.fixture
def app_client():
    # Force import app with test configuration
    import app as application
    application.app.config["TESTING"] = True
    with application.app.test_client() as client:
        yield client


def test_app_init_with_key(monkeypatch):
    """
    Test app.py initialization when the OPENAI_API_KEY is configured,
    ensuring the log configuration branch is fully executed.
    """
    import app as application
    monkeypatch.setenv("OPENAI_API_KEY", "sk-reloadkey123")
    importlib.reload(application)
    assert application.api_key == "sk-reloadkey123"


def test_health_check_configured(app_client, monkeypatch):
    """
    Test the health check endpoint when the OPENAI_API_KEY is configured.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    response = app_client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["openai_configured"] is True
    assert "uptime_seconds" in data
    assert "timestamp" in data
    assert data["service"] == "chatgpt-flask-app"


def test_health_check_degraded(app_client, monkeypatch):
    """
    Test the health check endpoint when the OPENAI_API_KEY is NOT configured.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = app_client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "degraded"
    assert data["openai_configured"] is False


def test_chat_success(app_client, monkeypatch):
    """
    Test successful chat completion processing and validation.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")

    # Mock response object matching modern openai SDK structure
    mock_choice = MagicMock()
    mock_choice.message.content = "This is a mocked response."
    mock_openai_response = MagicMock()
    mock_openai_response.choices = [mock_choice]

    import app as application
    with patch.object(application.client.chat.completions, "create", return_value=mock_openai_response) as mock_create:
        response = app_client.post(
            "/chat",
            data=json.dumps({"message": "Hello Solomon!"}),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["reply"] == "This is a mocked response."
        mock_create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello Solomon!"}],
            timeout=30.0,
        )


def test_chat_invalid_json(app_client, monkeypatch):
    """
    Test payload validation with malformed or non-JSON payloads.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    response = app_client.post(
        "/chat",
        data="Not a JSON string",
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Malformed request" in data["error"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"message": ""},
        {"message": "   "},
        {"message": 123},
        {"message": None},
        {"msg": "Wrong key"},
    ],
)
def test_chat_payload_validation_failures(app_client, payload, monkeypatch):
    """
    Test validation failures for various malformed or missing payload options.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    response = app_client.post(
        "/chat",
        data=json.dumps(payload),
        content_type="application/json",
    )
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Invalid payload" in data["error"]


def test_chat_missing_api_key_configuration(app_client, monkeypatch):
    """
    Test that endpoints gracefully report 500 when OPENAI_API_KEY is not defined.
    """
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    response = app_client.post(
        "/chat",
        data=json.dumps({"message": "Should fail configuration check"}),
        content_type="application/json",
    )
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "OpenAI API Key is missing on the server" in data["error"]


def test_chat_timeout_exception(app_client, monkeypatch):
    """
    Test OpenAI request APITimeoutError handling.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    import app as application

    raised_err = APITimeoutError(request=mock_req)
    with patch.object(application.client.chat.completions, "create", side_effect=raised_err):
        response = app_client.post(
            "/chat",
            data=json.dumps({"message": "Trigger timeout"}),
            content_type="application/json",
        )
        assert response.status_code == 504
        data = response.get_json()
        assert "timed out" in data["error"]


def test_chat_ratelimit_exception(app_client, monkeypatch):
    """
    Test OpenAI request RateLimitError handling.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    import app as application

    raised_err = RateLimitError(message="Rate limit exceeded", response=mock_resp, body=None)
    with patch.object(application.client.chat.completions, "create", side_effect=raised_err):
        response = app_client.post(
            "/chat",
            data=json.dumps({"message": "Trigger rate limit"}),
            content_type="application/json",
        )
        assert response.status_code == 429
        data = response.get_json()
        assert "rate limit exceeded" in data["error"]


def test_chat_auth_exception(app_client, monkeypatch):
    """
    Test OpenAI request AuthenticationError handling.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    import app as application

    raised_err = AuthenticationError(message="Invalid API Key", response=mock_resp, body=None)
    with patch.object(application.client.chat.completions, "create", side_effect=raised_err):
        response = app_client.post(
            "/chat",
            data=json.dumps({"message": "Trigger auth failure"}),
            content_type="application/json",
        )
        assert response.status_code == 500
        data = response.get_json()
        assert "authentication failed" in data["error"]


def test_chat_connection_exception(app_client, monkeypatch):
    """
    Test OpenAI request APIConnectionError handling.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    import app as application

    raised_err = APIConnectionError(request=mock_req)
    with patch.object(application.client.chat.completions, "create", side_effect=raised_err):
        response = app_client.post(
            "/chat",
            data=json.dumps({"message": "Trigger connection error"}),
            content_type="application/json",
        )
        assert response.status_code == 502
        data = response.get_json()
        assert "connect to OpenAI API" in data["error"]


def test_chat_api_exception(app_client, monkeypatch):
    """
    Test OpenAI request general APIError handling.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    import app as application

    raised_err = APIError(message="Internal OpenAI Server Error", request=mock_req, body=None)
    with patch.object(application.client.chat.completions, "create", side_effect=raised_err):
        response = app_client.post(
            "/chat",
            data=json.dumps({"message": "Trigger API error"}),
            content_type="application/json",
        )
        assert response.status_code == 502
        data = response.get_json()
        assert "OpenAI API error: Internal OpenAI Server Error" in data["error"]


def test_chat_unexpected_exception(app_client, monkeypatch):
    """
    Test that general unexpected exceptions inside the endpoint are caught cleanly.
    """
    monkeypatch.setenv("OPENAI_API_KEY", "sk-testkey123")
    import app as application

    raised_err = RuntimeError("Unexpected failure")
    with patch.object(application.client.chat.completions, "create", side_effect=raised_err):
        response = app_client.post(
            "/chat",
            data=json.dumps({"message": "Trigger unexpected exception"}),
            content_type="application/json",
        )
        assert response.status_code == 500
        data = response.get_json()
        assert "unexpected error occurred" in data["error"]
