import logging
import uuid
from typing import Dict, Any, List, Optional

logger = logging.getLogger("SPLE_PAT_Memory")

class PATNode:
    """A node in the Progressive Abstraction Tree."""
    def __init__(self, content: str, level: int, is_leaf: bool = False):
        self.node_id = str(uuid.uuid4())[:8]
        self.content = content
        self.level = level  # 0 = raw episodic fact, higher = more abstract
        self.is_leaf = is_leaf
        self.children_ids: List[str] = []
        self.parent_id: Optional[str] = None

    def to_dict(self):
        return {
            "id": self.node_id,
            "content": self.content,
            "level": self.level,
            "children": self.children_ids
        }

class ProgressiveAbstractionTree:
    """
    Handles deep memory consolidation (Part 8).
    Implements Progressive Abstraction Trees (PATs) where raw episodic facts
    (leaves) are clustered and synthesized into generalized semantic rules (parents).
    """
    def __init__(self):
        self.nodes: Dict[str, PATNode] = {}
        self.root_nodes: List[str] = [] # Highest level abstractions
        logger.info("Progressive Abstraction Tree (PAT) initialized.")

    def ingest_raw_fact(self, fact_content: str) -> str:
        """Ingests a raw, level 0 episodic fact."""
        node = PATNode(fact_content, level=0, is_leaf=True)
        self.nodes[node.node_id] = node
        self.root_nodes.append(node.node_id) # Initially, it is its own root
        logger.debug(f"Ingested raw fact: [{node.node_id}]")
        return node.node_id

    def abstract_cluster(self, child_node_ids: List[str], generalized_concept: str) -> str:
        """
        Simulates the 'Sleep Consolidation' phase where an LLM analyzes multiple
        similar raw facts and generates a higher-level abstract rule that governs them.
        """
        logger.info(f"Abstracting cluster of {len(child_node_ids)} nodes into concept: '{generalized_concept}'")

        # Determine the level of the new parent (max child level + 1)
        max_child_level = max([self.nodes[cid].level for cid in child_node_ids if cid in self.nodes])
        parent_node = PATNode(generalized_concept, level=max_child_level + 1, is_leaf=False)

        for cid in child_node_ids:
            if cid in self.nodes:
                child = self.nodes[cid]
                child.parent_id = parent_node.node_id
                parent_node.children_ids.append(child.node_id)
                # If child was a root, it no longer is
                if child.node_id in self.root_nodes:
                    self.root_nodes.remove(child.node_id)

        self.nodes[parent_node.node_id] = parent_node
        self.root_nodes.append(parent_node.node_id)

        logger.info(f"Created abstract parent node [{parent_node.node_id}] at Level {parent_node.level}")
        return parent_node.node_id

    def traverse_abstraction(self, node_id: str, direction: str = "up") -> List[Dict[str, Any]]:
        """
        Traverses the tree either 'up' (towards abstraction/generalization)
        or 'down' (towards concrete episodic facts).
        """
        path = []
        current = self.nodes.get(node_id)

        while current:
            path.append(current.to_dict())
            if direction == "up" and current.parent_id:
                current = self.nodes.get(current.parent_id)
            else:
                 # 'down' traversal requires a more complex search (e.g., BFS), returning simple path for now
                 break

        return path

    def get_highest_abstractions(self) -> List[Dict[str, Any]]:
        """Returns the current 'worldview' - the highest level abstract concepts."""
        return [self.nodes[rid].to_dict() for rid in self.root_nodes if rid in self.nodes]
