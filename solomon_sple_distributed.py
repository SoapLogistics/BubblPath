import logging
import uuid
from typing import Dict, Any, List

logger = logging.getLogger("SPLE_Swarm")

class SwarmNode:
    def __init__(self, role: str):
        self.node_id = str(uuid.uuid4())[:8]
        self.role = role
        self.status = "idle"

class DistributedSwarmManager:
    """
    Handles Part 7 of the SPLE blueprint: Distributed Learning.
    Coordinates multiple specialized agents (Mock implementation).
    """
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        # Pre-populate with some specialist nodes
        self.register_node("Critic")
        self.register_node("Coder")
        self.register_node("Researcher")
        logger.info("Distributed Swarm Manager initialized with base nodes.")

    def register_node(self, role: str) -> str:
        node = SwarmNode(role)
        self.nodes[node.node_id] = node
        logger.debug(f"Registered new swarm node [{node.node_id}] with role: {role}")
        return node.node_id

    def delegate_task(self, task_description: str, required_role: str) -> Dict[str, Any]:
        """Finds an available node with the required role and assigns the task."""
        logger.info(f"Attempting to delegate task '{task_description}' requiring role '{required_role}'")

        available_nodes = [n for n in self.nodes.values() if n.role == required_role and n.status == "idle"]

        if not available_nodes:
            logger.warning(f"No available nodes found for role: {required_role}. Spawning new node.")
            new_node_id = self.register_node(required_role)
            node = self.nodes[new_node_id]
        else:
            node = available_nodes[0]

        node.status = "busy"
        logger.info(f"Task delegated to Node [{node.node_id}].")

        # Simulate task completion
        node.status = "idle"

        return {
            "status": "completed",
            "node_id": node.node_id,
            "result": f"Task '{task_description}' executed by {required_role} agent."
        }

    def request_consensus(self, topic: str, participating_roles: List[str]) -> str:
        """Simulates Byzantine Fault Tolerance / Voting among nodes."""
        logger.info(f"Requesting swarm consensus on topic: {topic}")
        votes = []
        for role in participating_roles:
             # Simulate a vote (usually agree, occasionally disagree)
             import random
             vote = "Agree" if random.random() > 0.1 else "Disagree"
             votes.append(vote)

        consensus_result = "Approved" if votes.count("Agree") > len(votes) / 2 else "Rejected"
        logger.info(f"Consensus reached: {consensus_result} (Votes: {votes})")
        return consensus_result
