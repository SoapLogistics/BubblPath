import datetime
import random
from typing import Dict, Any, List

class LokiSimulator:
    """
    Phase 3A: Safe Simulation and Telemetry Engine.
    Tracks virtual bankroll, ROI, and Model EV vs Closing Line drift.
    NEVER accesses real money APIs.
    """
    def __init__(self, initial_bankroll: float = 10000.0):
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.max_bankroll = initial_bankroll
        self.bet_history: List[Dict[str, Any]] = []

    def place_paper_bet(self, event_id: str, selection: str, odds: float, stake: float, expected_value: float) -> bool:
        if stake > self.current_bankroll:
            return False

        bet = {
            "event_id": event_id,
            "selection": selection,
            "odds": odds,
            "stake": stake,
            "expected_value": expected_value,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "status": "pending",
            "closing_line": None
        }
        self.current_bankroll -= stake
        self.bet_history.append(bet)
        return True

    def resolve_bet(self, event_id: str, won: bool, closing_line: float = None) -> bool:
        for bet in self.bet_history:
            if bet["event_id"] == event_id and bet["status"] == "pending":
                bet["status"] = "won" if won else "lost"
                bet["closing_line"] = closing_line

                if won:
                    # Decimal odds payout = stake * odds
                    payout = bet["stake"] * bet["odds"]
                    self.current_bankroll += payout

                if self.current_bankroll > self.max_bankroll:
                    self.max_bankroll = self.current_bankroll

                return True
        return False

    def get_roi(self) -> float:
        total_staked = sum(b["stake"] for b in self.bet_history if b["status"] != "pending")
        if total_staked == 0:
            return 0.0
        profit = self.current_bankroll - self.initial_bankroll
        return round((profit / total_staked) * 100.0, 2)

    def get_max_drawdown(self) -> float:
        if self.max_bankroll == 0:
            return 0.0
        drawdown = self.max_bankroll - self.current_bankroll
        return round((drawdown / self.max_bankroll) * 100.0, 2)

    def calculate_model_drift(self) -> float:
        """
        Compares predicted EV to the actual EV dictated by the closing line.
        A positive number means the model beat the closing line.
        """
        drift_scores = []
        for bet in self.bet_history:
            if bet["closing_line"] is not None:
                # If we took it at 2.0 (50% implied) but closing is 1.8 (55% implied),
                # we beat the closing line by capturing +5% edge.
                implied_taken = 1.0 / bet["odds"]
                implied_close = 1.0 / bet["closing_line"]
                clv_edge = implied_close - implied_taken
                drift_scores.append(clv_edge)

        if not drift_scores:
            return 0.0
        return sum(drift_scores) / len(drift_scores)

    def calculate_bankruptcy_probability(self, simulations: int = 1000) -> float:
        """
        Monte Carlo simulation to determine chance of ruining the bankroll.
        Uses historical win rate and average odds.
        """
        resolved_bets = [b for b in self.bet_history if b["status"] in ("won", "lost")]
        if not resolved_bets:
            return 0.0

        wins = sum(1 for b in resolved_bets if b["status"] == "won")
        win_rate = wins / len(resolved_bets)
        avg_odds = sum(b["odds"] for b in resolved_bets) / len(resolved_bets)
        avg_stake = sum(b["stake"] for b in resolved_bets) / len(resolved_bets)

        bankruptcies = 0
        for _ in range(simulations):
            sim_bankroll = self.current_bankroll
            for _ in range(100): # Sim 100 future bets
                if sim_bankroll <= 0:
                    bankruptcies += 1
                    break

                sim_bankroll -= avg_stake
                if random.random() < win_rate:
                    sim_bankroll += avg_stake * avg_odds

        return round((bankruptcies / simulations) * 100.0, 2)
