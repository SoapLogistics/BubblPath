class Reader:
    def __init__(self):
        self.sources = []
        self.artifacts = {}
        self.workspace_active = False
        self.conversations = []

    def ingest_source(self, source):
        self.sources.append(source)
        return True

    def get_sources(self):
        return self.sources

    def save_artifact(self, id, content):
        self.artifacts[id] = {"status": "saved", "content": content}
        return True

    def reopen_artifact(self, id):
        if id in self.artifacts:
            self.artifacts[id]["status"] = "reopened"
            return True
        return False

    def recover_artifact(self, id):
        if id in self.artifacts:
            self.artifacts[id]["status"] = "recovered"
            return True
        return False

    def activate_workspace(self, workspace_id):
        self.workspace_active = True
        return {"id": workspace_id, "active": self.workspace_active}

    def add_conversation(self, context, continuation):
        self.conversations.append({"context": context, "continuation": continuation})
        return True

    def get_conversation_memory(self):
        return [c["continuation"] for c in self.conversations]
