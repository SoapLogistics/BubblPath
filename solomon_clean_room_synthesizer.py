import ast
import types

class CleanRoomSynthesizer:
    """
    Path 4: Clean-Room Code Synthesis Sandbox
    When Gabriel extracts a solid pattern, it writes native Python code for it.
    It parses it via AST for safety, and if valid, dynamically loads it as a native capability.
    """
    def __init__(self):
        self.active_capabilities = {}

    def synthesize_and_load(self, capability_name, python_code_string):
        """
        Safely parses a string of Python code via AST, compiles it, and binds it to memory.
        """
        try:
            # 1. AST Validation (Sandbox)
            parsed_ast = ast.parse(python_code_string)

            # Simple static analysis: ensure no dangerous imports (e.g., os, subprocess)
            for node in ast.walk(parsed_ast):
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name in ['os', 'sys', 'subprocess']:
                            return {"status": "rejected", "reason": f"Dangerous import '{alias.name}' blocked."}

            # 2. Compile to Bytecode
            compiled_code = compile(parsed_ast, filename="<ast>", mode="exec")

            # 3. Hot-Reload into an isolated namespace
            isolated_namespace = {}
            exec(compiled_code, isolated_namespace)

            # 4. Bind the first function found as the capability
            for key, val in isolated_namespace.items():
                if isinstance(val, types.FunctionType):
                    self.active_capabilities[capability_name] = val
                    return {"status": "success", "capability": capability_name, "function": key}

            return {"status": "failed", "reason": "No valid function found in code string."}

        except SyntaxError as e:
            return {"status": "rejected", "reason": f"Syntax Error: {str(e)}"}
        except Exception as e:
            return {"status": "error", "reason": str(e)}

    def execute_capability(self, capability_name, *args, **kwargs):
        """
        Executes a hot-reloaded capability natively.
        """
        if capability_name in self.active_capabilities:
            return self.active_capabilities[capability_name](*args, **kwargs)
        return {"error": "Capability not found."}

clean_room = CleanRoomSynthesizer()
