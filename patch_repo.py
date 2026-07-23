import os

filepath = 'solomon_knowledge_cards/api/repository.py'
with open(filepath, 'r') as f:
    content = f.read()

# Make create_card and update_card generate embeddings automatically
create_card_replacement = """    def create_card(self, card: KnowledgeCard, creator: str = "system", reason: Optional[str] = None) -> None:
        \"\"\"Creates a new card in the storage layer.\"\"\"
        if not card.embedding:
            combined_text = f"{card.title} {card.summary} {card.why_created} {card.problem_solved} {card.body}"
            card.embedding = self.embedder.generate_embedding(combined_text)
        self.db_manager.store_card(card, updater=creator, reason=reason or "Initial creation")"""

update_card_replacement = """    def update_card(self, card: KnowledgeCard, updater: str = "system", reason: Optional[str] = None) -> None:
        \"\"\"Updates an existing card in the database, appending to revision history.\"\"\"
        existing = self.db_manager.get_card(card.card_id)
        if not existing:
            raise ValueError(f"Card {card.card_id} does not exist. Use create_card first.")

        # Re-generate embedding on update
        combined_text = f"{card.title} {card.summary} {card.why_created} {card.problem_solved} {card.body}"
        card.embedding = self.embedder.generate_embedding(combined_text)

        self.db_manager.store_card(card, updater=updater, reason=reason or "Card update")"""

content = content.replace("""    def create_card(self, card: KnowledgeCard, creator: str = "system", reason: Optional[str] = None) -> None:
        \"\"\"Creates a new card in the storage layer.\"\"\"
        self.db_manager.store_card(card, updater=creator, reason=reason or "Initial creation")""", create_card_replacement)

content = content.replace("""    def update_card(self, card: KnowledgeCard, updater: str = "system", reason: Optional[str] = None) -> None:
        \"\"\"Updates an existing card in the database, appending to revision history.\"\"\"
        existing = self.db_manager.get_card(card.card_id)
        if not existing:
            raise ValueError(f"Card {card.card_id} does not exist. Use create_card first.")
        self.db_manager.store_card(card, updater=updater, reason=reason or "Card update")""", update_card_replacement)

with open(filepath, 'w') as f:
    f.write(content)
