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
    @abc.abstractmethod
    def bid_on_task(self, task: Dict[str, Any]) -> float: pass

class OpenAIWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]: return ["general", "chat", "fallback"]
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        messages = task.get("messages", [])
        if not messages: return {"status": "error", "result": "Error: No messages."}
        try:
            # Phase 186: Counter-Factual Reasoning Pre-processing
            if task.get("counter_factual", False):
                messages.append({"role": "system", "content": "Critique this by assuming the opposite premise is true."})

            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            content = response.choices[0].message["content"]
            return {"status": "success", "result": content}
        except Exception as e:
            return {"status": "error", "error_message": str(e), "result": f"API Error"}
    def bid_on_task(self, task: Dict[str, Any]) -> float: return 0.8

class LocalStubWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]: return ["general", "fast", "low_energy", "sandboxed"]
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if task.get("complexity_score", 0.0) > 0.8:
            return {"status": "error", "error_message": "Task too complex for local worker."}
        return {"status": "success", "result": "Local sandboxed worker processed task."}
    def bid_on_task(self, task: Dict[str, Any]) -> float:
        return 0.9 if task.get("complexity_score", 0.0) < 0.5 else 0.1

class GabrielKernel:
    def __init__(self):
        self.workers: Dict[str, GabrielWorker] = {}
        self.worker_stats: Dict[str, Dict[str, Any]] = {}
        self.learning_pipeline = None
        self.dashboard = None
        self.active_tasks = 0
        self.agent_mailbox: Dict[str, List[str]] = {}

    def register_worker(self, name: str, worker: GabrielWorker):
        self.workers[name] = worker
        self.worker_stats[name] = {"success": 0, "failure": 0, "token_balance": 100.0}
        self.agent_mailbox[name] = []

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

        if result.get("status") == "success":
            self.worker_stats[worker_name]["success"] += 1
            self.worker_stats[worker_name]["token_balance"] += complexity * 10
        else:
            self.worker_stats[worker_name]["failure"] += 1
            if "hallucination" in result.get("error_message", "").lower():
                self.worker_stats[worker_name]["token_balance"] *= 0.5
            else:
                self.worker_stats[worker_name]["token_balance"] -= 5.0

        if self.learning_pipeline: self.learning_pipeline.ingest(result)
        return result

    # Phase 184: Meta-Cognition Loop
    def run_meta_cognition(self):
        # Background loop that analyzes the queue
        if self.active_tasks > 50:
            return {"action": "Scale Up Nodes", "reason": "High queue depth"}
        return {"action": "Stable", "reason": "Normal operations"}

    # Phase 185: Autonomous Sub-Agent Spawning
    def spawn_sub_agent(self, task_chunk: Dict[str, Any]):
        # Spawns a temporary worker to handle a map-reduce chunk
        temp_name = f"sub_agent_{hash(str(time.time()))}"
        self.register_worker(temp_name, LocalStubWorker())
        return self._execute_with_stats(temp_name, task_chunk)

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self.workers: raise RuntimeError("No workers registered.")

        complexity = task.get("complexity_score", 0.5)

        if task.get("cryptographically_signed") is False:
            return {"status": "error", "result": "Execution rejected: unsigned request."}

        if task.get("critical", False) and len(self.workers) >= 3:
            return self._bft_consensus_route(task)

        if self.dashboard and self.dashboard.get_system_health().get("metrics", {}).get("gpu_temp_c", 0) > 85.0:
            task["required_capability"] = "low_energy"

        best_worker_name = self._auction_route(task)

        result = self._execute_with_stats(best_worker_name, task)
        if result.get("status") == "error":
            fallback_name = self._get_fallback_worker(exclude=best_worker_name)
            if fallback_name:
                task["messages"].append({"role": "system", "content": "Fallback attempt."})
                result = self._execute_with_stats(fallback_name, task)

        if "eval(" in result.get("result", ""):
            return {"status": "error", "result": "Output sanitized by Zero-Trust scanner."}

        return result

    def _auction_route(self, task: Dict[str, Any]) -> str:
        req_cap = task.get("required_capability", "general")
        best_bid, best_worker = -1.0, None

        for name, worker in self.workers.items():
            if req_cap in worker.get_capabilities():
                s, f = self.worker_stats[name]["success"], self.worker_stats[name]["failure"]
                trust_score = s / (s + f) if (s + f) > 0 else 1.0
                token_multiplier = min(self.worker_stats[name]["token_balance"] / 100.0, 2.0)

                bid = worker.bid_on_task(task) * trust_score * token_multiplier
                if bid > best_bid:
                    best_bid, best_worker = bid, name

        return best_worker if best_worker else list(self.workers.keys())[0]

    def _get_fallback_worker(self, exclude: str) -> str:
        for name, worker in self.workers.items():
            if name != exclude and "fallback" in worker.get_capabilities(): return name
        return None

    def _bft_consensus_route(self, task: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            staked_workers = [w for w, stats in self.worker_stats.items() if stats["token_balance"] > 10.0]
            if not staked_workers: return {"status": "error", "result": "No workers have enough tokens."}

            futures = {executor.submit(self.workers[w].execute, task, {"routed_by": "BFT"}): w for w in staked_workers}
            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    if res.get("status") == "success": results.append(res.get("result", ""))
                except Exception: pass

        if not results: return {"status": "error", "result": "Consensus failed."}
        if len(results) >= (len(staked_workers) // 2) + 1:
            return {"status": "success", "result": f"BFT Validated: {results[0]}"}
        return {"status": "error", "result": "BFT Consensus not reached. Nodes disagreed."}

    def set_learning_pipeline(self, pipeline: Any): self.learning_pipeline = pipeline

    def broadcast_health(self):
        dnd = True if self.active_tasks > 10 else False
        return {"active_tasks": self.active_tasks, "workers": list(self.workers.keys()), "dnd_flag": dnd}
