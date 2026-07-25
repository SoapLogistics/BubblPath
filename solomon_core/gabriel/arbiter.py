import os
import openai
import logging
from typing import Dict

logger = logging.getLogger("GabrielArbiter")

class SwarmArbiter:
    """
    The final consensus mechanism for the Gabriel Router.
    It takes the divergent outputs from the swarm workers and synthesizes them into a single truth.
    """
    def __init__(self):
        openai.api_key = os.environ.get("OPENAI_API_KEY")
        self.system_prompt = (
            "You are the Swarm Arbiter. Your job is to review the output of multiple specialized "
            "sub-agents. Synthesize their perspectives, resolve conflicts using logic, and produce "
            "a single, coherent, and highly accurate final answer."
        )

    def synthesize(self, task_prompt: str, swarm_outputs: Dict[str, str]) -> str:
        logger.info("Arbiter synthesizing swarm consensus...")

        compilation = f"Task: {task_prompt}\n\n"
        for role, output in swarm_outputs.items():
            if output != "FAILED":
                compilation += f"--- {role} Perspective ---\n{output}\n\n"

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Synthesize the following swarm responses:\n\n{compilation}"}
        ]

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.3, # Lower temp for logical consensus
                max_tokens=800
            )
            return response.choices[0].message["content"].strip()
        except Exception as e:
            logger.error(f"Arbiter API Error: {e}")
            return "Consensus Failed due to API Error."
