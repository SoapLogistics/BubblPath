import logging
import inspect
from typing import Callable
from solomon_core.soss.ast_injector import AdvancedASTInjector
from solomon_core.gabriel.router import GabrielTaskRouter

logger = logging.getLogger("SOSS_Synthesizer")

class CleanRoomSynthesizer:
    """
    SOSS Phase 5: Generates self-healing code logic utilizing the Gabriel Router,
    then automatically injects it back into the runtime using the AST Injector.
    """
    def __init__(self):
        self.router = GabrielTaskRouter()

    def heal_function(self, target_func: Callable, error_trace: str) -> bool:
        """
        Takes a broken function and its stack trace, asks Gabriel to rewrite the logic,
        and injects the new logic into the live system.
        """
        func_name = target_func.__name__
        try:
            source = inspect.getsource(target_func)
        except Exception as e:
            logger.error(f"Cannot get source for {func_name}: {e}")
            return False

        prompt = (
            f"The function '{func_name}' is throwing the following error:\n{error_trace}\n\n"
            f"Here is the current source code:\n```python\n{source}\n```\n\n"
            "Provide ONLY the raw python logic intended for the inside of the function body to fix this. "
            "Do not include the function def signature, only the indented body. No markdown formatting."
        )

        logger.info(f"Synthesizer delegating repair of '{func_name}' to Gabriel Swarm...")
        swarm_result = self.router.execute_task(prompt)
        new_logic = swarm_result.get("consensus_output")

        if not new_logic or new_logic == "Critical Swarm Failure":
            logger.error("Gabriel Swarm failed to generate a repair logic.")
            return False

        # Clean up the output in case LLM added markdown despite instructions
        if new_logic.startswith("```python"):
            new_logic = "\n".join(new_logic.split("\n")[1:-1])

        logger.info(f"Synthesizer injecting repaired logic into '{func_name}'...")
        return AdvancedASTInjector.mutate_function(target_func, new_logic)
