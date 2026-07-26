import os

def run_scan(seed=None, deterministic=False):
    if deterministic and seed is not None:
        print(f"Running deterministic scan with seed {seed}")
        return {"status": "success", "deterministic": True, "seed": seed}
    print("Running random scan")
    return {"status": "success", "deterministic": False}

if __name__ == "__main__":
    run_scan()
