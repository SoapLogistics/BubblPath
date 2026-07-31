import pytest
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from adapters.mock_ai_agent import MockAIAgentAdapter
from adapters.mock_git_adapter import MockGitAdapter

@pytest.mark.asyncio
async def test_mock_ai_agent():
    adapter = MockAIAgentAdapter()
    response = await adapter.chat([{"role": "user", "content": "Hello"}])
    assert "mock response" in response.lower()

    review = await adapter.review_code("def foo(): pass")
    assert "Mock Code Review" in review

def test_mock_git_adapter():
    adapter = MockGitAdapter()
    commits = adapter.get_commits("main")
    assert len(commits) == 2
    assert commits[0]["hash"] == "mock-hash-1"

    diff = adapter.diff("base", "head")
    assert "--- a/mock.txt" in diff
