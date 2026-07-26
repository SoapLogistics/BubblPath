# Project Solomon

# Phase 1 --- Architectural Convergence

## Engineering Specification MD4

### Event Bus & Runtime Architecture

> Status: Draft 1.0 Primary Implementer: Jules Review: Joe

# Mission

Create the canonical runtime nervous system for Solomon. Every subsystem communicates through a governed event architecture rather than direct coupling. This implementation utilizes a memory-mapped Zero-Copy Circular Event Buffer for extreme algorithmic efficiency, minimizing garbage collection overhead and supporting perpetual learning loops.

# Objectives

- Standardize internal event messaging using `mmap` backing.
- Separate producers from consumers using strict O(1) pub/sub queues.
- Support asynchronous execution with background polling.
- Eliminate hidden dependencies with strict topic routing.
- Provide deterministic runtime behavior via lock-free state progression.

# Runtime Responsibilities

The Runtime owns:
- Worker lifecycle (Init, Run, Halt)
- Job scheduling (Immediate, Delayed, Priority, DAG)
- Background queues (Circular buffers)
- Event dispatch (Zero-copy payload parsing)
- Retry policies (Exponential backoff bounded by `mmap` limits)
- Task prioritization (Strict priority integers)
- Resource allocation (Memory-mapped slots)

The Runtime never owns:
- Long-term memory
- Planning logic
- Capability engineering
- Governance decisions

# Canonical Event Bus

All subsystem communication uses fixed-size memory-mapped typed events.

Core event categories (uint8 mapped):
- System Events (0x01)
- Memory Events (0x02)
- Planning Events (0x03)
- Learning Events (0x04)
- Capability Events (0x05)
- Governance Events (0x06)
- Runtime Events (0x07)
- Browser Events (0x08)

# Worker Model

Workers are stateless, restartable, observable, and idempotent.

Supported worker classes:
- Retrieval Worker
- Planning Worker
- Learning Worker
- Engineering Worker
- Browser Worker
- Review Worker

# Scheduling Requirements

Supports:
- Immediate jobs (Priority 0)
- Delayed jobs (Timestamp trigger)
- Recurring jobs (Interval trigger)
- Priority queues (Lower number = higher priority)
- Dependency-aware execution (DAG wait queues)

# Failure Handling

Every failed event includes:
- Failure reason (uint16 error code mapping)
- Retry count (uint8)
- Stack trace (hash pointer to localized string map)
- Correlation ID (UUID)
- Recovery recommendation (uint8 enum)

Escalation rules:
1. Retry
2. Queue
3. Human review
4. Rollback if required

# Observability

Every event MUST log (in O(1) buffer):
- Timestamp (uint64)
- Source (hash)
- Destination (hash)
- Duration (uint32)
- Status (uint8)
- Correlation ID (16 bytes UUID)
