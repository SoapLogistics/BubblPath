# Adding Resident Startup hook to backend/main.py
import os
import threading
from core.solomon_resident_framework import ResidentFramework
from services.solomon_guardian import SolomonGuardian
from services.solomon_jules_resident import SolomonJulesResident

_residents_started = False
_resident_lock = threading.Lock()
_resident_instances = []

def start_residents():
    global _residents_started
    with _resident_lock:
        if not _residents_started:
            print("Starting Guardian and Jules residents...")
            fw = ResidentFramework()
            guardian = SolomonGuardian(fw)
            jules = SolomonJulesResident(fw)

            guardian.start()
            jules.start()

            _resident_instances.extend([guardian, jules])
            _residents_started = True

# Start residents automatically when the backend starts up in production
if __name__ == '__main__':
    start_residents()
