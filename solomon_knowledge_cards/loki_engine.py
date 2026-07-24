import os
import math
import random
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("solomon_loki_engine")

MOCK_TEAMS = {
    "Premier League": [
        ("Arsenal", "Manchester City"),
        ("Liverpool", "Chelsea"),
        ("Manchester United", "Tottenham"),
        ("Aston Villa", "Newcastle United")
    ],
    "NBA": [
        ("Los Angeles Lakers", "Boston Celtics"),
        ("Golden State Warriors", "Phoenix Suns"),
        ("Milwaukee Bucks", "Miami Heat"),
        ("Denver Nuggets", "Dallas Mavericks")
    ],
    "NFL": [
        ("Kansas City Chiefs", "San Francisco 49ers"),
        ("Philadelphia Eagles", "Dallas Cowboys"),
        ("Buffalo Bills", "Miami Dolphins"),
        ("Baltimore Ravens", "Cincinnati Bengals")
    ]
}

def solve_shin_probabilities(implied_probs: List[float], max_iter: int = 100, tol: float = 1e-9) -> Tuple[float, List[float]]:
    """
    Solves Shin's equations for the given implied probabilities (reciprocals of bookie decimal odds).
    Returns (z, true_probabilities) where z is the estimated fraction of informed traders.
    """
    n = len(implied_probs)
    if n == 0:
        return 0.0, []
    sum_implied = sum(implied_probs)
    if abs(sum_implied - 1.0) < tol:
        return 0.0, implied_probs

    # Binary search for z in [0, 1]
    low = 0.0
    high = 1.0 - tol
    best_z = 0.0
    best_probs = []

    for _ in range(max_iter):
        mid_z = (low + high) / 2.0
        probs = []
        for pi in implied_probs:
            denom = 2.0 * (1.0 - mid_z)
            if denom < tol:
                probs = [pi / sum_implied for pi in implied_probs]
                break
            val = mid_z**2 + 4.0 * (1.0 - mid_z) * (pi**2 / sum_implied)
            p_i = (math.sqrt(max(0.0, val)) - mid_z) / denom
            probs.append(p_i)

        sum_p = sum(probs)
        if abs(sum_p - 1.0) < tol:
            best_z = mid_z
            best_probs = probs
            break

        if sum_p > 1.0:
            low = mid_z
        else:
            high = mid_z
        best_z = mid_z
        best_probs = probs

    # Final normalization check to guarantee exact 1.0 sum
    sum_p = sum(best_probs)
    if sum_p > 0:
        best_probs = [p / sum_p for p in best_probs]
    return best_z, best_probs

def calculate_kelly_fraction(true_prob: float, odds: float, risk_fraction: float = 0.25) -> float:
    """
    Calculates the risk-adjusted fractional Kelly Criterion stake.
    true_prob: Shin true probability of outcome
    odds: bookmaker decimal odds
    risk_fraction: e.g. 0.25 for quarter-Kelly
    """
    if odds <= 1.0:
        return 0.0
    b = odds - 1.0
    f_star = (true_prob * odds - 1.0) / b
    if f_star <= 0.0:
        return 0.0
    return f_star * risk_fraction

