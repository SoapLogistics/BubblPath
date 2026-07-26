# Solomon Capability Registry

## Architecture Overview

The Solomon Capability Registry is the canonical capability registry designed to ensure that every subsystem, service, tool, worker, and future module is discoverable, versioned, governed, and safely integrated.

### Architectural Principles

1.  **Zero-Copy Execution:** The registry implements a memory-mapped (`mmap`) storage strategy over a binary file backing store (`capability_registry.bin`). This eliminates JSON parsing overhead entirely and guarantees strict O(1) reads and bound-latency writes.
2.  **O(1) Memory Index:** The system relies on a dictionary of offsets loaded into memory at initialization to provide lightning-fast, O(1) complexity record lookups by unique identifier (`uid`).
3.  **Strict Bounding:** It uses a static schema encoded into fixed-size structures (`struct`).
4.  **No Anonymous Execution:** Every capability must be strictly governed and registered here before activation or utilization.

## Record Standard Structure (1024 Bytes Aligned)

Each record conforms exactly to a `struct.calcsize` of `1024` bytes:

-   `1 byte (bool)` - Validation Flag
-   `32 bytes` - Unique Identifier
-   `64 bytes` - Human-readable Name
-   `128 bytes` - Module Path
-   `16 bytes` - Version
-   `32 bytes` - Owner
-   `128 bytes` - Description
-   `128 bytes` - Inputs
-   `128 bytes` - Outputs
-   `64 bytes` - Required Permissions
-   `128 bytes` - Dependencies (Comma-separated UID list)
-   `16 bytes` - Health State
-   `4 bytes` - SS Classification (e.g., SS1, SS2, SS3)
-   `8 bytes (double)` - Last Validation Timestamp
-   `147 bytes` - Structural Padding

## Registry Lifecycle

1.  **Discover:** New modules are indexed and proposed for registration.
2.  **Validate:** The system performs static checks on the module and dependency graph.
3.  **Register:** Writing zero-copy records directly into the active mapping.
4.  **Verify & Activate:** Capability becomes visible to the runtime layer.
5.  **Deprecate & Remove:** Capabilities are marked obsolete, halting execution pathways.

## Dependency Rules

-   Missing dependencies strictly block the activation and registration processes.
-   Dependency references in records are constrained to string representations of existing Unique Identifiers (`uid`).
-   Circular references must be prevented during validation sweeps.

## Integration & Operational Security

The `solomon_capability_registry` provides the foundational layer upon which the Solomon engine queries dependencies, validates health state constraints, and securely integrates newly assimilated code from systems like Gabriel. Anonymous code capabilities will inherently fail due to strict reliance on registry lookup tables in runtime evaluation.
