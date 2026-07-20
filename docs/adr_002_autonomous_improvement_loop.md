# ADR 002: Implementing the 24/7 Autonomous Improvement Loop (AIL) Daemon

## Status
Approved

## Context
The primary mandate of Project Mnemosyne is to operate as a self-improving, domain-neutral Perpetual Learning Core (PLC). Rather than functioning as a passive system relying on manual operator requests, the learning core needs to dynamically acquire, validate, sandboxed-test, and assimilate new capabilities on a continuous 24/7 background repeat interval.

## Decision
1. **Background Daemon (AIL):** Implement the `AutonomousImprovementLoop` class in `solomon_knowledge_cards/autonomous_loop.py` to act as an un-orchestrated background daemon.
2. **Static Security Auditing:** Integrate a robust regex-based static code scanner inside the core execution flow to block dangerous keywords (`__import__('os').system`, shell-injection `subprocess.Popen` calls, `chmod 777`, timing-attack vulnerabilities) before any sandboxed compilation occurs.
3. **Sandboxed Dynamic Execution:** Safely compile and execute approved code snippets inside an isolated Python context.
4. **Auto-Learning Ingestion:** If the code successfully compiles and runs with 0 exceptions, automatically generate a Candidate `DRAFT` card in Project Mnemosyne via the `ingest_worker_report` pipeline.
5. **Systemd Integration:** Create a systemd unit (`solomon-loop.service`) to run this loop continuously as a background service on SS1.

## Consequences
- **Safety:** Malicious code is caught during the static audit phase and excluded, preventing local container escapes.
- **Autonomy:** Solomon transitions from a passive interface into an active learning machine.
- **Isolate & Reusability:** The AIL loop daemon is 100% domain-neutral and can search, audit, and distill knowledge for other AI configurations (e.g. manufacturing defect codes or medical papers) by configuring alternative candidate discovery inputs.
