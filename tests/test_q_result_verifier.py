from services.q_result_verifier import QResultVerifier
import os

def test_q_result_verifier():
    db_path = "test_memory_atoms.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    verifier = QResultVerifier(db_path=db_path)
    packet = {"id": "packet_001", "context": "test"}
    verifier.verify(packet, {"status": "pass"})

    packet_fail = {"id": "packet_002"}
    verifier.verify(packet_fail, {"status": "fail", "error": "AssertionError"})

    verifier.record_repair("packet_002", "Fixed assertion")

    memories = verifier.get_recalled_memories()
    assert len(memories) == 3

    packet_new = {"id": "packet_003"}
    packet_new = verifier.inject_preface(packet_new)
    assert "preface" in packet_new
    assert len(packet_new["preface"]) == 3

    if os.path.exists(db_path):
        os.remove(db_path)
