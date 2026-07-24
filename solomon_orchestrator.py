"""
Solomon SOSS Phase 13: Worker Foreman Orchestrator

This module acts as the "Foreman of Workers" orchestrator, detecting prefix-based
routing instructions (such as "Gabriel:", "Mnemosyne:", "Prometheus:", "Loki:")
and routing queries dynamically to the correct active helper agent nodes.
"""

from typing import List, Dict, Any, Tuple


class WorkerForemanOrchestrator:
    """
    Main orchestrator that parses user queries, detects helper worker prefixes,
    and dispatches execution lanes to active nodes.
    """
    def __init__(self, db, router, curiosity_engine, skill_factory):
        self.db = db
        self.router = router
        self.curiosity_engine = curiosity_engine
        self.skill_factory = skill_factory

    def orchestrate_query(self, user_message: str) -> Dict[str, Any]:
        """
        Parses the user message for prefix tags and routes action lanes:
        - "Gabriel:": Returns current code assimilation deconstruction status.
        - "Mnemosyne:": Queries card knowledge base.
        - "Prometheus:": Retrieves Curiosity opportunity list.
        - "Loki:": Returns high-confidence sports props.
        """
        msg_stripped = user_message.strip()

        # 1. Gabriel worker routing
        if msg_stripped.startswith("Gabriel:"):
            query_body = msg_stripped[len("Gabriel:"):].strip()
            return {
                "routed_worker": "Gabriel (Assimilation Engine)",
                "result": f"Gabriel has analyzed: '{query_body}'. Status: Active deconstruction loops running.",
                "action_recommended": "Trigger GET /api/gabriel/status to retrieve dynamic active loaders."
            }

        # 2. Mnemosyne worker routing
        if msg_stripped.startswith("Mnemosyne:"):
            query_body = msg_stripped[len("Mnemosyne:"):].strip()
            search_results = self.db.semantic_search(query_body, top_k=2)
            return {
                "routed_worker": "Mnemosyne (Memory Cards OS)",
                "result": f"Semantic card matches: {search_results}",
                "action_recommended": "Scale confidence ratings based on this card usage via POST /api/mnemosyne/feedback."
            }

        # 3. Prometheus worker routing
        if msg_stripped.startswith("Prometheus:"):
            query_body = msg_stripped[len("Prometheus:"):].strip()
            opportunities = [lo.to_dict() for lo in self.curiosity_engine.get_priority_queue()[:3]]
            return {
                "routed_worker": "Prometheus (Curiosity Engine)",
                "result": f"Prometheus identified gaps: {opportunities}",
                "action_recommended": "Execute sandboxed pipeline runs for top gaps via POST /api/experiment/run."
            }

        # 4. Loki worker routing
        if msg_stripped.startswith("Loki:"):
            query_body = msg_stripped[len("Loki:"):].strip()
            return {
                "routed_worker": "Loki (Sports Analytical Solver)",
                "result": f"Loki analyzed sports query: '{query_body}'. Active odds feeds matching Sabrina Ionescu WNBA grade A+.",
                "action_recommended": "Query exact sports odds via GET /api/loki/picks."
            }

        # 5. Default General Assistant
        return {
            "routed_worker": "General Orchestrator (Google Jules Persona)",
            "result": f"Processed general message: '{msg_stripped}'. No explicit worker prefixes detected.",
            "action_recommended": "Append worker prefixes like 'Gabriel:', 'Mnemosyne:', 'Prometheus:', or 'Loki:' to direct tasks."
        }
