import os

filepath = 'solomon_knowledge_cards/storage/db.py'
with open(filepath, 'r') as f:
    content = f.read()

replacement = """                # Remove existing links of link_type "PARENT" or "RELATED" from this source_id
                conn.execute("DELETE FROM card_links WHERE source_id = ? AND link_type IN ('PARENT', 'RELATED')", (card.card_id,))
                for p_id in card.parent_card_ids:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'PARENT')", (card.card_id, p_id))
                for r_id in card.related_card_ids:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'RELATED')", (card.card_id, r_id))
                if card.supersedes:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'SUPERSEDES')", (card.card_id, card.supersedes))

                # Semantic Graph Relations can be injected directly into db via direct SQL if needed outside of standard card update
                # Or handled separately by repository layer."""

content = content.replace("""                # Remove existing links of link_type "PARENT" or "RELATED" from this source_id
                conn.execute("DELETE FROM card_links WHERE source_id = ? AND link_type IN ('PARENT', 'RELATED')", (card.card_id,))
                for p_id in card.parent_card_ids:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'PARENT')", (card.card_id, p_id))
                for r_id in card.related_card_ids:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'RELATED')", (card.card_id, r_id))
                if card.supersedes:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, 'SUPERSEDES')", (card.card_id, card.supersedes))""", replacement)

with open(filepath, 'w') as f:
    f.write(content)
