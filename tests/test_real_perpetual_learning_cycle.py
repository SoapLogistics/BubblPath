import pytest
import sqlite3
import datetime
from services.solomon_learning_writeback import LearningWriteback
from services.solomon_governance_approval_packet import GovernanceApprovalLane
import core.solomon_knowledge_cards.storage.db as db_manager

from core.solomon_knowledge_cards.models.card import KnowledgeCard

class DummyEmbedder:
    def get_embedding(self, text):
        return [0.1] * 128
    def cosine_similarity(self, v1, v2):
        return 0.9

from services.solomon_plc_engine import PerpetualLearningEngine

def test_real_perpetual_learning_cycle(tmp_path):
    # 0. Setup isolated state using tmp_path
    db_file = str(tmp_path / "solomon_soss.db")
    gov_log_file = str(tmp_path / "governance_log.bin")

    db = db_manager.DatabaseManager(db_file)
    engine = PerpetualLearningEngine(db_manager=db, embedder=DummyEmbedder(), gov_log_file=gov_log_file)

    # 1. Task failure -> event creation
    event_id = engine.record_event("task_failure", "Failed to connect to API on port 8080")

    # 2-4. Non-empty candidate -> duplicate check -> validation -> approval -> active memory
    lesson_content = "Always check firewall settings when connection fails."
    card_id = engine.process_failure("task_001", event_id, lesson_content)
    assert card_id is not None

    # Attempting duplicate creates no card
    dup_card_id = engine.process_failure("task_001", event_id, lesson_content)
    assert dup_card_id is None

    # 5. Retrieval before a similar task
    retrieved_card, competing, latency = engine.retrieve_memory("connection failed on port 8080")
    assert retrieved_card is not None
    assert retrieved_card.body == lesson_content

    # 6. Successful attempt -> outcome scoring
    engine.record_successful_use("task_002", retrieved_card)

    # 7. Checkpointing
    chk_id = engine.create_checkpoint("learning_cycle_completed")

    # 8. Restart check
    engine2 = PerpetualLearningEngine(db_manager=db_manager.DatabaseManager(db_file), embedder=DummyEmbedder(), gov_log_file=gov_log_file)
    latest_chk = engine2.get_latest_checkpoint()
    assert latest_chk is not None
    assert latest_chk["id"] == chk_id

    # Verify no state duplication allowed via duplicate writeback test
    res_dup = engine2.writeback.record_lesson("pkt_001", "fail", "event", lesson_content)
    assert res_dup["recorded"] == False
