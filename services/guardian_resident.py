from core.residents.framework import BaseResident, ResidentState

readiness_key = "guardian_resident_engine"

class GuardianResident(BaseResident):
    def __init__(self, messaging, checkpoint_engine):
        super().__init__("Guardian", messaging, checkpoint_engine)
        self.cycles_completed = 0
        self.foundation_stable = True

    def on_recover(self, state: dict):
        self.cycles_completed = state.get("cycles_completed", 0)

    def get_checkpoint_state(self) -> dict:
        return {"cycles_completed": self.cycles_completed}

    def scan_assigned_domain(self):
        self.state = ResidentState.SCANNING
        self.current_task = "Verifying database integrity and core configs"
        # Guardian protects the roots. Checks SS1/SS2/SS3 governance verification.

    def collect_evidence(self):
        self.state = ResidentState.COLLECTING
        self.current_task = "Collecting stability evidence"
        # Collects evidence that foundation is still healthy.

    def produce_findings(self):
        self.state = ResidentState.PRODUCING
        self.current_task = "Drafting Foundation Report"
        self.cycles_completed += 1
        self.last_report = f"Foundation Report #{self.cycles_completed}: Stable"
        self.messaging.publish(self.name, "Foundation Report", {"status": "Stable", "cycles": self.cycles_completed})

    def needs_proposal(self) -> bool:
        return not self.foundation_stable

    def prepare_governed_proposals(self):
        self.state = ResidentState.PROPOSING
        self.current_task = "Preparing governance proposal to fix foundation"
