import os
import openai
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger("GabrielWorker")

class GabrielWorker:
    """
    A specific Agent persona operating within the Gabriel Swarm.
    Uses the OpenAI SDK to generate domain-specific outputs.
    """
    def __init__(self, role_name: str, system_prompt: str):
        self.role_name = role_name
        self.system_prompt = system_prompt
        openai.api_key = os.environ.get("OPENAI_API_KEY")

    def generate(self, task_prompt: str, context: Optional[List[Dict[str, Any]]] = None) -> str:
        logger.info(f"Worker '{self.role_name}' generating response...")
        messages = [{"role": "system", "content": self.system_prompt}]

        if context:
            context_str = "\n".join([str(c) for c in context])
            messages.append({"role": "system", "content": f"Context provided:\n{context_str}"})

        messages.append({"role": "user", "content": task_prompt})

        try:
            # We wrap this in try/except so a single worker failing doesn't crash the swarm
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message["content"].strip()
        except Exception as e:
            logger.error(f"Worker '{self.role_name}' API Error: {e}")
            return "FAILED"