class LokiEngine:
    """Project Loki sports betting intelligence and predictive arbitrage engine."""
    def __init__(self, runtime):
        self.runtime = runtime
        self.risk_profile = "QUARTER_KELLY"

    def get_risk_fraction(self) -> float:
        """Translates active risk profile into numerical multiplier."""
        profile = self.risk_profile.upper()
        if profile == "FULL_KELLY":
            return 1.0
        elif profile == "HALF_KELLY":
            return 0.5
        # Default fallback is Quarter-Kelly for capital safety
        return 0.25

    def set_risk_profile(self, profile: str) -> bool:
        """Sets the active risk profile dynamically."""
        valid_profiles = ("QUARTER_KELLY", "HALF_KELLY", "FULL_KELLY")
        if profile.upper() in valid_profiles:
            self.risk_profile = profile.upper()
            logger.info(f"Loki risk profile calibrated dynamically to: {self.risk_profile}")
            return True
        return False

    def get_bankroll(self, conn=None) -> float:
        """Retrieves current virtual bankroll balance."""
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True
        try:
            cursor = conn.execute("SELECT balance FROM loki_bankroll WHERE bankroll_id = 'default'")
            row = cursor.fetchone()
            return row["balance"] if row else 10000.0
        except Exception as e:
            logger.error(f"Failed to get Loki bankroll: {str(e)}")
            return 10000.0
        finally:
            if close_conn:
                conn.close()

    def update_bankroll(self, change: float, conn=None):
        """Updates virtual bankroll balance atomically."""
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True
        try:
            if close_conn:
                with conn:
                    cursor = conn.execute("SELECT balance FROM loki_bankroll WHERE bankroll_id = 'default'")
                    row = cursor.fetchone()
                    current_balance = row["balance"] if row else 10000.0
                    new_balance = max(0.0, current_balance + change)
                    conn.execute("""
                        UPDATE loki_bankroll
                        SET balance = ?, updated_at = ?
                        WHERE bankroll_id = 'default'
                    """, (new_balance, datetime.utcnow().isoformat()))
                    logger.info(f"Loki bankroll updated by {change:+.2f} to {new_balance:.2f}")
            else:
                cursor = conn.execute("SELECT balance FROM loki_bankroll WHERE bankroll_id = 'default'")
                row = cursor.fetchone()
                current_balance = row["balance"] if row else 10000.0
                new_balance = max(0.0, current_balance + change)
                conn.execute("""
                    UPDATE loki_bankroll
                    SET balance = ?, updated_at = ?
                    WHERE bankroll_id = 'default'
                """, (new_balance, datetime.utcnow().isoformat()))
                logger.info(f"Loki bankroll updated by {change:+.2f} to {new_balance:.2f}")
        except Exception as e:
            logger.error(f"Failed to update Loki bankroll: {str(e)}")
            raise e
        finally:
            if close_conn:
                conn.close()

    def generate_fixtures(self) -> List[Dict[str, Any]]:
        """Generates a list of live fixtures with soft bookmaker odds and Pinnacle benchmarks."""
        api_key = os.environ.get("SOLOMON_THE_ODDS_API_KEY")
        if api_key:
            try:
                import urllib.request
                import json
                url = f"https://api.the-odds-api.com/v4/sports/soccer_uefa_champs_league/odds/?regions=us&markets=h2h&oddsFormat=decimal&apiKey={api_key}"
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read().decode('utf-8'))

                fixtures = []
                for game in data[:8]:
                    fixture_id = game["id"][:8]
                    home = game["home_team"]
                    away = game["away_team"]

                    pinnacle_odds = [2.0, 3.2, 3.0]
                    soft_odds = [2.1, 3.1, 3.1]
                    outcomes = [f"{home} Win", "Draw", f"{away} Win"]

                    for bookmaker in game.get("bookmakers", []):
                        if bookmaker["key"] in ("pinnacle", "lowvig"):
                            market = bookmaker["markets"][0]
                            pinnacle_odds = [outcome["price"] for outcome in market["outcomes"]]
                        elif bookmaker["key"] in ("draftkings", "fanduel"):
                            market = bookmaker["markets"][0]
                            soft_odds = [outcome["price"] for outcome in market["outcomes"]]
                            outcomes = [f"{outcome['name']} Win" if outcome['name'] != 'Draw' else 'Draw' for outcome in market['outcomes']]

                    fixtures.append({
                        "fixture_id": fixture_id,
                        "sport": "Champions League",
                        "fixture": f"{home} vs {away}",
                        "outcomes": outcomes,
                        "base_probabilities": [1.0/o for o in pinnacle_odds],
                        "pinnacle_odds": pinnacle_odds,
                        "soft_odds": soft_odds,
                        "is_soft_line": True,
                        "soft_outcome_index": 0
                    })
                if fixtures:
                    logger.info(f"Successfully fetched {len(fixtures)} live games from The Odds API.")
                    return fixtures
            except Exception as e:
                logger.error(f"Failed to fetch live odds from The Odds API: {str(e)}. Falling back to mock generator.")

        fixtures = []
        for sport, matchups in MOCK_TEAMS.items():
            for home, away in matchups:
                fixture_id = str(uuid.uuid4())[:8]
                is_three_way = (sport == "Premier League")

                # Base probabilities
                home_base_prob = random.uniform(0.35, 0.55)
                if is_three_way:
                    draw_base_prob = random.uniform(0.20, 0.28)
                    away_base_prob = 1.0 - home_base_prob - draw_base_prob
                    base_probs = [home_base_prob, draw_base_prob, away_base_prob]
                    outcomes = [f"{home} Win", "Draw", f"{away} Win"]
                else:
                    away_base_prob = 1.0 - home_base_prob
                    base_probs = [home_base_prob, away_base_prob]
                    outcomes = [f"{home} Win", f"{away} Win"]

                # Generate tight Pinnacle odds representing true probability + 2% vig
                pinnacle_vig = 1.02
                pinnacle_odds = [pinnacle_vig / p for p in base_probs]

                # Generate soft bookmaker odds representing true probability + 6% average overround,
                # but occasionally we inflate one side to represent an arbitrage / soft line!
                soft_vig = 1.06
                soft_odds = [soft_vig / p for p in base_probs]

                # Introduce deliberate soft lines with 30% probability
                is_soft_line = (random.random() < 0.3)
                chosen_idx = None
                if is_soft_line:
                    chosen_idx = random.randint(0, len(outcomes) - 1)
                    # Inflate the decimal odds for the chosen outcome by 10-18% (creating high EV!)
                    soft_odds[chosen_idx] = soft_odds[chosen_idx] * random.uniform(1.10, 1.18)

                fixtures.append({
                    "fixture_id": fixture_id,
                    "sport": sport,
                    "fixture": f"{home} vs {away}",
                    "outcomes": outcomes,
                    "base_probabilities": base_probs,
                    "pinnacle_odds": pinnacle_odds,
                    "soft_odds": soft_odds,
                    "is_soft_line": is_soft_line,
                    "soft_outcome_index": chosen_idx
                })
        return fixtures

    def get_active_value_picks(self) -> List[Dict[str, Any]]:
        """
        Scours live mock fixtures, runs Shin overround correction, and identifies
        all outcomes containing positive expected value (value-betting picks).
        """
        fixtures = self.generate_fixtures()
        picks = []

        for f in fixtures:
            pinnacle_implied = [1.0 / o for o in f["pinnacle_odds"]]
            z, true_probs = solve_shin_probabilities(pinnacle_implied)

            for idx, outcome in enumerate(f["outcomes"]):
                true_p = true_probs[idx]
                soft_o = f["soft_odds"][idx]
                expected_value = true_p * soft_o

                if expected_value > 1.02: # Clear 2%+ edge
                    kelly_frac = calculate_kelly_fraction(true_p, soft_o, risk_fraction=self.get_risk_fraction())
                    if kelly_frac > 0:
                        picks.append({
                            "fixture_id": f["fixture_id"],
                            "sport": f["sport"],
                            "fixture": f["fixture"],
                            "market": "Moneyline",
                            "outcome": outcome,
                            "outcome_index": idx,
                            "odds": round(soft_o, 2),
                            "pinnacle_odds": round(f["pinnacle_odds"][idx], 2),
                            "shin_true_prob": round(true_p, 4),
                            "expected_value": round(expected_value, 4),
                            "kelly_fraction": round(kelly_frac, 4),
                            "base_probabilities": f["base_probabilities"]
                        })
        return picks

    def simulate_tick(self) -> Dict[str, Any]:
        """
        Simulates one full cognitive sports betting tick:
        1. Resolves all existing PENDING bets using true event probability.
        2. Scours new live games and calculates value using Shin + Kelly.
        3. Executes live virtual bets, updating the bankroll atomically.
        """
        conn = self.runtime.db.get_connection()
        resolved_bets = []
        new_bets_placed = []
        initial_bankroll = self.get_bankroll(conn)

        try:
            with conn:
                # 1. Resolve pending bets
                cursor = conn.execute("SELECT * FROM loki_bets WHERE status = 'PENDING'")
                pending_rows = [dict(r) for r in cursor.fetchall()]

                for bet in pending_rows:
                    win_roll = random.random()
                    if win_roll < bet["shin_prob"]:
                        status = "WON"
                        profit_loss = bet["stake"] * (bet["odds"] - 1.0)
                    else:
                        status = "LOST"
                        profit_loss = -bet["stake"]

                    conn.execute("""
                        UPDATE loki_bets
                        SET status = ?, profit_loss = ?, resolved_at = ?
                        WHERE bet_id = ?
                    """, (status, profit_loss, datetime.utcnow().isoformat(), bet["bet_id"]))

                    if status == "WON":
                        self.update_bankroll(bet["stake"] + profit_loss, conn)

                    resolved_bets.append({
                        "bet_id": bet["bet_id"],
                        "fixture": bet["fixture"],
                        "outcome": bet["outcome"],
                        "status": status,
                        "stake": bet["stake"],
                        "profit_loss": profit_loss
                    })

                current_bankroll = self.get_bankroll(conn)

                # 2. Scan and place new bets if Loki is in LIVE_BETTING mode
                cursor_modes = conn.execute("SELECT mode FROM worker_modes WHERE worker_id = 'loki'")
                mode_row = cursor_modes.fetchone()
                active_mode = mode_row["mode"] if mode_row else "RESEARCH_ONLY"

                if active_mode == "LIVE_BETTING":
                    picks = self.get_active_value_picks()
                    for pick in picks:
                        stake = current_bankroll * pick["kelly_fraction"]
                        stake = round(stake / 5.0) * 5.0
                        if stake < 10.0:
                            continue
                        if stake > current_bankroll * 0.15:
                            stake = round((current_bankroll * 0.15) / 5.0) * 5.0

                        if current_bankroll >= stake:
                            bet_id = str(uuid.uuid4())[:8]
                            conn.execute("""
                                INSERT INTO loki_bets (
                                    bet_id, sport, fixture, market, outcome, odds, shin_prob,
                                    kelly_fraction, stake, status, profit_loss, created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', 0.0, ?)
                            """, (
                                bet_id,
                                pick["sport"],
                                pick["fixture"],
                                pick["market"],
                                pick["outcome"],
                                pick["odds"],
                                pick["shin_true_prob"],
                                pick["kelly_fraction"],
                                stake,
                                datetime.utcnow().isoformat()
                            ))

                            self.update_bankroll(-stake, conn)
                            current_bankroll -= stake

                            new_bets_placed.append({
                                "bet_id": bet_id,
                                "fixture": pick["fixture"],
                                "outcome": pick["outcome"],
                                "odds": pick["odds"],
                                "shin_prob": pick["shin_true_prob"],
                                "stake": stake
                            })
                else:
                    logger.info("Loki is in RESEARCH_ONLY mode. Skipping simulated live bet executions.")

            return {
                "ok": True,
                "initial_bankroll": initial_bankroll,
                "final_bankroll": self.get_bankroll(conn),
                "resolved_bets_count": len(resolved_bets),
                "resolved_bets": resolved_bets,
                "new_bets_count": len(new_bets_placed),
                "new_bets_placed": new_bets_placed,
                "active_mode": active_mode
            }
        except Exception as e:
            logger.error(f"Failed to execute Loki simulation tick: {str(e)}")
            return {"ok": False, "error": str(e)}
        finally:
            conn.close()

    def get_betting_stats(self) -> Dict[str, Any]:
        """Calculates total bets, win rate, ROI, net profit, and list of historic bets."""
        conn = self.runtime.db.get_connection()
        try:
            bankroll = self.get_bankroll(conn)

            cursor_total = conn.execute("SELECT COUNT(*) as count FROM loki_bets")
            total_bets = cursor_total.fetchone()["count"]

            cursor_won = conn.execute("SELECT COUNT(*) as count FROM loki_bets WHERE status = 'WON'")
            won_bets = cursor_won.fetchone()["count"]

            cursor_pending = conn.execute("SELECT COUNT(*) as count FROM loki_bets WHERE status = 'PENDING'")
            pending_bets = cursor_pending.fetchone()["count"]

            cursor_resolved = conn.execute("SELECT SUM(stake) as total_stake, SUM(profit_loss) as net_profit FROM loki_bets WHERE status != 'PENDING'")
            res_row = cursor_resolved.fetchone()
            total_stake_resolved = res_row["total_stake"] if res_row and res_row["total_stake"] else 0.0
            net_profit = res_row["net_profit"] if res_row and res_row["net_profit"] else 0.0

            resolved_bets_count = total_bets - pending_bets
            win_rate = (won_bets / resolved_bets_count) if resolved_bets_count > 0 else 0.0
            roi = (net_profit / total_stake_resolved) if total_stake_resolved > 0 else 0.0

            cursor_bets = conn.execute("SELECT * FROM loki_bets ORDER BY created_at DESC LIMIT 50")
            bets = [dict(row) for row in cursor_bets.fetchall()]

            return {
                "balance": bankroll,
                "total_bets": total_bets,
                "won_bets": won_bets,
                "pending_bets": pending_bets,
                "resolved_bets": resolved_bets_count,
                "win_rate": round(win_rate, 4),
                "roi": round(roi, 4),
                "net_profit": round(net_profit, 2),
                "bets_history": bets
            }
        except Exception as e:
            logger.error(f"Failed to fetch Loki betting stats: {str(e)}")
            return {
                "balance": 10000.0,
                "total_bets": 0,
                "won_bets": 0,
                "pending_bets": 0,
                "resolved_bets": 0,
                "win_rate": 0.0,
                "roi": 0.0,
                "net_profit": 0.0,
                "bets_history": []
            }
        finally:
            conn.close()


