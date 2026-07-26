import json
import os

class CheckpointEngine:
    def __init__(self, directory="data/checkpoints"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def save(self, resident_name: str, state_data: dict):
        path = os.path.join(self.directory, f"{resident_name}.json")
        with open(path, "w") as f:
            json.dump(state_data, f)

    def load(self, resident_name: str) -> dict:
        path = os.path.join(self.directory, f"{resident_name}.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}
