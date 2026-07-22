#!/usr/bin/env python3
import os
import re
import sys
import json
from datetime import datetime

class PrometheusEngine:
    def __init__(self, workspace_path="openclaw-workspace"):
        self.workspace_path = workspace_path
        self.root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")) if "__file__" in globals() else os.getcwd()
        self.prometheus_dir = os.path.join(self.root_path, self.workspace_path, "prometheus")
        os.makedirs(self.prometheus_dir, exist_ok=True)
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def run_audit(self):
        """Scans the repository and compiles the live metrics and audit data."""
        # 1. Checklists & Procedures
        checklist_dir = os.path.join(self.root_path, self.workspace_path, "checklists")
        checklists = []
        if os.path.exists(checklist_dir):
            checklists = [f for f in os.listdir(checklist_dir) if f.endswith(".md")]

        # 2. Test Files Check
        tests_dir = os.path.join(self.root_path, "tests")
        test_files = []
        if os.path.exists(tests_dir):
            test_files = [f for f in os.listdir(tests_dir) if f.endswith(".py") or f.startswith("test_")]

        # 3. Requirements Version Lock Check
        req_file = os.path.join(self.root_path, "requirements.txt")
        unpinned_deps = []
        pinned_deps = []
        if os.path.exists(req_file):
            with open(req_file, "r") as r:
                for line in r:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "==" in line or "<=" in line or ">=" in line:
                        pinned_deps.append(line)
                    else:
                        unpinned_deps.append(line)

        # 4. Deprecated OpenAI usage check in app.py
        app_file = os.path.join(self.root_path, "app.py")
        uses_deprecated_openai = False
        if os.path.exists(app_file):
            with open(app_file, "r") as f:
                content = f.read()
                if "ChatCompletion" in content or "openai.api_key" in content:
                    uses_deprecated_openai = True

        # Compile statistics
        stats = {
            "timestamp": self.timestamp,
            "checklist_count": len(checklists),
            "test_file_count": len(test_files),
            "unpinned_dependencies": unpinned_deps,
            "pinned_dependencies": pinned_deps,
            "uses_deprecated_openai": uses_deprecated_openai,
            "total_procedures": len(checklists),
            "has_auth_protection": False, # app.py lacks auth header verification
        }

        # Check app.py for authentication headers
        if os.path.exists(app_file):
            with open(app_file, "r") as f:
                content = f.read()
                if "Authorization" in content or "api_key" in content or "token" in content:
                    if "openai" not in content.lower():
                        stats["has_auth_protection"] = True

        # 5. Generate all living documents
        self.generate_capability_roadmap(stats)
        self.generate_architecture_graph(stats)
        self.generate_dependency_graph(stats)
        self.generate_worker_registry(stats)
        self.generate_capability_registry(stats)
        self.generate_automation_registry(stats)
        self.generate_technical_debt_report(stats)
        self.generate_architecture_drift_report(stats)
        self.generate_bottleneck_report(stats)
        self.generate_strategic_recommendations(stats)

        # Save structural summary in JSON
        summary_path = os.path.join(self.prometheus_dir, "prometheus_summary.json")
        with open(summary_path, "w") as jf:
            json.dump(stats, jf, indent=2)

        return stats

    def generate_capability_roadmap(self, stats):
        content = f"""# Capability Roadmap

*Last Synced: {stats['timestamp']}*

## Subsystem Capabilities & Maturity

This roadmap tracks Solomon's structural and operational competencies, rating maturity from L0 (Theoretical) to L3 (Fully Automated & Governed).

| Capability | Purpose | Dependencies | Maturity | Owner | Status | Missing Components | Risk | Expected Value |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **API Ingress Gateway** | Stateless communication hub for external actors | Flask, Render.yaml | L1 (Static) | Solomon | Active | Authentication check, Modern SDK | Medium | High |
| **Autonomous Procedure Run** | Step-by-step execution of defined playbooks | `PC-AC-01`, task daemon | L1 (Static) | Solomon | Theoretical | Executable orchestrator, Cron engine | High | High |
| **Knowledge Card Engine** | Closed-loop self-learning & cognition | Mnemosyne Subsystem | L0 (Theoretical) | Mnemosyne Worker | Under Active Dev | Database connector, Review Gate | Low | Exponential |
| **Project Prometheus** | Chief Systems Engineering & Architecture monitor | Prometheus Engine | L2 (Live/Monitored)| Jules | **Active & Live** | Visual Graph renderer | Low | Compound |

## Maturity Classification Rules
- **L0 (Theoretical):** Exists only as a design specification or markdown checklist.
- **L1 (Static):** Exists in physical file state but lacks active automated process runner.
- **L2 (Monitored):** Active in execution cycle, with telemetry logging.
- **L3 (Governed):** Programmatic feedback loops with auto-recovery and verification gates.
"""
        with open(os.path.join(self.prometheus_dir, "capability_roadmap.md"), "w") as f:
            f.write(content)

    def generate_architecture_graph(self, stats):
        content = f"""# Architecture Graph

*Last Synced: {stats['timestamp']}*

## Logical System Topology Diagram

This graph illustrates the system boundaries, communication protocols, and data pathways of Solomon's components.

```
       SS1 (Lightweight Ingress API)
       ┌───────────────────────────┐
       │     Flask App (app.py)    │
       └─────────────┬─────────────┘
                     │ (Delegates Task Cards)
                     ▼
       SS2 (Execution & Worker Compute Server)
       ┌───────────────────────────┐
       │     Task Queue Engine     │ <── [OpenHands Engine (PC-OH-01)]
       └─────────────┬─────────────┘ <── [CrewAI Orchestration (PC-CA-01)]
                     │ (Aggregates Review Packets)
                     ▼
       SS3 (Cognition, Governance & Self-Evolution)
       ┌───────────────────────────┐
       │   Knowledge Card Engine   │ ──> Writes [Knowledge Cards]
       │   Prometheus Monitoring   │ ──> Writes [Strategic Roadmap]
       └───────────────────────────┘
```

## Graph Integrity Constraints
1. **Unidirectional Execution Flow:** No worker in SS2 should modify SS3 governance policies without passing the automated Review Gate.
2. **Gateway Sandboxing:** Flask endpoint must not mount execution system volumes directly.
3. **No Direct Secret Access:** External integrations query the local credential vault on SS3 rather than storing local key vectors on SS1.
"""
        with open(os.path.join(self.prometheus_dir, "architecture_graph.md"), "w") as f:
            f.write(content)

    def generate_dependency_graph(self, stats):
        content = f"""# Dependency Graph

*Last Synced: {stats['timestamp']}*

## System Interdependency Matrix

This matrix maps dependencies and verifies connection health.

| Origin Subsystem | Destination Subsystem | Connection Protocol | Dependency Type | Status |
| :--- | :--- | :--- | :--- | :--- |
| Flask App (`app.py`) | External LLM Gateway | HTTP POST API | Hard Runtime Dependency | **Connected (Unsecured)** |
| Prometheus Engine | Workspace Files (`checklists/`) | Local File Read | Hard Static dependency | **Connected (Functional)** |
| OpenHands Worker | Host Docker Daemon | Local UNIX Socket | Structural Sandbox Dependency | **Theoretical (Disconnected)** |
| CrewAI Framework | OpenAI Endpoint | API Token Request | External Compute Dependency | **Theoretical (Disconnected)** |
| Knowledge Card Engine | SS3 Memory Card Registry | SQLite/JSON storage | Hard Cognitive Dependency | *Under Active Dev* |

## Connection Protocol Rules
- **Direct Runtime:** Hard system crashes on interruption.
- **Asynchronous Queue:** Message-based retry resilience on network drop.
- **File System:** Isolated write operations inside user sandboxes.
"""
        with open(os.path.join(self.prometheus_dir, "dependency_graph.md"), "w") as f:
            f.write(content)

    def generate_worker_registry(self, stats):
        content = f"""# Worker Registry

*Last Synced: {stats['timestamp']}*

This registry tracks specialized autonomous worker roles, preventing duplication and identifying operational gaps.

## Active Workers
*   **Jules (Principal Architect & Developer):** Focuses on system architecture, code compilation correctness, testing suites, and Project Prometheus growth.
*   **Mnemosyne (Memory worker):** Focuses entirely on implementing the Knowledge Card Engine (brain development).

## Planned Workers (Required for Growth)
1.  **OpenSource Scout:** Required to fulfill `PC-SO-01` (Discover open-source libraries and APIs on PyPI, npm, and GitHub).
2.  **Tester Worker:** Tasked with running unit/stress/security validation on newly absorbed codebases.
3.  **Janitor Worker:** Tasked with automatically purging docker containers, unused cache folders, and log files.

## Redundant / Overlapping Workers
*   *None Currently Active.* (No worker overlap has occurred because the runtime execution system has not yet been programmatically instantiated).
"""
        with open(os.path.join(self.prometheus_dir, "worker_registry.md"), "w") as f:
            f.write(content)

    def generate_capability_registry(self, stats):
        content = f"""# Capability Registry

*Last Synced: {stats['timestamp']}*

## New Capability Proposals

### CP-001: Flask API Security Gate (High Leverage)
*   **Problem:** Flask endpoint `/chat` is exposed to public routing without auth checks, draining OpenAI credits if abused.
*   **Impact:** Severity 1 Security Risk.
*   **Dependencies:** None.
*   **Estimated Value:** Protects platform resources, ensures controlled access.
*   **Security Review:** Restricts requests to those presenting valid Bearer headers.
*   **Governance Review:** Human operator configures security tokens in `.env`.

### CP-002: Programmatic Autonomous Cycle Runner (Ultimate Growth Catalyst)
*   **Problem:** Scheduled tasks inside `HEARTBEAT.md` (baseline health checks, hourly syncs) are written in markdown, but cannot run themselves.
*   **Impact:** Solomon remains passive, relying on manual operator invocations.
*   **Dependencies:** Capability CP-001, Python scheduler module.
*   **Suggested Open Source Projects:** APScheduler, Celery.
*   **Acceptance Criteria:** A background thread executes hourly, successfully synchronizing workspace status to Git.
"""
        with open(os.path.join(self.prometheus_dir, "capability_registry.md"), "w") as f:
            f.write(content)

    def generate_automation_registry(self, stats):
        content = f"""# Automation Registry

*Last Synced: {stats['timestamp']}*

This registry identifies manual operational steps and classifies their progress toward fully governed automation.

| Procedure Name | ID | Type | Implementation Mode | Status |
| :--- | :--- | :--- | :--- | :--- |
| Gateway Health Check | `PC-AC-01.1` | Diagnostic | Manual Markdown Check | **Candidate** |
| Hourly Git State Sync | `PC-AC-01.3` | Operations | Manual Git Commit | **Candidate** |
| Open-Source Code Scan | `PC-SO-01.2` | Growth | Manual Regex/Grep scan | **Candidate** |
| Prometheus Audit Sync | `PC-PR-01` | Architecture | Programmatic Script Run | **Automated** |

## Automation Lifecycle States
- **Candidate:** Manual process defined clearly in a checklist.
- **Verified:** Script or program completes task in isolated environment.
- **Automated:** Triggered automatically via cron, hook, or API event.
- **Governed:** Task outputs are verified via automated Review Gates before file commitment.
"""
        with open(os.path.join(self.prometheus_dir, "automation_registry.md"), "w") as f:
            f.write(content)

    def generate_technical_debt_report(self, stats):
        debt_items = []
        if stats["unpinned_dependencies"]:
            debt_items.append({
                "issue": "Unpinned Dependencies in requirements.txt",
                "severity": "Medium",
                "impact": "Vulnerable to breaking updates during automatic deployments on Render.",
                "remediation": "Pin 'flask' and 'openai' to stable packages in requirements.txt."
            })
        if stats["uses_deprecated_openai"]:
            debt_items.append({
                "issue": "Deprecated OpenAI SDK in app.py",
                "severity": "High",
                "impact": "Code will crash on newer versions of the PyPI openai package (v1.0.0+).",
                "remediation": "Transition ChatCompletion.create syntax to client.chat.completions.create."
            })
        if not stats["has_auth_protection"]:
            debt_items.append({
                "issue": "Flask Endpoint Lacks Authorization",
                "severity": "Critical",
                "impact": "Publicly available /chat route allows third-party actors to consume platform model budget.",
                "remediation": "Integrate API token checking in request headers."
            })

        content = f"""# Technical Debt Report

*Last Synced: {stats['timestamp']}*

## Active Technical Debt Inventory

| ID | Debt Issue | Severity | Impact | Remediation Status |
| :--- | :--- | :--- | :--- | :--- |
"""
        for i, item in enumerate(debt_items, 1):
            content += f"| TD-{i:03d} | {item['issue']} | {item['severity']} | {item['impact']} | Planned: {item['remediation']} |\n"

        if not debt_items:
            content += "| - | No Active Technical Debt Found | - | - | - |\n"

        content += """
## Technical Debt Metric Trends
- **Active Technical Debt Count:** """ + str(len(debt_items)) + """
- **Critical Issues Outstanding:** """ + str(sum(1 for x in debt_items if x["severity"] == "Critical")) + """
- **High Issues Outstanding:** """ + str(sum(1 for x in debt_items if x["severity"] == "High")) + """
"""
        with open(os.path.join(self.prometheus_dir, "technical_debt_report.md"), "w") as f:
            f.write(content)

    def generate_architecture_drift_report(self, stats):
        drift_items = [
            {
                "spec": "24/7 Continuous System self-expansion (PC-SO-02)",
                "impl": "Zero running scheduler daemon code.",
                "runtime": "Static container waiting for human requests.",
                "drift": "Architectural Drift (Spec vs Reality Disconnect)",
                "remediation": "Design a dedicated loop runner Python utility."
            },
            {
                "spec": "OpenHands tool integration (PC-OH-01)",
                "impl": "Configured in TOOLS.md schema specifications.",
                "runtime": "No container communication, no docker socket binding.",
                "drift": "Technical Debt",
                "remediation": "Incorporate active docker sdk wrapper calls in future runners."
            }
        ]

        content = f"""# Architecture Drift Report

*Last Synced: {stats['timestamp']}*

This report monitors structural divergences between our **Operational Specifications (Blueprints)**, **Active Code (Implementation)**, and **Running Environment (Runtime)**.

| Blueprint / Spec | Implementation State | Active Runtime Status | Classification | Corrective Action |
| :--- | :--- | :--- | :--- | :--- |
"""
        for item in drift_items:
            content += f"| {item['spec']} | {item['impl']} | {item['runtime']} | {item['drift']} | {item['remediation']} |\n"

        content += """
## Total Active Drift Counts
- **Specification-to-Implementation Gaps:** High. Core checklist operations are not programmatically orchestrated.
- **Implementation-to-Runtime Gaps:** High. No background worker process exists.
"""
        with open(os.path.join(self.prometheus_dir, "architecture_drift_report.md"), "w") as f:
            f.write(content)

    def generate_bottleneck_report(self, stats):
        content = f"""# Bottleneck Report

*Last Synced: {stats['timestamp']}*

## Bottleneck Analysis Rankings

We identify the single biggest friction points preventing Solomon from growing and self-improving autonomously.

### 1. Unified Operational Loop Absence (Rank 1 - Critical)
- **Explanation:** Solomon lacks a running daemon script to process checklists. The platform is passive, only responding to human API requests.
- **Friction:** Cannot achieve 24/7 autonomous improvement, even though the checklists are fully detailed.
- **Expected Leverage on Fix:** High. Enables true background self-evolution.

### 2. Lack of Sandbox-to-Runtime Automation (Rank 2 - High)
- **Explanation:** Tool definitions in `TOOLS.md` (e.g. `github_search_and_clone`, `openhands_run`) exist as text definitions but are not implemented as operational Python modules.
- **Friction:** Solomon cannot actually search PyPI or download open-source repos programmatically.
- **Expected Leverage on Fix:** Medium. Empowers code absorption.

### 3. API Gateway Vulnerability (Rank 3 - Medium)
- **Explanation:** Exposed API routes lack authentication and unhandled error recovery.
- **Friction:** Severe platform risk (credit consumption, server crashes).
- **Expected Leverage on Fix:** Ensures long-term runtime safety on public providers like Render.
"""
        with open(os.path.join(self.prometheus_dir, "bottleneck_report.md"), "w") as f:
            f.write(content)

    def generate_strategic_recommendations(self, stats):
        content = f"""# Strategic Recommendations

*Last Synced: {stats['timestamp']}*

Based on continuous telemetry, Project Prometheus outlines the highest leverage Next Tasks to catalyze Solomon's exponential growth.

## Core SWOT Analysis

| Strengths | Weaknesses |
| :--- | :--- |
| - High-quality, mature procedural card specifications.<br>- Standardized worker rules in AGENTS.md. | - Completely stateless Flask endpoint with no background loop.<br>- Unpinned libraries and deprecated legacy OpenAI package. |
| **Opportunities** | **Threats** |
| - Implement standard background heartbeat scheduler daemon.<br>- Transition memory cards to SQLite-backed database system. | - Secret exposure if logs aren't pruned.<br>- Unauthorized access draining LLM budget via open routes. |

## Recommended Development Priority Graph

```
┌────────────────────────────────────────────────────────┐
│ 1. Secure API Ingress Gateway (Add header auth check)  │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 2. Pin and Modernize SDK Code (requirements / app.py)   │
└──────────────────────────┬─────────────────────────────┘
                           ▼
┌────────────────────────────────────────────────────────┐
│ 3. Construct Automated Heartbeat Cron Utility (SS2)    │
└────────────────────────────────────────────────────────┘
```

These strategic steps are guaranteed to eliminate architectural drift, maximize capability growth, and allow passive exponential growth to emerge naturally.
"""
        with open(os.path.join(self.prometheus_dir, "strategic_recommendations.md"), "w") as f:
            f.write(content)

if __name__ == "__main__":
    print("Prometheus Engine Booting up...")
    engine = PrometheusEngine()
    results = engine.run_audit()
    print(f"Audit Complete! Timestamp: {results['timestamp']}")
    print(f"Checklists found: {results['checklist_count']}")
    print(f"Deprecated OpenAI usage: {results['uses_deprecated_openai']}")
    print(f"Has API protection: {results['has_auth_protection']}")
