import os
import time
import re
import threading
import subprocess
import openai
from typing import List, Dict, Optional

class JulesTask:
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
        self.status = "pending" # pending, in_progress, completed, failed
        self.logs = []
        self.commit_hash = None

class JulesAutonomousDaemon:
    def __init__(self):
        self.is_running = False
        self.current_blueprint_name = None
        self.tasks: List[JulesTask] = []
        self.current_task_index = 0
        self.worker_thread: Optional[threading.Thread] = None

        # System prompt ensuring the AI acts as an autonomous coder
        self.system_prompt = (
            "You are the Jules Autonomous Coder Daemon. You are running as a background agent inside Project Solomon. "
            "Your objective is to execute the given architectural task, write the necessary Python code, "
            "and output the raw code implementation. Do not include markdown formatting or explanations, ONLY output the raw code "
            "or shell commands required. If you are modifying a file, output the complete file."
        )

    def parse_blueprint(self, blueprint_text: str) -> List[JulesTask]:
        """Parses a markdown blueprint looking for headers or numbered lists to create tasks."""
        tasks = []
        # Look for headers like '## Phase 1: ...' or '1. ...'
        lines = blueprint_text.split('\n')
        current_title = None
        current_desc = []

        for line in lines:
            header_match = re.match(r'^(?:##\s+|\d+\.\s+\**)(.+)', line)
            if header_match:
                if current_title:
                    tasks.append(JulesTask(current_title, "\n".join(current_desc).strip()))
                current_title = header_match.group(1).replace('*', '').strip()
                current_desc = []
            elif current_title and line.strip():
                current_desc.append(line.strip())

        if current_title:
            tasks.append(JulesTask(current_title, "\n".join(current_desc).strip()))

        return tasks

    def start_blueprint_execution(self, blueprint_name: str, blueprint_text: str):
        if self.is_running:
            raise Exception("Daemon is already running a blueprint.")

        self.tasks = self.parse_blueprint(blueprint_text)
        if not self.tasks:
            raise Exception("Could not parse any tasks from the blueprint.")

        self.current_blueprint_name = blueprint_name
        self.current_task_index = 0
        self.is_running = True

        self.worker_thread = threading.Thread(target=self._execution_loop, daemon=True)
        self.worker_thread.start()

    def _execution_loop(self):
        try:
            while self.current_task_index < len(self.tasks):
                task = self.tasks[self.current_task_index]
                task.status = "in_progress"
                task.logs.append(f"[{time.strftime('%H:%M:%S')}] Starting task: {task.title}")

                try:
                    self._execute_single_task(task)
                    task.status = "completed"
                    task.logs.append(f"[{time.strftime('%H:%M:%S')}] Task completed successfully.")
                except Exception as e:
                    task.status = "failed"
                    task.logs.append(f"[{time.strftime('%H:%M:%S')}] FATAL ERROR: {str(e)}")
                    # If a task fails, we halt the continuous loop to prevent catastrophic cascading errors
                    self.is_running = False
                    return

                self.current_task_index += 1

                # Sleep between tasks to prevent aggressive rate limiting and allow OS to breathe
                if self.current_task_index < len(self.tasks):
                    task.logs.append("Sleeping for 60 seconds before next phase...")
                    time.sleep(60)

        finally:
            self.is_running = False

    def _execute_single_task(self, task: JulesTask):
        """Uses OpenAI to generate code, writes it to disk, and commits it."""
        client = openai.Client() # Assumes OPENAI_API_KEY is in environment

        # 1. Ask Jules to write the implementation
        prompt = (
            f"Current Task: {task.title}\n"
            f"Description: {task.description}\n\n"
            f"Provide the exact Python implementation to satisfy this task. "
            f"Start your response with the filename on the first line (e.g., # filename: module.py), "
            f"then provide the raw code."
        )

        task.logs.append("Requesting code generation from Jules Core (OpenAI)...")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview", # Use a highly capable model for autonomous coding
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2 # Low temp for deterministic coding
        )

        output = response.choices[0].message.content.strip()

        # 2. Parse filename and content
        lines = output.split('\n')
        filename = "jules_autonomous_output.py" # Default fallback
        if lines[0].startswith('# filename:'):
            filename = lines[0].replace('# filename:', '').strip()
            content = '\n'.join(lines[1:]).strip()
        else:
            content = output

        # Strip markdown code blocks if the AI accidentally included them
        if content.startswith('```python'):
            content = content[9:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]

        # 3. Write to disk securely (prevent directory traversal)
        # Ensure the filename is just a safe basename within the current repo directory
        safe_filename = os.path.basename(filename)
        if not safe_filename or safe_filename == "" or safe_filename == ".":
            safe_filename = "jules_autonomous_output.py"

        # Optional check: ensure it has a python extension to prevent arbitrary executable writes
        if not safe_filename.endswith(".py"):
             safe_filename += ".py"

        task.logs.append(f"Writing implementation securely to {safe_filename}...")
        with open(safe_filename, 'w') as f:
            f.write(content.strip() + "\n")

        # override filename for git add
        filename = safe_filename

        # 4. Run Git Commit
        task.logs.append("Committing to repository...")
        try:
            subprocess.run(["git", "add", filename], check=True, capture_output=True)

            commit_msg = f"jules(auto): complete {task.title.lower()}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True, capture_output=True)

            # Get the commit hash
            res = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
            task.commit_hash = res.stdout.strip()
            task.logs.append(f"Committed successfully. Hash: {task.commit_hash}")
        except subprocess.CalledProcessError as e:
            task.logs.append(f"Git commit failed (might be no changes). Stderr: {e.stderr}")

    def get_status(self) -> Dict:
        return {
            "is_running": self.is_running,
            "current_blueprint": self.current_blueprint_name,
            "progress": f"{self.current_task_index} / {len(self.tasks)}",
            "tasks": [
                {
                    "title": t.title,
                    "status": t.status,
                    "commit_hash": t.commit_hash,
                    "logs": t.logs[-5:] # Return last 5 logs to save bandwidth
                } for t in self.tasks
            ]
        }
