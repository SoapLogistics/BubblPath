import pytest
from backend.services.kac.operations.operations_center import OperationsCenter

class MockKACManager:
    def get_queue(self):
        return [{"status": "Waiting", "filename": "test.pdf"}]

    def get_stats(self):
        return {"books_processed": 10, "knowledge_yield": 95.0, "vault_capacity": 5.0}

def test_operations_center():
    mock_kac = MockKACManager()
    oc = OperationsCenter(mock_kac)

    state = oc.get_comprehensive_dashboard_state()

    assert state["health"]["status"] == "ONLINE"
    assert state["health"]["queue_depth"] == 1
    assert state["learning_activity"]["books_completed"] == 10
    assert state["learning_activity"]["current_book"] == "test.pdf"
