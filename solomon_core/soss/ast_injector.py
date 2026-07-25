import ast
import inspect
import types

class InjectionError(Exception):
    pass

class ASTInjector:
    """
    In-memory live-code mutation and hot-reloading.
    Dynamically swaps __code__ objects to change functionality in O(1) time
    without breaking references or requiring server restarts.
    """

    @staticmethod
    def hot_reload_function(target_func: types.FunctionType, new_code_str: str) -> None:
        """
        Takes a running function and completely replaces its logic with new_code_str
        by mutating the underlying bytecode (__code__ object).
        """
        if not isinstance(target_func, types.FunctionType):
            raise InjectionError("Target must be a Python function.")

        func_name = target_func.__name__

        # 1. Parse the new code string into an AST
        try:
            tree = ast.parse(new_code_str)
        except SyntaxError as e:
            raise InjectionError(f"Syntax Error in new code: {str(e)}")

        # 2. Find the target function definition in the AST
        new_func_node = None
        for node in tree.body:
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                new_func_node = node
                break

        if not new_func_node:
            raise InjectionError(f"Could not find function '{func_name}' in the provided code string.")

        # 3. Compile the new AST into a code object
        # We need a new module to compile it properly so we can extract the function's code object.
        try:
            compiled_module = compile(tree, filename="<ast_injector>", mode="exec")
        except Exception as e:
            raise InjectionError(f"Failed to compile new code: {str(e)}")

        # 4. Execute the compiled module in a clean namespace to extract the new function
        namespace = {}
        try:
            exec(compiled_module, namespace)
        except Exception as e:
            raise InjectionError(f"Failed to execute compiled module to extract function: {str(e)}")

        new_func = namespace.get(func_name)
        if not isinstance(new_func, types.FunctionType):
            raise InjectionError(f"Extracted object '{func_name}' is not a function.")

        # 5. Extract the __code__ object and perform the O(1) mutation
        try:
            # We preserve the original __closure__ if needed, but for purely isolated functions,
            # this works beautifully. We are pushing boundaries by literally mutating the runtime.
            target_func.__code__ = new_func.__code__
            # Also update defaults if they changed
            target_func.__defaults__ = new_func.__defaults__
            target_func.__kwdefaults__ = new_func.__kwdefaults__
        except Exception as e:
            raise InjectionError(f"Failed to mutate __code__ object: {str(e)}")
