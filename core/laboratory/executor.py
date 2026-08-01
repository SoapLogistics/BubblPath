from typing import Protocol, List
from .models import ExperimentDesign, Observation

class ExperimentExecutor(Protocol):
    """
    Protocol for pluggable experiment executors.
    Runners implement this to execute designs against real systems, APIs, or simulations.
    """

    def execute(self, design: ExperimentDesign) -> List[Observation]:
        """
        Executes the provided experiment design and returns a list of Observations.
        If the experiment fails, it should raise an exception or return partial observations
        (depending on the runner's policy), but null results should still return Observations.
        """
        ...
