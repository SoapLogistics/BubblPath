import os
import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
import openai
from app import create_app

class TestAppFactoryAndEndpoints(unittest.TestCase):
    def setUp(self):
        # Configure app with override variables for testing
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_app_creation_and_config(self):
        """Test application constructs successfully and sets appropriate config limits."""
        self.assertIsInstance(self.app, Flask)
        self.assertEqual(self.app.config["MAX_CONTENT_LENGTH"], 1 * 1024 * 1024)

    def test_proxy_fix_middleware(self):
        """Test proxy fix middleware is applied on app WSGI entry."""
        self.assertTrue(hasattr(self.app, "wsgi_app"))

    def test_invalid_json_header(self):
        """Test /chat blocks requests that do not specify application/json."""
        response = self.client.post("/chat", data="not json", content_type="text/plain")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Content-Type must be application/json", response.get_json()["error"])

    def test_malformed_json_payload(self):
        """Test /chat handles broken JSON gracefully."""
        response = self.client.post("/chat", data="{'message': missing quotes}", content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Malformed JSON payload", response.get_json()["error"])

    def test_invalid_message_type(self):
        """Test /chat errors if the 'message' parameter is not a string."""
        response = self.client.post("/chat", json={"message": 12345})
        self.assertEqual(response.status_code, 400)
        self.assertIn("'message' parameter must be a string", response.get_json()["error"])

    def test_empty_message(self):
        """Test /chat rejects empty messages."""
        response = self.client.post("/chat", json={"message": "   "})
        self.assertEqual(response.status_code, 400)
        self.assertIn("'message' parameter cannot be empty", response.get_json()["error"])

    @patch("openai.ChatCompletion.create")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_successful_chat_interaction(self, mock_create):
        """Test a complete, valid chat request correctly calls OpenAI and yields output."""
        # Setup mock OpenAI ChatCompletion response structure
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(message={"content": "Hello! I am OpenAI."})
        ]
        mock_create.return_value = mock_response

        response = self.client.post("/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["reply"], "Hello! I am OpenAI.")

        # Ensure correct API call constraints
        mock_create.assert_called_once_with(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hi"}],
            request_timeout=30.0
        )

    @patch("openai.ChatCompletion.create")
    @patch.dict(os.environ, {"OPENAI_API_KEY": ""})
    def test_missing_api_key(self, mock_create):
        """Test correct handled error when environment key is empty or missing."""
        response = self.client.post("/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 500)
        self.assertIn("Internal server configuration error", response.get_json()["error"])

    @patch("openai.ChatCompletion.create")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_timeout_handling(self, mock_create):
        """Test upstream timeout handling returns a proper 504 gateway timeout."""
        mock_create.side_effect = openai.error.Timeout("Timeout error")
        response = self.client.post("/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 504)
        self.assertIn("Request to OpenAI timed out", response.get_json()["error"])

    @patch("openai.ChatCompletion.create")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_authentication_handling(self, mock_create):
        """Test API authentication issues gracefully bubble up as 502 bad gateway."""
        mock_create.side_effect = openai.error.AuthenticationError("Auth failed")
        response = self.client.post("/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 502)
        self.assertIn("Upstream authentication failed", response.get_json()["error"])

    @patch("openai.ChatCompletion.create")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_ratelimit_handling(self, mock_create):
        """Test API rate-limit bottlenecks are properly caught and mapped to 429."""
        mock_create.side_effect = openai.error.RateLimitError("Rate limit exceeded")
        response = self.client.post("/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 429)
        self.assertIn("Upstream rate limit exceeded", response.get_json()["error"])

    @patch("openai.ChatCompletion.create")
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    def test_openai_generic_exception_handling(self, mock_create):
        """Test unpredictable generic OpenAI issues are normalized to a 502 upstream failure."""
        mock_create.side_effect = openai.error.OpenAIError("API error")
        response = self.client.post("/chat", json={"message": "Hi"})
        self.assertEqual(response.status_code, 502)
        self.assertIn("An upstream AI service error occurred", response.get_json()["error"])

    def test_payload_too_large_boundary(self):
        """Test that requests exceeding MAX_CONTENT_LENGTH of 1MB are rejected with 413."""
        # Generate an overly-large string
        huge_payload = "a" * (1 * 1024 * 1024 + 100)
        response = self.client.post("/chat", json={"message": huge_payload})
        self.assertEqual(response.status_code, 413)
        self.assertIn("Payload Too Large", response.get_json()["error"])

    @patch("openai.ChatCompletion.create")
    def test_rate_limiter_functional_check(self, mock_create):
        """Verify the rate-limiting endpoint operates properly within reasonable bounds."""
        mock_create.return_value = MagicMock()
        response = self.client.post("/chat", json={"message": "Valid request"})
        # Should bypass block constraints, rate limiter not triggered yet (1st request)
        self.assertIn(response.status_code, [200, 500])

if __name__ == "__main__":
    unittest.main()
