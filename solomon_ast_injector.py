"""Solomon Perpetual Learning Machine
AST Injector & Code Rewriter (SOSS Phase 4)

This module uses Python's native AST (Abstract Syntax Tree) module
to dynamically parse class definitions, programmatically inject
new methods/wrappers, and compile and hot-reload code in-memory,
delivering zero-downtime self-healing software execution.
"""
import ast
import inspect
import sys
import importlib
from typing import Dict, Any, Type, Optional

class ClassMethodInjector(ast.NodeTransformer):
    """
    AST Transformer to locate a ClassDef by name and append new method AST nodes into its body.
    """
    def __init__(self, target_class_name: str, method_node: ast.FunctionDef):
        self.target_class_name = target_class_name
        self.method_node = method_node
        self.injection_successful = False

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        """
        Locates the targeted class Def and appends the function node to its body.
        """
        if node.name == self.target_class_name:
            # Check if method already exists, if so, replace it
            node.body = [item for item in node.body if not (isinstance(item, ast.FunctionDef) and item.name == self.method_node.name)]
            node.body.append(self.method_node)
            self.injection_successful = True
        return self.generic_visit(node)

class ASTInjector:
    """
    Manages in-memory and disk-based programmatic AST class mutations and hot-reloading.
    """
    @classmethod
    def inject_method_to_file(
        cls,
        filepath: str,
        target_class_name: str,
        method_source: str
    ) -> Dict[str, Any]:
        """
        Reads a python file, parses its AST, programmatically injects a new method
        into target_class_name, and writes it back to disk.
        """
        # Read the file's current source
        with open(filepath, "r", encoding="utf-8") as f:
            source_code = f.read()

        # Parse the file's AST
        module_ast = ast.parse(source_code)

        # Parse the new method source code
        method_ast = ast.parse(method_source.strip())
        if not method_ast.body or not isinstance(method_ast.body[0], ast.FunctionDef):
            raise ValueError("Provided method source must contain a valid function definition.")

        function_def_node = method_ast.body[0]

        # Transform the AST (Inject the function def node)
        transformer = ClassMethodInjector(target_class_name, function_def_node)
        modified_ast = transformer.visit(module_ast)

        if not transformer.injection_successful:
            return {
                "success": False,
                "message": f"Class '{target_class_name}' not found in AST of {filepath}."
            }

        # Re-generate the modified source code using native ast.unparse() (standard in Python 3.9+)
        modified_source = ast.unparse(modified_ast)

        # Write modified source back to disk
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(modified_source)

        return {
            "success": True,
            "modified_source": modified_source,
            "injected_method_name": function_def_node.name,
            "message": f"Successfully injected method '{function_def_node.name}' into Class '{target_class_name}'."
        }

    @classmethod
    def hot_reload_module(cls, module_name: str, class_name: str) -> Optional[Type]:
        """
        Dynamically reload the specified module and retrieve the mutated class definition,
        instantly updating the execution environment.
        """
        if module_name in sys.modules:
            # Force dynamic reload of the updated python file from disk
            reloaded_module = importlib.reload(sys.modules[module_name])
        else:
            reloaded_module = importlib.import_module(module_name)

        mutated_class = getattr(reloaded_module, class_name, None)
        return mutated_class
