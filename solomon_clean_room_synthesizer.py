import ast
import inspect
import sys
import types
from typing import Callable, Any, Optional, Dict

class SwarmHealer:
    """Simulates a Gabriel Swarm helper for self-healing broken functions."""
    def attempt_heal(self, source_code: str, error_msg: str) -> str:
        # In a real scenario, this calls an LLM or swarm to fix the code.
        # Here we provide a simple naive fix for a specific test case, or return original.
        if "ZeroDivisionError" in error_msg:
            # Very naive AST manipulation logic substitute
            return source_code.replace("return a / b", "return a / b if b != 0 else 0")
        return source_code

class ASTInjector(ast.NodeTransformer):
    """
    SOSS AST Injector.
    Utilizes Python's ast.NodeTransformer for in-memory live-code mutation.
    """
    def __init__(self, target_func_name: str, new_func_ast: ast.FunctionDef):
        self.target_func_name = target_func_name
        self.new_func_ast = new_func_ast
        self.mutated = False

    def visit_FunctionDef(self, node):
        if node.name == self.target_func_name:
            self.mutated = True
            return self.new_func_ast
        return self.generic_visit(node)


class CleanRoomSynthesizer:
    """
    Clean Room Synthesizer.
    Orchestrates in-memory live-code mutation and hot-reloading with automated rollback on failure.
    Leverages a SwarmHealer to dynamically heal broken functions.
    """
    def __init__(self):
        self.healer = SwarmHealer()
        # Keep track of original source for rollback
        self._history: Dict[str, str] = {}

    def mutate_and_reload(self, module_name: str, func_name: str, new_source: str) -> bool:
        """
        Attempts to replace func_name in module_name with new_source in memory.
        If it fails to compile or load, it rolls back.
        """
        if module_name not in sys.modules:
            return False

        module = sys.modules[module_name]

        # 1. Get original module source (fallback to simple string if impossible, but for clean room we assume we have it)
        try:
             original_source = inspect.getsource(module)
        except TypeError:
             # Can't get source of built-ins etc
             return False

        if module_name not in self._history:
            self._history[module_name] = original_source

        # 2. Parse new function
        try:
            new_tree = ast.parse(new_source)
            new_func_ast = new_tree.body[0]
            if not isinstance(new_func_ast, ast.FunctionDef):
                raise ValueError("New source must be a single function definition.")
        except Exception as e:
            print(f"Compilation error in new source: {e}")
            return False

        # 3. Parse original module
        try:
             original_tree = ast.parse(original_source)
        except Exception as e:
             return False

        # 4. Inject
        injector = ASTInjector(func_name, new_func_ast)
        mutated_tree = injector.visit(original_tree)
        ast.fix_missing_locations(mutated_tree)

        if not injector.mutated:
            print(f"Function {func_name} not found in module {module_name}.")
            return False

        # 5. Compile and Hot Reload (in-memory)
        try:
            compiled_code = compile(mutated_tree, filename="<ast>", mode="exec")
            # Create a new namespace to execute the mutated code
            new_namespace = module.__dict__.copy()
            exec(compiled_code, new_namespace)

            # Update the actual module's dict with the new function
            module.__dict__[func_name] = new_namespace[func_name]
            return True
        except Exception as e:
            print(f"Failed to hot-reload: {e}")
            # Rollback is implicit because we didn't update module.__dict__
            return False

    def execute_with_healing(self, func: Callable, *args, max_retries=3) -> Any:
        """
        Executes a function. If it raises an exception, utilizes the SwarmHealer
        to rewrite its AST, hot-reload it, and retry.
        """
        module_name = func.__module__
        func_name = func.__name__

        for attempt in range(max_retries):
            try:
                # Need to fetch the latest version of the function from the module dict
                # in case it was hot-reloaded in a previous iteration
                current_func = sys.modules[module_name].__dict__[func_name]
                return current_func(*args)
            except Exception as e:
                error_msg = repr(e)
                print(f"Execution failed on attempt {attempt+1}: {error_msg}")
                if attempt == max_retries - 1:
                    raise e

                try:
                    source_code = inspect.getsource(sys.modules[module_name].__dict__[func_name])
                except Exception:
                    raise e # Can't get source, can't heal

                print(f"Attempting swarm heal...")
                healed_source = self.healer.attempt_heal(source_code, error_msg)

                if healed_source == source_code:
                    print("Healer could not modify code.")
                    raise e

                success = self.mutate_and_reload(module_name, func_name, healed_source)
                if not success:
                    print("Hot-reload of healed code failed.")
                    raise e
                print("Hot-reload successful. Retrying execution.")
