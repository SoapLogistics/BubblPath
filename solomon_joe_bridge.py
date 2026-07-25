import os
import time
import re
import threading
import subprocess
import openai
from typing import List, Dict, Optional

import json
import concurrent.futures

class JoeTask:
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
        self.status = "pending" # pending, in_progress, completed, failed
        self.logs = []
        self.commit_hash = None

class BlueprintJob:
    def __init__(self, name: str, text: str):
        self.name = name
        self.text = text
        self.tasks: List[JoeTask] = []
        self.helpers_needed = 1

class JoeOmegaEngine:
    def __init__(self):
        self.is_running = False
        self.blueprint_queue: List[BlueprintJob] = []
        self.current_job: Optional[BlueprintJob] = None
        self.worker_thread: Optional[threading.Thread] = None
        self.max_retries = 5

        # Git lock for concurrent swarm commits
        self.git_lock = threading.Lock()

        # System prompt ensuring the AI acts as an autonomous coder
        self.system_prompt = (
            "You are J.O.E. (Jules Omega Engine). You are running as an autonomous background swarm inside Project Solomon. "
            "Your objective is to execute the given architectural task, write the necessary Python code, "
            "and output the raw code implementation. Do not include markdown formatting or explanations, ONLY output the raw code "
            "or shell commands required. If you are modifying a file, output the complete file."
        )

    def queue_blueprint(self, blueprint_name: str, blueprint_text: str):
        if len(self.blueprint_queue) >= 5:
            raise Exception("J.O.E. Queue is full (Max 5). Let him cook.")

        job = BlueprintJob(blueprint_name, blueprint_text)
        self.blueprint_queue.append(job)

        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._master_loop, daemon=True)
            self.worker_thread.start()

    def _analyze_and_expand_blueprint(self, job: BlueprintJob):
        """Uses LLM to determine swarm helper count and push boundaries."""
        client = openai.Client()
        prompt = (
            f"Analyze this architectural blueprint:\n{job.text}\n\n"
            "1. Output a JSON array of discrete sequential tasks (title, description). "
            "2. If there is a way to push boundaries and make this system significantly more advanced/optimal, "
            "append 1 or 2 extra tasks at the end to do so.\n"
            "3. Determine 'helpers': How many parallel worker threads (1 to 5) can execute these tasks concurrently?\n\n"
            "Format strictly as JSON:\n"
            "{\n  \"helpers\": int,\n  \"tasks\": [{\"title\": \"...\", \"description\": \"...\"}]\n}"
        )

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" },
            temperature=0.4
        )

        try:
            data = json.loads(response.choices[0].message.content)
            job.helpers_needed = min(5, max(1, data.get("helpers", 1)))
            for t in data.get("tasks", []):
                job.tasks.append(JoeTask(t.get("title", "Task"), t.get("description", "")))
        except Exception as e:
            # Fallback if json parsing fails
            job.helpers_needed = 1
            job.tasks.append(JoeTask("Fallback Task", job.text))

    def _master_loop(self):
        try:
            while self.blueprint_queue:
                self.current_job = self.blueprint_queue.pop(0)

                # 1. Analyze & Expand
                self._analyze_and_expand_blueprint(self.current_job)

                # 2. Execute with Swarm Helpers
                with concurrent.futures.ThreadPoolExecutor(max_workers=self.current_job.helpers_needed) as executor:
                    futures = {executor.submit(self._execute_single_task_with_retry, task): task for task in self.current_job.tasks}
                    for future in concurrent.futures.as_completed(futures):
                        task = futures[future]
                        try:
                            future.result()
                        except Exception as e:
                            task.logs.append(f"FATAL THREAD EXHAUSTION: {str(e)}")

                # Sleep between blueprints
                if self.blueprint_queue:
                    time.sleep(30)

        finally:
            self.is_running = False
            self.current_job = None

    def _execute_single_task_with_retry(self, task: JoeTask):
        task.status = "in_progress"
        task.logs.append(f"[{time.strftime('%H:%M:%S')}] Starting task: {task.title}")

        attempts = 0
        success = False
        last_error_feedback = ""

        while attempts < self.max_retries and not success:
            attempts += 1
            try:
                self._execute_single_task(task, last_error_feedback)
                task.status = "completed"
                task.logs.append(f"[{time.strftime('%H:%M:%S')}] Task completed successfully on attempt {attempts}.")
                success = True
            except Exception as e:
                last_error_feedback = str(e)
                task.logs.append(f"[{time.strftime('%H:%M:%S')}] Attempt {attempts} failed: {last_error_feedback}")
                if attempts < self.max_retries:
                    task.logs.append("Self-healing... feeding error back to J.O.E. Core.")
                    time.sleep(10)

        if not success:
            task.status = "exhausted"
            task.logs.append(f"[{time.strftime('%H:%M:%S')}] EXHAUSTION FATAL: Failed after {self.max_retries} attempts.")
            raise Exception(f"Task {task.title} exhausted.")

    def _execute_single_task(self, task: JoeTask, previous_error: str = ""):
        """Uses OpenAI to generate code, writes it to disk, and commits it. Self-corrects if previous_error provided."""
        client = openai.Client() # Assumes OPENAI_API_KEY is in environment

        # 1. Ask Jules to write the implementation
        prompt = (
            f"Current Task: {task.title}\n"
            f"Description: {task.description}\n\n"
            f"Provide the exact Python implementation to satisfy this task. "
            f"Start your response with the filename on the first line (e.g., # filename: module.py), "
            f"then provide the raw code."
        )

        if previous_error:
            prompt += f"\n\nWARNING: Your previous attempt failed with the following error:\n{previous_error}\nAnalyze the error and provide the FIXED code."

        task.logs.append("Requesting code generation from J.O.E. Core (OpenAI)...")
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2 if not previous_error else 0.4 # Slightly higher temp on retries for creative fixing
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

        # 4. Syntax check (Self-Healing Step 1)
        if safe_filename.endswith(".py"):
            try:
                subprocess.run(["python", "-m", "py_compile", safe_filename], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                raise Exception(f"Syntax Error in generated Python code: {e.stderr}")

        # 5. Run Git Commit (Self-Healing Step 2)
        task.logs.append("Committing to repository...")

        with self.git_lock:
            try:
                subprocess.run(["git", "add", safe_filename], check=True, capture_output=True, text=True)

                commit_msg = f"omega(auto): complete {task.title.lower()}"
                res = subprocess.run(["git", "commit", "-m", commit_msg], capture_output=True, text=True)

                if res.returncode != 0:
                    if "nothing to commit" in res.stdout or "nothing to commit" in res.stderr:
                        task.logs.append("Git commit skipped: No changes made by the generated code.")
                    else:
                        raise Exception(f"Git commit failed: {res.stderr} \n {res.stdout}")
                else:
                    # Get the commit hash
                    res_hash = subprocess.run(["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
                    task.commit_hash = res_hash.stdout.strip()
                    task.logs.append(f"Committed successfully. Hash: {task.commit_hash}")

            except subprocess.CalledProcessError as e:
                 raise Exception(f"Git subprocess error: {e.stderr}")

    def get_status(self) -> Dict:
        status = {
            "is_running": self.is_running,
            "queued_blueprints": len(self.blueprint_queue),
            "current_job": None
        }

        if self.current_job:
            completed = sum(1 for t in self.current_job.tasks if t.status in ["completed", "exhausted"])
            status["current_job"] = {
                "name": self.current_job.name,
                "helpers_active": self.current_job.helpers_needed,
                "progress": f"{completed} / {len(self.current_job.tasks)}",
                "tasks": [
                    {
                        "title": t.title,
                        "status": t.status,
                        "commit_hash": t.commit_hash,
                        "logs": t.logs[-3:]
                    } for t in self.current_job.tasks
                ]
            }
        return status
