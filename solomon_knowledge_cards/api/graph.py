from typing import List, Dict, Any, Set, Tuple, Optional
from solomon_knowledge_cards.api.repository import CardRepository
from solomon_knowledge_cards.models.card import KnowledgeCard

class RelationGraph:
    def __init__(self, repository: CardRepository):
        self.repository = repository

    def get_all_outgoing_links(self, card: KnowledgeCard) -> List[Tuple[str, str]]:
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

        # Add custom links stored in extra_metadata
        custom_links = card.extra_metadata.get("links", [])
        for cl in custom_links:
            target_id = cl.get("target_id")
            link_type = cl.get("link_type")
            if target_id and link_type:
                links.append((target_id, link_type))

        return links

    def find_dependency_chain(self, card_id: str, relation_type: str = "DEPENDS_ON") -> List[str]:
        """
        Traverses DEPENDS_ON relations recursively to find the full dependency chain.
        Guards against circular dependencies cleanly.
        """
        chain = []
        visited = set()

        def traverse(current_id: str):
            if current_id in visited:
                # Circular dependency detected, break gracefully
                return
            visited.add(current_id)

            card = self.repository.get_card(current_id)
            if not card:
                return

            # Find outgoing links of specific relation_type
            outgoing = self.get_all_outgoing_links(card)
            for target_id, l_type in outgoing:
                if l_type.upper() == relation_type.upper():
                    # Traverse dependency first (post-order traversal to build correct topological order)
                    traverse(target_id)

            if current_id not in chain:
                chain.append(current_id)

        traverse(card_id)
        # Reverse chain to return execution order (from first dependency to leaf target)
        return chain[:-1] if chain else []

    def get_subgraph(self, card_id: str, max_depth: int = 2) -> Dict[str, Any]:
        """
        Retrieves the semantic subgraph surrounding a given card using BFS traversal.
        Returns a dictionary representing nodes and edge links.
        """
        nodes: Dict[str, Dict[str, Any]] = {}
        edges: List[Dict[str, str]] = []

        # Queue format: (card_id, current_depth)
        queue = [(card_id, 0)]
        visited = {card_id}

        while queue:
            curr_id, depth = queue.pop(0)

            card = self.repository.get_card(curr_id)
            if not card:
                continue

            # Register node
            nodes[curr_id] = {
                "card_id": card.card_id,
                "card_type": card.card_type,
                "title": card.title,
                "status": card.status,
                "confidence": card.confidence
            }

            if depth >= max_depth:
                continue

            # Traverse outgoing links
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
