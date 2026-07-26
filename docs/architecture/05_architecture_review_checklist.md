# Architecture Review Checklist

Every new subsystem, packet, or major modification must satisfy this checklist before being considered "Done" and merging into the canonical repository.

## 1. Single Responsibility & Canonical Integration
* [ ] **No Duplication:** Does this capability already exist in Prometheus, Mnemosyne, or Gabriel?
* [ ] **Pattern B Compliance:** If exposing an API, is the logic contained within `services/` and merely proxied by `backend/services/`?
* [ ] **Unified Store:** Does the system write durable state exclusively to `solomon_soss.db` via thread-safe (`RLock`) managers?

## 2. Registry & Metadata
* [ ] **Engine Registry:** Is the engine officially recorded in `solomon_api/engine_registry.json`?
* [ ] **Status Declaration:** Does the module contain a string variable declaring its status (e.g., `route_key`, `readiness_key`)?
* [ ] **Documentation:** Is the engine documented in `docs/solomon_engine_registry.md` with explicit owner metadata?

## 3. High Efficiency & Quantization
* [ ] **Memory Mapping:** Does high-frequency IPC leverage `mmap` zero-copy binary logs (`*.bin`)?
* [ ] **Struct Packing:** Are hashes masked (`& 0xffffffff`) and strings safely padded/stripped to prevent `struct.error` misalignment?
* [ ] **Object Footprint:** Do core memory objects utilize `__slots__`?

## 4. Governance & Safety
* [ ] **SS1 Muation Safety:** Are all high-risk actions explicitly routed through the Governance Approval Lane (`solomon_governance_approval_packet.py`) requiring SS3 review and explicit approval?
* [ ] **Quarantine Check:** If dynamic execution (AST injection, module loading) occurs, is it strictly isolated to the Gabriel SS2 Quarantine?
* [ ] **Path Sanitization:** Are dynamic filenames sanitized and constrained to valid workspace boundaries?

## 5. System Health
* [ ] **Testing:** Do all unit/integration tests pass with `PYTHONPATH=.` set?
* [ ] **Daemon Initialization:** Are background tasks (Swarm, Residents) lazily initialized and protected by threading locks to prevent duplicate execution in tests and multi-worker setups?
* [ ] **Time Handling:** Are all timestamps leveraging timezone-aware `datetime.now(datetime.UTC)` (replacing deprecated `utcnow`)?
