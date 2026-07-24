import abc
from typing import Any, Dict, List
import openai

class GabrielWorker(abc.ABC):
    """
    The interchangeable worker interface.
    """
    @abc.abstractmethod
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abc.abstractmethod
    def get_capabilities(self) -> List[str]:
        pass

class OpenAIWorker(GabrielWorker):
    """
    Actual implementation of the GabrielWorker that calls the OpenAI API,
    preserving the existing functional behavior.
    """
    def get_capabilities(self) -> List[str]:
        return ["general", "chat"]

    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        messages = task.get("messages", [])
        if not messages:
            return {"result": "Error: No messages provided to OpenAIWorker."}

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )
            return {"result": response.choices[0].message["content"]}
        except Exception as e:
            return {"result": f"Error communicating with OpenAI: {str(e)}"}


class GabrielKernel:
    """
    The permanent learning kernel.
    """
    def __init__(self):
        self.workers: Dict[str, GabrielWorker] = {}
        self.learning_pipeline = None

    def register_worker(self, name: str, worker: GabrielWorker):
        self.workers[name] = worker

    def route_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if not self.workers:
            raise RuntimeError("No workers registered in Gabriel Kernel.")

        required_capability = task.get("required_capability", "chat")

        selected_worker = None
        for name, worker in self.workers.items():
            if required_capability in worker.get_capabilities():
                selected_worker = worker
                break

        if not selected_worker:
            selected_worker = list(self.workers.values())[0] # fallback

        result = selected_worker.execute(task, context={"routed_by": "GabrielKernel"})

        if self.learning_pipeline:
            self.learning_pipeline.ingest(result)

        return result

    def set_learning_pipeline(self, pipeline: Any):
        self.learning_pipeline = pipeline
