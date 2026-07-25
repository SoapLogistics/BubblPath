import time
import logging
import threading
from typing import Dict, Any, Callable, List, Optional
from collections import defaultdict
import uuid

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger("SolomonKernel")

class SolomonModule:
    """
    Base class for all Solomon Subsystems (Modules).
    Functions like a Linux kernel module.
    """
    def __init__(self):
        self.name = self.__class__.__name__
        self.kernel = None
        self.state = "INIT"
        self.start_time = None
        self.dependencies: List[str] = []

    def attach(self, kernel):
        self.kernel = kernel

    def start(self):
        """Lifecycle hook: Called when the module is loaded."""
        self.state = "RUNNING"
        self.start_time = time.time()
        logger.info(f"Module {self.name} started.")

    def stop(self):
        """Lifecycle hook: Called when the module is unloaded."""
        self.state = "STOPPED"
        logger.info(f"Module {self.name} stopped.")

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state,
            "uptime": time.time() - self.start_time if self.start_time else 0
        }

class Event:
    def __init__(self, topic: str, sender: str, payload: Dict[str, Any]):
        self.id = str(uuid.uuid4())
        self.topic = topic
        self.sender = sender
        self.payload = payload
        self.timestamp = time.time()

class SolomonKernel:
    """
    The core kernel of the Solomon OS.
    Manages modules, event bus (IPC), and RPC calls.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SolomonKernel, cls).__new__(cls)
            cls._instance.modules = {}
            cls._instance.event_subscribers = defaultdict(list)
            cls._instance.rpc_registry = {}
            cls._instance._lock = threading.RLock()
            cls._instance.state = "BOOTING"
        return cls._instance

    def boot(self):
        self.state = "RUNNING"
        logger.info("Solomon OS Kernel Booted.")

    def load_module(self, module: SolomonModule):
        """Analogue to insmod. Checks dependencies before loading."""
        with self._lock:
            if module.name in self.modules:
                logger.warning(f"Module {module.name} is already loaded.")
                return

            # Check dependencies
            for dep in module.dependencies:
                if dep not in self.modules or self.modules[dep].state != "RUNNING":
                    logger.error(f"Failed to load {module.name}: Missing dependency {dep}")
                    return False

            module.attach(self)
            self.modules[module.name] = module
            module.start()
            logger.info(f"Loaded module: {module.name}")
            return True

    def unload_module(self, module_name: str):
        """Analogue to rmmod"""
        with self._lock:
            if module_name not in self.modules:
                logger.warning(f"Module {module_name} is not loaded.")
                return

            module = self.modules.pop(module_name)
            module.stop()

            # Remove RPCs and Subscribers associated with this module
            # (In a full implementation, we'd track these by module)

            logger.info(f"Unloaded module: {module_name}")

    def get_module(self, module_name: str) -> Optional[SolomonModule]:
        return self.modules.get(module_name)

    # --- IPC: Event Bus (Pub/Sub) ---
    def subscribe(self, topic: str, callback: Callable[[Event], None]):
        with self._lock:
            self.event_subscribers[topic].append(callback)

    def publish(self, topic: str, sender: str, payload: Dict[str, Any]):
        event = Event(topic, sender, payload)
        with self._lock:
            subscribers = list(self.event_subscribers.get(topic, []))
            # Also notify wildcard subscribers if we wanted to implement that

        for callback in subscribers:
            try:
                # In a real OS, this might be dispatched to a thread pool or queue
                callback(event)
            except Exception as e:
                logger.error(f"Error in event subscriber for {topic}: {e}")

    # --- IPC: RPC (Request/Response) ---
    def register_rpc(self, method_name: str, handler: Callable):
        with self._lock:
            self.rpc_registry[method_name] = handler

    def call_rpc(self, method_name: str, *args, **kwargs):
        handler = self.rpc_registry.get(method_name)
        if not handler:
            raise ValueError(f"RPC method {method_name} not found.")
        return handler(*args, **kwargs)

    def get_system_status(self) -> Dict[str, Any]:
        return {
            "kernel_state": self.state,
            "modules": {name: mod.get_status() for name, mod in self.modules.items()},
            "topics_count": len(self.event_subscribers),
            "rpc_count": len(self.rpc_registry)
        }

# Global singleton accessor
kernel = SolomonKernel()
