import openai
import json
import logging
import types
import traceback
import multiprocessing
from solomon_core.soss.ast_validator import prove_code_safety
from solomon_core.soss.ast_injector import ASTInjector, InjectionError

logger = logging.getLogger(__name__)

class SynthesisError(Exception):
    pass

class CleanRoomSynthesizer:
    """
    The orchestrator for the Clean-Room Code Synthesis Sandbox.
    Generates code via LLM, mathematically proves it safe (AST Validator),
    runs sandbox unit tests, and hot-reloads via AST Injector.
    """
    def __init__(self, model="gpt-4o-mini"): # Use a fast/smart model
        self.model = model

    def synthesize_and_inject(self, algorithm_request: str, target_function: types.FunctionType) -> dict:
        """
        The full capability pipeline:
        1. Generate Code & Tests
        2. AST Validation
        3. Sandboxed Test Execution
        4. In-Memory Hot-Reload
        """
        func_name = target_function.__name__

        # Step 1: Generate Code
        try:
            generated_data = self._generate_code_and_tests(algorithm_request, func_name)
            new_code = generated_data.get("code")
            test_code = generated_data.get("test_code")
        except Exception as e:
            return {"status": "error", "step": "generation", "message": str(e)}

        if not new_code or not test_code:
            return {"status": "error", "step": "generation", "message": "Missing code or test_code in generation."}

        # Step 2: AST Validation
        is_safe, reason = prove_code_safety(new_code)
        if not is_safe:
            return {"status": "error", "step": "ast_validation", "message": reason, "code": new_code}

        is_safe_test, reason_test = prove_code_safety(test_code)
        if not is_safe_test:
            return {"status": "error", "step": "ast_validation", "message": f"Test code unsafe: {reason_test}", "code": test_code}

        # Step 3: Sandboxed Test Execution
        test_passed, test_msg = self._run_sandboxed_tests(new_code, test_code, func_name)
        if not test_passed:
            return {"status": "error", "step": "testing", "message": test_msg, "code": new_code, "test_code": test_code}

        # Step 4: In-Memory Hot-Reload
        try:
            # We backup the original code object just in case
            original_code_obj = target_function.__code__
            original_defaults = target_function.__defaults__
            original_kwdefaults = target_function.__kwdefaults__

            ASTInjector.hot_reload_function(target_function, new_code)

            # Post-injection sanity check - can we run it? (Basic test, but the unit tests proved the logic)
            # We rely on the unit tests from Step 3 as the primary validation.

            return {
                "status": "success",
                "message": f"Successfully synthesized and hot-reloaded '{func_name}'.",
                "code": new_code
            }

        except InjectionError as e:
            # Rollback (though ASTInjector doesn't mutate until the very end, so it should be safe)
            try:
                 target_function.__code__ = original_code_obj
                 target_function.__defaults__ = original_defaults
                 target_function.__kwdefaults__ = original_kwdefaults
            except Exception as rollback_e:
                 logger.error(f"CRITICAL: Failed to rollback after injection error: {rollback_e}")

            return {"status": "error", "step": "injection", "message": str(e)}
        except Exception as e:
             return {"status": "error", "step": "unknown", "message": str(e)}

    def _generate_code_and_tests(self, request: str, func_name: str) -> dict:
        """Calls OpenAI to generate the raw python code and tests."""
        prompt = f"""
        You are an elite, ultra-efficient AI coder.
        I need a Python algorithm for: "{request}"

        Requirements:
        1. Write a single, highly optimized function named strictly '{func_name}'.
        2. Do NOT use any forbidden modules (os, sys, etc.) or dangerous functions (eval, exec).
        3. Write a separate block of unit tests using standard `assert` statements (no pytest/unittest framework needed).
           The tests should call '{func_name}' directly and raise AssertionError on failure.
        4. Wrap the tests in a function named `run_tests()`.

        Return ONLY a raw JSON object with this exact schema (no markdown, no backticks):
        {{
            "code": "def {func_name}(...):\n    ...",
            "test_code": "def run_tests():\n    assert {func_name}(...) == ...\nrun_tests()"
        }}
        """
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        )

        content = response.choices[0].message["content"].strip()
        # Clean up markdown if the LLM ignored instructions
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]

        return json.loads(content.strip())

    def _execute_test_worker(self, code: str, test_code: str, func_name: str, result_queue: multiprocessing.Queue):
        """Worker function to run the tests in a separate process."""
        sandbox_globals = {
            "__builtins__": {
                "range": range, "len": len, "sum": sum, "min": min, "max": max,
                "abs": abs, "round": round, "int": int, "float": float, "str": str,
                "list": list, "dict": dict, "set": set, "tuple": tuple, "bool": bool,
                "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
                "Exception": Exception, "AssertionError": AssertionError, "ValueError": ValueError,
                "TypeError": TypeError
            }
        }

        try:
            compiled_code = compile(code, filename="<soss_gen>", mode="exec")
            exec(compiled_code, sandbox_globals)

            if func_name not in sandbox_globals:
                result_queue.put((False, f"Function '{func_name}' was not defined in generated code."))
                return

            compiled_test = compile(test_code, filename="<soss_test>", mode="exec")
            exec(compiled_test, sandbox_globals)

            result_queue.put((True, "Tests passed."))
        except AssertionError as e:
            result_queue.put((False, f"Unit tests failed (AssertionError): {str(e)}"))
        except Exception as e:
            result_queue.put((False, f"Error running tests: {str(e)}\n{traceback.format_exc()}"))


    def _run_sandboxed_tests(self, code: str, test_code: str, func_name: str, timeout: int = 5) -> tuple:
        """Executes the tests in a highly restricted globals environment with a timeout to prevent DoS."""
        result_queue = multiprocessing.Queue()

        process = multiprocessing.Process(
            target=self._execute_test_worker,
            args=(code, test_code, func_name, result_queue)
        )
        process.start()
        process.join(timeout)

        if process.is_alive():
            process.terminate()
            process.join()
            return False, f"Execution timed out after {timeout} seconds. (Potential infinite loop)"

        if not result_queue.empty():
            return result_queue.get()

        return False, "Unknown error during sandboxed test execution."
