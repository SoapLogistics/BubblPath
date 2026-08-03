#!/usr/bin/env python3
import datetime
import os
from inventory.collectors import host, docker, tests, git_repo, databases, services, capabilities
from inventory import report, compare

def main():
    today = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    base_dir = f"daily_inventory/{today}"

    inventory_data = {}
    all_evidence = []

    print("Collecting Host data...")
    h_data, h_ev = host.collect(["localhost", "ss1", "ss2", "ss3"])
    inventory_data["01_HOST_INVENTORY"] = {"data": h_data}
    all_evidence.extend(h_ev)

    print("Collecting Repositories...")
    r_data, r_ledger, r_ev = git_repo.collect()
    inventory_data["02_REPOSITORY_INVENTORY"] = {"data": r_data}
    inventory_data["03_24_HOUR_WORK_LEDGER"] = {"data": r_ledger}
    all_evidence.extend(r_ev)

    print("Collecting Docker data...")
    d_data, d_ev = docker.collect()
    inventory_data["RUNTIME_SERVICES_DOCKER"] = {"data": d_data}
    all_evidence.extend(d_ev)

    print("Collecting Services...")
    s_data, s_ev = services.collect()
    inventory_data["05_RUNTIME_SERVICES"] = {"data": s_data}
    all_evidence.extend(s_ev)

    print("Collecting Capabilities...")
    c_data, c_ev = capabilities.collect()
    inventory_data["06_CAPABILITY_REGISTRY"] = {"data": c_data}
    all_evidence.extend(c_ev)

    print("Collecting Databases...")
    db_data, db_ev = databases.collect()
    inventory_data["07_DATABASE_INVENTORY"] = {"data": db_data}
    all_evidence.extend(db_ev)

    print("Collecting Test data...")
    t_data, t_ev = tests.collect()
    inventory_data["09_TEST_AND_VALIDATION_REPORT"] = {"data": t_data}
    all_evidence.extend(t_ev)

    # Run Comparison
    comp_data = compare.run_compare(inventory_data)
    inventory_data["COMPARISON_REPORT"] = comp_data

    # Save unified evidence log
    inventory_data["EVIDENCE_LOG"] = {"evidence": all_evidence}

    print("Generating Reports...")
    report.generate(inventory_data, base_dir)
    print(f"Inventory saved to {base_dir}")

if __name__ == "__main__":
    main()
