import ast


class ASTCodeInjector:
    """
    Parses, traverses, and programmatically mutates Python files using Abstract Syntax Trees (AST).
    Enables Gabriel to modify his own active codebase and inject dynamic endpoints or modules
    at runtime without relying on simple string concatenation.
    """

    @staticmethod
    def inject_function_to_class(
        file_path: str,
        class_name: str,
        function_source: str,
        output_path: str | None = None
    ) -> str:
        """
        Parses a Python file, locates the class `class_name`, parses `function_source`
        as an AST FunctionDef node, and appends it to the class's body.
        Saves changes to `output_path` (or overwrites `file_path` if not specified).
        Returns the generated source code.
        """
        if not output_path:
            output_path = file_path

        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        func_tree = ast.parse(function_source)

        # Extract the FunctionDef node from target source
        func_node = None
        for node in func_tree.body:
            if isinstance(node, ast.FunctionDef):
                func_node = node
                break

        if not func_node:
            raise ValueError("Provided function_source does not contain a valid function definition.")

        # Traverse AST to find class definition node
        class_found = False
        class ast_visitor(ast.NodeTransformer):
            def visit_ClassDef(self, node):
                nonlocal class_found
                if node.name == class_name:
                    class_found = True
                    # Check if function with the same name already exists to avoid duplication
                    existing_names = {item.name for item in node.body if isinstance(item, ast.FunctionDef)}
                    if func_node.name not in existing_names:
                        node.body.append(func_node)
                return self.generic_visit(node)

        visitor = ast_visitor()
        visitor.visit(tree)

        if not class_found:
            raise ValueError(f"Class '{class_name}' was not found in AST of {file_path}.")

        # Regenerate source code from mutated AST
        new_source = ast.unparse(tree)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_source)

        return new_source

    @staticmethod
    def inject_to_module_body(
        file_path: str,
        code_source: str,
        output_path: str | None = None
    ) -> str:
        """
        Parses a Python file and appends the parsed `code_source` node structure
        directly to the bottom of the module body.
        """
        if not output_path:
            output_path = file_path

        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source)
        code_tree = ast.parse(code_source)

        # Append nodes to module level body
        for node in code_tree.body:
            tree.body.append(node)

        new_source = ast.unparse(tree)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(new_source)

        return new_source