class KalshiPredictor:
    """SOSS Phase 16 Prediction Market Active Inference Kalshi module."""
    def __init__(self, runtime):
        self.runtime = runtime

    def get_active_contracts(self) -> List[Dict[str, Any]]:
        """Simulates / loads active Kalshi event contracts (e.g. US interest rates, tech indices)."""
        return [
            {
                "ticker": "FED-26-JULY",
                "title": "US Fed Interest Rate remains unchanged in July 2026",
                "yes_price_cents": 58,
                "no_price_cents": 44,
                "pinnacle_true_prob": 0.65
            },
            {
                "ticker": "TECH-NVDA-ATH",
                "title": "NVIDIA hits new All-Time High in August 2026",
                "yes_price_cents": 72,
                "no_price_cents": 30,
                "pinnacle_true_prob": 0.80
            },
            {
                "ticker": "AI-AGI-2026",
                "title": "AGI declared by major research labs in 2026",
                "yes_price_cents": 35,
                "no_price_cents": 67,
                "pinnacle_true_prob": 0.45
            }
        ]

    def calculate_contract_value_picks(self) -> List[Dict[str, Any]]:
        """
        Compares true probabilities with Kalshi cents contract prices.
        Calculates positive Expected Value (EV) and Kelly staking sizes.
        """
        contracts = self.get_active_contracts()
        picks = []
        for c in contracts:
            # Yes
            yes_odds = 100.0 / c["yes_price_cents"]
            yes_true_p = c["pinnacle_true_prob"]
            yes_ev = yes_true_p * yes_odds

            if yes_ev > 1.02:
                b = yes_odds - 1.0
                f_star = (yes_true_p * yes_odds - 1.0) / b
                kelly_stake = max(0.0, f_star * 0.25)
                if kelly_stake > 0:
                    picks.append({
                        "ticker": c["ticker"],
                        "title": c["title"],
                        "selection": "YES",
                        "price_cents": c["yes_price_cents"],
                        "true_probability": yes_true_p,
                        "expected_value": round(yes_ev, 4),
                        "kelly_fraction": round(kelly_stake, 4)
                    })

            # No
            no_odds = 100.0 / c["no_price_cents"]
            no_true_p = 1.0 - yes_true_p
            no_ev = no_true_p * no_odds
            if no_ev > 1.02:
                b = no_odds - 1.0
                f_star = (no_true_p * no_odds - 1.0) / b
                kelly_stake = max(0.0, f_star * 0.25)
                if kelly_stake > 0:
                    picks.append({
                        "ticker": c["ticker"],
                        "title": c["title"],
                        "selection": "NO",
                        "price_cents": c["no_price_cents"],
                        "true_probability": no_true_p,
                        "expected_value": round(no_ev, 4),
                        "kelly_fraction": round(kelly_stake, 4)
                    })
        return picks
