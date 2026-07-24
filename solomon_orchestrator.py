"""
Solomon Perpetual Learning Machine
Phase 13: Worker Foreman Orchestrator (solomon_orchestrator.py)

This module implements the Worker Foreman Orchestrator which parses prefix tags
(such as Gabriel:, Mnemosyne:, Prometheus:, Loki:) to dynamically delegate
incoming user messages to specialized cognitive worker loops.
"""

from typing import Dict, Any

class WorkerForemanOrchestrator:
    """
    Parses prefix tags to dynamically route user actions or system messages
    to the correct specialized worker agents under the SOSS architecture.
    """

    def __init__(self, db_manager: Any = None):
        self.db = db_manager

    def delegate_message(self, message: str) -> Dict[str, Any]:
        """
        Parses prefix tags in the user message and delegates execution.
        """
        stripped = message.strip()

        # Check for Gabriel prefix
        if stripped.lower().startswith("gabriel:"):
            query_content = stripped[len("gabriel:"):].strip()
            return {
                "target_worker": "Gabriel (Assimilation & Synthesis Engine)",
                "action_query": query_content,
                "routing_status": "DELEGATED",
                "message_processed": f"Gabriel has taken ownership of: '{query_content}'"
            }

        # Check for Mnemosyne prefix
        elif stripped.lower().startswith("mnemosyne:"):
            query_content = stripped[len("mnemosyne:"):].strip()
            return {
                "target_worker": "Mnemosyne (Relational Memory Database)",
                "action_query": query_content,
                "routing_status": "DELEGATED",
                "message_processed": f"Mnemosyne is scanning memory cards for: '{query_content}'"
            }

        # Check for Prometheus prefix
        elif stripped.lower().startswith("prometheus:"):
            query_content = stripped[len("prometheus:"):].strip()
            return {
                "target_worker": "Prometheus (Curiosity Discovery Engine)",
                "action_query": query_content,
                "routing_status": "DELEGATED",
                "message_processed": f"Prometheus is checking cognitive gaps for: '{query_content}'"
            }

        # Check for Loki prefix
        elif stripped.lower().startswith("loki:"):
            query_content = stripped[len("loki:"):].strip()
            return {
                "target_worker": "Loki (Sports & Predictive Analytics)",
                "action_query": query_content,
                "routing_status": "DELEGATED",
                "message_processed": f"Loki is resolving bets/picks model for: '{query_content}'"
            }

        # No prefix fallback (Standard router / Albert Einstein's absurdity fallback)
        else:
            return {
                "target_worker": "Solomon Core Orchestrator",
                "action_query": stripped,
                "routing_status": "STANDARD_ROUTED",
                "message_processed": f"Standard cognitive routing activated for: '{stripped}'"
            }
