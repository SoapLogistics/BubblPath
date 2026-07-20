import time
import random
from typing import Callable, Any, Type, Tuple

class ExponentialBackoffRetry:
    """
    Executes calls with standard exponential delay backoffs,
    catching transient errors and retrying up to a fixed limit.
    """
    def __init__(self, max_retries: int = 4, base_delay: float = 0.5, max_delay: float = 4.0, jitter: bool = True):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def execute(self, func: Callable[..., Any], *args, exceptions_to_catch: Tuple[Type[Exception], ...] = (Exception,), **kwargs) -> Any:
        retries = 0
        while True:
            try:
                return func(*args, **kwargs)
            except exceptions_to_catch as e:
                if retries >= self.max_retries:
                    raise e

                # Calculate delay: base_delay * 2^retries
                delay = min(self.base_delay * (2 ** retries), self.max_delay)
                if self.jitter:
                    delay = random.uniform(0, delay)

                time.sleep(delay)
                retries += 1
