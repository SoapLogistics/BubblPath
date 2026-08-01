import uuid
import datetime
from typing import List, Dict, Any, Optional
from .models import ExperimentDesign, Observation
from .executor import ExperimentExecutor

class FakeExecutor(ExperimentExecutor):
    """
    Deterministic fake executor for testing.
    Uses seeded behaviors based on the experiment design ID or variables to simulate
    success, null results, partial results, or failures.
    """
    def __init__(self, override_observations: Optional[List[Observation]] = None, fail_on_run: bool = False):
        self.override_observations = override_observations
        self.fail_on_run = fail_on_run

    def execute(self, design: ExperimentDesign) -> List[Observation]:
        if self.fail_on_run:
            raise RuntimeError("FakeExecutor configured to fail.")

        if self.override_observations is not None:
            return self.override_observations

        # Default behavior: generate one observation that matches metrics with dummy values
        metrics_recorded = {metric: 1.0 for metric in design.metrics}

        obs = Observation(
            id=str(uuid.uuid4()),
            experiment_id=design.id,
            timestamp=datetime.datetime.now(datetime.UTC).isoformat(),
            metrics_recorded=metrics_recorded,
            metadata={"source": "FakeExecutor", "note": "Deterministic default observation"}
        )
        return [obs]
