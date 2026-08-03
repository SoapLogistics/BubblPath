import json
import os
import datetime

def generate(inventory_data, base_dir):
    os.makedirs(base_dir, exist_ok=True)
    with open("daily_inventory/LATEST", "w") as f:
        f.write(f"{base_dir}/\n")

    for section_name, data in inventory_data.items():
        if isinstance(data, dict):
            with open(os.path.join(base_dir, f"{section_name}.json"), "w") as f:
                json.dump(data, f, indent=2)

    with open(os.path.join(base_dir, "18_FULL_DAILY_INVENTORY_REPORT.md"), "w") as f:
        f.write("# Solomon Daily Inventory Report\n\nGenerated automatically.")
