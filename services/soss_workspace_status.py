class SossWorkspaceStatus:
    readiness_key = "soss_workspace_ready"

    def get_status(self):
        return {"status": "ok"}
