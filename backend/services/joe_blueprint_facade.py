# backend/services/joe_blueprint_facade.py

# Registry metadata
route_key = "joe_blueprint_facade"

from services.solomon_joe_bridge import JoeOmegaEngine

class JoeBlueprintFacade:
    def __init__(self):
        self.engine = JoeOmegaEngine()

    def handle_queue_request(self, payload):
        """
        Safe HTTP facade handler. Enforces dry-run default.
        """
        # Always defaults to dry-run
        is_execute = payload.get("execute", False)

        # Facade enforce dry run for unapproved mutations
        # Here we hardcode dry run to True unless explicitly handled by governance later
        return self.engine.queue_blueprint(payload.get("blueprint"), run_execute=False)
