import os

filepath = 'solomon_knowledge_cards/api/repository.py'
with open(filepath, 'r') as f:
    content = f.read()

replacement = """        if link_type == "PARENT":
            if target_id not in source_card.parent_card_ids:
                source_card.parent_card_ids.append(target_id)
        elif link_type == "RELATED":
            if target_id not in source_card.related_card_ids:
                source_card.related_card_ids.append(target_id)
        elif link_type in ("DEPENDS_ON", "PREVENTS", "ENHANCES"):
            with self.db_manager._lock:
                conn = self.db_manager._get_connection()
                try:
                    conn.execute("INSERT OR IGNORE INTO card_links (source_id, target_id, link_type) VALUES (?, ?, ?)", (source_id, target_id, link_type))
                    conn.commit()
                finally:
                    conn.close()
            return # Don't need to re-save the source card fully
        else:
            raise ValueError(f"Unsupported link type: {link_type}")"""

content = content.replace("""        if link_type == "PARENT":
            if target_id not in source_card.parent_card_ids:
                source_card.parent_card_ids.append(target_id)
        elif link_type == "RELATED":
            if target_id not in source_card.related_card_ids:
                source_card.related_card_ids.append(target_id)
        elif link_type in ("DEPENDS_ON", "PREVENTS", "ENHANCES"):
            # We track these graph relations directly in the db layer for now
            # They don't have dedicated lists on the model, but the DB allows link_type strings.
            pass
        else:
            raise ValueError(f"Unsupported link type: {link_type}")""", replacement)

with open(filepath, 'w') as f:
    f.write(content)
