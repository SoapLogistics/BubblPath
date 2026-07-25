import ast
import inspect
import importlib
import logging
import textwrap
import subprocess
from typing import Callable, Any

logger = logging.getLogger("SOSS_AST_Injector")

class AdvancedASTInjector:
    """
    SOSS Phase 4/5: Advanced AST Injector & Self-Healing Rollback.
    Dynamically rewrites Python function logic at runtime, hot-reloads it,
    and automatically reverts via Git if the newly injected code crashes.
    """

    @staticmethod
    def mutate_function(target_func: Callable, new_logic_str: str) -> bool:
        """
        Attempts to replace the body of target_func with new_logic_str.
        Returns True if successful, False if self-healing rollback was triggered.
        """
        func_name = target_func.__name__
        module = inspect.getmodule(target_func)
        if not module or not hasattr(module, '__file__'):
            logger.error(f"Cannot mutate built-in or undefined module for {func_name}")
            return False

        filepath = module.__file__

        # 1. Read existing source
        with open(filepath, "r") as f:
            source = f.read()

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            logger.error(f"Original source file syntax error: {e}")
            return False

        # 2. Parse new logic
        # Wrap new logic in a dummy function to parse its body correctly
        dummy_def = f"def {func_name}():\n" + textwrap.indent(new_logic_str, "    ")
        try:
            new_tree = ast.parse(dummy_def)
            new_body = new_tree.body[0].body
        except SyntaxError as e:
            logger.error(f"Generated logic contains syntax error: {e}")
            return False

        # 3. Apply NodeTransformer mutation
        class FunctionBodyMutator(ast.NodeTransformer):
            def visit_FunctionDef(self, node):
                if node.name == func_name:
                    logger.info(f"Mutating AST for function: {func_name}")
                    node.body = new_body
                return node

        mutator = FunctionBodyMutator()
        modified_tree = mutator.visit(tree)
        ast.fix_missing_locations(modified_tree)

        # 4. Write back to disk (Attempt)
        try:
            # We use unparse if python >= 3.9
            new_source = ast.unparse(modified_tree)
            with open(filepath, "w") as f:
                f.write(new_source)
        except Exception as e:
            logger.error(f"Failed to unparse or write mutated AST: {e}")
            return False

        # 5. Hot Reload and Verify
        try:
            importlib.reload(module)
            logger.info(f"Successfully hot-reloaded module: {module.__name__}")
            return True
        except Exception as e:
            logger.critical(f"Hot-reload failed! Code was broken by mutation: {e}")
            logger.critical("Initiating SOSS Phase 2 Git Hard Reset...")
            subprocess.run(["git", "checkout", "--", filepath], check=True)
            # Re-reload original module
            importlib.reload(module)
            logger.info(f"Self-Healing complete. {filepath} restored to previous commit state.")
            return False
