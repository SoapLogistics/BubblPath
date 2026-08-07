from services.solomon_futures_engine import Candidate, FuturesEngine, WilsonInterval


def test_wilson_interval():
    lower, upper = WilsonInterval.calculate(900, 1000, 0.95)
    assert 0.87 < lower < 0.89
    assert 0.91 < upper < 0.93

def test_candidate_gate_a_qualification():
    engine = FuturesEngine()

    # Valid candidate
    valid_c = Candidate(
        candidate_id="c1", event_id="e1", domain="sports", source_name="src",
        source_record_id="rec1", source_mode="SHADOW", source_timestamp="2026-07-26",
        ingested_at="2026-07-26", pre_simulation_confidence=92.0, data_quality_score=95.0,
        features={"win_prob": 0.92}
    )
    qual = engine._evaluate_gate_a(valid_c)
    assert qual.pre_simulation_qualified is True

    # Invalid confidence
    invalid_c = Candidate(
        candidate_id="c2", event_id="e2", domain="sports", source_name="src",
        source_record_id="rec2", source_mode="SHADOW", source_timestamp="2026-07-26",
        ingested_at="2026-07-26", pre_simulation_confidence=85.0, data_quality_score=95.0,
        features={"win_prob": 0.85}
    )
    qual2 = engine._evaluate_gate_a(invalid_c)
    assert qual2.pre_simulation_qualified is False
    assert "PRE_SIMULATION_SCORE_BELOW_90" in qual2.reasons

def test_full_simulation_gate_b_confirmation():
    # We set seed so that out of 1000 trials, the success count hits roughly the probability
    engine = FuturesEngine()
    c = Candidate(
        candidate_id="c3", event_id="e3", domain="sports", source_name="src",
        source_record_id="rec3", source_mode="SHADOW", source_timestamp="2026-07-26",
        ingested_at="2026-07-26", pre_simulation_confidence=95.0, data_quality_score=95.0,
        features={"win_prob": 0.95} # High probability ensuring Wilson lower bound > 0.90
    )

    result = engine.process_candidate(c, seed=42)
    assert result.status == "CONFIRMED_90_PLUS"
    assert result.simulation["simulation_probability"] >= 0.90
    assert result.simulation["interval_lower"] >= 0.90
