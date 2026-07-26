import time
import uuid

class StructuredEvent:
    def __init__(self, sender: str, event_type: str, payload: dict):
        self.event_id = str(uuid.uuid4())
        self.sender = sender
        self.event_type = event_type
        self.payload = payload
        self.timestamp = time.time()

class ResidentMessaging:
    def __init__(self):
        self.events = []

    def publish(self, sender: str, event_type: str, payload: dict):
        event = StructuredEvent(sender, event_type, payload)
        self.events.append(event)
        # In a real system, might use a queue or Redis
        return event

    def get_events(self, limit=100):
        return self.events[-limit:]
