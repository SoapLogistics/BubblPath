import ast
import os
import importlib
import sys
import logging

logger = logging.getLogger(__name__)

class FunctionMutator(ast.NodeTransformer):
    """
    Transforms the AST to replace an existing function with a new implementation.
    """
    def __init__(self, target_function_name: str, new_function_node: ast.FunctionDef):
        self.target = target_function_name
        self.new_node = new_function_node
        self.mutated = False

    def visit_FunctionDef(self, node):
        if node.name == self.target:
            self.mutated = True
            return ast.copy_location(self.new_node, node)
        return self.generic_visit(node)

class ASTInjector:
    """
    SOSS Advanced AST Injector.
    Allows for dynamic, in-memory Python code mutation and hot-reloading.
    """
    @staticmethod
    def inject_and_reload(filepath: str, function_name: str, new_code: str) -> bool:
        """
        Parses the target file, replaces the specified function with new_code,
        writes it back, and attempts to hot-reload the module.
        """
        try:
            # Parse new code to get the new AST node
            new_tree = ast.parse(new_code)

            # Find the first function definition in the new code
            new_func_node = None
            for node in new_tree.body:
                if isinstance(node, ast.FunctionDef) and node.name == function_name:
                    new_func_node = node
                    break

            if not new_func_node:
                logger.error(f"Function {function_name} not found in the provided new code.")
                return False

            # Read and parse existing file
            with open(filepath, 'r') as f:
                source = f.read()
            original_tree = ast.parse(source)

            # Mutate the AST
            mutator = FunctionMutator(function_name, new_func_node)
            mutated_tree = mutator.visit(original_tree)

            if not mutator.mutated:
                logger.error(f"Target function {function_name} not found in {filepath}.")
                return False

            # Ensure the AST is valid
            ast.fix_missing_locations(mutated_tree)

            # Unparse the tree back to source code (Python 3.9+)
            new_source = ast.unparse(mutated_tree)

            # Write back safely
            backup_path = filepath + ".bak"
            os.rename(filepath, backup_path)
            with open(filepath, 'w') as f:
                f.write(new_source)

            # Hot-reload the module if it's already loaded in sys.modules
            module_name = ASTInjector._get_module_name(filepath)
            if module_name and module_name in sys.modules:
                importlib.reload(sys.modules[module_name])

            logger.info(f"Successfully injected {function_name} into {filepath}")
            return True

        except Exception as e:
            logger.error(f"AST Injection failed: {e}")
            # Rollback
            if os.path.exists(filepath + ".bak"):
                os.replace(filepath + ".bak", filepath)
            return False

    @staticmethod
    def _get_module_name(filepath: str) -> str:
        """Converts a filepath to a Python module name heuristically."""
        # This is a simplified heuristic for standard paths
        path = os.path.abspath(filepath)
        cwd = os.path.abspath(os.getcwd())
        if path.startswith(cwd):
            rel_path = os.path.relpath(path, cwd)
            module_str = rel_path.replace(os.sep, '.')
            if module_str.endswith('.py'):
                return module_str[:-3]
        return ""
