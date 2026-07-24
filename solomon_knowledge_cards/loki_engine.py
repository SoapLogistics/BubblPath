import json
import math
import random
import uuid
import logging
import json
from datetime import datetime
from typing import List, Dict, Any, Tuple

# Advanced math helpers
def norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function"""
    return (1.0 + math.erf(x / math.sqrt(2.0))) / 2.0

def norm_pdf(x: float) -> float:
    return math.exp(-x**2 / 2.0) / math.sqrt(2.0 * math.pi)

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




def black_scholes_call(S: float, K: float, T: float, r: float, sigma: float) -> float:
    """Feature 3: Black-Scholes-Merton Options Pricing"""
    if T <= 0 or sigma <= 0: return max(0.0, S - K)
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return S * norm_cdf(d1) - K * math.exp(-r * T) * norm_cdf(d2)

def implied_volatility_newton_raphson(C_market: float, S: float, K: float, T: float, r: float) -> float:
    """Feature 3: Back-solve for IV using Newton-Raphson"""
    sigma = 0.20 # initial guess
    for _ in range(20):
        d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
        vega = S * norm_pdf(d1) * math.sqrt(T)
        if vega < 1e-8: break
        C_est = black_scholes_call(S, K, T, r, sigma)
        diff = C_est - C_market
        if abs(diff) < 1e-4: break
        sigma -= diff / vega
    return max(0.01, min(sigma, 5.0))

def ornstein_uhlenbeck_spread(price_A: float, price_B: float, mu: float, theta: float) -> str:
    """Feature 2: OU Process for Stat Arb (Mean Reverting Pairs)"""
    spread = price_A - price_B
    z_score = (spread - mu) / (theta + 1e-5)
    if z_score > 2.0: return "SHORT_A_LONG_B"
    elif z_score < -2.0: return "LONG_A_SHORT_B"
    return "NEUTRAL"

def calculate_hurst_mock() -> float:
    """Feature 4: Fractional Brownian Motion & Hurst Exponent"""
    # Mocking a Hurst calculation over a time series
    return random.uniform(0.3, 0.7)

def garch_forecast(current_vol: float, recent_shock: float) -> float:
    """Feature 9: GARCH Volatility Forecasting"""
    omega = 0.0001
    alpha = 0.1
    beta = 0.85
    new_var = omega + alpha*(recent_shock**2) + beta*(current_vol**2)
    return math.sqrt(new_var)

def hidden_markov_regime_mock() -> str:
    """Feature 1: HMM Regime Switching"""
    roll = random.random()
    if roll < 0.6: return "BULL_LOW_VOL"
    elif roll < 0.8: return "BEAR_HIGH_VOL"
    else: return "SIDEWAYS_CHOP"

def update_glicko2(rating: float, rd: float, vol: float, outcome: float, opponent_rating: float, opponent_rd: float) -> Tuple[float, float, float]:
    """Feature 14: Mock Glicko-2 Rating Migration"""
    # Simplified mock update
    g = 1.0 / math.sqrt(1.0 + 3.0 * (opponent_rd ** 2) / (math.pi ** 2))
    e = 1.0 / (1.0 + math.exp(-g * (rating - opponent_rating)))
    d2 = 1.0 / ((g ** 2) * e * (1.0 - e))

    new_rating = rating + (g * (outcome - e)) * 10.0 # scalar
    new_rd = max(30.0, rd * 0.98) # Decay RD slightly on play
    return new_rating, new_rd, vol

def kalman_filter_odds(z_measured: float, x_est_prev: float, p_prev: float) -> Tuple[float, float]:
    """Feature 13: 1D Kalman Filter for True Odds Tracking"""
    R = 0.05 # Measurement noise
    Q = 0.01 # Process noise

    x_pred = x_est_prev
    p_pred = p_prev + Q

    K = p_pred / (p_pred + R)
    x_est = x_pred + K * (z_measured - x_pred)
    p_est = (1 - K) * p_pred

    return x_est, p_est

def bayesian_update(prior: float, likelihood: float, evidence: float) -> float:
    """Feature 8: Bayesian Probability Updating"""
    if evidence == 0: return prior
    posterior = (likelihood * prior) / evidence
    return max(0.01, min(0.99, posterior))

def solve_tennis_markov(p_point: float) -> float:
    """Feature 9: Markov Chain State Transitions for Tennis (Mocked chance to win game from point win %)"""
    # P(Win Game | Win Point) -> Simplified to p^4 / (p^4 + (1-p)^4) for illustration
    return (p_point**4) / ((p_point**4) + ((1.0 - p_point)**4))

class LokiEngine:
    def get_elo(self, team: str, conn) -> float:
        cursor = conn.execute("SELECT elo_rating FROM loki_team_elo WHERE team_name = ?", (team,))
        row = cursor.fetchone()
        return row["elo_rating"] if row else 1500.0

    def update_elo(self, team: str, new_elo: float, conn):
        now_str = datetime.utcnow().isoformat()
        conn.execute("""
            INSERT INTO loki_team_elo (team_name, elo_rating, matches_played, updated_at)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(team_name) DO UPDATE SET
                elo_rating = ?,
                matches_played = matches_played + 1,
                updated_at = ?
        """, (team, new_elo, now_str, new_elo, now_str))

    def calculate_elo_win_prob(self, rating_a: float, rating_b: float) -> float:
        return 1.0 / (1.0 + math.pow(10, (rating_b - rating_a) / 400.0))

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

    def get_glicko(self, team: str, conn) -> Tuple[float, float, float]:
        cursor = conn.execute("SELECT rating, rating_deviation, volatility FROM loki_glicko_ratings WHERE team_name = ?", (team,))
        row = cursor.fetchone()
        return (row["rating"], row["rating_deviation"], row["volatility"]) if row else (1500.0, 350.0, 0.06)

    def update_glicko_db(self, team: str, r: float, rd: float, vol: float, conn):
        now_str = datetime.utcnow().isoformat()
        conn.execute("""
            INSERT INTO loki_glicko_ratings (team_name, rating, rating_deviation, volatility, updated_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(team_name) DO UPDATE SET
                rating = ?, rating_deviation = ?, volatility = ?, updated_at = ?
        """, (team, r, rd, vol, now_str, r, rd, vol, now_str))

    def get_strategy_weight(self, strategy_name: str, conn) -> float:
        """Feature 18: Algorithmic Meta-Scoring"""
        cursor = conn.execute("SELECT weight FROM loki_strategy_leaderboard WHERE strategy_name = ?", (strategy_name,))
        row = cursor.fetchone()
        return row["weight"] if row else 1.0

    def generate_kalshi_markets(self) -> List[Dict[str, Any]]:
        """Generates mock Kalshi Prediction Markets (Feature 2, 3, 4, 5, 6, 7)"""
        markets = []
        topics = ["Fed Rate Hike > 0.25%", "US Inflation > 3.0%", "Bitcoin > $100k", "Election: Candidate X Wins"]

        for topic in topics:
            market_id = f"kalshi_{str(uuid.uuid4())[:6]}"

            # True probability generated based on sentiment (Feature 3)
            sentiment = random.uniform(0.1, 0.9)
            true_prob = sentiment + random.uniform(-0.1, 0.1)
            true_prob = max(0.01, min(0.99, true_prob))

            # Kalshi Prices (Cents per share = probability)
            # Feature 2: Order Book Imbalance (Skew the price slightly away from true)
            imbalance = random.uniform(-0.15, 0.15)
            yes_price = max(0.01, min(0.99, true_prob + imbalance))
            no_price = 1.0 - yes_price

            # Feature 7: Open Interest
            open_interest = random.uniform(5000, 500000)

            # Feature 4: Resolution Decay
            days_to_expiry = random.uniform(1.0, 60.0)

            # Feature 6: Regulatory Risk Premium
            reg_premium = 0.05 if "Crypto" in topic or "Election" in topic else 0.0

            markets.append({
                "market_id": market_id,
                "topic": topic,
                "true_prob": true_prob,
                "yes_price": yes_price,
                "no_price": no_price,
                "open_interest": open_interest,
                "days_to_expiry": days_to_expiry,
                "sentiment": sentiment,
                "reg_premium": reg_premium
            })
        return markets

    def generate_equities_and_commodities(self, conn) -> List[Dict[str, Any]]:
        """Feature 8 (Commodities), Feature 7 (NLP), Feature 6 (Order Book Toxicity)"""
        markets = []

        # Stocks
        stocks = [("AAPL", 150.0), ("MSFT", 350.0), ("TSLA", 60000.0)]
        for ticker, base_price in stocks:
            # Random walk
            price = base_price * random.uniform(0.95, 1.05)

            # Feature 6: VPIN (Order Book Toxicity)
            vpin = random.uniform(0.0, 1.0)
            toxicity_alert = vpin > 0.8

            # Feature 7: NLP Sentiment Aggregation
            sentiment = random.uniform(-1.0, 1.0)

            # Feature 3: BSM IV Backsolving
            mock_call_price = price * random.uniform(0.02, 0.08)
            iv = implied_volatility_newton_raphson(mock_call_price, price, price*1.05, 30/365.0, 0.05)

            # Feature 4: Hurst Exponent
            hurst = calculate_hurst_mock()

            markets.append({
                "ticker": ticker,
                "asset_class": "STOCK",
                "price": price,
                "vpin_toxic": toxicity_alert,
                "sentiment": sentiment,
                "iv": iv,
                "hurst": hurst
            })

        # Commodities
        commodities = [("OIL", 80.0), ("WHEAT", 600.0)]
        for ticker, base_price in commodities:
            price = base_price * random.uniform(0.95, 1.05)

            # Feature 8: Contango / Backwardation Analyzer
            front_month = price
            back_month = price * random.uniform(0.9, 1.1)
            is_backwardation = front_month > back_month

            markets.append({
                "ticker": ticker,
                "asset_class": "COMMODITY",
                "price": price,
                "vpin_toxic": False,
                "sentiment": 0.0,
                "iv": 0.3,
                "hurst": 0.5,
                "is_backwardation": is_backwardation
            })

        return markets

    def calculate_cvar(self, conn) -> float:
        """Feature 5: Monte Carlo Value at Risk (VaR) & CVaR"""
        cursor = conn.execute("SELECT stake, shin_prob, odds FROM loki_bets WHERE status = 'PENDING'")
        rows = cursor.fetchall()
        if not rows: return 0.0

        simulations = 1000
        portfolio_losses = []

        for _ in range(simulations):
            sim_loss = 0.0
            for r in rows:
                if random.random() > r["shin_prob"]:
                    sim_loss += r["stake"]
                else:
                    sim_loss -= (r["stake"] * (r["odds"] - 1.0))
            portfolio_losses.append(sim_loss)

        portfolio_losses.sort(reverse=True)
        # 95% VaR index
        idx_95 = int(simulations * 0.05)
        tail_losses = portfolio_losses[:idx_95]

        if not tail_losses: return 0.0
        cvar = sum(tail_losses) / len(tail_losses)
        return max(0.0, cvar)

    def generate_fixtures(self) -> List[Dict[str, Any]]:
        conn = self.runtime.db.get_connection()
        fixtures = []
        try:
            for sport, matchups in MOCK_TEAMS.items():
                for home, away in matchups:
                    fixture_id = str(uuid.uuid4())[:8]
                    is_three_way = (sport == "Premier League")

                    # Feature 6: Simulated Injury Report Shocks (5% chance)
                    injury_shock = random.random() < 0.05
                    injury_victim = "home" if random.random() < 0.5 else "away"

                    sentiment_trap = (random.random() < 0.1)
                    volatility_multiplier = random.uniform(1.2, 1.8) if sentiment_trap else (random.uniform(1.0, 1.2) if random.random() < 0.2 else 1.0)
                    if injury_shock: volatility_multiplier *= 1.5

                    # Feature 14: Glicko-2 instead of Elo
                    home_rating, home_rd, home_vol = self.get_glicko(home, conn)
                    away_rating, away_rd, away_vol = self.get_glicko(away, conn)

                    # Feature 11: Fourier Transform Seasonality Detection (Mocked via RD bump if team usually slumps)
                    if random.random() < 0.1: home_rd *= 1.2 # Team slumping

                    if injury_shock:
                        if injury_victim == "home": home_rating -= 250.0
                        else: away_rating -= 250.0

                    base_vig = 1.04 if sport == "NFL" else (1.06 if sport == "NBA" else 1.08)

                    if is_three_way:
                        home_xg = random.uniform(0.5, 3.5) * (home_rating / 1500.0)
                        away_xg = random.uniform(0.5, 3.5) * (away_rating / 1500.0)
                        base_probs = solve_soccer_poisson(home_xg, away_xg)
                        outcomes = [f"{home} Win", "Draw", f"{away} Win"]
                    else:
                        home_base_prob = self.calculate_elo_win_prob(home_rating, away_rating) # Reusing elo math for simplicity
                        away_base_prob = 1.0 - home_base_prob
                        base_probs = [home_base_prob, away_base_prob]
                        outcomes = [f"{home} Win", f"{away} Win"]

                    pinnacle_vig = 1.015
                    pinnacle_odds = [pinnacle_vig / p for p in base_probs]

                    books = ["DraftKings", "FanDuel", "BetMGM"]
                    multi_book_odds = {}
                    for book in books:
                        soft_vig = base_vig + random.uniform(-0.01, 0.02)
                        odds = [soft_vig / p for p in base_probs]

                        if random.random() < 0.3:
                            idx = random.randint(0, len(outcomes) - 1)
                            odds[idx] *= random.uniform(1.10, 1.18)

                        multi_book_odds[book] = odds

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

                    prop_fixture_id = str(uuid.uuid4())[:8]
                    if sport == "Premier League": prop_outcomes = ["Over 2.5 Goals", "Under 2.5 Goals"]
                    elif sport == "NBA": prop_outcomes = [f"{home} Star Points Over 25.5", f"{home} Star Points Under 25.5"]
                    else: prop_outcomes = [f"{home} QB Passing Yards Over 250.5", f"{home} QB Passing Yards Under 250.5"]

                    prop_base = random.uniform(0.40, 0.60)
                    prop_base_probs = [prop_base, 1.0 - prop_base]
                    prop_pinnacle_odds = [pinnacle_vig / p for p in prop_base_probs]

                    multi_prop_odds = {}
                    for book in books:
                        soft_vig = base_vig + 0.02
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
        finally:
            conn.close()

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
                cursor = conn.execute("SELECT bet_id, sport, market, odds, status, profit_loss, created_at FROM loki_bets WHERE status != 'PENDING'")
                bets = cursor.fetchall()

                stats = {}
                total_profit = 0.0
                total_bets_count = 0
                to_archive = []
                now = datetime.utcnow()

                for bet in bets:
                    band = "Favorite" if bet["odds"] < 1.75 else ("Coinflip" if bet["odds"] < 2.5 else "Longshot")
                    cat = f"{bet['sport']}_{bet['market']}_{band}".replace(" ", "_")
                    if cat not in stats:
                        stats[cat] = {"sport": bet["sport"], "market": bet["market"], "band": band, "total": 0, "won": 0, "implied_sum": 0.0, "profit": 0.0}
                    stats[cat]["total"] += 1
                    stats[cat]["implied_sum"] += (1.0 / bet["odds"])
                    stats[cat]["profit"] += bet["profit_loss"]
                    total_bets_count += 1
                    total_profit += bet["profit_loss"]
                    if bet["status"] == "WON":
                        stats[cat]["won"] += 1

                    bet_date = datetime.fromisoformat(bet["created_at"])
                    if (now - bet_date).days > 30:
                        to_archive.append(dict(bet))

                updates = []
                for cat, data in stats.items():
                    win_rate = data["won"] / data["total"] if data["total"] > 0 else 0

                    dynamic_baseline = data["implied_sum"] / data["total"] if data["total"] > 0 else 0.5238

                    diff = win_rate - dynamic_baseline

                    # Feature 20: Reinforcement Learning Reward Clipping
                    # Don't let an insane +1000 longshot lucky hit skew the model permanently
                    if data["band"] == "Longshot" and diff > 0.5:
                        diff = 0.25 # Clip reward

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

                    # Feature 16: Solomon Strategy Discovery Loop
                    if data["total"] >= 10 and data["profit"] > 500.0:
                        # Auto-promote a strategy rule
                        strat_name = f"Strat_{cat}"
                        conn.execute("""
                            INSERT OR REPLACE INTO loki_strategy_leaderboard (strategy_name, total_bets, won_bets, roi, weight, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (strat_name, data["total"], data["won"], data["profit"]/(data["total"]*100), 1.2, datetime.utcnow().isoformat()))

                    updates.append({
                        "category": cat,
                        "total_bets": data["total"],
                        "won_bets": data["won"],
                        "new_modifier": round(modifier, 4),
                        "baseline": round(dynamic_baseline, 4)
                    })

                if len(to_archive) > 0:
                    archive_id = str(uuid.uuid4())[:8]
                    conn.execute("INSERT INTO loki_bet_archive (archive_id, bets_json, archived_at) VALUES (?, ?, ?)", (archive_id, json.dumps(to_archive), datetime.utcnow().isoformat()))

                card_id = f"loki_report_{datetime.utcnow().strftime('%Y%m%d')}"
                summary = f"Loki processed {total_bets_count} total bets for a net profit of {total_profit:.2f}."
                body = "Learning Adjustments:\n" + "\n".join([f"- {u['category']}: Modifier -> {u['new_modifier']} (vs {u['baseline']})" for u in updates])
                conn.execute("""
                    INSERT OR REPLACE INTO knowledge_cards (card_id, card_type, title, summary, body, confidence, validation_state, security_classification, source_ids, created_at, updated_at)
                    VALUES (?, 'SYSTEM_REPORT', ?, ?, ?, 1.0, 'ACTIVE', 'INTERNAL', '[]', ?, ?)
                """, (card_id, "Loki Nightly Engine Report", summary, body, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))

                return {"ok": True, "learning_updates": updates, "profit": total_profit, "report_card_id": card_id, "archived": len(to_archive)}
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

    def get_mean_reversion_penalty(self, team: str, conn) -> float:
        """Feature 2: Mean Reversion Trap Detection (Mocked via rapid recent wins)"""
        cursor = conn.execute("SELECT current_streak FROM loki_team_stats WHERE team_name = ?", (team,))
        row = cursor.fetchone()
        streak = row["current_streak"] if row else 0
        if streak >= 5: return 0.85 # Mean reversion penalty
        return 1.0

    def get_active_value_picks(self, conn=None) -> List[Dict[str, Any]]:
        close_conn = False
        if conn is None:
            conn = self.runtime.db.get_connection()
            close_conn = True

        fixtures = self.generate_fixtures()
        kalshi_markets = self.generate_kalshi_markets()
        picks = []

        try:
            # Evaluate Kalshi Markets
            for m in kalshi_markets:
                # Feature 3: Sentiment-to-Prediction Gap Analysis
                if m["sentiment"] > 0.8 and m["yes_price"] < 0.4:
                    self.notify("KALSHI_ANOMALY", f"High sentiment disconnect in {m['topic']}!", conn)

                # Feature 6: Regulatory Premium
                true_p = m["true_prob"] - m["reg_premium"]
                expected_value = true_p / m["yes_price"]

                # Feature 4: Event Resolution Decay
                time_decay_scalar = max(0.1, m["days_to_expiry"] / 60.0)

                if expected_value > 1.05:
                    kelly_frac = calculate_kelly_fraction(true_p, 1.0/m["yes_price"], risk_fraction=0.25)
                    adjusted_kelly = kelly_frac * time_decay_scalar

                    if adjusted_kelly > 0:
                        max_liquidity = 5000.0
                        # Feature 7: Liquidity Shadow Staking
                        if m["open_interest"] < 10000:
                            adjusted_kelly *= 0.1
                            max_liquidity = 100.0

                        picks.append({
                            "fixture_id": m["market_id"],
                            "sport": "Kalshi",
                            "fixture": m["topic"],
                            "market": "Prediction",
                            "outcome": "Yes",
                            "outcome_index": 0,
                            "odds": round(1.0/m["yes_price"], 2),
                            "book": "Kalshi",
                            "pinnacle_odds": round(1.0/m["yes_price"], 2),
                            "shin_true_prob": round(true_p, 4),
                            "expected_value": round(expected_value, 4),
                            "kelly_fraction": round(adjusted_kelly, 4),
                            "max_liquidity": max_liquidity,
                            "volatility": 1.0,
                            "streak_mod": 1.0,
                            "correlation_key": m["market_id"]
                        })

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
                    lp_fee = 0.005
                    arb_margin = 1.0 - best_implied_sum
                    if arb_margin > lp_fee:
                        self.notify("ARBITRAGE_DETECTED", f"Arb found in {f['fixture']}! Net margin: {(arb_margin-lp_fee)*100:.2f}% across {f['best_books']}", conn)

                for idx, outcome in enumerate(f["outcomes"]):
                    true_p = true_probs[idx]

                    # Feature 13: Kalman Filter Smoothing
                    # Mock finding previous estimate from DB (omitted for brevity, using true_p directly as prior)
                    filtered_p, _ = kalman_filter_odds(true_p, true_p * random.uniform(0.9, 1.1), 0.1)
                    true_p = max(0.01, min(0.99, filtered_p))

                    if true_p <= 0.0: continue
                    soft_o = f["soft_odds"][idx]

                    # Feature 19: Contrarian Trigger Engine
                    public_money = random.uniform(0.1, 0.95)
                    if public_money > 0.85 and soft_o > 2.0:
                        self.notify("CONTRARIAN_TRIGGER", f"Heavy public money ({public_money*100:.1f}%) fading sharp line on {outcome}", conn)
                        true_p *= 1.1 # Boost our confidence

                    # Feature 15: ARIMA Mock (Wait for better odds)
                    arima_says_wait = (random.random() < 0.05)
                    if arima_says_wait: continue

                    team_name = outcome.replace(" Win", "").replace(" Over 2.5 Goals", "").strip()
                    streak_mod = self.get_team_streak_modifier(team_name, conn)
                    mean_rev_pen = self.get_mean_reversion_penalty(team_name, conn)

                    # Feature 18: Meta-Scoring (Multiply confidence by Strategy weight)
                    strat_weight = self.get_strategy_weight(sport, conn)
                    modifier = self.get_confidence_modifier(sport, market, soft_o, conn) * strat_weight

                    expected_value = true_p * soft_o * modifier * streak_mod * mean_rev_pen

                    time_to_start_hours = random.uniform(0.5, 48.0)
                    ev_decay = max(0.92, 1.0 - (0.002 * (48.0 - time_to_start_hours)))
                    expected_value *= ev_decay

                    tax_rate = 0.02
                    profit_portion = soft_o - 1.0
                    taxed_soft_o = 1.0 + (profit_portion * (1.0 - tax_rate))
                    expected_value_after_tax = expected_value * (taxed_soft_o / soft_o)

                    # Feature 23: Live Spread Penalty
                    is_live = (random.random() < 0.1)
                    if is_live: expected_value_after_tax /= 1.08

                    required_edge = 1.02 * volatility

                    if expected_value_after_tax > required_edge:
                        kelly_frac = calculate_kelly_fraction(true_p, taxed_soft_o, risk_fraction=0.25)
                        adjusted_kelly = kelly_frac * modifier
                        if adjusted_kelly > 0:

                            # Feature 17: Cluster Analysis for Props (High Variance players get smaller Kelly)
                            if market == "Prop_Bet" and random.random() < 0.5:
                                adjusted_kelly *= 0.5

                            max_liquidity = 250.0 if market == "Prop_Bet" else 1000.0
                            duration_scalar = 1.0 if market != "Futures" else 0.5

                            correlation_key = f"{f['fixture_id']}_{outcome.split(' ')[0]}" if market == "Prop_Bet" else f"{f['fixture_id']}_ML_{idx}"

                            picks.append({
                                "fixture_id": f["fixture_id"],
                                "sport": sport,
                                "fixture": f["fixture"],
                                "market": market,
                                "outcome": outcome,
                                "outcome_index": idx,
                                "odds": round(soft_o, 2),
                                "book": f["best_books"][idx] if sport != "Kalshi" else "Kalshi",
                                "pinnacle_odds": round(f["pinnacle_odds"][idx], 2),
                                "shin_true_prob": round(true_p, 4),
                                "expected_value": round(expected_value_after_tax, 4),
                                "kelly_fraction": round(adjusted_kelly * duration_scalar, 4),
                                "max_liquidity": max_liquidity,
                                "volatility": volatility,
                                "streak_mod": streak_mod,
                                "correlation_key": correlation_key
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

    def get_currency_balance(self, currency_id: str, conn) -> float:
        cursor = conn.execute("SELECT balance FROM loki_currencies WHERE currency_id = ?", (currency_id,))
        row = cursor.fetchone()
        return row["balance"] if row else 0.0

    def simulate_tick(self) -> Dict[str, Any]:
        conn = self.runtime.db.get_connection()
        resolved_bets = []
        new_bets_placed = []
        hedged_bets = []
        initial_bankroll = self.get_bankroll(conn)

        try:
            with conn:
                cursor = conn.execute("SELECT * FROM loki_bets WHERE status = 'PENDING'")
                pending_rows = [dict(r) for r in cursor.fetchall()]

                cursor_s = conn.execute("SELECT balance FROM loki_bankroll WHERE bankroll_id = 'shadow_flat'")
                sr = cursor_s.fetchone()
                shadow_bankroll = sr["balance"] if sr else 10000.0

                for bet in pending_rows:
                    win_roll = random.random()

                    current_live_prob = bet.get("live_win_prob", -1.0)
                    if current_live_prob < 0: current_live_prob = bet["shin_prob"]
                    live_shift = random.uniform(-0.15, 0.15)
                    new_live_prob = max(0.01, min(0.99, current_live_prob + live_shift))

                    if new_live_prob > bet["shin_prob"] + 0.20 and random.random() < 0.3:
                        hedge_profit = bet["stake"] * 0.15
                        conn.execute("UPDATE loki_bets SET status = 'HEDGED', profit_loss = ?, resolved_at = ?, live_win_prob = ? WHERE bet_id = ?", (hedge_profit, datetime.utcnow().isoformat(), new_live_prob, bet["bet_id"]))
                        self.update_bankroll(bet["stake"] + hedge_profit, conn)
                        hedged_bets.append(bet["bet_id"])
                        shadow_profit = 50.0 * 0.15
                        shadow_bankroll += shadow_profit
                        continue

                    is_resolved = (random.random() < 0.3)
                    if not is_resolved:
                        conn.execute("UPDATE loki_bets SET live_win_prob = ? WHERE bet_id = ?", (new_live_prob, bet["bet_id"]))
                        continue

                    if win_roll < bet["shin_prob"]:
                        status = "WON"
                        profit_loss = bet["stake"] * (bet["odds"] - 1.0)
                        shadow_profit = 50.0 * (bet["odds"] - 1.0)
                    else:
                        status = "LOST"
                        profit_loss = -bet["stake"]
                        shadow_profit = -50.0

                    shadow_bankroll += shadow_profit

                    conn.execute("UPDATE loki_bets SET status = ?, profit_loss = ?, resolved_at = ?, live_win_prob = ? WHERE bet_id = ?", (status, profit_loss, datetime.utcnow().isoformat(), new_live_prob, bet["bet_id"]))

                    # Feature 8: Bayesian Updates (Mocked)
                    team_name = bet["outcome"].replace(" Win", "").replace(" Over 2.5 Goals", "").strip()
                    prior_elo = self.get_elo(team_name, conn)
                    likelihood = 0.8 if status == "WON" else 0.2
                    evidence = bet["shin_prob"]
                    posterior_scale = bayesian_update(prior_elo/3000.0, likelihood, evidence)
                    new_elo = prior_elo * posterior_scale * 1.5

                    # Feature 14: Glicko update
                    r, rd, vol = self.get_glicko(team_name, conn)
                    new_r, new_rd, new_vol = update_glicko2(r, rd, vol, 1.0 if status=="WON" else 0.0, 1500.0, 350.0)
                    self.update_glicko_db(team_name, new_r, new_rd, new_vol, conn)

                    self.update_elo(team_name, new_elo, conn)

                    cursor_st = conn.execute("SELECT current_streak FROM loki_team_stats WHERE team_name = ?", (team_name,))
                    r_st = cursor_st.fetchone()
                    st = r_st["current_streak"] if r_st else 0
                    if status == "WON": st = st + 1 if st > 0 else 1
                    else: st = st - 1 if st < 0 else -1
                    conn.execute("INSERT OR REPLACE INTO loki_team_stats (team_name, current_streak, updated_at) VALUES (?, ?, ?)", (team_name, st, datetime.utcnow().isoformat()))

                    if status == "WON":
                        self.update_bankroll(bet["stake"] + profit_loss, conn)

                conn.execute("UPDATE loki_bankroll SET balance = ?, updated_at = ? WHERE bankroll_id = 'shadow_flat'", (shadow_bankroll, datetime.utcnow().isoformat()))

                current_bankroll = self.get_bankroll(conn)

                cursor_modes = conn.execute("SELECT mode FROM worker_modes WHERE worker_id = 'loki'")
                mode_row = cursor_modes.fetchone()
                active_mode = mode_row["mode"] if mode_row else "RESEARCH_ONLY"

                cursor_cd = conn.execute("SELECT value FROM loki_system_state WHERE key = 'cooldown_timer'")
                cd_row = cursor_cd.fetchone()
                cooldown = int(cd_row["value"]) if cd_row else 0

                if cooldown > 0:
                    cooldown -= 1
                    conn.execute("UPDATE loki_system_state SET value = ?, updated_at = ? WHERE key = 'cooldown_timer'", (str(cooldown), datetime.utcnow().isoformat()))
                    if active_mode == "LIVE_BETTING":
                        conn.execute("UPDATE worker_modes SET mode = 'RESEARCH_ONLY', updated_at = ? WHERE worker_id = 'loki'", (datetime.utcnow().isoformat(),))
                        active_mode = "RESEARCH_ONLY"

                if current_bankroll < 8000.0 and active_mode == "LIVE_BETTING":
                    conn.execute("UPDATE worker_modes SET mode = 'RESEARCH_ONLY', updated_at = ? WHERE worker_id = 'loki'", (datetime.utcnow().isoformat(),))
                    conn.execute("UPDATE loki_system_state SET value = '24', updated_at = ? WHERE key = 'cooldown_timer'", (datetime.utcnow().isoformat(),))
                    active_mode = "RESEARCH_ONLY"
                    self.notify("CIRCUIT_BREAKER", "Drawdown > 20%. Reverting to RESEARCH_ONLY.", conn)

                # Feature 1: HMM Regime Switching
                current_regime = hidden_markov_regime_mock()
                conn.execute("INSERT OR REPLACE INTO loki_system_state (key, value, updated_at) VALUES ('regime_state', ?, ?)", (current_regime, datetime.utcnow().isoformat()))

                # If regime is BEAR_HIGH_VOL, slash risk parameters globally
                if current_regime == "BEAR_HIGH_VOL" and active_mode == "LIVE_BETTING":
                    self.notify("REGIME_SHIFT", "HMM detected High Volatility Bear Regime. Slashing risk exposure.", conn)
                    # We will artificially boost CVaR evaluation threshold to force halts more easily below

                # Evaluate Equities & Commodities
                equities = self.generate_equities_and_commodities(conn)
                for eq in equities:
                    now_str = datetime.utcnow().isoformat()
                    conn.execute("""
                        INSERT OR REPLACE INTO loki_equities (ticker, asset_class, price, implied_volatility, hurst_exponent, regime_state, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (eq["ticker"], eq["asset_class"], eq["price"], eq["iv"], eq["hurst"], current_regime, now_str))

                    if eq["sentiment"] != 0.0:
                        conn.execute("INSERT INTO loki_news_sentiment (article_id, asset, headline, sentiment_score, timestamp) VALUES (?, ?, ?, ?, ?)",
                                     (str(uuid.uuid4())[:8], eq["ticker"], f"{eq['ticker']} Momentum Update", eq["sentiment"], now_str))

                    # Mock placing equity positions based on signals
                    if active_mode == "LIVE_BETTING":
                        trade_signal = "NONE"

                        # Feature 4 (Hurst) & Feature 6 (VPIN) & Feature 7 (Sentiment)
                        if eq["asset_class"] == "STOCK":
                            if eq["hurst"] > 0.6 and eq["sentiment"] > 0.5 and not eq["vpin_toxic"]:
                                trade_signal = "LONG"
                            elif eq["vpin_toxic"] and eq["sentiment"] < -0.5:
                                trade_signal = "SHORT"

                        # Feature 8 (Backwardation)
                        if eq["asset_class"] == "COMMODITY" and eq.get("is_backwardation"):
                            trade_signal = "LONG"

                        if trade_signal != "NONE":
                            # Feature 9: GARCH Volatility Forecasting dynamically sizing position
                            forecast_vol = garch_forecast(eq["iv"], 0.05)
                            position_size = current_bankroll * (0.02 / forecast_vol) # Inverse vol sizing
                            position_size = min(position_size, current_bankroll * 0.10)

                            if current_bankroll >= position_size:
                                conn.execute("""
                                    INSERT INTO loki_positions (position_id, asset, position_type, entry_price, current_price, size, unrealized_pnl, created_at, updated_at)
                                    VALUES (?, ?, ?, ?, ?, ?, 0.0, ?, ?)
                                """, (str(uuid.uuid4())[:8], eq["ticker"], trade_signal, eq["price"], eq["price"], position_size, now_str, now_str))
                                self.update_bankroll(-position_size, conn)
                                current_bankroll -= position_size

                # Feature 2: OU Process Stat Arb (Mock pairs trading Coke vs Pepsi)
                pair_signal = ornstein_uhlenbeck_spread(100.0, 95.0, 5.0, 2.0)
                if pair_signal != "NEUTRAL" and active_mode == "LIVE_BETTING":
                    pair_size = current_bankroll * 0.05
                    if current_bankroll >= pair_size:
                        conn.execute("""
                            INSERT INTO loki_positions (position_id, asset, position_type, entry_price, current_price, size, unrealized_pnl, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, 0.0, ?, ?)
                        """, (str(uuid.uuid4())[:8], "COKE_PEPSI_SPREAD", pair_signal, 5.0, 5.0, pair_size, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
                        self.update_bankroll(-pair_size, conn)
                        current_bankroll -= pair_size

                # Feature 21: Expected Shortfall Halt (Monte Carlo updated)
                cvar = self.calculate_cvar(conn)
                cvar_threshold = 0.15 if current_regime != "BEAR_HIGH_VOL" else 0.05
                if cvar > current_bankroll * cvar_threshold and active_mode == "LIVE_BETTING":
                    logger.warning(f"CVaR limit exceeded ({cvar:.2f}). Halting new bets.")
                    self.notify("RISK_LIMIT", f"CVaR exceeded ({cvar:.2f}).", conn)
                    picks = []
                elif active_mode == "LIVE_BETTING":
                    picks = self.get_active_value_picks(conn)
                else:
                    picks = []

                if current_bankroll > 12000.0:

                    excess = current_bankroll - 12000.0
                    sweep_amount = excess * 0.5
                    self.update_bankroll(-sweep_amount, conn)
                    self.update_vault(sweep_amount, conn)
                    current_bankroll -= sweep_amount

                vault = self.get_vault(conn)
                snapshot_id = str(uuid.uuid4())[:8]
                conn.execute("INSERT INTO loki_equity_snapshots (snapshot_id, bankroll, vault, shadow_flat, timestamp) VALUES (?, ?, ?, ?, ?)", (snapshot_id, current_bankroll, vault, shadow_bankroll, datetime.utcnow().isoformat()))

                if active_mode == "LIVE_BETTING" and len(picks) > 0:

                    cursor_form = conn.execute("SELECT status FROM loki_bets WHERE status != 'PENDING' AND status != 'HEDGED' ORDER BY created_at DESC LIMIT 10")
                    form_rows = cursor_form.fetchall()
                    recent_wins = sum(1 for r in form_rows if r["status"] == "WON")

                    # Feature 22: Fractional Blending based on sport
                    kelly_divisor = 5.0
                    if len(form_rows) == 10:
                        if recent_wins <= 3: kelly_divisor = 8.0
                        elif recent_wins >= 6: kelly_divisor = 4.0

                    num_picks = len(picks)
                    if num_picks > 0:
                        simultaneous_decay = max(1.0, math.sqrt(num_picks))
                        kelly_divisor *= simultaneous_decay

                    c_mode = conn.execute("SELECT value FROM loki_system_state WHERE key = 'kelly_mode'").fetchone()
                    km = c_mode["value"] if c_mode else "HALF"
                    kelly_scalar = 1.0 if km == "FULL" else (0.5 if km == "HALF" else 0.25)

                    active_fixtures = set()
                    active_correlations = set()

                    c_exp = conn.execute("SELECT sport, market, SUM(stake) as total_stake FROM loki_bets WHERE status = 'PENDING' GROUP BY sport, market").fetchall()
                    exposure = {"sport": {}, "market": {}}
                    total_exposure = 0
                    for r in c_exp:
                        s = r["total_stake"]
                        total_exposure += s
                        exposure["sport"][r["sport"]] = exposure["sport"].get(r["sport"], 0) + s
                        exposure["market"][r["market"]] = exposure["market"].get(r["market"], 0) + s

                    for pick in picks:
                        if pick["fixture_id"] in active_fixtures or pick["correlation_key"] in active_correlations:
                            continue

                        if pick["market"] == "Prop_Bet" and (exposure["market"].get("Prop_Bet", 0) > current_bankroll * 0.35):
                            continue

                        if exposure["sport"].get(pick["sport"], 0) > current_bankroll * 0.50:
                            continue

                        stake = current_bankroll * pick["kelly_fraction"] * kelly_scalar / kelly_divisor
                        stake = round(stake / 5.0) * 5.0
                        if stake < 10.0: continue

                        max_stake = min(current_bankroll * 0.15, pick.get("max_liquidity", 1000.0))
                        if stake > max_stake: stake = round(max_stake / 5.0) * 5.0

                        usd_balance = self.get_currency_balance('USD', conn)
                        if usd_balance < stake: continue

                        if current_bankroll >= stake:
                            active_fixtures.add(pick["fixture_id"])
                            active_correlations.add(pick["correlation_key"])

                            bet_id = str(uuid.uuid4())[:8]
                            conn.execute("""
                                INSERT INTO loki_bets (
                                    bet_id, sport, fixture, market, outcome, odds, shin_prob,
                                    kelly_fraction, stake, status, profit_loss, created_at, correlation_key
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'PENDING', 0.0, ?, ?)
                            """, (bet_id, pick["sport"], pick["fixture"], pick["market"], pick["outcome"], pick["odds"], pick["shin_true_prob"], pick["kelly_fraction"], stake, datetime.utcnow().isoformat(), pick["correlation_key"]))

                            exposure["sport"][pick["sport"]] = exposure["sport"].get(pick["sport"], 0) + stake
                            exposure["market"][pick["market"]] = exposure["market"].get(pick["market"], 0) + stake

                            # Feature 10: Z-Score Outlier
                            z_score = random.uniform(0.0, 3.0)

                            ml_features = {
                                "ev": pick["expected_value"],
                                "shin": pick["shin_true_prob"],
                                "volatility": pick.get("volatility", 1.0),
                                "streak_mod": pick.get("streak_mod", 1.0),
                                "book": pick.get("book", "Unknown"),
                                "z_score": z_score
                            }
                            conn.execute("INSERT INTO loki_ml_features (bet_id, feature_json, timestamp) VALUES (?, ?, ?)", (bet_id, json.dumps(ml_features), datetime.utcnow().isoformat()))

                            self.update_bankroll(-stake, conn)
                            current_bankroll -= stake

                            # Feature 25: Dark Pool Mocking
                            if stake > 2000.0:
                                self.notify("DARK_POOL_ROUTE", f"Routing ${stake} for {pick['fixture']} via dark pool chunks.", conn)

                            new_bets_placed.append({
                                "bet_id": bet_id,
                                "fixture": pick["fixture"],
                                "outcome": pick["outcome"],
                                "stake": stake
                            })
                else:
                    logger.info(f"Loki is in {active_mode} mode. Skipping simulated live bet executions.")

            return {
                "ok": True,
                "initial_bankroll": initial_bankroll,
                "final_bankroll": self.get_bankroll(conn),
                "vault": vault,
                "shadow_flat": shadow_bankroll,
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
