# Interface Standards

This document standardizes the communication boundaries and integration contracts across the Solomon architecture to ensure high efficiency and rigorous governance.

## 1. Engine Registration (`solomon_api/engine_registry.json`)
All engines within `services/`, `backend/services/`, and `solomon_api/` must be registered.

**Required Metadata Schema:**
*   `engine_id`: (String) Unique identifier matching the module name.
*   `status_class`: (Enum) `'active_route'` (for HTTP endpoints), `'active_readiness'` (for background residents), `'approval_blocked'`, or `'retired_reason'`.
*   `owner_family`: (String) Architectural layer (e.g., `'joe_jules'`, `'gabriel'`).
*   `route_paths`: (Array) List of API endpoints handled (required if `active_route`).
*   `readiness_key`: (String) Health check marker (required if `active_readiness`).

## 2. API Facade Contract ("Pattern B")
*   **Rule:** HTTP endpoints defined in `backend/services/` must act solely as thin proxies.
*   **Implementation:** They may validate payloads and enforce HTTP codes but must delegate execution logic to `services/` engines or dispatch messages to `O(1)` queues. They must not contain raw execution code.

## 3. High-Efficiency Memory Operations (Zero-Copy)
To bypass serialization overhead for high-frequency internal state:
*   **Substrate:** Use Python's `mmap` module combined with `struct` for binary packing.
*   **String Encoding:** Strings must be fixed-width, byte-padded (e.g., `.ljust(64, b'\x00')`), and safely decoded (`.rstrip(b'\x00').decode('utf-8', errors='ignore')`).
*   **Hashing:** Cryptographic or deterministic integer hashes must be bitmasked (`& 0xffffffff`) to fit into unsigned integer (`'I'`) struct formats to prevent out-of-bounds exceptions.

## 4. Database Interactions (Mnemosyne / SQLite)
*   **Thread Safety:** The unified store (`solomon_soss.db`) must be accessed via singleton managers employing `threading.RLock()` to prevent write contention from concurrent Resident daemons.
*   **Mode:** Must operate in Write-Ahead Logging (WAL) mode (`PRAGMA journal_mode=WAL`).

## 5. Structured Data & Packets
*   **Efficiency:** Core packet objects (e.g., `WorkPacket`) must utilize `__slots__` to minimize memory footprint.
*   **Format:** Cross-boundary communications should use standardized JSON payloads or direct struct unpacking for speed.
