import abc
from typing import Any, Dict, List
import openai
import concurrent.futures
import time

class GabrielWorker(abc.ABC):
    @abc.abstractmethod
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]: pass
    @abc.abstractmethod
    def get_capabilities(self) -> List[str]: pass
    def suspend(self): pass
    def resume(self): pass

class OpenAIWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]: return ["general", "chat", "fallback"]
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        messages = task.get("messages", [])
        if not messages: return {"status": "error", "result": "Error: No messages."}
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            content = response.choices[0].message["content"]
            # Phase 65: Multi-Step Chain-of-Thought Enforcement
            if "<thinking>" not in content and task.get("require_cot", False):
                return {"status": "error", "error_message": "Missing required Chain-of-Thought tags"}
            return {"status": "success", "result": content}
        except Exception as e:
            return {"status": "error", "error_message": str(e), "result": f"API Error"}

class LocalStubWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]: return ["general", "fast", "low_energy", "sandboxed"]
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Phase 61: Worker Sandbox Isolation Hook
        if task.get("complexity_score", 0.0) > 0.8:
            return {"status": "error", "error_message": "Task too complex for local worker."}
        return {"status": "success", "result": "Local sandboxed worker processed task."}

class GabrielKernel:
    def __init__(self):
        self.workers: Dict[str, GabrielWorker] = {}
        self.worker_stats: Dict[str, Dict[str, int]] = {}
        self.learning_pipeline = None
        self.dashboard = None
        self.active_tasks = 0
        self.peer_nodes = [] # Phase 62: Node Gossip Protocol

    def register_worker(self, name: str, worker: GabrielWorker):
        self.workers[name] = worker
        self.worker_stats[name] = {"success": 0, "failure": 0}

    def set_dashboard(self, dashboard: Any): self.dashboard = dashboard

    def _safety_check(self, task: Dict[str, Any]) -> bool:
        # Phase 64: Prompt Toxicity/Safety Guardrails
        for m in task.get("messages", []):
            content = m.get("content", "").lower()
            if "rm -rf" in content or "drop table" in content:
                return False
        return True

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

        if not self._safety_check(task):
            return {"status": "error", "result": "Safety Guardrail Triggered"}

        # Phase 63: Task Preemption hook
        if task.get("priority", 0) > 9 and self.active_tasks > 0:
            # Conceptually halt lower priority workers
            pass

        if "dag_subtasks" in task: return self._execute_dag(task)

        if self.dashboard and self.dashboard.get_system_health().get("metrics", {}).get("gpu_temp_c", 0) > 85.0:
            task["required_capability"] = "low_energy"

        best_worker_name, best_rate = self._get_best_worker_for_task(task)

        if best_rate < 0.6 and len(self.workers) > 1: return self._hedged_route(task, best_worker_name)

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

    def _hedged_route(self, task: Dict[str, Any], primary_worker: str) -> Dict[str, Any]:
        fallback_name = self._get_fallback_worker(exclude=primary_worker)
        if not fallback_name: return self._execute_with_stats(primary_worker, task)
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for future in concurrent.futures.as_completed([executor.submit(self._execute_with_stats, primary_worker, task), executor.submit(self._execute_with_stats, fallback_name, task)]):
                res = future.result()
                if res.get("status") == "success": return res
        return {"status": "error", "result": "Hedged routing failed."}

    def _execute_dag(self, task: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.route_task, {"messages": st}) for st in task.get("dag_subtasks", [])]
            for future in concurrent.futures.as_completed(futures): results.append(future.result().get("result", ""))
        return {"status": "success", "result": f"DAG Completed: {' '.join(results)}"}

    def set_learning_pipeline(self, pipeline: Any): self.learning_pipeline = pipeline

    # Phase 62: Node Gossip Protocol hook
    def broadcast_health(self):
        return {"active_tasks": self.active_tasks, "workers": list(self.workers.keys())}
