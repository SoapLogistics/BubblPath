import os
import shutil
from typing import Dict

class CodexParallelWorktrees:
    """
    Handles parallel workspace execution sandboxing.
    Creates, tracks, and cleans up isolated task-specific git-style worktrees or directories
    enabling concurrent branch-based code modifications without state pollution.
    """
    def __init__(self, root_dir: str = "/tmp/codex_workspaces"):
        self.root_dir = root_dir
        os.makedirs(self.root_dir, exist_ok=True)
        self.active_worktrees: Dict[str, str] = {}

    def create_worktree(self, task_id: str, origin_src_dir: str) -> str:
        """
        Clones or copies an existing codebase into an isolated worktree folder.
        """
        workspace_path = os.path.join(self.root_dir, f"worktree_{task_id}")
        if os.path.exists(workspace_path):
            shutil.rmtree(workspace_path)

        if os.path.exists(origin_src_dir):
            shutil.copytree(origin_src_dir, workspace_path, ignore=shutil.ignore_patterns('.git', '__pycache__'))
        else:
            os.makedirs(workspace_path, exist_ok=True)

        self.active_worktrees[task_id] = workspace_path
        return workspace_path

    def run_tests_in_worktree(self, task_id: str) -> bool:
        """
        Simulates running test validations in the isolated worktree sandbox.
        """
        if task_id not in self.active_worktrees:
            raise KeyError(f"No active worktree found for task: {task_id}")
        return True

    def remove_worktree(self, task_id: str):
        """
        Cleans up and deletes the worktree folder.
        """
        if task_id in self.active_worktrees:
            path = self.active_worktrees[task_id]
            if os.path.exists(path):
                shutil.rmtree(path)
            del self.active_worktrees[task_id]
