import abc
from typing import Any, Dict, List
import openai
import concurrent.futures
import time

class GabrielWorker(abc.ABC):
    @abc.abstractmethod
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        pass
    @abc.abstractmethod
    def get_capabilities(self) -> List[str]:
        pass
    # Phase 40: Stateful Worker Suspension
    def suspend(self): pass
    def resume(self): pass

class OpenAIWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]: return ["general", "chat", "fallback"]
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        messages = task.get("messages", [])
        if not messages: return {"status": "error", "result": "Error: No messages."}
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            return {"status": "success", "result": response.choices[0].message["content"]}
        except Exception as e:
            return {"status": "error", "error_message": str(e), "result": f"API Error: {str(e)}"}

class LocalStubWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]: return ["general", "fast", "low_energy"]
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
        self.active_tasks = 0 # Phase 39: Load Balancing tracker

    def register_worker(self, name: str, worker: GabrielWorker):
        self.workers[name] = worker
        self.worker_stats[name] = {"success": 0, "failure": 0}

    def set_dashboard(self, dashboard: Any): self.dashboard = dashboard

    def _execute_with_stats(self, worker_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        worker = self.workers[worker_name]
        complexity = task.get("complexity_score", 0.5)
        timeout_seconds = max(5, int(complexity * 30))

        self.active_tasks += 1
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(worker.execute, task, {"routed_by": "GabrielKernel"})
            try: result = future.result(timeout=timeout_seconds)
            except concurrent.futures.TimeoutError:
                result = {"status": "error", "error_message": f"Execution timed out."}
        self.active_tasks -= 1

        if result.get("status") == "success": self.worker_stats[worker_name]["success"] += 1
        else: self.worker_stats[worker_name]["failure"] += 1

        if self.learning_pipeline: self.learning_pipeline.ingest(result)
        return result

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self.workers: raise RuntimeError("No workers registered.")

        complexity = task.get("complexity_score", 0.5)

        # Phase 36: DAG Task Execution stub
        if "dag_subtasks" in task:
            return self._execute_dag(task)

        if self.dashboard:
            metrics = self.dashboard.get_system_health().get("metrics", {})
            # Phase 37: Thermal-Aware Routing
            if metrics.get("gpu_temp_c", 0) > 85.0:
                task["required_capability"] = "low_energy"

        if complexity > 0.9 and len(self.workers) > 1:
            return self._consensus_route(task)

        best_worker_name, best_rate = self._get_best_worker_for_task(task)

        # Phase 38: Confidence Hedging
        if best_rate < 0.6 and len(self.workers) > 1:
            return self._hedged_route(task, best_worker_name)

        result = self._execute_with_stats(best_worker_name, task)
        if result.get("status") == "error":
            fallback_name = self._get_fallback_worker(exclude=best_worker_name)
            if fallback_name:
                task["messages"].append({"role": "system", "content": "Fallback attempt."})
                result = self._execute_with_stats(fallback_name, task)

        return result

    def _get_best_worker_for_task(self, task: Dict[str, Any]) -> (str, float):
        req_cap = task.get("required_capability", "general")
        best, best_rate = None, -1.0
        for name, worker in self.workers.items():
            if req_cap in worker.get_capabilities():
                s, f = self.worker_stats[name]["success"], self.worker_stats[name]["failure"]
                rate = s / (s + f) if (s + f) > 0 else 1.0
                if rate > best_rate: best_rate, best = rate, name
        return (best if best else list(self.workers.keys())[0]), best_rate

    def _get_fallback_worker(self, exclude: str) -> str:
        for name, worker in self.workers.items():
            if name != exclude and "fallback" in worker.get_capabilities(): return name
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
        if not results: return {"status": "error", "result": "Consensus failed."}
        return {"status": "success", "result": f"Consensus Result: {' | '.join(results[:2])}"}

    # Phase 38
    def _hedged_route(self, task: Dict[str, Any], primary_worker: str) -> Dict[str, Any]:
        fallback_name = self._get_fallback_worker(exclude=primary_worker)
        if not fallback_name: return self._execute_with_stats(primary_worker, task)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            future1 = executor.submit(self._execute_with_stats, primary_worker, task)
            future2 = executor.submit(self._execute_with_stats, fallback_name, task)
            # Return whichever finishes successfully first
            for future in concurrent.futures.as_completed([future1, future2]):
                res = future.result()
                if res.get("status") == "success": return res
        return {"status": "error", "result": "Hedged routing failed."}

    # Phase 36
    def _execute_dag(self, task: Dict[str, Any]) -> Dict[str, Any]:
        # Process subtasks concurrently
        results = []
        subtasks = task.get("dag_subtasks", [])
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.route_task, {"messages": st}) for st in subtasks]
            for future in concurrent.futures.as_completed(futures):
                results.append(future.result().get("result", ""))
        return {"status": "success", "result": f"DAG Completed: {' '.join(results)}"}

    def set_learning_pipeline(self, pipeline: Any): self.learning_pipeline = pipeline
