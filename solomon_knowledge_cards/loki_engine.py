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
        fixtures = []
        for sport, matchups in MOCK_TEAMS.items():
            for home, away in matchups:
                # 1. Main Moneyline Market
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
                    "market": "Moneyline",
                    "outcomes": outcomes,
                    "base_probabilities": base_probs,
                    "pinnacle_odds": pinnacle_odds,
                    "soft_odds": soft_odds,
                    "is_soft_line": is_soft_line,
                    "soft_outcome_index": chosen_idx
                })

                # 2. Add a Prop Bet Market
                prop_fixture_id = str(uuid.uuid4())[:8]
                if sport == "Premier League":
                    prop_outcomes = ["Over 2.5 Goals", "Under 2.5 Goals"]
                elif sport == "NBA":
                    prop_outcomes = [f"{home} Star Points Over 25.5", f"{home} Star Points Under 25.5"]
                else:
                    prop_outcomes = [f"{home} QB Passing Yards Over 250.5", f"{home} QB Passing Yards Under 250.5"]

                prop_base = random.uniform(0.40, 0.60)
                prop_base_probs = [prop_base, 1.0 - prop_base]
                prop_pinnacle_odds = [pinnacle_vig / p for p in prop_base_probs]
                prop_soft_odds = [soft_vig / p for p in prop_base_probs]

                prop_is_soft = (random.random() < 0.3)
                prop_chosen_idx = None
                if prop_is_soft:
                    prop_chosen_idx = random.randint(0, 1)
                    prop_soft_odds[prop_chosen_idx] = prop_soft_odds[prop_chosen_idx] * random.uniform(1.10, 1.18)

                fixtures.append({
                    "fixture_id": prop_fixture_id,
                    "sport": sport,
                    "fixture": f"{home} vs {away}",
                    "market": "Prop_Bet",
                    "outcomes": prop_outcomes,
                    "base_probabilities": prop_base_probs,
                    "pinnacle_odds": prop_pinnacle_odds,
                    "soft_odds": prop_soft_odds,
                    "is_soft_line": prop_is_soft,
                    "soft_outcome_index": prop_chosen_idx
                })

        return fixtures

    def get_confidence_modifier(self, sport: str, market: str, conn=None) -> float:
        """Retrieves the learned confidence modifier for a given sport and market."""
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True
        try:
            category_id = f"{sport}_{market}".replace(" ", "_")
            cursor = conn.execute("SELECT confidence_modifier FROM loki_learning_weights WHERE category_id = ?", (category_id,))
            row = cursor.fetchone()
            return row["confidence_modifier"] if row else 1.0
        except Exception as e:
            logger.error(f"Failed to fetch confidence modifier for {sport}_{market}: {e}")
            return 1.0
        finally:
            if close_conn:
                conn.close()

    def nightly_learning_review(self) -> Dict[str, Any]:
        """
        Reviews all resolved bets to improve future forecasting.
        Calculates win rate by sport/market and updates confidence multipliers.
        """
        conn = self.runtime.db.get_connection()
        try:
            with conn:
                cursor = conn.execute("SELECT sport, market, status FROM loki_bets WHERE status != 'PENDING'")
                bets = cursor.fetchall()

                stats = {}
                for bet in bets:
                    cat = f"{bet['sport']}_{bet['market']}".replace(" ", "_")
                    if cat not in stats:
                        stats[cat] = {"sport": bet["sport"], "market": bet["market"], "total": 0, "won": 0}
                    stats[cat]["total"] += 1
                    if bet["status"] == "WON":
                        stats[cat]["won"] += 1

                updates = []
                for cat, data in stats.items():
                    win_rate = data["won"] / data["total"] if data["total"] > 0 else 0

                    # Target win rate is roughly 52.38% (breakeven at -110)
                    # If doing better, boost confidence (up to 1.5). If worse, penalize (down to 0.5)
                    baseline = 0.5238
                    diff = win_rate - baseline
                    modifier = max(0.5, min(1.5, 1.0 + (diff * 2.0)))

                    conn.execute("""
                        INSERT INTO loki_learning_weights (category_id, sport, market, total_bets, won_bets, confidence_modifier, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(category_id) DO UPDATE SET
                            total_bets = excluded.total_bets,
                            won_bets = excluded.won_bets,
                            confidence_modifier = excluded.confidence_modifier,
                            updated_at = excluded.updated_at
                    """, (cat, data["sport"], data["market"], data["total"], data["won"], modifier, datetime.utcnow().isoformat()))

                    updates.append({
                        "category": cat,
                        "total_bets": data["total"],
                        "won_bets": data["won"],
                        "new_modifier": modifier
                    })

                return {"ok": True, "learning_updates": updates}
        except Exception as e:
            logger.error(f"Failed during nightly learning review: {e}")
            return {"ok": False, "error": str(e)}
        finally:
            conn.close()

    def get_active_value_picks(self) -> List[Dict[str, Any]]:
        """
        Scours live mock fixtures, runs Shin overround correction, and identifies
        all outcomes containing positive expected value (value-betting picks).
        It learns from historical performance by applying the confidence_modifier.
        """
        fixtures = self.generate_fixtures()
        picks = []

        for f in fixtures:
            pinnacle_implied = [1.0 / o for o in f["pinnacle_odds"]]
            z, true_probs = solve_shin_probabilities(pinnacle_implied)

            market = f.get("market", "Moneyline")
            sport = f["sport"]
            modifier = self.get_confidence_modifier(sport, market)

            for idx, outcome in enumerate(f["outcomes"]):
                true_p = true_probs[idx]
                soft_o = f["soft_odds"][idx]

                # Apply learned confidence modifier to our expected value
                # A modifier > 1 means we historically win this more often
                expected_value = true_p * soft_o * modifier

                if expected_value > 1.02: # Clear 2%+ edge after modifier
                    kelly_frac = calculate_kelly_fraction(true_p, soft_o, risk_fraction=0.25)
                    # Adjust stake based on confidence as well
                    adjusted_kelly = kelly_frac * modifier
                    if adjusted_kelly > 0:
                        picks.append({
                            "fixture_id": f["fixture_id"],
                            "sport": sport,
                            "fixture": f["fixture"],
                            "market": market,
                            "outcome": outcome,
                            "outcome_index": idx,
                            "odds": round(soft_o, 2),
                            "pinnacle_odds": round(f["pinnacle_odds"][idx], 2),
                            "shin_true_prob": round(true_p, 4),
                            "expected_value": round(expected_value, 4),
                            "kelly_fraction": round(adjusted_kelly, 4),
                            "base_probabilities": f["base_probabilities"],
                            "confidence_modifier": round(modifier, 4)
                        })

        # Sort picks so the highest expected value (most likely to hit + value) are first
        picks.sort(key=lambda x: x["expected_value"], reverse=True)
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
