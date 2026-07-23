"""
Solomon Perpetual Learning Machine
Autonomous Hot-Swapping Model Router

This module implements real-time semantic query routing.
By evaluating semantic proximity and card confidence scores,
it hot-swaps execution between a High-Precision Target Model
and an Ultra-Light Quantized model, maximizing RAM efficiency.
"""
from typing import Dict, Any, Tuple
from solomon_mnemosyne_db import SolomonMnemosyneDB

class ModelRouter:
    """
    Dynamically routes LLM queries based on semantic proximity and confidence metrics
    to optimize memory footprints, generation latencies, and execution costs.
    Supports a feedback-driven self-healing strategy.
    """
    TARGET_MODEL = {'name': 'High-Precision FP16/INT8 Target Model (70B/32B)', 'precision': 'FP16/INT8', 'ram_footprint_gb': 14.0, 'base_latency_ms': 55.0, 'token_cost_multiplier': 1.0}
    QUANTIZED_MODEL = {'name': 'Ultra-Light Quantized INT4/Ternary Model (2B/1.58b)', 'precision': 'INT4/Ternary', 'ram_footprint_gb': 0.7, 'base_latency_ms': 12.0, 'token_cost_multiplier': 0.05}

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def route_query(self, query: str, threshold: float=0.15) -> Dict[str, Any]:
        """
        Routes the query semantically, factoring SOK card confidence ratings.

        Effective Threshold:
            effective_threshold = threshold * confidence
            (Bounded between 0.5 * threshold and 1.5 * threshold)

        If similarity >= effective_threshold, route to Target Model.
        Else, route to Quantized Model.
        """
        search_results = self.db.semantic_search(query, top_k=1)
        max_similarity = 0.0
        best_match_card = None
        card_confidence = 1.0
        if search_results:
            best_match_card = search_results[0]
            max_similarity = best_match_card['similarity']
            card_confidence = best_match_card.get('confidence', 1.0)
        confidence_factor = max(0.5, min(1.5, card_confidence))
        effective_threshold = threshold * confidence_factor
        if max_similarity >= effective_threshold:
            routed_model = self.TARGET_MODEL
            decision_reason = f"Query matched SOK card '{best_match_card['card_id']}' with a similarity of {max_similarity:.4f} >= effective threshold {effective_threshold:.4f} (base threshold: {threshold:.4f}, confidence: {card_confidence:.4f}). High-precision validation is required."
            model_type = 'high_precision'
        else:
            routed_model = self.QUANTIZED_MODEL
            best_match_id = best_match_card['card_id'] if best_match_card else 'None'
            decision_reason = f'No close SOK card matches found (best similarity: {max_similarity:.4f} < effective threshold {effective_threshold:.4f} based on base threshold: {threshold:.4f}, confidence: {card_confidence:.4f}). Routing query to ultra-light ternary model for maximum RAM efficiency.'
            model_type = 'ultra_light'
        vram_saved_gb = self.TARGET_MODEL['ram_footprint_gb'] - routed_model['ram_footprint_gb']
        latency_reduction_percent = round((self.TARGET_MODEL['base_latency_ms'] - routed_model['base_latency_ms']) / self.TARGET_MODEL['base_latency_ms'] * 100.0, 1)
        cost_savings_percent = round((1.0 - routed_model['token_cost_multiplier'] / self.TARGET_MODEL['token_cost_multiplier']) * 100.0, 1)
        return {'query': query, 'base_threshold': threshold, 'effective_threshold': round(effective_threshold, 4), 'best_match_card_id': best_match_card['card_id'] if best_match_card else None, 'best_match_similarity': max_similarity, 'best_match_confidence': round(card_confidence, 4), 'routed_model': routed_model['name'], 'model_type': model_type, 'precision_allocated': routed_model['precision'], 'active_ram_footprint_gb': routed_model['ram_footprint_gb'], 'estimated_latency_ms': routed_model['base_latency_ms'], 'decision_reason': decision_reason, 'resource_impact': {'vram_saved_gb': round(max(0.0, vram_saved_gb), 2), 'latency_reduction_percent': max(0.0, latency_reduction_percent), 'cost_savings_percent': cost_savings_percent}}

    def injected_telemetry_probe(self):
        return 'ast_injection_active_soss'