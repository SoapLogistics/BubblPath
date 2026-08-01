import json
import datetime
from typing import Optional, List
from core.solomon_knowledge_cards.storage.db import DatabaseManager
from .models import Hypothesis, ExperimentDesign, Observation, EvaluationResult, BeliefUpdateRecord

class LaboratoryRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def store_hypothesis(self, hypothesis: Hypothesis) -> None:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                data = hypothesis.model_dump_json()

                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM lab_hypotheses WHERE id = ?", (hypothesis.id,))
                exists = cursor.fetchone()[0] > 0

                if exists:
                    conn.execute(
                        "UPDATE lab_hypotheses SET version = ?, data = ? WHERE id = ?",
                        (hypothesis.version, data, hypothesis.id)
                    )
                else:
                    conn.execute(
                        "INSERT INTO lab_hypotheses (id, version, data, created_at) VALUES (?, ?, ?, ?)",
                        (hypothesis.id, hypothesis.version, data, hypothesis.created_at)
                    )
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM lab_hypotheses WHERE id = ?", (hypothesis_id,))
                row = cursor.fetchone()
                if row:
                    return Hypothesis.model_validate_json(row[0])
                return None
            finally:
                conn.close()

    def store_experiment_design(self, design: ExperimentDesign) -> None:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                data = design.model_dump_json()

                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM lab_experiment_designs WHERE id = ?", (design.id,))
                exists = cursor.fetchone()[0] > 0

                if exists:
                    conn.execute(
                        "UPDATE lab_experiment_designs SET hypothesis_id = ?, version = ?, data = ? WHERE id = ?",
                        (design.hypothesis_id, design.version, data, design.id)
                    )
                else:
                    conn.execute(
                        "INSERT INTO lab_experiment_designs (id, hypothesis_id, version, data, created_at) VALUES (?, ?, ?, ?, ?)",
                        (design.id, design.hypothesis_id, design.version, data, design.created_at)
                    )
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def get_experiment_design(self, design_id: str) -> Optional[ExperimentDesign]:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM lab_experiment_designs WHERE id = ?", (design_id,))
                row = cursor.fetchone()
                if row:
                    return ExperimentDesign.model_validate_json(row[0])
                return None
            finally:
                conn.close()

    def store_observation(self, observation: Observation) -> None:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                data = observation.model_dump_json()

                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM lab_observations WHERE id = ?", (observation.id,))
                exists = cursor.fetchone()[0] > 0

                if exists:
                    conn.execute(
                        "UPDATE lab_observations SET experiment_id = ?, data = ? WHERE id = ?",
                        (observation.experiment_id, data, observation.id)
                    )
                else:
                    conn.execute(
                        "INSERT INTO lab_observations (id, experiment_id, data, created_at) VALUES (?, ?, ?, ?)",
                        (observation.id, observation.experiment_id, data, observation.timestamp)
                    )
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def get_observations_for_experiment(self, experiment_id: str) -> List[Observation]:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT data FROM lab_observations WHERE experiment_id = ?", (experiment_id,))
                rows = cursor.fetchall()
                return [Observation.model_validate_json(row[0]) for row in rows]
            finally:
                conn.close()

    def store_evaluation_result(self, result: EvaluationResult) -> None:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                data = result.model_dump_json()

                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM lab_evaluation_results WHERE id = ?", (result.id,))
                exists = cursor.fetchone()[0] > 0

                if exists:
                    conn.execute(
                        "UPDATE lab_evaluation_results SET experiment_id = ?, data = ? WHERE id = ?",
                        (result.experiment_id, data, result.id)
                    )
                else:
                    conn.execute(
                        "INSERT INTO lab_evaluation_results (id, experiment_id, data, created_at) VALUES (?, ?, ?, ?)",
                        (result.id, result.experiment_id, data, result.timestamp)
                    )
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()

    def get_evaluation_result(self, experiment_id: str) -> Optional[EvaluationResult]:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                cursor = conn.cursor()
                # Assuming one evaluation per experiment design for now, ordering by newest
                cursor.execute("SELECT data FROM lab_evaluation_results WHERE experiment_id = ? ORDER BY created_at DESC LIMIT 1", (experiment_id,))
                row = cursor.fetchone()
                if row:
                    return EvaluationResult.model_validate_json(row[0])
                return None
            finally:
                conn.close()

    def store_belief_update(self, update: BeliefUpdateRecord) -> None:
        with self.db._lock:
            conn = self.db._get_connection()
            try:
                conn.execute("BEGIN TRANSACTION;")
                data = update.model_dump_json()

                cursor = conn.cursor()
                cursor.execute("SELECT count(*) FROM lab_belief_updates WHERE id = ?", (update.id,))
                exists = cursor.fetchone()[0] > 0

                if exists:
                    conn.execute(
                        "UPDATE lab_belief_updates SET hypothesis_id = ?, experiment_id = ?, data = ? WHERE id = ?",
                        (update.hypothesis_id, update.experiment_id, data, update.id)
                    )
                else:
                    conn.execute(
                        "INSERT INTO lab_belief_updates (id, hypothesis_id, experiment_id, data, created_at) VALUES (?, ?, ?, ?, ?)",
                        (update.id, update.hypothesis_id, update.experiment_id, data, update.timestamp)
                    )
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
