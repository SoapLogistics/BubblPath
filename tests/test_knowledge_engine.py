import unittest
import os
import json
import tempfile

# Set environment variables for the test suite before importing app or db
os.environ["SOLOMON_DB_PATH"] = "test_app_only.db"

from solomon_knowledge_cards.models import KnowledgeCardModel, CardType, CardStatus, ValidationState, CardRelation
from solomon_knowledge_cards.db import SQLiteDatabase
from solomon_knowledge_cards.repository import KnowledgeRepository
from solomon_knowledge_cards.engine import KnowledgeEngine
from solomon_knowledge_cards.importer import DoctrineImporter
from app import app

class TestKnowledgeCardEngine(unittest.TestCase):
    def setUp(self):
        # Establish unique, isolated sqlite database files at the module level
        self.db_path = "test_app_only.db"
        self.db = SQLiteDatabase(self.db_path)
        self.repo = KnowledgeRepository(self.db)
        self.engine = KnowledgeEngine(self.repo)
        self.importer = DoctrineImporter(self.repo)

        # Override the app database components to point to our isolated test run DB
        import app as flask_app
        flask_app.db = self.db
        flask_app.repo = self.repo
        flask_app.engine = self.engine

    def tearDown(self):
        # Ensure clean file system handles and release DB locks
        self.db = None
        self.repo = None
        self.engine = None
        if os.path.exists(self.db_path):
            try:
                os.remove(self.db_path)
            except Exception:
                pass

    def test_schema_validation_and_creation(self):
        # Confirm required fields structure
        card = KnowledgeCardModel(
            card_id="TEST-001",
            card_type=CardType.LESSON,
            title="Valid Lesson Card",
            summary="This is a test summary.",
            body="This is a test body.",
            why_created="Reason",
            problem_solved="Problem",
            future_work_dependent="None"
        )
        card.validate()
        self.repo.create_card(card)

        fetched = self.repo.get_card("TEST-001")
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.title, "Valid Lesson Card")
        self.assertEqual(fetched.status, CardStatus.DRAFT)
        self.assertEqual(fetched.validation_state, ValidationState.PENDING)

    def test_invalid_schema_throws_value_error(self):
        # Invalid confidence bounds
        with self.assertRaises(ValueError):
            card = KnowledgeCardModel(
                card_id="TEST-INVALID",
                card_type=CardType.LESSON,
                title="Invalid Confidence",
                summary="Sum",
                body="Body",
                confidence=1.5
            )
            card.validate()

    def test_revision_history_tracking(self):
        card = KnowledgeCardModel(
            card_id="REVISION-001",
            card_type=CardType.KNOWLEDGE,
            title="Initial Title",
            summary="Init summary",
            body="Init body"
        )
        self.repo.create_card(card)

        # Update card
        card.title = "Updated Title"
        self.repo.update_card(card, actor="REVISER_ACTOR")

        history = self.repo.get_revision_history("REVISION-001")
        # History lists revisions in descending order
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["title"], "Updated Title")
        self.assertEqual(history[0]["updated_by"], "REVISER_ACTOR")
        self.assertEqual(history[1]["title"], "Initial Title")

    def test_duplicate_and_concurrency_robustness(self):
        card = KnowledgeCardModel(
            card_id="DUP-001",
            card_type=CardType.DECISION,
            title="First Decision",
            summary="Dec",
            body="Body"
        )
        self.repo.create_card(card)

        # Re-saving identical ID overwrites gracefully (Upsert behaves correctly)
        card_dup = KnowledgeCardModel(
            card_id="DUP-001",
            card_type=CardType.DECISION,
            title="Overwritten Decision",
            summary="Dec Overwrite",
            body="Body Overwrite"
        )
        self.repo.update_card(card_dup, actor="UPDATING_ACTOR")

        fetched = self.repo.get_card("DUP-001")
        self.assertEqual(fetched.title, "Overwritten Decision")

    def test_link_cards_relationships(self):
        parent = KnowledgeCardModel(card_id="PARENT-01", card_type=CardType.PROCEDURE, title="Parent SOP", summary="P", body="P")
        child = KnowledgeCardModel(card_id="CHILD-01", card_type=CardType.LESSON, title="Child Lesson", summary="C", body="C")

        self.repo.create_card(parent)
        self.repo.create_card(child)

        self.repo.link_cards("PARENT-01", "CHILD-01", relation_type=CardRelation.ENHANCES)

        fetched_parent = self.repo.get_card("PARENT-01")
        fetched_child = self.repo.get_card("CHILD-01")

        self.assertIn("CHILD-01", fetched_parent.related_card_ids)
        self.assertIn("PARENT-01", fetched_child.parent_card_ids)
        self.assertEqual(fetched_parent.metadata["links"]["CHILD-01"], CardRelation.ENHANCES)

        related = self.repo.retrieve_related_cards("PARENT-01")
        self.assertEqual(len(related), 1)
        self.assertEqual(related[0].card_id, "CHILD-01")

    def test_worker_report_extraction_success_lessons(self):
        report = {
            "task_id": "TASK-SUCCESS-100",
            "procedure_id": "PC-SO-01",
            "success": True,
            "summary": "Everything completed successfully. Performance improved by 20%.",
            "evidence": "Commit hash de40ff7"
        }

        generated = self.engine.extract_from_report(report)
        self.assertEqual(len(generated), 1)

        lesson_card = generated[0]
        self.assertEqual(lesson_card.card_type, CardType.LESSON)
        self.assertEqual(lesson_card.status, CardStatus.DRAFT)
        self.assertEqual(lesson_card.validation_state, ValidationState.PENDING)
        self.assertEqual(lesson_card.evidence, "Commit hash de40ff7")
        self.assertIn("PC-SO-01", lesson_card.parent_card_ids)

    def test_worker_report_extraction_failure_and_repair(self):
        report = {
            "task_id": "TASK-FAIL-200",
            "procedure_id": "PC-SO-02",
            "success": False,
            "summary": "Encountered timeout error while contacting openhands endpoint.",
            "error_logs": "Connection timeout after 30s.",
            "resolution": "Applied explicit timeout multiplier retry parameter inside config.",
            "evidence": "Run #740 log trace"
        }

        generated = self.engine.extract_from_report(report)
        # Yields both FAILURE card and REPAIR card
        self.assertEqual(len(generated), 2)

        fail_card = next(c for c in generated if c.card_type == CardType.FAILURE)
        repair_card = next(c for c in generated if c.card_type == CardType.REPAIR)

        self.assertEqual(fail_card.status, CardStatus.DRAFT)
        self.assertIn("PC-SO-02", fail_card.parent_card_ids)

        self.assertEqual(repair_card.status, CardStatus.DRAFT)
        self.assertIn(fail_card.card_id, repair_card.parent_card_ids)

    def test_review_gate_approval_and_rejection(self):
        card = KnowledgeCardModel(card_id="PROMOTION-01", card_type=CardType.LESSON, title="P", summary="S", body="B")
        self.repo.create_card(card)

        # Promotion Gate transitions: DRAFT -> REVIEWED -> APPROVED -> ACTIVE
        self.engine.promote_card("PROMOTION-01", reviewer="SS3")
        fetched = self.repo.get_card("PROMOTION-01")
        self.assertEqual(fetched.status, CardStatus.REVIEWED)
        self.assertEqual(fetched.validation_state, ValidationState.LLM_EVAL)

        self.engine.promote_card("PROMOTION-01", reviewer="SS3")
        fetched = self.repo.get_card("PROMOTION-01")
        self.assertEqual(fetched.status, CardStatus.APPROVED)
        self.assertEqual(fetched.validation_state, ValidationState.SYSTEM_VALIDATED)

        # Rejecting card sets status to DEPRECATED
        self.engine.reject_card("PROMOTION-01", reason="Flawed evidence", reviewer="SS3")
        fetched = self.repo.get_card("PROMOTION-01")
        self.assertEqual(fetched.status, CardStatus.DEPRECATED)
        self.assertEqual(fetched.validation_state, ValidationState.REJECTED)
        self.assertEqual(fetched.metadata["rejection_reason"], "Flawed evidence")

    def test_search_and_ranking_retrieval(self):
        c1 = KnowledgeCardModel(card_id="SRCH-01", card_type=CardType.FAILURE, title="OpenHands Timeout Error", summary="Encountered standard API timeout error", body="Body")
        c2 = KnowledgeCardModel(card_id="SRCH-02", card_type=CardType.REPAIR, title="Resolve Timeout issues", summary="Fix error config", body="Apply explicit timeouts")

        # Bypass repo.create_card which resets status to DRAFT
        c1.status = CardStatus.APPROVED
        c2.status = CardStatus.APPROVED

        self.repo.update_card(c1)
        self.repo.update_card(c2)

        results = self.engine.retrieve_active_operational_guidance("timeout")
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["card_id"], "SRCH-01")

    def test_import_and_export_round_trip(self):
        c = KnowledgeCardModel(card_id="EXPORT-01", card_type=CardType.SKILL, title="Specialized Coding Skill", summary="S", body="B")
        self.repo.create_card(c)

        # Temp backup files
        temp_dir = tempfile.mkdtemp()
        backup_path = os.path.join(temp_dir, "backup.jsonl")

        self.repo.export_cards(backup_path)
        self.assertTrue(os.path.exists(backup_path))

        # Clear and restore
        self.db.delete_card("EXPORT-01")
        self.repo.import_cards(backup_path)

        restored = self.repo.get_card("EXPORT-01")
        self.assertIsNotNone(restored)
        self.assertEqual(restored.title, "Specialized Coding Skill")

        # Cleanup
        os.unlink(backup_path)
        os.rmdir(temp_dir)

    def test_transitive_traversal(self):
        c1 = KnowledgeCardModel(card_id="A", card_type=CardType.PROCEDURE, title="Proc A", summary="S", body="B")
        c2 = KnowledgeCardModel(card_id="B", card_type=CardType.LESSON, title="Lesson B", summary="S", body="B")
        c3 = KnowledgeCardModel(card_id="C", card_type=CardType.FAILURE, title="Fail C", summary="S", body="B")

        self.repo.create_card(c1)
        self.repo.create_card(c2)
        self.repo.create_card(c3)

        # Build dependency chains: A -> B -> C
        self.repo.link_cards("A", "B", CardRelation.DEPENDS_ON)
        self.repo.link_cards("B", "C", CardRelation.PREVENTS)

        transitive_closure = self.repo.retrieve_transitive_relations("A")
        card_ids = [c.card_id for c in transitive_closure]
        self.assertIn("B", card_ids)
        self.assertIn("C", card_ids)

    def test_metrics_calculation(self):
        c1 = KnowledgeCardModel(card_id="METRIC-01", card_type=CardType.KNOWLEDGE, title="K", summary="S", body="B", confidence=0.8)
        c2 = KnowledgeCardModel(card_id="METRIC-02", card_type=CardType.DECISION, title="D", summary="S", body="B", confidence=0.4)
        c2.status = CardStatus.APPROVED

        self.repo.create_card(c1)
        self.repo.update_card(c2)

        # Run calculation
        temp_dir = tempfile.mkdtemp()
        metrics_path = os.path.join(temp_dir, "metrics.json")

        metrics = self.engine.calculate_sok_metrics(export_path=metrics_path)
        self.assertEqual(metrics["total_cards_count"], 2)
        self.assertEqual(metrics["distribution_by_type"]["KNOWLEDGE"], 1)
        self.assertEqual(metrics["distribution_by_type"]["DECISION"], 1)
        self.assertTrue(os.path.exists(metrics_path))

        # Cleanup
        os.unlink(metrics_path)
        os.rmdir(temp_dir)

    def test_skill_auto_generation(self):
        report = {
            "task_id": "TASK-GAP-1",
            "procedure_id": "PC-SO-01",
            "success": False,
            "summary": "Attempt failed to execute AST mapping.",
            "error_logs": "Exception: missing capability 'ASTInjector' not found.",
            "evidence": "Log seg #9"
        }

        generated = self.engine.extract_from_report(report)
        skill_cards = [c for c in generated if c.card_type == CardType.SKILL]
        self.assertEqual(len(skill_cards), 1)
        self.assertEqual(skill_cards[0].status, CardStatus.DRAFT)
        self.assertIn("missing capability 'ASTInjector' not found.", skill_cards[0].body)

    def test_growth_deduplication(self):
        c1 = KnowledgeCardModel(card_id="MAIN-SOP", card_type=CardType.LESSON, title="Main", summary="S", body="Exact Duplicate Content text.")
        c2 = KnowledgeCardModel(card_id="DUP-SOP", card_type=CardType.LESSON, title="Duplicate", summary="S", body="Exact Duplicate Content text.")
        stale_card = KnowledgeCardModel(card_id="STALE-01", card_type=CardType.LESSON, title="Stale", summary="S", body="Other text.", metadata={"is_stale_simulation": True})

        c1.status = CardStatus.APPROVED
        self.repo.update_card(c1)
        self.repo.create_card(c2)
        self.repo.create_card(stale_card)

        # Run background deduplication
        growth_results = self.engine.run_passive_growth_maintenance()
        self.assertEqual(growth_results["duplicates_merged"], 1)
        self.assertEqual(growth_results["stale_drafts_archived"], 1)

        # Confirm duplicate card got deprecated
        fetched_dup = self.repo.get_card("DUP-SOP")
        self.assertEqual(fetched_dup.status, CardStatus.DEPRECATED)
        self.assertIn("Merged as duplicate", fetched_dup.metadata["deduplication_status"])

        # Confirm stale card got archived
        fetched_stale = self.repo.get_card("STALE-01")
        self.assertEqual(fetched_stale.status, CardStatus.ARCHIVED)

    # NEW HTTP Endpoint Tests
    def test_status_endpoint(self):
        app.config["TESTING"] = True
        with app.test_client() as client:
            res = client.get("/api/command-center/status")
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["status"], "HEALTHY")

    def test_worker_report_endpoint(self):
        app.config["TESTING"] = True
        with app.test_client() as client:
            report_payload = {
                "task_id": "WEB-TASK-001",
                "procedure_id": "PC-SO-01",
                "success": True,
                "summary": "Everything ran correctly.",
                "evidence": "Log trace"
            }
            res = client.post("/api/command-center/worker-report", json=report_payload)
            self.assertEqual(res.status_code, 201)
            data = json.loads(res.data)
            self.assertEqual(data["status"], "SUCCESS")
            self.assertEqual(len(data["draft_cards"]), 1)

    def test_review_endpoint(self):
        app.config["TESTING"] = True

        # Insert a draft card
        c = KnowledgeCardModel(card_id="WEB-REV-01", card_type=CardType.LESSON, title="P", summary="S", body="B")
        self.repo.create_card(c)

        with app.test_client() as client:
            review_payload = {
                "card_id": "WEB-REV-01",
                "action": "APPROVE"
            }
            res = client.post("/api/command-center/review", json=review_payload)
            self.assertEqual(res.status_code, 200)
            data = json.loads(res.data)
            self.assertEqual(data["status"], "SUCCESS")
            self.assertEqual(data["card_status"], CardStatus.REVIEWED)

if __name__ == "__main__":
    unittest.main()
