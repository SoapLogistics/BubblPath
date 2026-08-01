import pytest
import os
import sys
import uuid
import threading
from pydantic import ValidationError

# Ensure core is on the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../core')))

from solomon_knowledge_cards.storage.db import DatabaseManager
from laboratory.repository import LaboratoryRepository
from laboratory.service import LaboratoryService
from laboratory.models import Hypothesis, ExperimentDesign, Observation
from laboratory.fake_executor import FakeExecutor

@pytest.fixture
def db_manager():
    # Use file based db for tests, since memory db drops schema in threaded contexts
    db_path = f"test_lab_{uuid.uuid4().hex}.db"
    manager = DatabaseManager(db_path)
    yield manager
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except Exception:
            pass

@pytest.fixture
def lab_repo(db_manager):
    return LaboratoryRepository(db_manager)

@pytest.fixture
def lab_service(lab_repo):
    return LaboratoryService(lab_repo)

def test_register_hypothesis(lab_service):
    hypo = lab_service.register_hypothesis(
        scope="memory_compression",
        predicted_direction="increase",
        predicted_magnitude="20%",
        falsification_conditions="compression ratio < 1.0"
    )
    assert hypo.id is not None
    assert hypo.scope == "memory_compression"
    assert hypo.predicted_direction == "increase"

    # Retrieve from DB
    retrieved = lab_service.repository.get_hypothesis(hypo.id)
    assert retrieved is not None
    assert retrieved.id == hypo.id

def test_experiment_design_validation(lab_service):
    hypo = lab_service.register_hypothesis(
        scope="test", predicted_direction="increase",
        predicted_magnitude="1", falsification_conditions="x < 1"
    )

    # Missing controls when required
    with pytest.raises(ValidationError, match="Controls are required"):
        lab_service.design_experiment(
            hypothesis_id=hypo.id,
            metrics=["speed"],
            budget=10.0,
            evaluation_policy="v1",
            controls=[], # Empty controls
            requires_controls=True
        )

    # Missing metrics
    with pytest.raises(ValidationError, match="at least 1 item after validation"):
        lab_service.design_experiment(
            hypothesis_id=hypo.id,
            metrics=[], # Empty metrics
            budget=10.0,
            evaluation_policy="v1",
            controls=["baseline"],
            requires_controls=True
        )

    # Negative budget
    with pytest.raises(ValidationError, match="ge"):
        lab_service.design_experiment(
            hypothesis_id=hypo.id,
            metrics=["speed"],
            budget=-5.0, # Negative budget
            evaluation_policy="v1",
            controls=["baseline"],
            requires_controls=True
        )

def test_execute_and_evaluate_success(lab_service):
    hypo = lab_service.register_hypothesis(
        scope="test", predicted_direction="increase",
        predicted_magnitude="1", falsification_conditions="x < 1"
    )

    design = lab_service.design_experiment(
        hypothesis_id=hypo.id,
        metrics=["speed"],
        budget=10.0,
        evaluation_policy="v1",
        controls=["baseline"],
        requires_controls=True
    )

    # Inject fake observations that clearly show an increase (mean > 0, p < 0.05)
    obs = [
        Observation(id=str(uuid.uuid4()), experiment_id=design.id, metrics_recorded={"speed": 5.0}),
        Observation(id=str(uuid.uuid4()), experiment_id=design.id, metrics_recorded={"speed": 6.0}),
        Observation(id=str(uuid.uuid4()), experiment_id=design.id, metrics_recorded={"speed": 5.5})
    ]
    executor = FakeExecutor(override_observations=obs)

    result = lab_service.execute_and_evaluate(design.id, executor)
    assert result.is_successful is True
    assert result.is_negative is False
    assert result.is_null is False
    assert "t_statistic" in result.statistics

def test_execute_and_evaluate_negative(lab_service):
    hypo = lab_service.register_hypothesis(
        scope="test", predicted_direction="increase",
        predicted_magnitude="1", falsification_conditions="x < 1"
    )

    design = lab_service.design_experiment(
        hypothesis_id=hypo.id,
        metrics=["speed"],
        budget=10.0,
        evaluation_policy="v1",
        controls=["baseline"],
        requires_controls=True
    )

    # Inject fake observations that clearly show a decrease (mean < 0, p < 0.05) when increase was expected
    obs = [
        Observation(id=str(uuid.uuid4()), experiment_id=design.id, metrics_recorded={"speed": -5.0}),
        Observation(id=str(uuid.uuid4()), experiment_id=design.id, metrics_recorded={"speed": -6.0}),
        Observation(id=str(uuid.uuid4()), experiment_id=design.id, metrics_recorded={"speed": -5.5})
    ]
    executor = FakeExecutor(override_observations=obs)

    result = lab_service.execute_and_evaluate(design.id, executor)
    assert result.is_successful is False
    assert result.is_negative is True
    assert result.is_null is False

def test_executor_failure(lab_service):
    hypo = lab_service.register_hypothesis(
        scope="test", predicted_direction="increase",
        predicted_magnitude="1", falsification_conditions="x < 1"
    )
    design = lab_service.design_experiment(
        hypothesis_id=hypo.id, metrics=["speed"], budget=10.0,
        evaluation_policy="v1", controls=["baseline"]
    )

    executor = FakeExecutor(fail_on_run=True)
    with pytest.raises(RuntimeError, match="configured to fail"):
        lab_service.execute_and_evaluate(design.id, executor)

def test_propose_belief_update(lab_service):
    hypo = lab_service.register_hypothesis(
        scope="test", predicted_direction="increase",
        predicted_magnitude="1", falsification_conditions="x < 1"
    )
    design = lab_service.design_experiment(
        hypothesis_id=hypo.id, metrics=["speed"], budget=10.0,
        evaluation_policy="v1", controls=["baseline"]
    )

    # Default FakeExecutor creates a positive result with N=1 (mean=1.0)
    # Our small sample fallback will evaluate this as success since mean > 0 and pred="increase"
    executor = FakeExecutor()
    lab_service.execute_and_evaluate(design.id, executor)

    update = lab_service.propose_belief_update(design.id)
    assert "Increase confidence" in update.proposed_belief_shift

def test_export_reproducibility_bundle(lab_service):
    hypo = lab_service.register_hypothesis(
        scope="test", predicted_direction="increase",
        predicted_magnitude="1", falsification_conditions="x < 1"
    )
    design = lab_service.design_experiment(
        hypothesis_id=hypo.id, metrics=["speed"], budget=10.0,
        evaluation_policy="v1", controls=["baseline"]
    )

    executor = FakeExecutor()
    lab_service.execute_and_evaluate(design.id, executor)

    bundle = lab_service.export_reproducibility_bundle(design.id)
    assert bundle.experiment_id == design.id
    assert bundle.hypothesis.id == hypo.id
    assert bundle.design.id == design.id
    assert len(bundle.observations) == 1
    assert bundle.evaluation is not None

def test_persistence_round_trip(db_manager):
    # Test that db migrations hold up across new repository instances
    repo1 = LaboratoryRepository(db_manager)
    service1 = LaboratoryService(repo1)

    hypo = service1.register_hypothesis(
        scope="persist", predicted_direction="neutral",
        predicted_magnitude="0", falsification_conditions="none"
    )

    repo2 = LaboratoryRepository(db_manager)
    hypo_retrieved = repo2.get_hypothesis(hypo.id)

    assert hypo_retrieved is not None
    assert hypo_retrieved.id == hypo.id
    assert hypo_retrieved.scope == "persist"
