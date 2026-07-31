from typing import List, Dict, Any
import sys
import os

# Add parent dir to path to import contracts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contracts.ai_agent_adapter import AIAgentAdapter

class MockAIAgentAdapter(AIAgentAdapter):
    async def chat(self, messages: List[Dict[str, Any]]) -> str:
        return "This is a mock response from the AI Agent."

    async def review_code(self, code: str) -> str:
        return "Mock Code Review:\n- Looks good!\n- No issues found."
