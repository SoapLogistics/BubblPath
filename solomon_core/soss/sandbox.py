import ast
import traceback
import sys
import io
from typing import Dict, Any
from solomon_core.interfaces import ISandbox

class SafeASTNodeVisitor(ast.NodeVisitor):
    """
    Validates AST to prevent dangerous imports (e.g., os, subprocess)
    in the execution sandbox.
    """
    def __init__(self):
        self.banned_modules = {'os', 'sys', 'subprocess', 'shutil', 'socket'}
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name.split('.')[0] in self.banned_modules:
                self.errors.append(f"Import of {alias.name} is forbidden.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module and node.module.split('.')[0] in self.banned_modules:
            self.errors.append(f"Import from {node.module} is forbidden.")
        self.generic_visit(node)

class PythonCrucible(ISandbox):
    """
    Crucible (SS2) Environment for evaluating generated code.
    Utilizes AST inspection and standard library `exec` with a restricted globals dictionary.
    Note: For a true 20-year production system, this would be isolated via Docker/WASM.
    """

    def execute(self, code: str, inputs: Dict[str, Any], timeout: int = 5) -> Dict[str, Any]:
        # 1. Parse and validate AST
        try:
            tree = ast.parse(code)
            visitor = SafeASTNodeVisitor()
            visitor.visit(tree)
            if visitor.errors:
                return {"success": False, "error": "Security validation failed.", "details": visitor.errors}
        except SyntaxError as e:
            return {"success": False, "error": "Syntax Error", "details": str(e)}

        # 2. Setup restricted environment
        # Capture stdout
        old_stdout = sys.stdout
        redirected_output = sys.stdout = io.StringIO()

        # Inject inputs securely
        restricted_globals = {
            "__builtins__": __builtins__,
            **inputs
        }

        # 3. Execute
        # Note: timeout enforcement in pure Python `exec` is complex.
        # In a real environment, we'd use `multiprocessing` to enforce timeouts,
        # but per SED we start simple.
        try:
            # We compile first to catch compilation errors cleanly
            compiled_code = compile(tree, filename="<ast>", mode="exec")
            exec(compiled_code, restricted_globals)
            success = True
            error_msg = None
        except Exception as e:
            success = False
            error_msg = traceback.format_exc()
        finally:
            sys.stdout = old_stdout

        output = redirected_output.getvalue()

        # Extract variables mutated during execution (excluding builtins)
        state_changes = {k: v for k, v in restricted_globals.items() if k != "__builtins__"}

        return {
            "success": success,
            "stdout": output,
            "error": error_msg,
            "state": state_changes
        }
