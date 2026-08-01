import uuid
from typing import List, Optional, Dict, Any
import scipy.stats as stats
import numpy as np

from .models import Hypothesis, ExperimentDesign, Observation, EvaluationResult, BeliefUpdateRecord, ReproducibilityBundle
from .repository import LaboratoryRepository
from .executor import ExperimentExecutor

class LaboratoryService:
    def __init__(self, repository: LaboratoryRepository):
        self.repository = repository

    def register_hypothesis(
        self,
        scope: str,
        predicted_direction: str,
        predicted_magnitude: str,
        falsification_conditions: str,
        assumptions: List[str] = None,
        linked_evidence_ids: List[str] = None
    ) -> Hypothesis:
        hypothesis = Hypothesis(
            id=str(uuid.uuid4()),
            scope=scope,
            predicted_direction=predicted_direction,
            predicted_magnitude=predicted_magnitude,
            falsification_conditions=falsification_conditions,
            assumptions=assumptions or [],
            linked_evidence_ids=linked_evidence_ids or []
        )
        self.repository.store_hypothesis(hypothesis)
        return hypothesis

    def design_experiment(
        self,
        hypothesis_id: str,
        metrics: List[str],
        budget: float,
        evaluation_policy: str,
        variables: Dict[str, Any] = None,
        controls: List[str] = None,
        safety_constraints: List[str] = None,
        requires_controls: bool = True
    ) -> ExperimentDesign:

        # Verify hypothesis exists
        if not self.repository.get_hypothesis(hypothesis_id):
            raise ValueError(f"Hypothesis {hypothesis_id} not found.")

        design = ExperimentDesign(
            id=str(uuid.uuid4()),
            hypothesis_id=hypothesis_id,
            variables=variables or {},
            controls=controls or [],
            metrics=metrics,
            safety_constraints=safety_constraints or [],
            budget=budget,
            evaluation_policy=evaluation_policy,
            requires_controls=requires_controls
        )
        self.validate_design(design)
        self.repository.store_experiment_design(design)
        return design

    def validate_design(self, design: ExperimentDesign) -> bool:
        # Relies on Pydantic validation, but adds logical checks
        if design.budget < 0:
            raise ValueError("Budget cannot be negative.")
        if design.requires_controls and not design.controls:
            raise ValueError("Controls are required but none provided.")
        return True

    def execute_and_evaluate(self, design_id: str, executor: ExperimentExecutor) -> EvaluationResult:
        design = self.repository.get_experiment_design(design_id)
        if not design:
            raise ValueError(f"Experiment design {design_id} not found.")

        # 1. Execute
        observations = executor.execute(design)
        for obs in observations:
            self.repository.store_observation(obs)

        # 2. Evaluate
        return self.evaluate_results(design_id, observations)

    def evaluate_results(self, experiment_id: str, observations: List[Observation]) -> EvaluationResult:
        design = self.repository.get_experiment_design(experiment_id)
        if not design:
            raise ValueError(f"Experiment design {experiment_id} not found.")

        hypothesis = self.repository.get_hypothesis(design.hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {design.hypothesis_id} not found.")

        if not observations:
            # Null result - no data
            result = EvaluationResult(
                id=str(uuid.uuid4()),
                experiment_id=experiment_id,
                policy_version=design.evaluation_policy,
                is_successful=False,
                is_null=True,
                is_negative=False,
                statistics={},
                reasoning="No observations recorded."
            )
            self.repository.store_evaluation_result(result)
            return result

        # Basic statistical evaluation using scipy.stats
        # For this prototype, we'll extract the first metric defined in the design
        primary_metric = design.metrics[0]
        metric_values = []
        for obs in observations:
            if primary_metric in obs.metrics_recorded:
                metric_values.append(obs.metrics_recorded[primary_metric])

        stats_dict = {"n_observations": len(metric_values)}

        if len(metric_values) == 0:
             result = EvaluationResult(
                id=str(uuid.uuid4()),
                experiment_id=experiment_id,
                policy_version=design.evaluation_policy,
                is_successful=False,
                is_null=True,
                is_negative=False,
                statistics=stats_dict,
                reasoning=f"No data for primary metric: {primary_metric}"
            )
        elif len(metric_values) < 3:
             # Not enough data for a robust t-test, simple mean check against baseline 0
             mean_val = float(np.mean(metric_values))
             stats_dict["mean"] = mean_val

             # Rudimentary logic based on predicted direction
             is_success = False
             is_negative = False

             if hypothesis.predicted_direction.lower() == "increase" and mean_val > 0:
                 is_success = True
             elif hypothesis.predicted_direction.lower() == "decrease" and mean_val < 0:
                 is_success = True
             elif hypothesis.predicted_direction.lower() == "increase" and mean_val < 0:
                 is_negative = True
             elif hypothesis.predicted_direction.lower() == "decrease" and mean_val > 0:
                 is_negative = True

             result = EvaluationResult(
                id=str(uuid.uuid4()),
                experiment_id=experiment_id,
                policy_version=design.evaluation_policy,
                is_successful=is_success,
                is_null=not is_success and not is_negative,
                is_negative=is_negative,
                statistics=stats_dict,
                reasoning=f"Small sample size (n={len(metric_values)}). Mean={mean_val} evaluated against direction '{hypothesis.predicted_direction}'"
            )
        else:
            # Enough data for a 1-sample t-test against 0
            t_stat, p_val = stats.ttest_1samp(metric_values, 0.0)
            mean_val = float(np.mean(metric_values))

            stats_dict["mean"] = mean_val
            stats_dict["t_statistic"] = float(t_stat) if not np.isnan(t_stat) else 0.0
            stats_dict["p_value"] = float(p_val) if not np.isnan(p_val) else 1.0

            is_success = False
            is_negative = False

            # Using standard p < 0.05 for significance
            if stats_dict["p_value"] < 0.05:
                if hypothesis.predicted_direction.lower() == "increase" and mean_val > 0:
                    is_success = True
                elif hypothesis.predicted_direction.lower() == "decrease" and mean_val < 0:
                    is_success = True
                else:
                    # Significant effect in wrong direction
                    is_negative = True

            result = EvaluationResult(
                id=str(uuid.uuid4()),
                experiment_id=experiment_id,
                policy_version=design.evaluation_policy,
                is_successful=is_success,
                is_null=not is_success and not is_negative,
                is_negative=is_negative,
                statistics=stats_dict,
                reasoning=f"T-test evaluation: p={stats_dict['p_value']:.4f}, mean={mean_val}. Predicted: {hypothesis.predicted_direction}"
            )

        self.repository.store_evaluation_result(result)
        return result

    def propose_belief_update(self, experiment_id: str) -> BeliefUpdateRecord:
        design = self.repository.get_experiment_design(experiment_id)
        if not design:
            raise ValueError(f"Experiment design {experiment_id} not found.")

        evaluation = self.repository.get_evaluation_result(experiment_id)
        if not evaluation:
            raise ValueError(f"Evaluation for experiment {experiment_id} not found. Must evaluate first.")

        if evaluation.is_successful:
            shift = "Increase confidence in hypothesis. Evidence supports predictions."
        elif evaluation.is_negative:
            shift = "Decrease confidence in hypothesis. Evidence contradicts predictions."
        else:
            shift = "No change in confidence. Evidence is null or inconclusive."

        update = BeliefUpdateRecord(
            id=str(uuid.uuid4()),
            hypothesis_id=design.hypothesis_id,
            experiment_id=experiment_id,
            policy_version=evaluation.policy_version,
            proposed_belief_shift=shift
        )
        self.repository.store_belief_update(update)
        return update

    def export_reproducibility_bundle(self, experiment_id: str) -> ReproducibilityBundle:
        design = self.repository.get_experiment_design(experiment_id)
        if not design:
            raise ValueError(f"Experiment design {experiment_id} not found.")

        hypothesis = self.repository.get_hypothesis(design.hypothesis_id)
        if not hypothesis:
            raise ValueError(f"Hypothesis {design.hypothesis_id} not found.")

        observations = self.repository.get_observations_for_experiment(experiment_id)
        evaluation = self.repository.get_evaluation_result(experiment_id)

        return ReproducibilityBundle(
            experiment_id=experiment_id,
            hypothesis=hypothesis,
            design=design,
            observations=observations,
            evaluation=evaluation
        )
