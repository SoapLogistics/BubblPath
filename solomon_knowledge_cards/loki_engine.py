import json
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


def poisson_probability(lam: float, k: int) -> float:
    """Returns the probability of exactly k occurrences given lambda."""
    return (math.exp(-lam) * (lam ** k)) / math.factorial(k)

def solve_soccer_poisson(home_xg: float, away_xg: float) -> List[float]:
    """
    Runs a Poisson distribution monte-carlo approximation for Soccer (Home Win, Draw, Away Win).
    Caps at 10 goals. Returns [Home%, Draw%, Away%].
    """
    home_win, draw, away_win = 0.0, 0.0, 0.0
    for home_goals in range(10):
        for away_goals in range(10):
            prob = poisson_probability(home_xg, home_goals) * poisson_probability(away_xg, away_goals)
            if home_goals > away_goals:
                home_win += prob
            elif home_goals == away_goals:
                draw += prob
            else:
                away_win += prob

    # Normalize
    total = home_win + draw + away_win
    if total == 0: return [0.33, 0.34, 0.33]
    return [home_win/total, draw/total, away_win/total]

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
        """Generates fixtures with multi-book line shopping (DraftKings, FanDuel, BetMGM)."""
        fixtures = []
        for sport, matchups in MOCK_TEAMS.items():
            for home, away in matchups:
                fixture_id = str(uuid.uuid4())[:8]
                is_three_way = (sport == "Premier League")

                # Feature 4: Mock Weather & Injury Variance
                volatility_multiplier = random.uniform(1.0, 1.5) if random.random() < 0.2 else 1.0

                # Feature 2: Poisson Solver for Soccer (Base probabilities)
                if is_three_way:
                    home_xg = random.uniform(0.5, 3.5)
                    away_xg = random.uniform(0.5, 3.5)
                    base_probs = solve_soccer_poisson(home_xg, away_xg)
                    outcomes = [f"{home} Win", "Draw", f"{away} Win"]
                else:
                    home_base_prob = random.uniform(0.35, 0.55)
                    away_base_prob = 1.0 - home_base_prob
                    base_probs = [home_base_prob, away_base_prob]
                    outcomes = [f"{home} Win", f"{away} Win"]

                # Pinnacle true odds
                pinnacle_vig = 1.02
                pinnacle_odds = [pinnacle_vig / p for p in base_probs]

                # Feature 5: Multi-Bookmaker Line Shopping
                books = ["DraftKings", "FanDuel", "BetMGM"]
                multi_book_odds = {}
                for book in books:
                    soft_vig = random.uniform(1.04, 1.08)
                    odds = [soft_vig / p for p in base_probs]

                    if random.random() < 0.3: # Random soft line injection
                        idx = random.randint(0, len(outcomes) - 1)
                        odds[idx] *= random.uniform(1.10, 1.18)

                    multi_book_odds[book] = odds

                # Resolve the "best" odds by line shopping
                best_odds = []
                best_book_for_outcome = []
                for idx in range(len(outcomes)):
                    best = 0.0
                    bb = ""
                    for book, odds_list in multi_book_odds.items():
                        if odds_list[idx] > best:
                            best = odds_list[idx]
                            bb = book
                    best_odds.append(best)
                    best_book_for_outcome.append(bb)

                fixtures.append({
                    "fixture_id": fixture_id,
                    "sport": sport,
                    "fixture": f"{home} vs {away}",
                    "market": "Moneyline",
                    "outcomes": outcomes,
                    "base_probabilities": base_probs,
                    "pinnacle_odds": pinnacle_odds,
                    "soft_odds": best_odds,
                    "best_books": best_book_for_outcome,
                    "volatility_multiplier": volatility_multiplier
                })

                # Prop Bet Market
                prop_fixture_id = str(uuid.uuid4())[:8]
                if sport == "Premier League": prop_outcomes = ["Over 2.5 Goals", "Under 2.5 Goals"]
                elif sport == "NBA": prop_outcomes = [f"{home} Star Points Over 25.5", f"{home} Star Points Under 25.5"]
                else: prop_outcomes = [f"{home} QB Passing Yards Over 250.5", f"{home} QB Passing Yards Under 250.5"]

                prop_base = random.uniform(0.40, 0.60)
                prop_base_probs = [prop_base, 1.0 - prop_base]
                prop_pinnacle_odds = [pinnacle_vig / p for p in prop_base_probs]

                multi_prop_odds = {}
                for book in books:
                    soft_vig = random.uniform(1.04, 1.08)
                    p_odds = [soft_vig / p for p in prop_base_probs]
                    if random.random() < 0.3:
                        idx = random.randint(0, 1)
                        p_odds[idx] *= random.uniform(1.10, 1.18)
                    multi_prop_odds[book] = p_odds

                best_prop_odds = []
                best_prop_books = []
                for idx in range(2):
                    best = 0.0
                    bb = ""
                    for book, odds_list in multi_prop_odds.items():
                        if odds_list[idx] > best:
                            best = odds_list[idx]
                            bb = book
                    best_prop_odds.append(best)
                    best_prop_books.append(bb)

                fixtures.append({
                    "fixture_id": prop_fixture_id,
                    "sport": sport,
                    "fixture": f"{home} vs {away}",
                    "market": "Prop_Bet",
                    "outcomes": prop_outcomes,
                    "base_probabilities": prop_base_probs,
                    "pinnacle_odds": prop_pinnacle_odds,
                    "soft_odds": best_prop_odds,
                    "best_books": best_prop_books,
                    "volatility_multiplier": volatility_multiplier
                })

        return fixtures

    def get_confidence_modifier(self, sport: str, market: str, odds: float, conn=None) -> float:
        """Retrieves the learned confidence modifier for a given sport, market, and odds band."""
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True
        try:
            band = "Favorite" if odds < 1.75 else ("Coinflip" if odds < 2.5 else "Longshot")
            category_id = f"{sport}_{market}_{band}".replace(" ", "_")
            cursor = conn.execute("SELECT confidence_modifier FROM loki_advanced_learning WHERE category_id = ?", (category_id,))
            row = cursor.fetchone()
            return row["confidence_modifier"] if row else 1.0
        except Exception as e:
            logger.error(f"Failed to fetch confidence modifier for {sport}_{market}: {e}")
            return 1.0
        finally:
            if close_conn:
                conn.close()

    def nightly_learning_review(self) -> Dict[str, Any]:
        conn = self.runtime.db.get_connection()
        try:
            with conn:
                cursor = conn.execute("SELECT sport, market, odds, status, profit_loss FROM loki_bets WHERE status != 'PENDING'")
                bets = cursor.fetchall()

                stats = {}
                total_profit = 0.0
                total_bets_count = 0
                for bet in bets:
                    band = "Favorite" if bet["odds"] < 1.75 else ("Coinflip" if bet["odds"] < 2.5 else "Longshot")
                    cat = f"{bet['sport']}_{bet['market']}_{band}".replace(" ", "_")
                    if cat not in stats:
                        stats[cat] = {"sport": bet["sport"], "market": bet["market"], "band": band, "total": 0, "won": 0, "implied_sum": 0.0}
                    stats[cat]["total"] += 1
                    stats[cat]["implied_sum"] += (1.0 / bet["odds"])
                    total_bets_count += 1
                    total_profit += bet["profit_loss"]
                    if bet["status"] == "WON":
                        stats[cat]["won"] += 1

                updates = []
                for cat, data in stats.items():
                    win_rate = data["won"] / data["total"] if data["total"] > 0 else 0

                    # Feature 6: Dynamic Baseline thresholds based on actual implied odds
                    dynamic_baseline = data["implied_sum"] / data["total"] if data["total"] > 0 else 0.5238

                    diff = win_rate - dynamic_baseline
                    modifier = max(0.5, min(1.5, 1.0 + (diff * 2.0)))

                    conn.execute("""
                        INSERT INTO loki_advanced_learning (category_id, sport, market, odds_band, total_bets, won_bets, confidence_modifier, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(category_id) DO UPDATE SET
                            total_bets = excluded.total_bets,
                            won_bets = excluded.won_bets,
                            confidence_modifier = excluded.confidence_modifier,
                            updated_at = excluded.updated_at
                    """, (cat, data["sport"], data["market"], data["band"], data["total"], data["won"], modifier, datetime.utcnow().isoformat()))

                    updates.append({
                        "category": cat,
                        "total_bets": data["total"],
                        "won_bets": data["won"],
                        "new_modifier": round(modifier, 4),
                        "baseline": round(dynamic_baseline, 4)
                    })

                card_id = f"loki_report_{datetime.utcnow().strftime('%Y%m%d')}"
                summary = f"Loki processed {total_bets_count} total bets for a net profit of {total_profit:.2f}."
                body = "Learning Adjustments:\n" + "\n".join([f"- {u['category']}: Modifier -> {u['new_modifier']} (vs {u['baseline']})" for u in updates])
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_cards (card_id, card_type, title, summary, body, confidence, validation_state, security_classification, source_ids, created_at, updated_at)
                    VALUES (?, 'SYSTEM_REPORT', ?, ?, ?, 1.0, 'ACTIVE', 'INTERNAL', '[]', ?, ?)
                """, (card_id, "Loki Nightly Engine Report", summary, body, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))

                return {"ok": True, "learning_updates": updates, "profit": total_profit, "report_card_id": card_id}
        except Exception as e:
            logger.error(f"Failed during nightly learning review: {e}")
            return {"ok": False, "error": str(e)}
        finally:
            conn.close()

    def solve_mpo_probabilities(self, implied_probs: List[float]) -> List[float]:
        """Margin Proportional to Odds (MPO) elimination, better for props/longshots."""
        margin = sum(implied_probs) - 1.0
        n = len(implied_probs)
        return [p - (margin / n) for p in implied_probs]

    def notify(self, type_str: str, message: str, conn=None):
        """Feature 9: Event-Driven Webhook / Notification Protocol"""
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True
        try:
            conn.execute("INSERT INTO loki_notifications (notification_id, type, message, created_at) VALUES (?, ?, ?, ?)", (str(uuid.uuid4())[:8], type_str, message, datetime.utcnow().isoformat()))
        finally:
            if close_conn: conn.close()

    def get_team_streak_modifier(self, team: str, conn=None) -> float:
        """Feature 3: Team Form Streak tracking"""
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True
        try:
            cursor = conn.execute("SELECT current_streak FROM loki_team_stats WHERE team_name = ?", (team,))
            row = cursor.fetchone()
            streak = row["current_streak"] if row else 0
            if streak >= 3: return 1.05 # Hot
            if streak <= -3: return 0.95 # Cold
            return 1.0
        except: return 1.0
        finally:
            if close_conn: conn.close()

    def get_active_value_picks(self, conn=None) -> List[Dict[str, Any]]:
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True

        fixtures = self.generate_fixtures()
        picks = []

        try:
            for f in fixtures:
                pinnacle_implied = [1.0 / o for o in f["pinnacle_odds"]]
                market = f.get("market", "Moneyline")

                if market == "Prop_Bet":
                    true_probs = self.solve_mpo_probabilities(pinnacle_implied)
                else:
                    z, true_probs = solve_shin_probabilities(pinnacle_implied)

                sport = f["sport"]
                volatility = f.get("volatility_multiplier", 1.0)

                best_implied_sum = sum(1.0 / o for o in f["soft_odds"])
                if best_implied_sum < 0.99:
                    self.notify("ARBITRAGE_DETECTED", f"Arb found in {f['fixture']}! Implied sum: {best_implied_sum:.3f} across {f['best_books']}", conn)

                for idx, outcome in enumerate(f["outcomes"]):
                    true_p = true_probs[idx]
                    if true_p <= 0.0: continue
                    soft_o = f["soft_odds"][idx]

                    team_name = outcome.replace(" Win", "").replace(" Over 2.5 Goals", "").strip()
                    streak_mod = self.get_team_streak_modifier(team_name, conn)

                    modifier = self.get_confidence_modifier(sport, market, soft_o, conn)

                    expected_value = true_p * soft_o * modifier * streak_mod
                    time_decay = random.uniform(0.95, 1.0)
                    expected_value *= time_decay

                    required_edge = 1.02 * volatility

                    if expected_value > required_edge:
                        kelly_frac = calculate_kelly_fraction(true_p, soft_o, risk_fraction=0.25)
                        adjusted_kelly = kelly_frac * modifier
                        if adjusted_kelly > 0:

                            max_liquidity = 250.0 if market == "Prop_Bet" else 1000.0

                            duration_scalar = 1.0 if market != "Futures" else 0.5

                            picks.append({
                                "fixture_id": f["fixture_id"],
                                "sport": sport,
                                "fixture": f["fixture"],
                                "market": market,
                                "outcome": outcome,
                                "outcome_index": idx,
                                "odds": round(soft_o, 2),
                                "book": f["best_books"][idx],
                                "pinnacle_odds": round(f["pinnacle_odds"][idx], 2),
                                "shin_true_prob": round(true_p, 4),
                                "expected_value": round(expected_value, 4),
                                "kelly_fraction": round(adjusted_kelly * duration_scalar, 4),
                                "max_liquidity": max_liquidity,
                                "volatility": volatility,
                                "streak_mod": streak_mod
                            })

            picks.sort(key=lambda x: x["expected_value"], reverse=True)
            return picks
        finally:
            if close_conn:
                conn.close()

    def get_vault(self, conn=None) -> float:
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True
        try:
            cursor = conn.execute("SELECT balance FROM loki_bankroll WHERE bankroll_id = 'vault'")
            row = cursor.fetchone()
            return row["balance"] if row else 0.0
        except Exception:
            return 0.0
        finally:
            if close_conn: conn.close()

    def update_vault(self, change: float, conn=None):
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True
        try:
            cursor = conn.execute("SELECT balance FROM loki_bankroll WHERE bankroll_id = 'vault'")
            row = cursor.fetchone()
            current = row["balance"] if row else 0.0
            conn.execute("UPDATE loki_bankroll SET balance = ?, updated_at = ? WHERE bankroll_id = 'vault'", (current + change, datetime.utcnow().isoformat()))
        finally:
            if close_conn: conn.close()

    def simulate_tick(self) -> Dict[str, Any]:
        """
        Simulates one full cognitive sports betting tick.
        Features: Drawdown Circuit Breaker, Dynamic Kelly, Hedging, Exposure Limits, Vault Sweeping, Equity Snapshots.
        """
        conn = self.runtime.db.get_connection()
        resolved_bets = []
        new_bets_placed = []
        hedged_bets = []
        initial_bankroll = self.get_bankroll(conn)

        try:
            with conn:
                # 1. Resolve pending bets & Feature 3: Hedging Engine
                cursor = conn.execute("SELECT * FROM loki_bets WHERE status = 'PENDING'")
                pending_rows = [dict(r) for r in cursor.fetchall()]

                # Quick check to see if we should hedge (mock shift in probability)
                for bet in pending_rows:
                    win_roll = random.random()

                    # Feature 3: Mock a hedge scenario (10% chance)
                    if random.random() < 0.10:
                        hedge_profit = bet["stake"] * 0.15 # Secure 15% guaranteed return
                        conn.execute("UPDATE loki_bets SET status = 'HEDGED', profit_loss = ?, resolved_at = ? WHERE bet_id = ?", (hedge_profit, datetime.utcnow().isoformat(), bet["bet_id"]))
                        self.update_bankroll(bet["stake"] + hedge_profit, conn)
                        hedged_bets.append(bet["bet_id"])
                        continue

                    if win_roll < bet["shin_prob"]:
                        status = "WON"
                        profit_loss = bet["stake"] * (bet["odds"] - 1.0)
                    else:
                        status = "LOST"
                        profit_loss = -bet["stake"]

                    conn.execute("UPDATE loki_bets SET status = ?, profit_loss = ?, resolved_at = ? WHERE bet_id = ?", (status, profit_loss, datetime.utcnow().isoformat(), bet["bet_id"]))

                    if status == "WON":
                        self.update_bankroll(bet["stake"] + profit_loss, conn)

                    resolved_bets.append({
                        "bet_id": bet["bet_id"],
                        "status": status,
                        "profit_loss": profit_loss
                    })

                current_bankroll = self.get_bankroll(conn)

                # Feature 1: Drawdown Circuit Breaker
                cursor_modes = conn.execute("SELECT mode FROM worker_modes WHERE worker_id = 'loki'")
                mode_row = cursor_modes.fetchone()
                active_mode = mode_row["mode"] if mode_row else "RESEARCH_ONLY"

                # If we've dropped below $8,000 (20% drawdown on starting $10K), emergency halt
                if current_bankroll < 8000.0 and active_mode == "LIVE_BETTING":
                    conn.execute("UPDATE worker_modes SET mode = 'RESEARCH_ONLY', updated_at = ? WHERE worker_id = 'loki'", (datetime.utcnow().isoformat(),))
                    active_mode = "RESEARCH_ONLY"
                    logger.warning("LOKI CIRCUIT BREAKER TRIGGERED: Drawdown > 20%. Reverting to RESEARCH_ONLY.")

                # Feature 7: Automated Profit Vault Sweeping
                if current_bankroll > 12000.0:
                    excess = current_bankroll - 12000.0
                    sweep_amount = excess * 0.5 # Sweep 50% of excess above 12K
                    self.update_bankroll(-sweep_amount, conn)
                    self.update_vault(sweep_amount, conn)
                    current_bankroll -= sweep_amount

                # Feature 6: Bankroll Equity Curve Snapshots
                vault = self.get_vault(conn)
                snapshot_id = str(uuid.uuid4())[:8]
                conn.execute("INSERT INTO loki_equity_snapshots (snapshot_id, bankroll, vault, timestamp) VALUES (?, ?, ?, ?)", (snapshot_id, current_bankroll, vault, datetime.utcnow().isoformat()))

                if active_mode == "LIVE_BETTING":
                    picks = self.get_active_value_picks(conn)

                    # Calculate recent form for Dynamic Kelly (Feature 2)
                    cursor_form = conn.execute("SELECT status FROM loki_bets WHERE status != 'PENDING' AND status != 'HEDGED' ORDER BY created_at DESC LIMIT 10")
                    form_rows = cursor_form.fetchall()
                    recent_wins = sum(1 for r in form_rows if r["status"] == "WON")

                    kelly_divisor = 5.0
                    if len(form_rows) == 10:
                        if recent_wins <= 3: kelly_divisor = 8.0 # Cold streak, risk less
                        elif recent_wins >= 6: kelly_divisor = 4.0 # Hot streak, risk more

                    # Feature 4: Exposure Limits
                    active_fixtures = set()

                    for pick in picks:
                        # Max 1 bet per fixture per tick
                        if pick["fixture_id"] in active_fixtures:
                            continue

                        stake = current_bankroll * pick["kelly_fraction"] / kelly_divisor
                        stake = round(stake / 5.0) * 5.0
                        if stake < 10.0: continue

                    # Feature 4b: Dynamic Max Stake Cap & Feature 7 Liquidity
                        max_stake = min(current_bankroll * 0.15, pick.get("max_liquidity", 1000.0))
                        if stake > max_stake: stake = round(max_stake / 5.0) * 5.0

                        if current_bankroll >= stake:
                            active_fixtures.add(pick["fixture_id"])
                            bet_id = str(uuid.uuid4())[:8]
                            conn.execute("""
                                INSERT INTO loki_bets (
                                    bet_id, sport, fixture, market, outcome, odds, shin_prob,
                                    kelly_fraction, stake, status, profit_loss, created_at
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', 0.0, ?)
                            """, (bet_id, pick["sport"], pick["fixture"], pick["market"], pick["outcome"], pick["odds"], pick["shin_true_prob"], pick["kelly_fraction"], stake, datetime.utcnow().isoformat()))

                            # Feature 8: ML Feature Extraction logging
                            ml_features = {
                                "ev": pick["expected_value"],
                                "shin": pick["shin_true_prob"],
                                "volatility": pick.get("volatility", 1.0),
                                "streak_mod": pick.get("streak_mod", 1.0),
                                "book": pick.get("book", "Unknown")
                            }
                            conn.execute("INSERT INTO loki_ml_features (bet_id, feature_json, timestamp) VALUES (?, ?, ?)", (bet_id, json.dumps(ml_features), datetime.utcnow().isoformat()))

                            self.update_bankroll(-stake, conn)
                            current_bankroll -= stake

                            new_bets_placed.append({
                                "bet_id": bet_id,
                                "fixture": pick["fixture"],
                                "outcome": pick["outcome"],
                                "stake": stake
                            })

                else:
                    logger.info("Loki is in RESEARCH_ONLY mode. Skipping simulated live bet executions.")

            return {
                "ok": True,
                "initial_bankroll": initial_bankroll,
                "final_bankroll": self.get_bankroll(conn),
                "vault": vault,
                "resolved_bets_count": len(resolved_bets),
                "hedged_bets_count": len(hedged_bets),
                "new_bets_count": len(new_bets_placed),
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
