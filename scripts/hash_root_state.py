import os
import json
import hashlib
import argparse

def get_file_hash(filepath):
    if not os.path.exists(filepath):
        return "MISSING"
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    root_files = ["memory_atoms.db", "governance_log.bin", "fact_memory.log"]
    hashes = {}
    for f in root_files:
        path = os.path.join(args.repository, f)
        hashes[f] = {
            "path": path,
            "exists": os.path.exists(path),
            "sha256": get_file_hash(path),
            "size": os.path.getsize(path) if os.path.exists(path) else 0
        }

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as out:
        json.dump(hashes, out, indent=2)
    print(f"Hashes written to {args.output}")

if __name__ == "__main__":
    main()
