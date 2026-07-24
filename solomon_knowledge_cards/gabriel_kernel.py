import abc
from typing import Any, Dict, List
import openai
import concurrent.futures

class GabrielWorker(abc.ABC):
    @abc.abstractmethod
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def get_capabilities(self) -> List[str]:
        pass

class OpenAIWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]:
        return ["general", "chat", "fallback"]

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        messages = task.get("messages", [])
        if not messages: return {"status": "error", "result": "Error: No messages provided."}
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            return {"status": "success", "result": response.choices[0].message["content"]}
        except Exception as e:
            return {"status": "error", "error_message": str(e), "result": f"API Error: {str(e)}"}

class LocalStubWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]:
        return ["general", "fast", "low_energy"]

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if task.get("complexity_score", 0.0) > 0.8:
            return {"status": "error", "error_message": "Task too complex for local worker."}
        return {"status": "success", "result": "Local worker processed task successfully."}

class GabrielKernel:
    def __init__(self):
        self.workers: Dict[str, GabrielWorker] = {}
        self.worker_stats: Dict[str, Dict[str, int]] = {}
        self.learning_pipeline = None
        self.dashboard = None

    def register_worker(self, name: str, worker: GabrielWorker):
        self.workers[name] = worker
        self.worker_stats[name] = {"success": 0, "failure": 0}

    def set_dashboard(self, dashboard: Any):
        self.dashboard = dashboard

    def _execute_with_stats(self, worker_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        worker = self.workers[worker_name]

        # Phase 21: Adaptive Worker Timeouts
        complexity = task.get("complexity_score", 0.5)
        timeout_seconds = max(5, int(complexity * 30))

        # Execute with simulated timeout wrapper
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(worker.execute, task, {"routed_by": "GabrielKernel"})
            try:
                result = future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                result = {"status": "error", "error_message": f"Execution timed out after {timeout_seconds}s"}

        if result.get("status") == "success":
            self.worker_stats[worker_name]["success"] += 1
        else:
            self.worker_stats[worker_name]["failure"] += 1

        if self.learning_pipeline:
            self.learning_pipeline.ingest(result)

        return result

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self.workers:
            raise RuntimeError("No workers registered.")

        complexity = task.get("complexity_score", 0.5)

        # Phase 24: Energy-Aware Routing
        if self.dashboard:
            metrics = self.dashboard.get_system_health()
            if metrics.get("energy_cost_kwh", 0) > 5.0: # threshold breached
                task["required_capability"] = "low_energy"

        if complexity > 0.9 and len(self.workers) > 1:
            return self._consensus_route(task)

        best_worker_name = self._get_best_worker_for_task(task)
        result = self._execute_with_stats(best_worker_name, task)

        if result.get("status") == "error":
            fallback_name = self._get_fallback_worker(exclude=best_worker_name)
            if fallback_name:
                task["messages"].append({"role": "system", "content": f"Previous worker {best_worker_name} failed. Attempting fallback."})
                result = self._execute_with_stats(fallback_name, task)

        return result

    def _get_best_worker_for_task(self, task: Dict[str, Any]) -> str:
        req_cap = task.get("required_capability", "general")
        best, best_rate = None, -1.0
        for name, worker in self.workers.items():
            if req_cap in worker.get_capabilities():
                s, f = self.worker_stats[name]["success"], self.worker_stats[name]["failure"]
                rate = s / (s + f) if (s + f) > 0 else 1.0
                if rate > best_rate:
                    best_rate, best = rate, name
        return best if best else list(self.workers.keys())[0]

    def _get_fallback_worker(self, exclude: str) -> str:
        for name, worker in self.workers.items():
            if name != exclude and "fallback" in worker.get_capabilities():
                return name
        return None

    def _consensus_route(self, task: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.workers[w].execute, task, {"routed_by": "Consensus"}): w for w in self.workers.keys()}
            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    if res.get("status") == "success": results.append(res.get("result", ""))
                except Exception: pass
        if not results: return {"status": "error", "result": "Consensus routing failed."}
        return {"status": "success", "result": f"Consensus Result: {' | '.join(results[:2])}"}

    def set_learning_pipeline(self, pipeline: Any):
        self.learning_pipeline = pipeline
