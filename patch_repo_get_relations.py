import os

filepath = 'solomon_knowledge_cards/api/repository.py'
with open(filepath, 'r') as f:
    content = f.read()

replacement = """    def get_related_cards(self, card_id: str) -> List[KnowledgeCard]:
        \"\"\"Retrieves linked parent and related cards of a given card.\"\"\"
        card = self.get_card(card_id)
        if not card:
            return []
        related = []
        for p_id in card.parent_card_ids:
            p_card = self.get_card(p_id)
            if p_card:
                related.append(p_card)
        for r_id in card.related_card_ids:
            r_card = self.get_card(r_id)
            if r_card:
                related.append(r_card)

        # Also grab any semantic relationships from the DB directly
        with self.db_manager._lock:
            conn = self.db_manager._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT target_id FROM card_links WHERE source_id = ? AND link_type IN ('DEPENDS_ON', 'PREVENTS', 'ENHANCES')", (card_id,))
                for row in cursor.fetchall():
                    target_id = row[0]
                    t_card = self.get_card(target_id)
                    if t_card and target_id not in [c.card_id for c in related]:
                        related.append(t_card)
            finally:
                conn.close()

        return related"""

content = content.replace("""    def get_related_cards(self, card_id: str) -> List[KnowledgeCard]:
        \"\"\"Retrieves linked parent and related cards of a given card.\"\"\"
        card = self.get_card(card_id)
        if not card:
            return []
        related = []
        for p_id in card.parent_card_ids:
            p_card = self.get_card(p_id)
            if p_card:
                related.append(p_card)
        for r_id in card.related_card_ids:
            r_card = self.get_card(r_id)
            if r_card:
                related.append(r_card)
        return related""", replacement)

with open(filepath, 'w') as f:
    f.write(content)
