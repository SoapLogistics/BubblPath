class CasinoLab:
    """
    Offline Casino Strategy Lab.
    Provides mathematical advice based on manual inputs.
    """

    def __init__(self):
        # 3. Casino Rules Knowledgebase
        self.rules = {
            "blackjack": "Aim for 21. Dealer usually stands on soft 17. Blackjack pays 3:2. Doubling down allows 1 more card.",
            "baccarat": "Bet on Player, Banker, or Tie. Closest to 9 wins. Banker bet has slightly better odds.",
            "craps": "Pass line is the fundamental bet. 7 or 11 on come-out wins. 2, 3, or 12 loses.",
            "roulette": "European (single zero) has better odds than American (double zero). Outside bets (Red/Black) are nearly 50/50."
        }

    def get_card_value(self, card_str: str) -> int:
        card = card_str.upper().strip()
        if card in ['J', 'Q', 'K', '10']:
            return 10
        elif card == 'A':
            return 11
        else:
            try:
                return int(card)
            except ValueError:
                return 0

    def get_hi_lo_value(self, card_str: str) -> int:
        # 2. Hi-Lo Card Counting Engine
        val = self.get_card_value(card_str)
        if 2 <= val <= 6:
            return 1
        elif 7 <= val <= 9:
            return 0
        elif val >= 10 or card_str.upper() == 'A':
            return -1
        return 0

    def get_blackjack_advice(self, player_cards: list, dealer_upcard: str, running_count: int = 0, decks_remaining: float = 6.0) -> dict:
        """
        1. Blackjack Basic Strategy Engine
        A simplified basic strategy advisor.
        """
        player_values = [self.get_card_value(c) for c in player_cards if c]
        if not player_values or not dealer_upcard:
             return {"error": "Invalid inputs"}

        dealer_val = self.get_card_value(dealer_upcard)
        total = sum(player_values)
        has_ace = 'A' in [c.upper() for c in player_cards]
        is_soft = has_ace and total <= 21

        # Adjust Aces if we bust
        if total > 21 and has_ace:
            total -= 10
            is_soft = False

        is_pair = len(player_cards) == 2 and player_cards[0].upper() == player_cards[1].upper()

        action = "HIT"
        reason = "Basic Strategy Default"

        # Simplified Basic Strategy
        if is_pair:
            pair_val = player_values[0]
            if pair_val == 11 or pair_val == 8:
                action = "SPLIT"
                reason = "Always split Aces and 8s."
            elif pair_val == 10:
                action = "STAND"
                reason = "Never split 10s."
            elif pair_val == 9 and dealer_val not in [7, 10, 11]:
                action = "SPLIT"
            elif pair_val == 7 and dealer_val <= 7:
                action = "SPLIT"
            elif pair_val in [2,3,6] and dealer_val <= 6:
                action = "SPLIT"
        elif is_soft:
            if total >= 19:
                action = "STAND"
                reason = "Soft 19+ is strong."
            elif total == 18 and dealer_val <= 8:
                action = "STAND"
            elif total <= 17 and dealer_val in [3,4,5,6]:
                action = "DOUBLE (or HIT)"
                reason = "Double if allowed, else hit against weak dealer."
        else: # Hard total
            if total >= 17:
                action = "STAND"
                reason = "Hard 17+ always stands."
            elif 13 <= total <= 16:
                if dealer_val <= 6:
                    action = "STAND"
                    reason = "Dealer shows weak card; let them bust."
                else:
                    action = "HIT"
                    reason = "Dealer shows strong card; must improve."
            elif total == 12:
                if dealer_val in [4,5,6]:
                    action = "STAND"
                else:
                    action = "HIT"
            elif total == 11:
                action = "DOUBLE (or HIT)"
            elif total == 10:
                if dealer_val < 10:
                    action = "DOUBLE (or HIT)"
            elif total == 9:
                if dealer_val in [3,4,5,6]:
                    action = "DOUBLE (or HIT)"

        # True count adjustment
        true_count = running_count / max(0.5, decks_remaining)
        tc_advice = "Neutral"
        if true_count >= 2:
            tc_advice = f"Favorable (True Count: +{round(true_count, 1)}). Consider raising bets."
        elif true_count <= -1:
            tc_advice = f"Unfavorable (True Count: {round(true_count, 1)}). Minimum bets recommended."

        return {
            "total": total,
            "is_soft": is_soft,
            "action": action,
            "reason": reason,
            "true_count_advice": tc_advice
        }