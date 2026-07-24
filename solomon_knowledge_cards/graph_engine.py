import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger("solomon_graph_engine")

class KnowledgeGraph:
    """Project Prometheus topological Knowledge Graph and dependency resolution engine."""
    def __init__(self, runtime):
        self.runtime = runtime

    def load_graph(self) -> tuple:
        """
        Loads all active cards and relational links from the SQLite database.
        Returns a tuple (nodes, edges) where nodes is a dict mapping card_id -> card,
        and edges is a list of link dicts.
        """
        conn = self.runtime.db.get_connection()
        nodes = {}
        edges = []
        try:
            # Fetch all cards
            cursor_cards = conn.execute("SELECT * FROM knowledge_cards")
            for row in cursor_cards.fetchall():
                c = dict(row)
                nodes[c["card_id"]] = c

            # Fetch all links
            cursor_links = conn.execute("SELECT * FROM card_links")
            for row in cursor_links.fetchall():
                edges.append(dict(row))
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {str(e)}")
        finally:
            conn.close()
        return nodes, edges

    def resolve_topology(self) -> List[str]:
        """
        Performs a Kahn's topological sort on card nodes based on DEPENDS_ON relations.
        Returns a list of card_ids ordered by procedural dependencies (prerequisites first).
        """
        nodes, edges = self.load_graph()

        # Build adjacency list and compute in-degrees for DEPENDS_ON relationships
        adj = {cid: set() for cid in nodes}
        in_degree = {cid: 0 for cid in nodes}

        for edge in edges:
            if edge["relationship_type"] == "DEPENDS_ON":
                u = edge["source_id"] # source_id depends on target_id
                v = edge["target_id"] # target_id is the prerequisite of source_id
                # v -> u edge represents dependency
                if v in adj and u in adj:
                    if u not in adj[v]:
                        adj[v].add(u)
                        in_degree[u] += 1

        # Queue nodes with in-degree 0 (no prerequisites)
        queue = [cid for cid in nodes if in_degree[cid] == 0]
        topo_order = []

        while queue:
            # Sort to guarantee deterministic order
            queue.sort()
            curr = queue.pop(0)
            topo_order.append(curr)

            for neighbor in adj[curr]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return topo_order

    def get_failure_safeguards_for_query(self, query: str, clearance: str) -> List[Dict[str, Any]]:
        """
        Scours matching cards for a query and clearance. For each matching node,
        traverses the links to find related FAILURE or REPAIR cards, extracting
        root causes and repair actions to serve as pre-emptive safeguards.
        """
        # 1. Retrieve cards matching user intent
        bundle = self.runtime.retrieve_context(query=query, clearance=clearance, limit=3)
        retrieved_ids = bundle["retrieved_card_ids"]
        if not retrieved_ids:
            return []

        nodes, edges = self.load_graph()
        safeguards = []
        visited = set()

        for card_id in retrieved_ids:
            # Find any linked FAILURE or REPAIR cards related to this node
            for edge in edges:
                linked_id = None
                if edge["source_id"] == card_id:
                    linked_id = edge["target_id"]
                elif edge["target_id"] == card_id:
                    linked_id = edge["source_id"]

                if linked_id and linked_id in nodes and linked_id not in visited:
                    linked_node = nodes[linked_id]
                    if linked_node["card_type"] in ("FAILURE", "REPAIR"):
                        visited.add(linked_id)
                        safeguards.append({
                            "card_id": linked_node["card_id"],
                            "title": linked_node["title"],
                            "summary": linked_node["summary"],
                            "body": linked_node["body"],
                            "relationship_type": edge["relationship_type"]
                        })
        return safeguards


class SelfStudyOptimizer:
    """SOSS Phase 6 Self-Study Optimizer Engine."""
    def __init__(self, runtime):
        self.runtime = runtime
        self.retrieval_threshold = 0.50

    def optimize_retrieval_thresholds(self, success_rate: float) -> Dict[str, Any]:
        """
        Dynamically tunes SOK search similarity thresholds based on downstream
        worker outcome feedback latency.
        """
        old_threshold = self.retrieval_threshold
        # If success rate is high (>85%), lower threshold slightly to broaden recall
        if success_rate > 0.85:
            self.retrieval_threshold = max(0.20, self.retrieval_threshold - 0.05)
        # If success rate is low, increase threshold to narrow matches to high-confidence cards
        else:
            self.retrieval_threshold = min(0.85, self.retrieval_threshold + 0.08)

        return {
            "old_threshold": round(old_threshold, 4),
            "new_threshold": round(self.retrieval_threshold, 4),
            "tuned_retrieval_gain": round(self.retrieval_threshold - old_threshold, 4),
            "feedback_success_rate": success_rate
        }


class PrometheusCuriosityEngine:
    """SOSS Phase 10 Prometheus Curiosity & Active Gap Discovery Engine."""
    def __init__(self, runtime):
        self.runtime = runtime

    def scan_for_knowledge_gaps(self) -> List[Dict[str, Any]]:
        """
        Proactively audits SOK card links to locate informational density gaps
        and return suggested research targets.
        """
        graph = KnowledgeGraph(self.runtime)
        nodes, edges = graph.load_graph()

        gaps = []
        for cid, node in nodes.items():
            # Check how many links connect to this card
            card_degree = 0
            for edge in edges:
                if edge["source_id"] == cid or edge["target_id"] == cid:
                    card_degree += 1

            # A degree of 0 means the card is completely isolated (isolated knowledge island!)
            if card_degree == 0:
                gaps.append({
                    "target_card_id": cid,
                    "target_title": node["title"],
                    "gap_detected": "Isolated Knowledge Node (0 linked references)",
                    "suggested_curiosity_subject": f"Establish semantic dependencies and links for: {node['title']}"
                })
        return gaps
