from typing import List, Dict, Any, Set, Tuple
import sqlite3

class TopologicalResolutionEngine:
    def __init__(self, db_path: str = "solomon_mnemosyne_demo.db"):
        self.db_path = db_path

    def resolve_plan(self, primary_card_ids: List[str], confidence_threshold: float = 0.5) -> Dict[str, Any]:
        """
        Traverses the graph starting from primary cards.
        Follows dependencies, collects safeguards and warnings.
        Detects circular dependencies.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        visited: Set[str] = set()
        recursion_stack: Set[str] = set()

        resolved_sequence: List[str] = []
        warnings: List[Dict[str, str]] = []
        safeguards: List[Dict[str, str]] = []
        explanations: List[str] = []

        def dfs(card_id: str) -> bool:
            if card_id in recursion_stack:
                warnings.append({
                    "type": "CIRCULAR_DEPENDENCY",
                    "message": f"Circular dependency detected involving card '{card_id}'."
                })
                return False

            if card_id in visited:
                return True

            recursion_stack.add(card_id)

            try:
                # Fetch card details to check confidence
                cursor.execute("SELECT confidence, family FROM knowledge_cards WHERE card_id = ?", (card_id,))
                card_row = cursor.fetchone()
                if not card_row:
                    warnings.append({
                        "type": "MISSING_CARD",
                        "message": f"Referenced card '{card_id}' does not exist."
                    })
                    recursion_stack.remove(card_id)
                    return True # Skip missing, but don't fail entire graph

                confidence = float(card_row["confidence"])

                # Fetch outgoing links
                cursor.execute("""
                    SELECT target_id, relationship_type
                    FROM card_links
                    WHERE source_id = ?
                """, (card_id,))
                links = cursor.fetchall()

                # Process DEPENDS_ON first to ensure topological ordering
                for link in links:
                    target_id = link["target_id"]
                    rel_type = link["relationship_type"]

                    if rel_type == "DEPENDS_ON":
                        explanations.append({"action": "dependency_chain", "source": card_id, "target": target_id})
                        if not dfs(target_id):
                            # Circular dependency caught deeper
                            pass

                    elif rel_type == "PREVENTS":
                        safeguards.append({
                            "source": card_id,
                            "target": target_id,
                            "message": f"Action defined in '{card_id}' PREVENTS '{target_id}'."
                        })

                    elif rel_type == "CONFLICTS_WITH":
                        warnings.append({
                            "type": "CONFLICT",
                            "message": f"Card '{card_id}' conflicts with '{target_id}'."
                        })

                    elif rel_type in ("REPAIRS", "CAUSED_FAILURE"):
                        explanations.append({"action": "history_note", "source": card_id, "target": target_id, "type": rel_type})

            except sqlite3.Error as e:
                warnings.append({"type": "DB_ERROR", "message": str(e)})

            recursion_stack.remove(card_id)
            visited.add(card_id)
            resolved_sequence.append(card_id)
            return True

        # Run DFS from all primary targets
        for cid in primary_card_ids:
            dfs(cid)

        conn.close()

        return {
            "status": "success",
            "execution_sequence": resolved_sequence,
            "safeguards_injected": safeguards,
            "warnings": warnings,
            "explanations": explanations
        }
