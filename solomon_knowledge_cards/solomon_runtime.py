from typing import Dict, Any, List
import time

class UnifiedDashboard:
    def __init__(self):
        self.metrics: Dict[str, float] = {
            "cpu_cost": 0.0,
            "ram_cost_mb": 0.0,
            "token_cost": 0.0,
            "energy_cost_kwh": 0.0,
            "usd_cost_estimate": 0.0,
            "latency_budgeting_ms": 0.0, # Phase 15
            "latency_routing_ms": 0.0,   # Phase 15
        }

    def report_telemetry(self, subsystem: str, costs: Dict[str, float]):
        for key in self.metrics.keys():
            if key in costs:
                self.metrics[key] += costs[key]

    def get_system_health(self):
        return self.metrics

class SolomonOSKernel:
    def __init__(self, kernel, graph, context, ai_stack, learning):
        self.gabriel_kernel = kernel
        self.graph = graph
        self.context_engine = context
        self.ai_stack = ai_stack
        self.learning = learning
        self.dashboard = UnifiedDashboard()

    # Phase 11: Predictive Task Complexity Analysis
    def _predict_complexity(self, messages: List[Dict[str, str]]) -> float:
        total_len = sum(len(m.get("content", "")) for m in messages)
        complexity = min(total_len / 5000.0, 1.0)
        # simplistic prediction logic
        return complexity

    def execute_workload(self, task: Dict[str, Any]):
        t_start = time.time()

        # Predictive Scoring
        messages = task.get("messages", [])
        task["complexity_score"] = self._predict_complexity(messages)

        # 1. Budget Context
        t_budget_start = time.time()
        budgeted = self.context_engine.budget_context(current_vram_usage=500.0, messages=messages)
        task["messages"] = budgeted
        t_budget_ms = (time.time() - t_budget_start) * 1000

        # 2. Route Task through Gabriel Engine
        t_route_start = time.time()
        result = self.gabriel_kernel.route_task(task)
        t_route_ms = (time.time() - t_route_start) * 1000

        # 3. Log Performance (Phase 15: Latency profiling)
        total_time = time.time() - t_start
        token_cost = sum(len(m.get("content", "")) for m in budgeted) / 4.0

        self.dashboard.report_telemetry("GabrielEngine", {
            "cpu_cost": total_time,
            "ram_cost_mb": 15.0,
            "token_cost": token_cost,
            "usd_cost_estimate": token_cost * 0.000002,
            "energy_cost_kwh": total_time * 0.005,
            "latency_budgeting_ms": t_budget_ms,
            "latency_routing_ms": t_route_ms
        })

        return result
