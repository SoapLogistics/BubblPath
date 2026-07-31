from typing import List, Dict
import sys
import os

# Add parent dir to path to import contracts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contracts.git_adapter import GitAdapter

class MockGitAdapter(GitAdapter):
    def get_commits(self, branch: str) -> List[Dict[str, str]]:
        return [
            {"hash": "mock-hash-1", "message": "Initial commit"},
            {"hash": "mock-hash-2", "message": "Add README.md"}
        ]

    def diff(self, base: str, head: str) -> str:
        return "--- a/mock.txt\n+++ b/mock.txt\n@@ -1,1 +1,2 @@\n-old\n+new"
