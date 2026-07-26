import time
import threading
from core.residents.messaging import ResidentMessaging
from core.residents.checkpoint import CheckpointEngine

class RegistrationService:
    def __init__(self):
        self.residents = {}

    def register(self, resident):
        self.residents[resident.name] = resident

    def get_all(self):
        return list(self.residents.values())

    def get(self, name):
        return self.residents.get(name)

class Watchdog:
    def __init__(self, registration_service, timeout=30.0):
        self.registration = registration_service
        self.timeout = timeout

    def check_health(self):
        now = time.time()
        issues = []
        for res in self.registration.get_all():
            if now - res.last_heartbeat > self.timeout and res.running:
                issues.append(f"Resident {res.name} missed heartbeat.")
                res.health = "DEGRADED"
        return issues

class LifecycleEngine:
    def __init__(self):
        self.messaging = ResidentMessaging()
        self.checkpoint = CheckpointEngine()
        self.registration = RegistrationService()
        self.watchdog = Watchdog(self.registration)

    def register_resident(self, resident_class):
        resident = resident_class(messaging=self.messaging, checkpoint_engine=self.checkpoint)
        self.registration.register(resident)
        return resident

    def start_all(self):
        for res in self.registration.get_all():
            res.start()

    def stop_all(self):
        for res in self.registration.get_all():
            res.stop()
