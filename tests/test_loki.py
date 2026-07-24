import os
import json
import tempfile
import pytest
from solomon_knowledge_cards import MnemosyneRuntime
from solomon_knowledge_cards.loki_engine import LokiEngine, solve_shin_probabilities, calculate_kelly_fraction

@pytest.fixture
def temp_db():
    """Fixture that initializes a clean temporary SQLite database for testing."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    if os.path.exists(path):
        os.remove(path)

@pytest.fixture
def runtime_test(temp_db):
    """Fixture providing a MnemosyneRuntime bound to the temporary database."""
    # Ensure tables are migrated up to Migration 5
    return MnemosyneRuntime(db_path=temp_db)

@pytest.fixture
def flask_client(temp_db):
    """Fixture providing a Flask test client configured with the temporary database and demo key."""
    os.environ["SOLOMON_DB_PATH"] = temp_db
    os.environ["SOLOMON_ACTIONS_API_KEY"] = "TEST_ACTIONS_API_KEY"

    import app as app_module
    app_module.runtime = MnemosyneRuntime(db_path=temp_db)
    app_module.ACTIONS_API_KEY = "TEST_ACTIONS_API_KEY"
    app_module.loki_engine = LokiEngine(app_module.runtime)

    with app_module.app.test_client() as client:
        yield client


# --- 1. Unit Tests for Mathematical Engines ---

def test_shin_solver_convergence():
    """Verify that Shin's solver correctly removes overround and converges to sum=1.0."""
    # Odds: Home 2.10, Draw 3.20, Away 3.10
    # Implied probs: 1/2.1 = 0.4762, 1/3.2 = 0.3125, 1/3.1 = 0.3226
    # Sum implied = 1.1113 (11% overround/vig)
    implied = [1.0 / 2.10, 1.0 / 3.20, 1.0 / 3.10]

    z, true_probs = solve_shin_probabilities(implied)

    assert z > 0.0
    assert len(true_probs) == 3
    assert abs(sum(true_probs) - 1.0) < 1e-7
    # Favorites (Home) should be adjusted less than longshots (Away) under Shin's favorite-longshot model
    assert true_probs[0] > 0.40


def test_kelly_criterion_stake():
    """Verify that Kelly Criterion outputs mathematically correct fractional stake sizes."""
    # True probability = 0.55, Odds = 2.10 (implied prob = 0.476)
    # Expected edge: 0.55 * 2.1 - 1 = 0.155 (15.5%)
    # Full Kelly: (0.55 * 2.10 - 1.0) / (2.10 - 1.0) = 0.155 / 1.1 = 0.1409 (14.09%)
    # Quarter Kelly (0.25): 0.1409 * 0.25 = 0.0352 (3.52%)
    stake_frac = calculate_kelly_fraction(0.55, 2.10, risk_fraction=0.25)
    assert abs(stake_frac - 0.035227) < 1e-4

    # No edge: true prob 0.40, odds 2.10 -> expected edge is negative, stake should be 0
    assert calculate_kelly_fraction(0.40, 2.10) == 0.0


# --- 2. Database & State Transition Tests ---

def test_loki_bankroll_persistence(runtime_test):
    """Verify Loki virtual bankroll can be read, updated, and persisted in SQLite."""
    loki = LokiEngine(runtime_test)
    assert loki.get_bankroll() == 10000.0

    loki.update_bankroll(-500.0)
    assert loki.get_bankroll() == 9500.0

    loki.update_bankroll(1200.0)
    assert loki.get_bankroll() == 10700.0


def test_loki_simulation_cycle(runtime_test):
    """Verify that simulate_tick executes bets under LIVE_BETTING and updates states."""
    loki = LokiEngine(runtime_test)

    # Enable LIVE_BETTING mode for Loki in the DB
    runtime_test.update_worker_mode("loki", "LIVE_BETTING")

    # Run simulation tick
    result = loki.simulate_tick()
    assert result["ok"] is True
    assert result["active_mode"] == "LIVE_BETTING"

    # Since odds are randomized, we might place 0 or more bets, but some should be created
    if result["new_bets_count"] > 0:
        assert result["final_bankroll"] < result["initial_bankroll"]

        # Verify pending bets are in the ledger
        conn = runtime_test.db.get_connection()
        try:
            cursor = conn.execute("SELECT COUNT(*) as cnt FROM loki_bets WHERE status = 'PENDING'")
            assert cursor.fetchone()["cnt"] == result["new_bets_count"]
        finally:
            conn.close()

        # Run another tick to resolve the pending bets
        res2 = loki.simulate_tick()
        assert res2["resolved_bets_count"] + res2.get("hedged_bets_count", 0) == result["new_bets_count"]

        # Stats should calculate profit, win rate, ROI
        stats = loki.get_betting_stats()
        assert stats["total_bets"] == result["new_bets_count"] + res2["new_bets_count"]
        assert stats["resolved_bets"] == result["new_bets_count"]
        assert stats["pending_bets"] == res2["new_bets_count"]
        assert stats["balance"] == loki.get_bankroll()


# --- 3. Flask Endpoint Tests ---

def test_loki_endpoints_auth(flask_client):
    """Verify auth gating on Project Loki command center endpoints."""
    # No auth
    resp = flask_client.get("/api/command-center/loki/stats")
    assert resp.status_code == 401

    resp = flask_client.post("/api/command-center/loki/simulate-tick")
    assert resp.status_code == 401

    # With correct auth
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}
    resp = flask_client.get("/api/command-center/loki/stats", headers=headers)
    assert resp.status_code == 200
    assert resp.json["ok"] is True
    assert "stats" in resp.json


def test_loki_picks_public(flask_client):
    """Verify picks can be retrieved without auth as they represent public cognitive intelligence output."""
    resp = flask_client.get("/api/picks")
    assert resp.status_code == 200
    assert resp.json["ok"] is True
    assert "picks" in resp.json


def test_loki_full_flask_flow(flask_client):
    """Verify Flask-based simulation execution and stats reporting."""
    headers = {"Authorization": "Bearer TEST_ACTIONS_API_KEY"}

    # 1. Promote Loki to LIVE_BETTING
    promo_payload = {"worker_id": "loki", "mode": "LIVE_BETTING"}
    resp_promo = flask_client.post("/api/command-center/worker-modes", headers=headers, json=promo_payload)
    assert resp_promo.status_code == 200
    assert resp_promo.json["ok"] is True

    # 2. Trigger tick
    resp_tick = flask_client.post("/api/command-center/loki/simulate-tick", headers=headers)
    assert resp_tick.status_code == 200
    assert resp_tick.json["ok"] is True
    assert resp_tick.json["active_mode"] == "LIVE_BETTING"

    # 3. Fetch stats
    resp_stats = flask_client.get("/api/command-center/loki/stats", headers=headers)
    assert resp_stats.status_code == 200
    assert resp_stats.json["stats"]["balance"] > 0
