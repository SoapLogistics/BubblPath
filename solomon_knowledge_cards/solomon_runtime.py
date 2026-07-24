from typing import Dict, Any
import time

class UnifiedDashboard:
    def __init__(self):
        self.metrics: Dict[str, float] = {
            "cpu_cost": 0.0,
            "ram_cost_mb": 0.0,
            "token_cost": 0.0,
            "energy_cost_kwh": 0.0
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

    def execute_workload(self, task: Dict[str, Any]):
        start_time = time.time()

        # 1. Budget Context
        messages = task.get("messages", [])
        budgeted = self.context_engine.budget_context(current_vram_usage=500.0, messages=messages)
        task["messages"] = budgeted

        # 2. Route Task through Gabriel Engine
        result = self.gabriel_kernel.route_task(task)

        # 3. Log Performance
        execution_time = time.time() - start_time
        token_cost = sum(len(m.get("content", "")) for m in budgeted) / 4.0

        self.dashboard.report_telemetry("GabrielEngine", {
            "cpu_cost": execution_time,
            "ram_cost_mb": 15.0,
            "token_cost": token_cost
        })

        return result
