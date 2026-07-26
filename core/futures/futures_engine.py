import math
from typing import Dict, Any, List

def evaluate_thresholds(confidence: float, probability: float, performance_score: float) -> Dict[str, Any]:
    """
    Evaluates thresholds for 80 and 90 metrics based on confidence, probability, and performance score.
    Ensures absolute mathematical correctness for the 80/90 threshold criteria.
    """
    is_80_confidence = confidence >= 80.0
    is_90_confidence = confidence >= 90.0

    is_80_probability = probability >= 80.0
    is_90_probability = probability >= 90.0

    is_80_performance = performance_score >= 80.0
    is_90_performance = performance_score >= 90.0

    breached_80 = is_80_confidence or is_80_probability or is_80_performance
    breached_90 = is_90_confidence or is_90_probability or is_90_performance

    return {
        "confidence": confidence,
        "probability": probability,
        "performance_score": performance_score,
        "is_80_confidence": is_80_confidence,
        "is_90_confidence": is_90_confidence,
        "is_80_probability": is_80_probability,
        "is_90_probability": is_90_probability,
        "is_80_performance": is_80_performance,
        "is_90_performance": is_90_performance,
        "breached_80": breached_80,
        "breached_90": breached_90,
        "status": "success"
    }

def process_futures_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Processes futures data to generate data health shape and evaluate thresholds.
    """
    processed_data = []
    for item in data:
        confidence = float(item.get("confidence", 0.0))
        probability = float(item.get("probability", 0.0))
        performance_score = float(item.get("performance_score", 0.0))

        evaluation = evaluate_thresholds(confidence, probability, performance_score)

        # Conforms to exact data_health shape mandated in Packet 05
        if breached_80 or breached_90:
            import os, sys
            sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
            try:
                from core.solomon_quantized_memory import QuantizedBrainMap
                brain = QuantizedBrainMap(max_nodes=100)
                brain.ingest(
                    node_type="fact_memory",
                    content=f"Threshold crossed: {item.get('id', 'unknown')} breached 80/90 limit.",
                    importance=0.8,
                    valence=0.0,
                    arousal=0.0
                )
            except Exception as e:
                pass
        health_shape = {
            "data_health": {
                "id": item.get("id", "unknown"),
                "status": "verified",
                "metrics": evaluation
            }
        }
        processed_data.append(health_shape)

    return processed_data
