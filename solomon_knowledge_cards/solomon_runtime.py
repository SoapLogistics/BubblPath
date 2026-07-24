from typing import Dict, Any, List
import time
import gc

class UnifiedDashboard:
    def __init__(self):
        self.metrics: Dict[str, float] = {
            "cpu_cost": 0.0,
            "ram_cost_mb": 0.0,
            "token_cost": 0.0,
            "energy_cost_kwh": 0.0,
            "usd_cost_estimate": 0.0,
            "latency_budgeting_ms": 0.0,
            "latency_routing_ms": 0.0,
            "gpu_temp_c": 45.0 # Phase 51: Thermal Metrics
        }
        self.alerts = []
        self.cost_history_24h: List[float] = []

    def report_telemetry(self, subsystem: str, costs: Dict[str, float]):
        for key in self.metrics.keys():
            if key in costs:
                self.metrics[key] += costs[key]

        if self.metrics["ram_cost_mb"] > 2000.0:
            self.alerts.append("CRITICAL: RAM Threshold Breached")
        if costs.get("latency_routing_ms", 0.0) > 5000.0:
            self.alerts.append("WARNING: Routing Latency Spike Detected")
        # Phase 51
        if self.metrics["gpu_temp_c"] > 85.0:
            self.alerts.append("CRITICAL: Thermal Throttling Detected")

        # Record cost for Phase 52
        if "usd_cost_estimate" in costs:
            self.cost_history_24h.append(costs["usd_cost_estimate"])
            if len(self.cost_history_24h) > 1000:
                self.cost_history_24h.pop(0)

    def get_system_health(self) -> Dict[str, Any]:
        return {
            "metrics": self.metrics,
            "alerts": self.alerts[-10:], # Keep only recent alerts
            "forecast_usd_24h": self._forecast_cost() # Phase 52
        }

    # Phase 52: Cost Forecasting
    def _forecast_cost(self) -> float:
        if not self.cost_history_24h: return 0.0
        avg_cost_per_task = sum(self.cost_history_24h) / len(self.cost_history_24h)
        estimated_tasks_24h = 10000 # Mock average daily load
        return avg_cost_per_task * estimated_tasks_24h

class SolomonOSKernel:
    def __init__(self, kernel, graph, context, ai_stack, learning):
        self.gabriel_kernel = kernel
        self.graph = graph
        self.context_engine = context
        self.ai_stack = ai_stack
        self.learning = learning
        self.dashboard = UnifiedDashboard()
        self.gabriel_kernel.set_dashboard(self.dashboard)

    def _predict_complexity(self, messages: List[Dict[str, str]]) -> float:
        total_len = sum(len(m.get("content", "")) for m in messages)
        return min(total_len / 5000.0, 1.0)

    def execute_workload(self, task: Dict[str, Any]):
        t_start = time.time()

        messages = task.get("messages", [])
        task["complexity_score"] = self._predict_complexity(messages)

        t_budget_start = time.time()
        budgeted = self.context_engine.budget_context(current_vram_usage=500.0, messages=messages)

        # Phase 53: Automated GC Sweeps if massive eviction occurred
        if len(budgeted) < len(messages) / 2:
            gc.collect()

        task["messages"] = budgeted
        t_budget_ms = (time.time() - t_budget_start) * 1000

        t_route_start = time.time()
        result = self.gabriel_kernel.route_task(task)
        t_route_ms = (time.time() - t_route_start) * 1000

        total_time = time.time() - t_start
        token_cost = sum(len(m.get("content", "")) for m in budgeted) / 4.0

        # Mocking a slight temp increase during heavy execution
        simulated_temp = self.dashboard.metrics["gpu_temp_c"] + (task["complexity_score"] * 2.0)
        simulated_temp = min(simulated_temp, 90.0)

        self.dashboard.report_telemetry("GabrielEngine", {
            "cpu_cost": total_time,
            "ram_cost_mb": 15.0,
            "token_cost": token_cost,
            "usd_cost_estimate": token_cost * 0.000002,
            "energy_cost_kwh": total_time * 0.005,
            "latency_budgeting_ms": t_budget_ms,
            "latency_routing_ms": t_route_ms,
            "gpu_temp_c": simulated_temp
        })

        return result
