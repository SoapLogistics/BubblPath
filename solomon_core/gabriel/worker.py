import os
import json
from typing import Dict, Any, List
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

class WorkerRole:
    """Represents a specific role (e.g., Scout, Builder, Skeptic)."""
    def __init__(self, role_name: str, system_prompt: str, client: OpenAI):
        self.role_name = role_name
        self.system_prompt = system_prompt
        self.client = client

    def process(self, task: str, context: str) -> str:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Task:\n{task}\n\nContext:\n{context}"}
        ]

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Could be dynamically selected based on efficiency metrics
                messages=messages,
                temperature=0.3
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Worker {self.role_name} failed: {e}")
            return f"ERROR: {str(e)}"
