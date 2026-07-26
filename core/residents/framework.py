import abc
import time
import threading
from enum import Enum

class ResidentState(Enum):
    SLEEPING = "sleeping"
    WAKING = "waking"
    RECOVERING = "recovering"
    SCANNING = "scanning"
    COLLECTING = "collecting"
    PRODUCING = "producing"
    PROPOSING = "proposing"
    CHECKPOINTING = "checkpointing"
    ERROR = "error"

class BaseResident(abc.ABC):
    def __init__(self, name: str, messaging, checkpoint_engine):
        self.name = name
        self.messaging = messaging
        self.checkpoint_engine = checkpoint_engine

        self.state = ResidentState.SLEEPING
        self.last_heartbeat = 0.0
        self.last_checkpoint = 0.0
        self.current_task = "Idle"
        self.last_report = None
        self.resource_usage = {"cpu_estimate": 0, "memory_estimate": 0}
        self.health = "OK"
        self.running = False
        self._thread = None
        self._sleep_event = threading.Event()

    def get_health_status(self):
        return {
            "name": self.name,
            "heartbeat": self.last_heartbeat,
            "state": self.state.value,
            "current_task": self.current_task,
            "last_checkpoint": self.last_checkpoint,
            "last_report": self.last_report,
            "resource_usage": self.resource_usage,
            "health": self.health
        }

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self.loop, daemon=True, name=f"Resident_{self.name}")
            self._thread.start()

    def stop(self):
        self.running = False
        self._sleep_event.set()
        if self._thread:
            self._thread.join(timeout=2)

    def loop(self):
        while self.running:
            try:
                self.wake()
                self.recover_state()
                self.publish_heartbeat()
                self.scan_assigned_domain()
                self.collect_evidence()
                self.produce_findings()
                if self.needs_proposal():
                    self.prepare_governed_proposals()
                self.checkpoint()
                self.sleep_cycle()
            except Exception as e:
                self.state = ResidentState.ERROR
                self.health = f"ERROR: {str(e)}"
                self.current_task = "Recovering from error"
                self._sleep_event.wait(5.0)

    def wake(self):
        self.state = ResidentState.WAKING
        self.current_task = "Waking up"

    def sleep_cycle(self, duration=5.0):
        self.state = ResidentState.SLEEPING
        self.current_task = "Sleeping"
        self._sleep_event.wait(duration)
        self._sleep_event.clear()

    def recover_state(self):
        self.state = ResidentState.RECOVERING
        self.current_task = "Recovering state"
        state = self.checkpoint_engine.load(self.name)
        self.on_recover(state)

    def publish_heartbeat(self):
        self.last_heartbeat = time.time()
        self.health = "OK"
        self.messaging.publish(self.name, "HEARTBEAT", {"status": "OK"})

    def checkpoint(self):
        self.state = ResidentState.CHECKPOINTING
        self.current_task = "Checkpointing state"
        state = self.get_checkpoint_state()
        self.checkpoint_engine.save(self.name, state)
        self.last_checkpoint = time.time()

    @abc.abstractmethod
    def on_recover(self, state: dict):
        pass

    @abc.abstractmethod
    def get_checkpoint_state(self) -> dict:
        pass

    @abc.abstractmethod
    def scan_assigned_domain(self):
        pass

    @abc.abstractmethod
    def collect_evidence(self):
        pass

    @abc.abstractmethod
    def produce_findings(self):
        pass

    @abc.abstractmethod
    def needs_proposal(self) -> bool:
        pass

    @abc.abstractmethod
    def prepare_governed_proposals(self):
        pass
