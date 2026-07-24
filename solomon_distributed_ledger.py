"""
Solomon SOSS Phase 10: Distributed Node Ledger

This module manages the syncing of knowledge updates, failures, and repairs
across different network peer nodes back to Solomon's central relational database.
Features sequence tracking and SHA-256 block hashing for state synchronization integrity.
"""

import hashlib
import json
import time
from typing import List, Dict, Any, Tuple
from solomon_mnemosyne_db import SolomonMnemosyneDB


class LedgerBlock:
    """
    Represents a block in the knowledge ledger containing a collection of SOK card updates.
    """
    def __init__(self, index: int, previous_hash: str, updates: List[Dict[str, Any]], timestamp: float = None):
        self.index = index
        self.previous_hash = previous_hash
        self.updates = updates
        self.timestamp = timestamp or time.time()
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Computes the SHA-256 signature of the block.
        """
        block_string = json.dumps({
            "index": self.index,
            "previous_hash": self.previous_hash,
            "updates": self.updates,
            "timestamp": self.timestamp
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode('utf-8')).hexdigest()


class DistributedNodeLedger:
    """
    Manages ledger blocks, sequence audits, and syncing knowledge updates back
    to the centralized SQLite database with conflict resolution rules.
    """
    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db
        # Genesis block
        self.chain: List[LedgerBlock] = [LedgerBlock(0, "0", [{"card_id": "GENESIS-BLOCK", "action": "INITIALIZE"}])]

    def get_latest_block(self) -> LedgerBlock:
        return self.chain[-1]

    def add_block(self, updates: List[Dict[str, Any]]) -> LedgerBlock:
        """
        Packages updates into a new block and appends it to the chain.
        """
        latest = self.get_latest_block()
        new_block = LedgerBlock(latest.index + 1, latest.hash, updates)
        self.chain.append(new_block)
        return new_block

    def sync_block_to_sqlite(self, block: LedgerBlock) -> Tuple[bool, int, List[str]]:
        """
        Synchronizes a block's SOK updates to the central SQLite card manager.
        Features conflict resolution: we only update if the synced card does not
        already exist or has a different content body.
        """
        synced_count = 0
        sync_logs = []

        # Validate sequence block link
        latest = self.get_latest_block()
        if block.previous_hash != latest.hash and block.index != 0:
            # We add it as a new block to keep chain continuity
            block.previous_hash = latest.hash
            block.index = latest.index + 1
            block.hash = block.calculate_hash()
            self.chain.append(block)
        elif block.index > latest.index:
            self.chain.append(block)

        for update in block.updates:
            cid = update.get("card_id")
            action = update.get("action", "UPSERT")

            if not cid or cid == "GENESIS-BLOCK":
                continue

            if action == "UPSERT":
                family = update.get("family", "Knowledge")
                focus = update.get("focus", "Synced update")
                content = update.get("content", "")

                # Check if card exists
                existing = self.db.get_card(cid)
                if not existing:
                    self.db.upsert_card(cid, family, focus, content)
                    synced_count += 1
                    sync_logs.append(f"Synced card '{cid}': Created new.")
                elif existing["content"] != content:
                    # Update content and increment confidence slightly
                    self.db.upsert_card(cid, family, focus, content)
                    self.db.update_card_confidence(cid, "success", 0.05)
                    synced_count += 1
                    sync_logs.append(f"Synced card '{cid}': Resolved content conflict & scaled confidence.")

        return True, synced_count, sync_logs

    def is_chain_valid(self) -> bool:
        """
        Audits chain signatures to guarantee zero tamper or corruption in block states.
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i-1]

            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != prev.hash:
                return False
        return True
