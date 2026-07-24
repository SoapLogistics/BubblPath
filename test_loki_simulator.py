import pytest
from solomon_loki_simulator import LokiSimulator

def test_loki_simulator_basic():
    loki = LokiSimulator(initial_bankroll=1000.0)

    assert loki.place_paper_bet("E1", "Team A", odds=2.0, stake=100.0, expected_value=1.05)
    assert loki.current_bankroll == 900.0

    # Over bet
    assert not loki.place_paper_bet("E2", "Team B", odds=2.0, stake=2000.0, expected_value=1.05)

    assert loki.resolve_bet("E1", won=True, closing_line=1.9)
    # Win 100 at 2.0 odds -> payout 200 -> bankroll 1100
    assert loki.current_bankroll == 1100.0

    # ROI: Profit 100 / Staked 100 = 100%
    assert loki.get_roi() == 100.0

def test_loki_drawdown_and_drift():
    loki = LokiSimulator(initial_bankroll=1000.0)

    loki.place_paper_bet("E1", "Team A", odds=2.0, stake=500.0, expected_value=1.05)
    loki.resolve_bet("E1", won=False, closing_line=1.8)

    # Peak was 1000. Current is 500. Drawdown = 50%.
    assert loki.get_max_drawdown() == 50.0

    # Drift: Taken at 2.0 (50%). Close at 1.8 (55%). Edge = +5% (0.055...)
    drift = loki.calculate_model_drift()
    assert drift > 0.05 and drift < 0.06

if __name__ == "__main__":
    pytest.main(["-v", "test_loki_simulator.py"])
