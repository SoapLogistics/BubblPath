import logging
from typing import Any

from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.models.card import KnowledgeCard

logger = logging.getLogger("relation_graph")


class RelationGraph:
    def __init__(self, repository: CardRepository, max_recursion_depth: int = 50):
        self.repository = repository
        self.max_recursion_depth = max_recursion_depth

    def get_all_outgoing_links(self, card: KnowledgeCard) -> list[tuple[str, str]]:
        """
        Retrieves all outgoing link relations from a given card.
        Returns a list of tuples: (target_card_id, link_type)
        """
        links = []
        for p_id in card.parent_card_ids:
            links.append((p_id, "PARENT"))
        for r_id in card.related_card_ids:
            links.append((r_id, "RELATED"))
        if card.supersedes:
            links.append((card.supersedes, "SUPERSEDES"))

        custom_links = card.extra_metadata.get("links", [])
        for cl in custom_links:
            target_id = cl.get("target_id")
            link_type = cl.get("link_type")
            if target_id and link_type:
                links.append((target_id, link_type))

        return links

    def find_dependency_chain(self, card_id: str, relation_type: str = "DEPENDS_ON") -> list[str]:
        """
        Traverses DEPENDS_ON relations recursively to find the full dependency chain.
        Strictly limits recursion depth to prevent Stack Overflow / thread stack exhaustion.
        Guards against circular dependencies cleanly.
        """
        chain = []
        visited = set()

        def traverse(current_id: str, current_depth: int):
            if current_depth > self.max_recursion_depth:
                logger.warning(f"[RelationGraph] Recursion Limit Alert: Aborting traversal of {current_id} to prevent stack exhaustion.")
                return

            if current_id in visited:
                return
            visited.add(current_id)

            card = self.repository.get_card(current_id)
            if not card:
                return

            outgoing = self.get_all_outgoing_links(card)
            for target_id, l_type in outgoing:
                if l_type.upper() == relation_type.upper():
                    traverse(target_id, current_depth + 1)

            if current_id not in chain:
                chain.append(current_id)

        traverse(card_id, 1)
        return chain[:-1] if chain else []

    def get_subgraph(self, card_id: str, max_depth: int = 2) -> dict[str, Any]:
        """
        Retrieves the semantic subgraph surrounding a given card using BFS traversal.
        Strictly enforces max BFS queue size to prevent memory exhaustion on giant networks.
        """
        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, str]] = []

        queue = [(card_id, 0)]
        visited = {card_id}
        max_bfs_nodes = 500

        while queue:
            if len(nodes) >= max_bfs_nodes:
                logger.warning(f"[RelationGraph] BFS Nodes Limit Hit ({max_bfs_nodes}). Terminating subgraph search pre-emptively.")
                break

            curr_id, depth = queue.pop(0)

            card = self.repository.get_card(curr_id)
            if not card:
                continue

            nodes[curr_id] = {
                "card_id": card.card_id,
                "card_type": card.card_type,
                "title": card.title,
                "status": card.status,
                "confidence": card.confidence
            }

            if depth >= max_depth:
                continue

            outgoing = self.get_all_outgoing_links(card)
            for target_id, l_type in outgoing:
                edges.append({
                    "source": curr_id,
                    "target": target_id,
                    "type": l_type
                })

                if target_id not in visited:
                    visited.add(target_id)
                    queue.append((target_id, depth + 1))

        return {
            "nodes": list(nodes.values()),
            "edges": edges
        }
