from core.residents.framework import BaseResident, ResidentState

readiness_key = "jules_resident_engine"

class JulesResident(BaseResident):
    def __init__(self, messaging, checkpoint_engine):
        super().__init__("Jules", messaging, checkpoint_engine)
        self.mature_systems_unified = 0
        self.found_integration_opportunity = False

    def on_recover(self, state: dict):
        self.mature_systems_unified = state.get("mature_systems_unified", 0)

    def get_checkpoint_state(self) -> dict:
        return {"mature_systems_unified": self.mature_systems_unified}

    def scan_assigned_domain(self):
        self.state = ResidentState.SCANNING
        self.current_task = "Scanning for mature subsystems to unify"
        # Jules puts the vine back together. Detects duplicate mature implementations.

    def collect_evidence(self):
        self.state = ResidentState.COLLECTING
        self.current_task = "Analyzing architectural fragmentation"
        # Collects patterns of convergence.
        self.found_integration_opportunity = (self.mature_systems_unified < 10)

    def produce_findings(self):
        self.state = ResidentState.PRODUCING
        self.current_task = "Publishing Convergence Report"
        self.last_report = f"Convergence Report: found_opportunity={self.found_integration_opportunity}"
        self.messaging.publish(self.name, "Convergence Report", {"opportunity": self.found_integration_opportunity})

    def needs_proposal(self) -> bool:
        return self.found_integration_opportunity

    def prepare_governed_proposals(self):
        self.state = ResidentState.PROPOSING
        self.current_task = "Preparing SS2 -> SS3 -> SS1 governed integration proposal"
        self.mature_systems_unified += 1
