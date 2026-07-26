import time
import os
from core.residents.engine import LifecycleEngine
from services.guardian_resident import GuardianResident
from services.jules_resident import JulesResident

def run_soak_test():
    print("Starting Long-Duration Soak Test...")
    engine = LifecycleEngine()
    guardian = engine.register_resident(GuardianResident)
    jules = engine.register_resident(JulesResident)

    engine.start_all()

    print("Residents started. Monitoring for 15 seconds...")
    try:
        for _ in range(15):
            time.sleep(1)
            issues = engine.watchdog.check_health()
            if issues:
                print(f"Watchdog issues: {issues}")
    except KeyboardInterrupt:
        pass

    print("Stopping residents...")
    engine.stop_all()

    # Check checkpoints
    print("Verifying checkpoints...")
    assert os.path.exists("data/checkpoints/Guardian.json"), "Guardian checkpoint missing"
    assert os.path.exists("data/checkpoints/Jules.json"), "Jules checkpoint missing"
    print("Soak Test Successful.")

if __name__ == "__main__":
    run_soak_test()
