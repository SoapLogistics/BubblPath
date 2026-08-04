import json
import threading
import uuid
from typing import Any


class CodexKanban:
    """
    The Swarm Commander Kanban Board.
    Coordinates parallel worker agents to process multiple issues concurrently.
    """
    def __init__(self, workspace_root: str = ""):
        self.workspace_root = workspace_root
        
    def run_swarm(self, issues: list[dict[str, str]]) -> list[dict[str, Any]]:
        from gabriel_engine.assimilated_capabilities.codex_issue_to_pr_pipeline import (
            CodexIssueToPRPipeline,
        )
        from gabriel_engine.assimilated_capabilities.codex_parallel_worktrees import (
            CodexParallelWorktrees,
        )
        from gabriel_engine.assimilated_capabilities.renewable_worker_lease import (
            RenewableWorkerLease,
        )

        # Initialize Swarm dependencies
        lease_manager = RenewableWorkerLease(db_path=":memory:", lease_duration_sec=30)
        worktree_manager = CodexParallelWorktrees(root_dir="/tmp/codex_workspaces")
        pipeline = CodexIssueToPRPipeline(worktree_manager=worktree_manager)

        # 1. Populate Kanban Board
        for issue in issues:
            task_id = issue["issue_id"]
            payload = json.dumps(issue)
            lease_manager.add_task(task_id, payload)
            
        results = []
        lock = threading.Lock()
        
        def worker_thread(worker_id: str):
            while True:
                task = lease_manager.claim_task(worker_id)
                if not task:
                    break # No more tasks
                    
                task_id = task["task_id"]
                payload = json.loads(task["payload"])
                
                # 2. Checkout Worktree
                worktree_path = worktree_manager.create_worktree(task_id, self.workspace_root)
                
                try:
                    # 3. Process Issue in isolated worktree
                    pr_result = pipeline.process_issue(
                        issue_id=payload["issue_id"],
                        description=payload["description"],
                        codebase_path=worktree_path
                    )
                    
                    # Mark complete
                    lease_manager.complete_task(task_id, worker_id)
                    
                    with lock:
                        pr_result["worker_id"] = worker_id
                        results.append(pr_result)
                    
                finally:
                    # 4. Clean up Worktree
                    worktree_manager.remove_worktree(task_id)

        # 5. Spin up parallel Swarm Workers
        threads = []
        # Max 3 workers for safety
        num_workers = min(len(issues), 3)
        for i in range(num_workers):
            worker_id = f"worker_{uuid.uuid4().hex[:6]}"
            t = threading.Thread(target=worker_thread, args=(worker_id,))
            threads.append(t)
            t.start()

        # Wait for Swarm to finish
        for t in threads:
            t.join()

        return results
