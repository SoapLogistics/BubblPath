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
        # Even if True is passed in a standard facade route, we override for safety until governance kicks in
        return self.engine.queue_blueprint(payload.get("blueprint"), run_execute=False)

# Added as part of Phase 2 runbook
