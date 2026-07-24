import sqlite3
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("solomon_knowledge_graph")

class KnowledgeGraph:
    """Project Prometheus topological Knowledge Graph and dependency resolution engine."""

    def __init__(self, db):
        """Initialize with an instance of SolomonMnemosyneDB."""
        self.db = db

    def load_graph(self) -> tuple:
        """
        Loads all active cards and relational links from the SQLite database.
        Returns a tuple (nodes, edges) where nodes is a dict mapping card_id -> card,
        and edges is a list of link dicts.
        """
        nodes = {}
        edges = []
        try:
            conn = sqlite3.connect(self.db.db_path)
            conn.row_factory = sqlite3.Row
            cursor_cards = conn.execute("SELECT * FROM knowledge_cards")
            for row in cursor_cards.fetchall():
                c = dict(row)
                nodes[c["card_id"]] = c

            cursor_links = conn.execute("SELECT * FROM card_links")
            for row in cursor_links.fetchall():
                edges.append(dict(row))
        except Exception as e:
            logger.error(f"Failed to load knowledge graph: {str(e)}")
        finally:
            if 'conn' in locals() and conn:
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

        # Include nodes that were not part of the dependencies (in case of cycles or disconnected nodes)
        for cid in sorted(nodes.keys()):
            if cid not in topo_order:
                topo_order.append(cid)

        return topo_order

    def reason_over_relationships(self, start_card_id: str) -> Dict[str, Any]:
        """
        Traverses relationships to build a comprehensive reasoning context for a card.
        Handles USES, REPLACES, SUPERSEDES, CONFLICTS_WITH, GENERATED_BY, and DEPENDS_ON.
        """
        nodes, edges = self.load_graph()

        if start_card_id not in nodes:
            return {"error": f"Card {start_card_id} not found."}

        context = {
            "target_card": nodes[start_card_id],
            "dependencies": [],      # DEPENDS_ON
            "uses": [],              # USES
            "replaces": [],          # REPLACES
            "supersedes": [],        # SUPERSEDES
            "conflicts_with": [],    # CONFLICTS_WITH
            "generated_by": [],      # GENERATED_BY
            "active_version": start_card_id # The card ID that should be used (e.g. if superseded, follow link)
        }

        # Follow REPLACES or SUPERSEDES chains to find the most active version
        current_id = start_card_id
        visited = set([current_id])

        # Determine if this card is superseded or replaced by checking incoming links
        found_newer = True
        while found_newer:
            found_newer = False
            for edge in edges:
                if edge["target_id"] == current_id and edge["relationship_type"] in ["REPLACES", "SUPERSEDES"]:
                    newer_id = edge["source_id"]
                    if newer_id not in visited and newer_id in nodes:
                        current_id = newer_id
                        visited.add(current_id)
                        found_newer = True
                        break

        context["active_version"] = current_id

        if current_id != start_card_id:
            context["target_card"] = nodes[current_id]

        # Gather relationships for the active version
        for edge in edges:
            src = edge["source_id"]
            tgt = edge["target_id"]
            rel = edge["relationship_type"]

            # If our active card is the source (outgoing relationships)
            if src == current_id and tgt in nodes:
                if rel == "DEPENDS_ON":
                    context["dependencies"].append(nodes[tgt])
                elif rel == "USES":
                    context["uses"].append(nodes[tgt])
                elif rel in ["REPLACES", "SUPERSEDES"]:
                    if rel == "REPLACES":
                        context["replaces"].append(nodes[tgt])
                    else:
                        context["supersedes"].append(nodes[tgt])
                elif rel == "CONFLICTS_WITH":
                    context["conflicts_with"].append(nodes[tgt])
                elif rel == "GENERATED_BY":
                    context["generated_by"].append(nodes[tgt])

            # If our active card is the target (incoming relationships)
            if tgt == current_id and src in nodes:
                if rel == "CONFLICTS_WITH":
                    # Conflict goes both ways conceptually
                    if nodes[src] not in context["conflicts_with"]:
                        context["conflicts_with"].append(nodes[src])

        return context

    def format_reasoning_for_llm(self, context: Dict[str, Any]) -> str:
        """
        Formats the resolved relational reasoning context into a strict text string for LLM injection.
        """
        if "error" in context:
            return context["error"]

        target = context["target_card"]
        lines = [
            f"--- KNOWLEDGE GRAPH REASONING CONTEXT ---",
            f"Active Focus Node: [{target['card_id']}] ({target['family']}) - {target['focus']}",
        ]

        if context["active_version"] != target["card_id"]:
            lines.append(f"WARNING: The originally requested node was superseded. Showing the most up-to-date active version.")

        if context["dependencies"]:
            lines.append("DEPENDENCIES (Must be resolved first):")
            for d in context["dependencies"]:
                lines.append(f"  - [{d['card_id']}] {d['focus']}")

        if context["uses"]:
            lines.append("USES (Tools/Concepts integrated):")
            for u in context["uses"]:
                lines.append(f"  - [{u['card_id']}] {u['focus']}")

        if context["replaces"] or context["supersedes"]:
            lines.append("REPLACES/SUPERSEDES (Legacy nodes deprecated by this node):")
            for r in context["replaces"] + context["supersedes"]:
                lines.append(f"  - [{r['card_id']}] {r['focus']}")

        if context["conflicts_with"]:
            lines.append("CONFLICTS (Do not use alongside):")
            for c in context["conflicts_with"]:
                lines.append(f"  - [{c['card_id']}] {c['focus']}")

        if context["generated_by"]:
            lines.append("GENERATED BY (Origin processes):")
            for g in context["generated_by"]:
                lines.append(f"  - [{g['card_id']}] {g['focus']}")

        lines.append("-----------------------------------------")
        return "\n".join(lines)
