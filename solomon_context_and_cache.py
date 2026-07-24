"""
Solomon Perpetual Learning Machine
Phases 24, 25, 28, 33: Context Isolation & Cache Compaction

Implements context isolation partitions, LRU KV cache page eviction managers,
P2P RAG synchronizers, and virtual compressed KV page allocators.
"""

import time
import json
from typing import Dict, List, Any
from solomon_mnemosyne_db import SolomonMnemosyneDB

class MultiTenantContextIsolator:
    """
    Quarantines and separates prompt histories between tenants to prevent cross-leakage.
    """
    def __init__(self):
        self.partitions: Dict[str, List[Dict[str, str]]] = {}

    def get_tenant_context(self, tenant_id: str) -> List[Dict[str, str]]:
        return self.partitions.setdefault(tenant_id, [])

    def append_message(self, tenant_id: str, role: str, content: str):
        context = self.get_tenant_context(tenant_id)
        context.append({"role": role, "content": content})


class KVCachePageEvictionManager:
    """
    Monitors cache pages and evicts the oldest, low-importance pages when limits are breached.
    """
    def __init__(self, max_pages: int = 100):
        self.max_pages = max_pages
        # page_id -> (timestamp, access_count, content)
        self.pages: Dict[str, tuple] = {}

    def access_page(self, page_id: str, content: str):
        timestamp = time.time()
        if page_id in self.pages:
            old_ts, count, _ = self.pages[page_id]
            self.pages[page_id] = (timestamp, count + 1, content)
        else:
            if len(self.pages) >= self.max_pages:
                self.evict_lru_page()
            self.pages[page_id] = (timestamp, 1, content)

    def evict_lru_page(self) -> str:
        # Find page with lowest timestamp
        lru_id = min(self.pages.keys(), key=lambda k: self.pages[k][0])
        del self.pages[lru_id]
        return lru_id


class P2PRAGSyncer:
    """
    Synchronizes semantic representations across peer node ledgers with conflict resolution.
    """
    def __init__(self, db: SolomonMnemosyneDB):
        self.db = db

    def sync_peer_card_updates(self, peer_nodes_cards: List[Dict[str, Any]]) -> Dict[str, Any]:
        synced_ids = []
        for card in peer_nodes_cards:
            card_id = card["card_id"]
            existing = self.db.get_card(card_id)
            # Resolve conflict: Keep local card if confidence is higher, otherwise update
            if not existing or card.get("confidence", 1.0) > existing.get("confidence", 1.0):
                self.db.upsert_card(
                    card_id=card_id,
                    family=card["family"],
                    focus=card.get("focus", ""),
                    content=card["content"],
                    status="ACTIVE"
                )
                self.db.update_card_status(card_id, "ACTIVE")
                synced_ids.append(card_id)
        return {
            "status": "success",
            "synced_cards_count": len(synced_ids),
            "synced_card_ids": synced_ids
        }


class VirtualKVPageAllocator:
    """
    Virtualizes physical key-value memory blocks into virtual pages (PagedAttention).
    """
    def __init__(self, page_size_mb: float = 4.0):
        self.page_size_mb = page_size_mb
        self.allocated_blocks = 0

    def allocate_virtual_pages(self, size_mb: float) -> int:
        pages_needed = int(size_mb / self.page_size_mb) + 1
        self.allocated_blocks += pages_needed
        return pages_needed
