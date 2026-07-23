import os
import sys
import threading
import importlib.util
from typing import Dict, Any, Optional

class DynamicCapabilityRegistry:
    """
    Manages dynamic runtime integration of assimilated capabilities.
    Saves generated capability code to disk under 'gabriel_engine/assimilated_capabilities/',
    and dynamically imports/executes the code at runtime.

    Fully hardened with threading locks for race condition prevention,
    and size-bounded LRU-style eviction strategy to avoid memory leaks.
    """

    def __init__(self, target_dir: str = "gabriel_engine/assimilated_capabilities", max_cached_modules: int = 50):
        self.target_dir = target_dir
        self.max_cached_modules = max_cached_modules
        os.makedirs(self.target_dir, exist_ok=True)

        # Touch __init__.py to make it a package
        init_file = os.path.join(self.target_dir, "__init__.py")
        if not os.path.exists(init_file):
            with open(init_file, "w") as f:
                f.write("# Assimilated capabilities package\n")

        # Cache for loaded modules: module_name -> module
        self._loaded_modules: Dict[str, Any] = {}
        # Keep track of insertion order for eviction
        self._loaded_keys: list = []

        # Thread safety locks
        self._lock = threading.RLock()

    def register_and_save(self, capability_name: str, code_content: str) -> str:
        """
        Saves the compiled Python code to a file in the assimilated capabilities directory.
        Returns the absolute filepath. Protected by reentrant locks.
        """
        # Defend against path traversal
        clean_name = os.path.basename(capability_name)
        if clean_name != capability_name or ".." in capability_name or "/" in capability_name or "\\" in capability_name:
            raise ValueError(f"Path traversal detected in capability name: {capability_name}")

        with self._lock:
            filename = f"{capability_name}.py"
            filepath = os.path.join(self.target_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code_content)

            return filepath

    def load_capability(self, capability_name: str) -> Any:
        """
        Dynamically imports the capability module from disk and returns it.
        Employs threading locks for safety, and an LRU eviction strategy to prevent memory leaks.
        """
        # Defend against path traversal
        clean_name = os.path.basename(capability_name)
        if clean_name != capability_name or ".." in capability_name or "/" in capability_name or "\\" in capability_name:
            raise ValueError(f"Path traversal detected in capability name: {capability_name}")

        with self._lock:
            module_name = f"gabriel_engine.assimilated_capabilities.{capability_name}"
            filepath = os.path.join(self.target_dir, f"{capability_name}.py")

            if not os.path.exists(filepath):
                raise FileNotFoundError(f"No source file found for capability {capability_name} at {filepath}")

            # Eviction strategy: if cache exceeds limits, evict the oldest module
            if len(self._loaded_modules) >= self.max_cached_modules:
                if capability_name not in self._loaded_modules:
                    oldest_key = self._loaded_keys.pop(0)
                    self._loaded_modules.pop(oldest_key, None)
                    # Safely remove from sys.modules to allow complete garbage collection
                    oldest_module_name = f"gabriel_engine.assimilated_capabilities.{oldest_key}"
                    sys.modules.pop(oldest_module_name, None)

            # Use importlib spec to load dynamically
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec for capability {capability_name} at {filepath}")

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Update cache maps
            if capability_name in self._loaded_modules:
                # Move to the end of the keys list (most recently used)
                self._loaded_keys.remove(capability_name)
            self._loaded_modules[capability_name] = module
            self._loaded_keys.append(capability_name)

            return module

    def execute_capability(
        self,
        capability_name: str,
        class_name: str,
        method_name: str,
        init_args: Optional[list] = None,
        init_kwargs: Optional[Dict[str, Any]] = None,
        method_args: Optional[list] = None,
        method_kwargs: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Loads the capability, instantiates the class, and executes the specified method.
        Fully protected by reentrant locks.
        """
        init_args = init_args or []
        init_kwargs = init_kwargs or {}
        method_args = method_args or []
        method_kwargs = method_kwargs or {}

        with self._lock:
            # 1. Load module safely
            module = self.load_capability(capability_name)

            # 2. Extract class
            if not hasattr(module, class_name):
                # Attempt case-insensitive or close matching if exact match fails
                attrs = [attr for attr in dir(module) if attr.lower() == class_name.lower()]
                if attrs:
                    class_name = attrs[0]
                else:
                    raise AttributeError(f"Module {capability_name} has no class named {class_name}")

            cls = getattr(module, class_name)

            # 3. Instantiate class
            instance = cls(*init_args, **init_kwargs)

            # 4. Extract and call method
            if not hasattr(instance, method_name):
                raise AttributeError(f"Class {class_name} has no method named {method_name}")

            method = getattr(instance, method_name)
            return method(*method_args, **method_kwargs)
