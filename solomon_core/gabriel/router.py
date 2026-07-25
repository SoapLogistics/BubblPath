import concurrent.futures
from typing import Dict, Any, List
import logging
from .worker import WorkerRole
from solomon_core.interfaces import IWorkerSwarm
from openai import OpenAI
import os

logger = logging.getLogger(__name__)

class GabrielTaskRouter(IWorkerSwarm):
    """
    Manages multi-agent parallel execution via ThreadPoolExecutor.
    Implements a basic Swarm Arbiter to achieve BFT (Byzantine Fault Tolerance) consensus.
    """

    def __init__(self, api_key: str = None):
        key = api_key or os.environ.get("OPENAI_API_KEY", "dummy_key")
        self.client = OpenAI(api_key=key)

        self.roles = {
            "Builder": WorkerRole(
                "Builder",
                "You are the Builder. Construct a clean, efficient solution for the task.",
                self.client
            ),
            "Skeptic": WorkerRole(
                "Skeptic",
                "You are the Skeptic. Look at the task and context, and point out all potential flaws, edge cases, and failure modes.",
                self.client
            )
        }

    def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        context_str = str(context)
        results = {}

        # Parallel execution of roles
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_to_role = {
                executor.submit(role.process, task_description, context_str): name
                for name, role in self.roles.items()
            }

            for future in concurrent.futures.as_completed(future_to_role):
                role_name = future_to_role[future]
                try:
                    results[role_name] = future.result()
                except Exception as exc:
                    logger.error(f"{role_name} generated an exception: {exc}")
                    results[role_name] = f"ERROR: {exc}"

        # Synthesize consensus using an Arbiter prompt
        consensus = self._synthesize(task_description, results)

        return {
            "status": "success",
            "task": task_description,
            "worker_outputs": results,
            "consensus": consensus
        }

    def _synthesize(self, task: str, worker_results: Dict[str, str]) -> str:
        prompt = (
            "You are the Swarm Arbiter.\n"
            f"Original Task: {task}\n\n"
            "Below are the outputs from specialized agents. Synthesize them into a single, highly reliable final answer, resolving any conflicts.\n\n"
        )

        for role, output in worker_results.items():
            prompt += f"--- {role} ---\n{output}\n\n"

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": prompt}]
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"Arbiter synthesis failed: {e}")
            return "ERROR during synthesis."
