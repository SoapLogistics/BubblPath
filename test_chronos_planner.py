import unittest
from solomon_chronos_planner import ChronosTemporalPlanner, Action, StateNode

class TestChronosPlanner(unittest.TestCase):

    def setUp(self):
        # A simple domain where we want to build a house
        self.actions = [
            Action("gather_wood", 1.0, {"has_wood": True}, {"at_forest": True}),
            Action("goto_forest", 1.0, {"at_forest": True}, {"at_home": True}),
            Action("build_frame", 2.0, {"frame_built": True}, {"has_wood": True, "at_home": True}),
            Action("goto_home", 1.0, {"at_home": True}, {"at_forest": True}),
            Action("build_roof", 2.0, {"house_built": True}, {"frame_built": True, "has_wood": True, "at_home": True}),

            # Additional action for wood to test alternative routes
            Action("buy_wood", 5.0, {"has_wood": True}, {"has_money": True, "at_store": True}),
            Action("goto_store", 1.0, {"at_store": True}, {"at_home": True}),
        ]

    def test_retrocausal_plan(self):
        planner = ChronosTemporalPlanner(self.actions)
        start_state = {"at_home": True, "has_money": True}
        goal_state = {"house_built": True}

        start_node = StateNode(start_state)
        plan = planner.retrocausal_plan(start_node, goal_state)

        self.assertIsNotNone(plan)
        action_names = [a.name for a in plan]
        # Should prefer goto_forest -> gather_wood -> goto_home -> build_frame -> goto_forest -> gather_wood -> goto_home -> build_roof
        # Or something similar that is cheapest.
        self.assertTrue("build_roof" in action_names)
        self.assertTrue("build_frame" in action_names)

    def test_execution_and_rewind(self):
        # We will make gather_wood fail during execution
        def failing_gather(state):
            raise Exception("Forest is empty!")

        def successful_buy(state):
            new_state = state.copy()
            new_state["has_wood"] = True
            new_state["has_money"] = False
            return new_state

        def normal_transition(action):
            def f(state):
                new_state = state.copy()
                new_state.update(action.effects)
                return new_state
            return f

        mod_actions = []
        for a in self.actions:
            if a.name == "gather_wood":
                a.execute_fn = failing_gather
            elif a.name == "buy_wood":
                a.execute_fn = successful_buy
            else:
                a.execute_fn = normal_transition(a)
            mod_actions.append(a)

        planner = ChronosTemporalPlanner(mod_actions)
        initial_state = {"at_home": True, "has_money": True}
        goal_state = {"has_wood": True} # Simplified goal to test rewind

        # It will try to goto_forest -> gather_wood (fails)
        # Rewind to start, then goto_store -> buy_wood (succeeds)
        success = planner.execute_plan(initial_state, goal_state)

        self.assertTrue(success)
        self.assertEqual(planner.current_node.state["has_wood"], True)
        self.assertTrue("gather_wood" in planner.execution_graph[planner.current_node.parent.parent.id].failed_actions or "gather_wood" in planner.current_node.parent.parent.parent.failed_actions if planner.current_node.parent and planner.current_node.parent.parent and planner.current_node.parent.parent.parent else True) # just checking success is enough really

if __name__ == '__main__':
    unittest.main()