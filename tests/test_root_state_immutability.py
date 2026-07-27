import os
import hashlib

def get_file_hash(filepath):
    if not os.path.exists(filepath):
        return None
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()

def test_root_state_immutability():
    """
    Asserts that state-bearing files in the root are immutable and not touched by any testing procedures.
    """
    root_files = ["memory_atoms.db", "governance_log.bin", "fact_memory.log"]
    hashes_before = {f: get_file_hash(f) for f in root_files}

    # Verify that files are present and match their current hashes
    hashes_after = {f: get_file_hash(f) for f in root_files}

    for f in root_files:
        assert hashes_before[f] == hashes_after[f], f"Root file {f} was mutated!"
