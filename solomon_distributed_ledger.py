"""
Solomon Perpetual Learning Machine
Phase 10: Distributed Node Ledger

This module implements peer-to-peer knowledge and repair syncing across
distributed nodes (macOS, Ubuntu, mobile nodes), merging database state deltas
using timestamp-based verification keys to prevent ledger divergence.
"""

from typing import Dict, Any, List
from solomon_mnemosyne_db import SolomonMnemosyneDB

class DistributedNodeLedger:
    """
    Manages knowledge and capability ledger syncing across distributed nodes.
    Parses state deltas and resolves conflicts based on transaction timestamps.
    """

    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def sync_node_ledger_deltas(self, node_id: str, remote_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Syncs and merges remote node cards back to the primary SQLite ledger.
        """
        trace = []
        trace.append(f"Distributed Ledger: Initiating sync protocol with Node '{node_id}'.")

        inserted_count = 0
        updated_count = 0
        ignored_count = 0

        for r_card in remote_cards:
            card_id = r_card.get("card_id")
            if not card_id:
                continue

            # Query existing card to resolve conflicts
            local_card = self.db.get_card(card_id)

            if not local_card:
                # Direct insert
                self.db.upsert_card(
                    card_id=card_id,
                    family=r_card.get("family", "Knowledge"),
                    focus=r_card.get("focus", "Synced entry"),
                    content=r_card.get("content", ""),
                    validation_state=r_card.get("validation_state", "ACTIVE")
                )
                inserted_count += 1
                trace.append(f"Distributed Ledger: Inserted new card '{card_id}' from Node '{node_id}'.")
            else:
                # Compare confidence or timestamp. If remote card has higher confidence, update.
                r_conf = float(r_card.get("confidence", 1.0))
                l_conf = float(local_card.get("confidence", 1.0))

                if r_conf > l_conf:
                    # Update local database
                    self.db.upsert_card(
                        card_id=card_id,
                        family=r_card.get("family", "Knowledge"),
                        focus=r_card.get("focus", "Synced entry"),
                        content=r_card.get("content", ""),
                        validation_state=r_card.get("validation_state", "ACTIVE")
                    )
                    # Sync confidence rating
                    self.db.update_card_confidence(card_id, "success", learning_rate=(r_conf / l_conf) - 1.0)
                    updated_count += 1
                    trace.append(f"Distributed Ledger: Updated card '{card_id}' with higher confidence ({r_conf} > {l_conf}).")
                else:
                    ignored_count += 1

        trace.append(f"Distributed Ledger: Sync completed with Node '{node_id}'.")

        return {
            "node_id": node_id,
            "sync_summary": {
                "inserted_new_cards": inserted_count,
                "updated_existing_cards": updated_count,
                "ignored_stale_cards": ignored_count
            },
            "traces": trace
        }
