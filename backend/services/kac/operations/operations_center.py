from typing import Dict, Any

class OperationsCenter:
    """
    Aggregates metrics and status across all KAC engines (Missions 1-9) for the Joe University Dashboard.
    """
    def __init__(self, kac_manager):
        self.kac_manager = kac_manager

    def get_comprehensive_dashboard_state(self) -> Dict[str, Any]:
        queue = self.kac_manager.get_queue()
        stats = self.kac_manager.get_stats()

        # Calculate derived operations metrics
        active_jobs = [j for j in queue if j['status'] not in ['Completed', 'Failed']]
        completed_jobs = [j for j in queue if j['status'] == 'Completed']

        return {
            "health": {
                "status": "ONLINE",
                "queue_depth": len(active_jobs),
                "vault_capacity_used_pct": stats.get("vault_capacity", 0.0),
            },
            "learning_activity": {
                "current_book": active_jobs[0]['filename'] if active_jobs else "Idle",
                "books_completed": stats.get("books_processed", 0),
                "knowledge_yield": stats.get("knowledge_yield", 0.0)
            },
            "intelligence_inventory": {
                "knowledge_cards": stats.get("knowledge_cards_created", 0),
                "algorithms": stats.get("algorithms_extracted", 0),
                "predictions": stats.get("prediction_models_generated", 0),
                "consensus_nodes": stats.get("consensus_nodes_created", 0),
                "conflicts": stats.get("conflicts_detected", 0),
                "research_campaigns": stats.get("research_campaigns_created", 0),
            },
            "queue_preview": active_jobs[:5]
        }
