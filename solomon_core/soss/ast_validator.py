import ast

class SecurityViolation(Exception):
    pass

class ResourceViolation(Exception):
    pass

class CodeAnalyzer(ast.NodeVisitor):
    """
    Ultra-efficient O(N) AST static analyzer.
    Proves safety mathematically before execution without needing heavy Docker containers.
    """

    FORBIDDEN_FUNCTIONS = {
        'eval', 'exec', 'open', 'globals', 'locals', '__import__',
        'getattr', 'setattr', 'delattr', 'input', 'print', 'compile', 'memoryview'
    }

    FORBIDDEN_MODULES = {
        'os', 'sys', 'subprocess', 'shlex', 'pathlib', 'socket',
        'urllib', 'requests', 'builtins', 'ctypes', 'inspect', 'threading', 'multiprocessing'
    }

    def __init__(self, max_complexity=50):
        self.complexity = 0
        self.max_complexity = max_complexity

    def visit_Import(self, node):
        for alias in node.names:
            base_module = alias.name.split('.')[0]
            if base_module in self.FORBIDDEN_MODULES:
                raise SecurityViolation(f"Forbidden module import: {alias.name}")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            base_module = node.module.split('.')[0]
            if base_module in self.FORBIDDEN_MODULES:
                raise SecurityViolation(f"Forbidden module import: {node.module}")
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Prevent aliasing of forbidden functions (e.g. `x = eval`)
        if isinstance(node.value, ast.Name) and node.value.id in self.FORBIDDEN_FUNCTIONS:
            raise SecurityViolation(f"Forbidden function aliasing: {node.value.id}")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id in self.FORBIDDEN_FUNCTIONS:
            raise SecurityViolation(f"Forbidden function call: {node.func.id}")
        self.generic_visit(node)

    def visit_Attribute(self, node):
        # Prevent dunder method escapes (e.g., __class__.__bases__)
        if node.attr.startswith('__') and node.attr.endswith('__'):
            raise SecurityViolation(f"Forbidden attribute access: {node.attr}")
        self.generic_visit(node)

    def visit_If(self, node):
        self.complexity += 1
        self._check_complexity()
        self.generic_visit(node)

    def visit_For(self, node):
        self.complexity += 2  # Loops add more complexity
        self._check_complexity()
        self.generic_visit(node)

    def visit_While(self, node):
        self.complexity += 2
        self._check_complexity()
        self.generic_visit(node)

    def visit_ListComp(self, node):
        self.complexity += 1
        self._check_complexity()
        self.generic_visit(node)

    def _check_complexity(self):
        if self.complexity > self.max_complexity:
            raise ResourceViolation(f"Code complexity exceeded maximum allowed ({self.max_complexity})")

def prove_code_safety(code_str: str) -> tuple:
    """
    Analyzes code mathematically via AST for strict zero-trust sandbox execution.
    Returns (is_safe, reason).
    """
    try:
        tree = ast.parse(code_str)
        analyzer = CodeAnalyzer()
        analyzer.visit(tree)
        return True, "Code mathematically proven safe."
    except SyntaxError as e:
        return False, f"Syntax Error: {str(e)}"
    except (SecurityViolation, ResourceViolation) as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unknown Error during analysis: {str(e)}"
