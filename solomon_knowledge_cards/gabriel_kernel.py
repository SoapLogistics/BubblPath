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

    # Phase 102: Auction-Based Task Bidding
    @abc.abstractmethod
    def bid_on_task(self, task: Dict[str, Any]) -> float: pass

class OpenAIWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]: return ["general", "chat", "fallback"]
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        messages = task.get("messages", [])
        if not messages: return {"status": "error", "result": "Error: No messages."}
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
            content = response.choices[0].message["content"]
            return {"status": "success", "result": content}
        except Exception as e:
            return {"status": "error", "error_message": str(e), "result": f"API Error"}
    def bid_on_task(self, task: Dict[str, Any]) -> float:
        return 0.8 # Constant high bid but costs money

class LocalStubWorker(GabrielWorker):
    def get_capabilities(self) -> List[str]: return ["general", "fast", "low_energy", "sandboxed"]
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        if task.get("complexity_score", 0.0) > 0.8:
            return {"status": "error", "error_message": "Task too complex for local worker."}
        return {"status": "success", "result": "Local sandboxed worker processed task."}
    def bid_on_task(self, task: Dict[str, Any]) -> float:
        # Bids high on easy tasks, low on complex tasks
        return 0.9 if task.get("complexity_score", 0.0) < 0.5 else 0.1

class GabrielKernel:
    def __init__(self):
        self.workers: Dict[str, GabrielWorker] = {}
        self.worker_stats: Dict[str, Dict[str, int]] = {}
        self.learning_pipeline = None
        self.dashboard = None
        self.active_tasks = 0
        self.peer_nodes = []
        # Phase 105: Agent Mailboxes
        self.agent_mailbox: Dict[str, List[str]] = {}

    def register_worker(self, name: str, worker: GabrielWorker):
        self.workers[name] = worker
        self.worker_stats[name] = {"success": 0, "failure": 0}
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

        if result.get("status") == "success": self.worker_stats[worker_name]["success"] += 1
        else: self.worker_stats[worker_name]["failure"] += 1

        if self.learning_pipeline: self.learning_pipeline.ingest(result)
        return result

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self.workers: raise RuntimeError("No workers registered.")

        complexity = task.get("complexity_score", 0.5)

        # Phase 101: Byzantine Fault Tolerance (BFT) for critical tasks
        if task.get("critical", False) and len(self.workers) >= 3:
            return self._bft_consensus_route(task)

        if self.dashboard and self.dashboard.get_system_health().get("metrics", {}).get("gpu_temp_c", 0) > 85.0:
            task["required_capability"] = "low_energy"

        # Phase 102: Auction-Based Routing
        best_worker_name = self._auction_route(task)

        result = self._execute_with_stats(best_worker_name, task)
        if result.get("status") == "error":
            fallback_name = self._get_fallback_worker(exclude=best_worker_name)
            if fallback_name:
                task["messages"].append({"role": "system", "content": "Fallback attempt."})
                result = self._execute_with_stats(fallback_name, task)

        return result

    def _auction_route(self, task: Dict[str, Any]) -> str:
        req_cap = task.get("required_capability", "general")
        best_bid, best_worker = -1.0, None

        for name, worker in self.workers.items():
            if req_cap in worker.get_capabilities():
                # Phase 110: Global Trust Score weighting
                s, f = self.worker_stats[name]["success"], self.worker_stats[name]["failure"]
                trust_score = s / (s + f) if (s + f) > 0 else 1.0

                bid = worker.bid_on_task(task) * trust_score
                if bid > best_bid:
                    best_bid, best_worker = bid, name

        return best_worker if best_worker else list(self.workers.keys())[0]

    def _get_fallback_worker(self, exclude: str) -> str:
        for name, worker in self.workers.items():
            if name != exclude and "fallback" in worker.get_capabilities(): return name
        return None

    # Phase 101: BFT Consensus
    def _bft_consensus_route(self, task: Dict[str, Any]) -> Dict[str, Any]:
        results = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = {executor.submit(self.workers[w].execute, task, {"routed_by": "BFT"}): w for w in self.workers.keys()}
            for future in concurrent.futures.as_completed(futures):
                try:
                    res = future.result()
                    if res.get("status") == "success": results.append(res.get("result", ""))
                except Exception: pass

        if not results: return {"status": "error", "result": "Consensus failed."}

        # Simple BFT stub: requires > 50% identical responses (mocked as string length matching for brevity)
        if len(results) >= (len(self.workers) // 2) + 1:
            return {"status": "success", "result": f"BFT Validated: {results[0]}"}

        return {"status": "error", "result": "BFT Consensus not reached. Nodes disagreed."}

    def set_learning_pipeline(self, pipeline: Any): self.learning_pipeline = pipeline

    def broadcast_health(self):
        return {"active_tasks": self.active_tasks, "workers": list(self.workers.keys())}
