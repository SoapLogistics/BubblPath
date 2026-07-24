import uuid
import json
import os
import time

class JulesBridge:
    def __init__(self, task_file="jules_tasks.json"):
        self.task_file = task_file
        self._init_task_file()

    def _init_task_file(self):
        if not os.path.exists(self.task_file):
            with open(self.task_file, "w") as f:
                json.dump({}, f)

    def _read_tasks(self):
        if not os.path.exists(self.task_file):
            self._init_task_file()
        with open(self.task_file, "r") as f:
            return json.load(f)

    def _write_tasks(self, tasks):
        with open(self.task_file, "w") as f:
            json.dump(tasks, f, indent=4)

    def create_jules_task(self, description, priority="normal"):
        tasks = self._read_tasks()
        task_id = f"JULES-TASK-{uuid.uuid4().hex[:8].upper()}"
        tasks[task_id] = {
            "description": description,
            "priority": priority,
            "status": "pending",
            "created_at": time.time(),
            "messages": [],
            "patch": None,
            "human_approval": False
        }
        self._write_tasks(tasks)
        return task_id

    def list_jules_tasks(self):
        return self._read_tasks()

    def read_jules_session(self, task_id):
        tasks = self._read_tasks()
        return tasks.get(task_id, {})

    def send_jules_message(self, task_id, message):
        tasks = self._read_tasks()
        if task_id in tasks:
            tasks[task_id]["messages"].append({"role": "user", "content": message, "timestamp": time.time()})
            self._write_tasks(tasks)
            return True
        return False

    def cancel_jules_task(self, task_id):
        tasks = self._read_tasks()
        if task_id in tasks:
            tasks[task_id]["status"] = "cancelled"
            self._write_tasks(tasks)
            return True
        return False

    def retrieve_jules_patch(self, task_id):
        tasks = self._read_tasks()
        task = tasks.get(task_id, {})
        return task.get("patch")

    def validate_jules_output(self, task_id, patch_data):
        tasks = self._read_tasks()
        if task_id in tasks:
            tasks[task_id]["patch"] = patch_data
            tasks[task_id]["status"] = "validation_pending"
            self._write_tasks(tasks)
            return True
        return False

    def request_human_approval(self, task_id):
        tasks = self._read_tasks()
        if task_id in tasks:
            tasks[task_id]["status"] = "awaiting_approval"
            self._write_tasks(tasks)
            return True
        return False
