import datetime
import uuid
from typing import List, Dict, Any, Tuple
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.planner.models import TaskPlan

class DynamicPlanner:
    def __init__(self, repository: CardRepository):
        self.repository = repository

    def draft_plan(self, task_id: str, objective: str) -> TaskPlan:
        """
        Formulates a step-by-step TaskPlan by querying Mnemosyne Memory Cards.
        Identifies historical failures and pre-emptively injects safeguarding steps to prevent regressions.
        """
        now_str = datetime.datetime.now(datetime.UTC).isoformat()
        plan_id = f"PLN-{uuid.uuid4().hex[:8].upper()}"

        # 1. Search memory database for relevant prior experiences
        memories = self.repository.search(objective)

        # Only use APPROVED or ACTIVE cards as trusted context
        trusted_memories = [
            m for m in memories
            if m["card"]["status"] in ("APPROVED", "ACTIVE")
        ]

        retrieved_ids = [m["card_id"] for m in trusted_memories]

        # 2. Extract failures and repairs to synthesize safeguards
        failures = [m for m in trusted_memories if m["card_type"] == "FAILURE"]
        repairs = [m for m in trusted_memories if m["card_type"] == "REPAIR"]

        injected_safeguards = []
        pre_emptive_steps = []

        # Synthesize safeguards from historical repairs
        for r_match in repairs:
            card_data = r_match["card"]
            safeguard_record = {
                "safeguard_id": f"SG-{uuid.uuid4().hex[:6].upper()}",
                "triggered_by_repair": card_data["card_id"],
                "remediation_instruction": card_data["body"],
                "reason": card_data["summary"]
            }
            injected_safeguards.append(safeguard_record)

            # Formulate the explicit pre-emptive step action
            pre_emptive_steps.append({
                "action": f"PRE-EMPTIVE SAFEGUARD: Execute environment recovery: {card_data['body']}",
                "tool": "bash_run",
                "expected_outcome": "Environment cleared of previous conflicting processes or state biases."
            })

        # 3. Formulate the standard baseline steps for the objective
        base_steps = []

        # Determine steps based on task keywords
        obj_lower = objective.lower()
        if "openhands" in obj_lower or "deploy" in obj_lower:
            base_steps = [
                {
                    "action": "Check port availability and system resources.",
                    "tool": "bash_run",
                    "expected_outcome": "System ready for container launch."
                },
                {
                    "action": "Spin up target Docker container as standard playbook parameters describe.",
                    "tool": "openhands_run",
                    "expected_outcome": "Container up and listening."
                },
                {
                    "action": "Execute system test suites to verify integration health.",
                    "tool": "bash_run",
                    "expected_outcome": "All test assertions passing."
                }
            ]
        elif "absorption" in obj_lower or "pypi" in obj_lower:
            base_steps = [
                {
                    "action": "Search npm or PyPI for popular packages.",
                    "tool": "github_search_and_clone",
                    "expected_outcome": "Source files cloned locally."
                },
                {
                    "action": "Scan source code for suspicious execution payloads.",
                    "tool": "bash_run",
                    "expected_outcome": "No eval/exec injection patterns found."
                },
                {
                    "action": "Integrate and mount wrappers.",
                    "tool": "pypi_npm_install",
                    "expected_outcome": "New capabilities integrated."
                }
            ]
        else:
            # Generic fallback steps
            base_steps = [
                {
                    "action": f"Formulate and execute discrete actions for: {objective}",
                    "tool": "bash_run",
                    "expected_outcome": "Objective satisfied."
                }
            ]

        # 4. Inject pre-emptive steps *before* the execution actions
        final_steps = []
        step_counter = 1

        # Insert pre-emptive actions first to guarantee self-healing setup
        for p_step in pre_emptive_steps:
            p_step["step_number"] = step_counter
            final_steps.append(p_step)
            step_counter += 1

        # Append remaining baseline steps
        for b_step in base_steps:
            b_step["step_number"] = step_counter
            final_steps.append(b_step)
            step_counter += 1

        return TaskPlan(
            plan_id=plan_id,
            task_id=task_id,
            objective=objective,
            steps=final_steps,
            retrieved_memory_card_ids=retrieved_ids,
            injected_safeguards=injected_safeguards,
            status="DRAFT",
            created_at=now_str,
            updated_at=now_str
        )
