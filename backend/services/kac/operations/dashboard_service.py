from .operations_center import OperationsCenter

class DashboardService:
    """
    Service layer providing HTTP-ready responses for the Joe KAOC UI.
    """
    def __init__(self, operations_center: OperationsCenter):
        self.operations = operations_center

    def fetch_ui_payload(self) -> dict:
        state = self.operations.get_comprehensive_dashboard_state()
        return {
            "status": "success",
            "data": state
        }
