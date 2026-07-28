import math

def calculate_knowledge_value(metrics: dict) -> float:
    """
    Calculates a Knowledge Value Score (0.0 to 1.0) based on extraction metrics.
    """
    novelty = metrics.get('novelty', 0.5)
    reuse_potential = metrics.get('reuse_potential', 0.5)
    confidence = metrics.get('confidence', 0.8)

    # Simple weighted average for now
    raw_score = (novelty * 0.4) + (reuse_potential * 0.4) + (confidence * 0.2)
    return min(1.0, max(0.0, raw_score))
