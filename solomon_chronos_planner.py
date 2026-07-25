import heapq
from typing import Dict, List, Tuple, Callable, Any, Optional

class ChronosNode:
    """Represents a state in time within the temporal graph."""
    def __init__(self, state_id: str, state_data: Any, cost: float = 0.0, heuristic: float = 0.0):
        self.state_id = state_id
        self.state_data = state_data
        self.cost = cost           # g(n): Cost from start to this node
        self.heuristic = heuristic # h(n): Estimated cost to goal
        self.parent: Optional['ChronosNode'] = None
        self.action_from_parent: Optional[str] = None

    def get_f_score(self) -> float:
        """f(n) = g(n) + h(n)"""
        return self.cost + self.heuristic

    def __lt__(self, other: 'ChronosNode'):
        return self.get_f_score() < other.get_f_score()


class ChronosTemporalPlanner:
    """
    Chronos Temporal Planner.
    Uses retrocausal execution (backward A* search from a perfect end-state)
    and graph-based temporal rewinding to recover from failures without complete restarts.
    """
    def __init__(self):
        self.temporal_graph: Dict[str, List[Tuple[str, float, str]]] = {} # state_id -> [(neighbor_state_id, cost, action), ...]
        self.heuristic_fn: Optional[Callable[[Any, Any], float]] = None

    def add_transition(self, from_state: str, to_state: str, cost: float, action: str):
        """Adds a directed transition to the temporal graph."""
        if from_state not in self.temporal_graph:
            self.temporal_graph[from_state] = []
        self.temporal_graph[from_state].append((to_state, cost, action))

    def set_heuristic(self, heuristic_fn: Callable[[Any, Any], float]):
        """Sets the heuristic function for A*."""
        self.heuristic_fn = heuristic_fn

    def retrocausal_plan(self, start_state: str, goal_state: str, state_data_lookup: Callable[[str], Any]) -> Optional[List[str]]:
        """
        Performs retrocausal planning.
        In true retrocausal form, we search backward from the goal_state to the start_state.
        This means we reverse the edges of our graph during search.
        """
        # Build reverse graph on the fly
        reverse_graph: Dict[str, List[Tuple[str, float, str]]] = {}
        for src, edges in self.temporal_graph.items():
            for dst, cost, action in edges:
                if dst not in reverse_graph:
                    reverse_graph[dst] = []
                reverse_graph[dst].append((src, cost, action)) # Store original action that takes src -> dst

        open_list = []
        # In retrocausal search, start at the GOAL
        goal_data = state_data_lookup(goal_state)
        start_node = ChronosNode(goal_state, goal_data, cost=0.0)

        # Heuristic estimates cost from current node to true start_state
        if self.heuristic_fn:
            start_node.heuristic = self.heuristic_fn(goal_data, state_data_lookup(start_state))

        heapq.heappush(open_list, start_node)

        g_scores = {goal_state: 0.0}
        closed_set = set()

        while open_list:
            current_node = heapq.heappop(open_list)

            # If we reached the true start state by searching backwards
            if current_node.state_id == start_state:
                return self._reconstruct_forward_plan(current_node)

            closed_set.add(current_node.state_id)

            neighbors = reverse_graph.get(current_node.state_id, [])
            for neighbor_id, cost, action in neighbors:
                if neighbor_id in closed_set:
                    continue

                tentative_g_score = current_node.cost + cost

                if neighbor_id not in g_scores or tentative_g_score < g_scores[neighbor_id]:
                    g_scores[neighbor_id] = tentative_g_score
                    neighbor_data = state_data_lookup(neighbor_id)
                    neighbor_node = ChronosNode(neighbor_id, neighbor_data, cost=tentative_g_score)
                    neighbor_node.parent = current_node
                    neighbor_node.action_from_parent = action # The action that took neighbor -> current in forward time

                    if self.heuristic_fn:
                        neighbor_node.heuristic = self.heuristic_fn(neighbor_data, state_data_lookup(start_state))

                    heapq.heappush(open_list, neighbor_node)

        return None # No path found

    def _reconstruct_forward_plan(self, node: ChronosNode) -> List[str]:
        """
        Reconstructs the forward plan.
        Because we searched backwards from goal to start, 'node' is the start state,
        and following parent pointers takes us to the goal state.
        """
        plan = []
        current = node
        while current.parent:
            plan.append(current.action_from_parent)
            current = current.parent
        return plan

    def temporal_rewind(self, current_plan: List[str], failed_step_index: int) -> Tuple[List[str], str]:
        """
        Simulates temporal rewinding when a failure occurs.
        Instead of completely restarting, we rewind to the last successful state (node before failure).
        Returns the actions executed up to the failure point, and the id of the divergence state.
        In a full system, this would trigger a re-plan from the divergence point.
        """
        if failed_step_index == 0:
             return [], "start_state_divergence"

        successful_actions = current_plan[:failed_step_index]
        return successful_actions, "divergence_point_after_action_" + str(failed_step_index-1)
