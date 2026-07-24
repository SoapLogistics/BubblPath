# Solomon Perpetual Learning Machine — Master Audit

**Audit date:** July 21, 2026
**Scope:** Nine Jules session archives supplied by Mark Miller
**Goal:** Determine where Solomon has been, where the system is now, and the build path to a perpetual machine whose primary job is to learn, accumulate skills, improve its learning process, and reuse what it learns.

---

## Executive verdict

The work is real, useful, and substantially farther along than a collection of design documents. Across seven executable archives, **88 automated tests pass** after installing the undeclared Python dependencies. The work contains four major assets:

1. **Mnemosyne:** a governed long-term memory/card system with ingestion, review states, retrieval, semantic ranking, graph relationships, proposals, reflection, and planning safeguards.
2. **Prometheus:** an early planning, auditing, and bottleneck-selection layer that can retrieve prior failures and repairs before drafting a plan.
3. **Gabriel:** an experimental capability-acquisition and optimization engine with acquisition records, structural analysis, permission lanes, clean-room build concepts, a crucible, dynamic loading, and prototype Codex/Jules-like tools.
4. **Deployment/bridge work:** proxy routes, authentication, SS1 runbooks, rollback procedures, systemd templates, and SolomonGPT reconnection documentation.

However, these assets are **not yet one operating perpetual-learning machine**. They are multiple branches and prototypes with overlapping Flask applications, independent stores, inconsistent schemas, undeclared dependencies, and no verified production deployment on SS1. The strongest path is not to choose Gabriel instead of Mnemosyne. It is to make **Mnemosyne the governed cognitive substrate**, **Prometheus the planner**, and **Gabriel a quarantined skill laboratory** whose outputs must pass evidence, security, and review gates before becoming usable skills.

**Current maturity:** approximately **Level 3 of 7 — governed learning prototype**.

Solomon can already represent learning. It can ingest outcomes, draft memory cards, retrieve prior knowledge, rank it, and alter plans in tests. It cannot yet reliably operate a continuous real-world loop that discovers learning opportunities, performs work on SS1/SS2/SS3, measures results, promotes verified skills, detects decay, and improves its own learning policy over weeks and months.

---

## Archive-by-archive reconstruction

### 1. `jules_session_7430717246158003424-2`

**Role:** Cognitive workspace seed.

This archive establishes Solomon's identity/workspace files and the first written knowledge-card architecture. It is primarily doctrine and configuration rather than runtime code.

**What it contributed:**
- Identity, soul, tools, user, heartbeat, and memory workspace documents.
- A conceptual knowledge-card architecture.

**Disposition:** Preserve the doctrine files as adapter configuration. Do not treat this as the canonical engine.

---

### 2. `jules_session_12808825663192238877-2`

**Role:** Prometheus audit seed.

This adds a small `PrometheusEngine` and architectural/inventory reports.

**Verification:** 1 test passed.

**Disposition:** Preserve the audit concepts, but merge the code only after comparing it with the later Prometheus copy in Phase 3C.

---

### 3. `jules_session_316198405264291563-3`

**Role:** First complete Memory Card engine.

This is the earliest executable perpetual-learning substrate. It defines card types and states, SQLite persistence, repository operations, review behavior, metrics, import/export, worker-report ingestion, and Flask endpoints.

**Verification:** 17 tests passed.

**Strengths:**
- Coherent first vertical slice.
- Explicit card lifecycle and validation.
- Good foundation for later Mnemosyne work.

**Weaknesses:**
- Older package structure.
- Direct coupling to the Flask application and OpenAI import.
- Superseded by later repository/review/extractor architecture.

**Disposition:** Historical baseline. Preserve tests as regression specifications, but do not use this package layout as the production baseline.

---

### 4. `jules_session_6544409802158304258-2`

**Role:** Mnemosyne Phase 3A integration.

This reorganizes the memory system into models, storage, repository, review, extraction, and migration modules. It adds runtime integration, a basic interface, architecture/threat-model documents, and Prometheus.

**Verification:** 11 tests passed.

**Strengths:**
- Cleaner separation of responsibilities.
- Worker reports become draft knowledge.
- Search ranking, clearance filtering, relationships, and review gates.
- Better integration documentation.

**Weaknesses:**
- Included generated `.pyc`, `.db`, and log files.
- Still not a reproducibly packaged service.
- Later archives supersede much of it.

**Disposition:** Intermediate branch. Use it to understand evolution, not as the canonical source tree.

---

### 5. `jules_session_15407387804973028003-3`

**Role:** Enhanced Phase 3A with autonomous daemon and reflection.

This adds a reflection engine, autonomous daemon, metrics route, vector/graph-oriented test expectations, research blueprint, and stronger persistence/recovery tests.

**Verification:** 12 tests passed.

**Strengths:**
- Demonstrates a complete ingest → retrieve → apply → reflect cycle in tests.
- Adds backup/recovery and concurrent-write coverage.
- Moves toward autonomous optimization.

**Weaknesses:**
- The daemon is still an isolated process prototype.
- Claims of perpetual learning exceed what is exercised in a real worker environment.

**Disposition:** Preserve reflection and daemon concepts, but supersede the runtime with the Phase 3B/3C branch.

---

### 6. `jules_session_2053092947882016941-3`

**Role:** Strongest Mnemosyne/Prometheus branch; canonical cognitive baseline.

This contains Phase 3B and Phase 3C work: semantic embedding, hybrid retrieval, graph traversal, safe mutation proposals, reflection/reinforcement signals, a dynamic planner, tool arbitration, API authentication, proxy integration, hardening tests, and Prometheus auditing.

**Verification:** 20 tests passed.

**Strengths:**
- Best structured and most complete cognitive branch.
- Security-focused tests for path traversal, payload limits, recursion bounds, division-by-zero, and error sanitization.
- Retrieval affects planning.
- Separates proposed procedural changes from automatic mutation.
- Provides the best starting point for the canonical repository.

**Weaknesses:**
- Embeddings appear local/simplified rather than production vector infrastructure.
- “Reinforcement learning” is feedback scoring, not trained policy optimization.
- Execution remains mostly an API/planning abstraction.
- No unified task/event ledger shared with Gabriel.
- No deployment proof from the actual SS1 runtime.

**Disposition:** **Use as the canonical cognitive core baseline.**

---

### 7. `jules_session_11744016475190968919-2`

**Role:** Deployment, reconnection, and domain-neutral PLC branch.

This archive contains the best deployment and SolomonGPT bridge materials, a compact alternate Mnemosyne runtime, an autonomous improvement loop, proxy routes, auth, SS1 verification scripts, rollback guidance, and the key domain-neutral Perpetual Learning Core blueprint.

**Verification:** 13 tests passed.

**Strengths:**
- Best practical deployment/runbook content.
- Clear core-versus-adapter separation.
- Stronger API authentication and explicit clearance hierarchy.
- Useful autonomous-loop security scanning and sandbox concepts.

**Weaknesses:**
- It is an alternate implementation rather than a clean continuation of the Phase 3C package.
- Combining it blindly would create duplicate models, schemas, and runtimes.

**Disposition:** Merge its deployment, auth, schema-validation, autonomous-loop safety, and domain-neutral design into the Phase 3C baseline. Do not replace Phase 3C wholesale.

---

### 8. `jules_session_2036715862452076436`

**Role:** Gabriel capability assimilation laboratory.

This is the broadest conceptual leap. It contains acquisition, permission gates, structural comprehension, behavioral experimentation, capability extraction, assimilation decisions, clean-room construction, crucible validation, dynamic loading, AST injection, recursive optimization, observational simulation, and prototype Codex/Jules capabilities.

**Verification:** 14 tests passed.

**Strengths:**
- Correctly identifies that learning must include reusable executable skills, not only text memory.
- Models the stages of acquiring, understanding, rebuilding, testing, and registering a capability.
- Contains useful primitives: retry, throttling, worktree management, task leases, MCP abstraction, patching, testing loops, and issue-to-PR workflow concepts.

**Critical limitations:**
- Much of the analysis and experimentation is simulated with defaults and synthetic metrics.
- State is stored in process memory and generated files rather than the governed Mnemosyne store.
- Dynamic code loading and AST injection are high-risk and not bounded by the mature review gate.
- Some exception handlers silently swallow failures.
- The global error handler leaks tracebacks.
- The chat route claims agent powers it does not actually possess.
- It references an obsolete OpenAI chat pattern/model.
- “Assimilated” capabilities are largely handcrafted prototypes, not demonstrated extraction from arbitrary external software.

**Disposition:** **Keep Gabriel quarantined as SS2 laboratory code. Never deploy its dynamic execution endpoints directly on SS1.** Convert its models and stages into governed skill-card workflows and require crucible evidence plus SS3 approval before promotion.

---

### 9. `jules_session_13174528251852195661`

**Role:** Loki communications/UI and Hugin analysis blueprint.

This archive is mainly documentation and an HTML workspace. It also contains a sports/betting-oriented Loki/Hugin blueprint that is not part of the domain-neutral learning core.

**Verification:** No executable test suite.

**Disposition:**
- Preserve the communications/workspace UI ideas as an optional adapter.
- Keep betting-domain logic completely outside the core.
- Hugin's static-analysis concepts may later become a security/evaluation adapter.

---

## Test audit

After installing the missing external dependencies (`flask`, `openai`, `pydantic`, and `pytest`), the available suites produced:

| Archive | Passed |
|---|---:|
| 117440... | 13 |
| 128088... | 1 |
| 154073... | 12 |
| 203671... | 14 |
| 205309... | 20 |
| 316198... | 17 |
| 654440... | 11 |
| **Total** | **88** |

These passing tests prove that the contained prototypes are internally coherent. They do **not** prove:
- SS1 deployment is active.
- The proxy, gateway, workers, and database share one live state.
- Solomon performs useful autonomous work over long durations.
- Learned skills improve real task success.
- Dynamic capability code is safe to promote.
- Recovery works after real power loss, disk pressure, OOM, or network failure.

Numerous tests emit `datetime.utcnow()` deprecation warnings. This is minor but should be fixed while creating the canonical branch.

---

## Where Solomon has been

The project has followed the correct general progression:

1. **Identity and doctrine** — define who Solomon is and how agents should behave.
2. **Memory representation** — turn experience into structured cards.
3. **Governance** — require review, provenance, status transitions, and clearance.
4. **Retrieval** — bring relevant cards into a task.
5. **Reflection** — inspect outcomes and propose improvements.
6. **Planning** — alter future plans using retrieved failures and repairs.
7. **Capability acquisition** — represent executable skills and test them.
8. **Deployment/communication** — reconnect SolomonGPT through an authenticated proxy.

This is a sound history. Jules did not simply reinvent the same wheel. It repeatedly rebuilt portions because each session was isolated and lacked a canonical integration branch. The next phase must stop creating parallel architectures and begin controlled consolidation.

---

## Where Solomon is now

### What exists now

Solomon has tested prototypes for:
- Structured episodic, factual, procedural, repair, warning, skill, and research memory.
- Provenance, confidence, lifecycle states, security clearances, and review gates.
- SQLite persistence, backups, recovery, concurrency checks, and search.
- Hybrid retrieval and graph relationships.
- Worker-report extraction and proposal generation.
- Reflection and task-plan safeguards.
- Tool arbitration based on prior knowledge.
- Capability acquisition and clean-room reconstruction concepts.
- Crucible-style testing and optimization concepts.
- Proxy authentication and deployment procedures.

### What does not exist yet

There is no verified, unified system that continuously performs:

```text
observe real work
→ identify a learning opportunity
→ choose the highest-value experiment
→ safely execute it
→ capture complete evidence
→ extract a reusable lesson or skill
→ validate against held-out tasks
→ review and promote it
→ route future work through it
→ measure whether it remains useful
→ revise or retire it
→ improve the learning process itself
```

That loop—not another document—is the perpetual-learning machine.

---

## The correct target architecture

### Naming and responsibility

- **Solomon:** the user-facing intelligence, mission holder, and orchestrator.
- **Mnemosyne:** durable governed memory and evidence ledger.
- **Prometheus:** task planning, curiosity, experiment selection, and tool arbitration.
- **Gabriel:** skill acquisition, reconstruction, testing, optimization, and packaging laboratory.
- **Crucible:** isolated evaluation environment.
- **Hugin:** optional static/security analysis evaluator.
- **Adapters:** software engineering, manufacturing, tutoring, household devices, and future domains.

### The unified loop

```text
1. OBSERVE
   Chats, tasks, worker events, test results, telemetry, documents, failures

2. NORMALIZE
   Convert every event into a common Experience Record with provenance

3. DIAGNOSE
   Detect novelty, repeated failure, low confidence, missing skill, or inefficiency

4. PRIORITIZE
   Estimate expected learning value / cost / risk / urgency

5. PLAN
   Retrieve relevant memories and produce a bounded experiment plan

6. EXECUTE IN LAB
   Run on SS2 with least privilege, checkpoints, quotas, and rollback

7. EVALUATE
   Run Crucible tests, adversarial tests, held-out tasks, and resource measurements

8. DISTILL
   Produce knowledge cards, repair cards, skill manifests, and evidence bundles

9. REVIEW
   SS3 verifies claims, reproducibility, security, licensing, and regression risk

10. PROMOTE
    Publish an immutable, versioned skill package to SS1

11. ROUTE AND USE
    Prometheus selects the learned skill when its applicability contract matches

12. MONITOR
    Measure success, latency, cost, confidence calibration, and regressions

13. REVISE OR RETIRE
    Update, merge, demote, quarantine, or deprecate stale knowledge and skills

14. META-LEARN
    Compare learning strategies and improve how Solomon selects experiments,
    extracts lessons, evaluates skills, and allocates compute.
```

---

## The most important design change: learning assets, not vague “assimilation”

A learned executable skill must be a versioned artifact with an explicit contract—not arbitrary Python loaded into the main process.

### Required Skill Package

Each promoted skill should contain:

- `skill.yaml` — identity, version, purpose, inputs, outputs, preconditions, permissions.
- `implementation/` — code or deterministic workflow.
- `tests/` — unit, integration, adversarial, and regression tests.
- `evidence.json` — source experiences, benchmark results, confidence, limitations.
- `sandbox_policy.yaml` — filesystem, network, process, time, memory, and tool boundaries.
- `rollback.yaml` — previous version and automatic rollback triggers.
- `license.json` — source/license analysis and clean-room record.
- `metrics.json` — baseline and post-promotion performance.
- `owner/reviewer` metadata — who or what approved it.

The production runtime should invoke skills through a runner interface or subprocess/container boundary. It should not dynamically import unreviewed files into the Solomon gateway.

---

## The real learning objective

“Learn as much as possible” is not sufficient. Without an objective, the machine will accumulate noise.

Use a measurable utility function:

```text
Learning Utility =
  expected future task value
  × probability the lesson generalizes
  × confidence improvement
  × reuse potential
  × safety factor
  ÷ (compute cost + human review cost + operational risk + complexity debt)
```

Prometheus should select the next learning job that maximizes expected utility subject to safety and budget constraints.

### Curiosity triggers

Create a Learning Opportunity whenever one of these occurs:
- The same failure appears twice.
- A task requires an unavailable capability.
- A worker used an expensive workaround.
- Confidence is low on a high-value decision.
- Two cards conflict.
- A skill's success rate declines.
- Human correction contradicts an active card.
- A new tool/repository/document may fill a known gap.
- A task succeeds unusually well and the method may generalize.
- The system spends excessive time searching or planning.

---

## Meta-learning: how Solomon learns to learn

The machine becomes genuinely perpetual only when it experiments with its own learning methods.

Track a `LearningStrategy` entity for methods such as:
- extraction prompt/version,
- retrieval weighting,
- chunking policy,
- experiment type,
- test generation policy,
- reviewer model or rubric,
- skill-routing policy,
- rehearsal schedule,
- forgetting/retirement rule.

For each strategy, record:
- learning yield,
- later reuse,
- false-positive rate,
- validation failure rate,
- compute/time cost,
- human corrections,
- downstream task improvement.

Prometheus can then use a bounded bandit or Bayesian-selection policy to allocate a small percentage of learning jobs to alternative strategies while keeping the best-known strategy as the default. This is safer and more honest than calling heuristic score updates “reinforcement learning.”

---

## Canonical repository plan

Start with the file tree from `jules_session_2053092947882016941-3` and create one repository:

```text
solomon/
  apps/
    gateway/                 # one production API, no duplicate Flask apps
    proxy/                   # 7420 authenticated edge
    command_center/
  plc/
    experience/              # normalized event ledger
    memory/                  # Mnemosyne cards, graph, retrieval, lifecycle
    planning/                # Prometheus planner and curiosity queue
    skills/                  # manifests, registry, routing contracts
    evaluation/              # Crucible and Hugin evaluators
    governance/              # review, clearance, policy, promotion
    metrics/                 # learning and task effectiveness
  adapters/
    software_engineering/
    solomon_gpt/
  workers/
    openhands/
    jules/
    codex/
    local_shell/
  deploy/
    ss1/
    ss2/
    ss3/
  tests/
    unit/
    integration/
    system/
    soak/
  migrations/
  pyproject.toml
  .env.example
```

### Merge sources

**Baseline:** `205309...`
**Merge from `117440...`:** deployment scripts, runbooks, action schema, auth validation, autonomous-loop scanner/sandbox ideas, domain-neutral PLC rules.
**Merge from `203671...`:** conceptual stages and selected safe utilities, rewritten behind skill manifests and subprocess boundaries.
**Preserve from older branches:** regression tests and any behavior missing from the baseline.
**Keep outside core:** Loki betting models, persona-specific prompts, UI experiments, generated databases/logs/bytecode.

---

## Database unification

Use one logical database boundary with migrations. SQLite can remain appropriate for the current three-box scale if configured carefully, but the schema must unify state.

Minimum tables/entities:

- `experiences`
- `tasks`
- `task_events`
- `knowledge_cards`
- `card_revisions`
- `card_relations`
- `evidence`
- `learning_opportunities`
- `experiments`
- `experiment_runs`
- `skills`
- `skill_versions`
- `skill_evaluations`
- `promotions`
- `rollbacks`
- `learning_strategies`
- `strategy_trials`
- `worker_leases`
- `metrics_daily`
- `audit_log`

Every promoted claim must trace back to evidence. Every skill invocation must trace to a version. Every change must be reversible.

---

## SS1 / SS2 / SS3 operating model

### SS1 — Production brain
- Stable gateway, planner, memory retrieval, approved skill runner.
- Read-only access to promoted skill artifacts.
- No arbitrary code generation or dynamic imports.
- Can create learning opportunities and dispatch lab work.

### SS2 — Learning laboratory
- Clones/repositories, builds, experiments, generated code, fault injection.
- Network and filesystem permissions granted per experiment.
- Mandatory snapshots/checkpoints.
- Disposable worktrees/containers.

### SS3 — Reviewer and gatekeeper
- Independently reruns tests from clean state.
- Runs security, license, regression, and reproducibility checks.
- Signs approved skill packages.
- Can reject, quarantine, or demand more evidence.

Promotion is SS2 → SS3 → SS1. Never SS2 → SS1 directly.

---

## Metrics that determine whether Solomon is truly learning

### Learning throughput
- Experiences ingested/day.
- Valid cards produced/day.
- Skills proposed, validated, promoted, rejected.
- Time from failure to verified repair.

### Learning quality
- Card retrieval precision and false-positive rate.
- Confidence calibration.
- Reproducibility rate.
- Skill held-out test success.
- Human correction rate.

### Reuse and value
- Percentage of tasks using prior knowledge.
- Percentage using promoted skills.
- Success improvement versus baseline.
- Time/cost saved through reuse.
- Number of distinct later tasks benefiting from each learning asset.

### Safety and stability
- Promotion rejection rate.
- Rollbacks.
- Sandbox violations.
- Unauthorized access attempts.
- Regression rate after promotion.
- Stale or contradictory cards detected.

### Meta-learning
- Utility gained per compute-hour.
- Utility gained per human-review minute.
- Performance by learning strategy.
- Search/planning overhead trend.
- Rate at which the machine reduces repeated mistakes.

The north-star metric should be:

> **Verified reusable capability gain per unit of cost and risk.**

---

## Build sequence from here

### Phase 0 — Freeze and preserve
1. Import all nine archives into a single Git repository as tagged historical snapshots.
2. Record hashes and never edit the snapshots.
3. Select `205309...` as the canonical baseline branch.

### Phase 1 — Reproducible canonical build
1. Add `pyproject.toml` and lock dependencies.
2. Remove `.db`, `.log`, `.pyc`, and generated artifacts from source control.
3. Merge all 88 tests into one suite, eliminate duplicates, and retain behavior coverage.
4. Fix timezone warnings and obsolete OpenAI usage.
5. Add migrations and configuration validation.

**Exit criterion:** one command creates a clean environment and all tests pass.

### Phase 2 — One gateway and one state boundary
1. Consolidate duplicate Flask applications.
2. Route proxy 7420 to one gateway on 18789.
3. Create a shared database manager and event ledger.
4. Connect chat, planner, worker reports, review, cards, and metrics to that state.
5. Add health/readiness/liveness checks.

**Exit criterion:** every interaction appears in one traceable ledger and survives restart.

### Phase 3 — Real worker loop
1. Define worker adapter protocol: claim, heartbeat, event, result, evidence, release.
2. Integrate one worker first—OpenHands or local shell—not all workers simultaneously.
3. Feed retrieved memory into plans.
4. Persist complete execution evidence.
5. Turn failures and corrections into draft learning opportunities.

**Exit criterion:** Solomon completes a bounded real repository task and learns a repair reused in a second task.

### Phase 4 — Governed skill factory
1. Convert Gabriel stages into a skill-building workflow.
2. Define Skill Package and signed promotion process.
3. Execute generated/rebuilt skills only in sandboxed subprocesses/containers.
4. Add held-out benchmarks and adversarial tests.
5. Require SS3 reproducibility before promotion.

**Exit criterion:** one new skill is generated or reconstructed, approved, promoted, routed, and successfully reused.

### Phase 5 — Curiosity and autonomous learning queue
1. Add curiosity triggers and expected-utility scoring.
2. Budget autonomous learning by CPU, time, storage, and risk.
3. Run only reversible learning jobs without human approval.
4. Escalate high-risk actions for approval.
5. Implement duplicate/conflict detection.

**Exit criterion:** Solomon independently selects and completes useful learning jobs without aimless activity.

### Phase 6 — Meta-learning
1. Version learning strategies.
2. Run controlled strategy trials.
3. Measure downstream reuse and value.
4. Allocate exploration budget.
5. Promote better learning policies through the same governance path.

**Exit criterion:** measured improvement in verified learning utility over successive evaluation windows.

### Phase 7 — Continuous operation and resilience
1. Multi-day soak tests.
2. Power/network/disk/OOM fault tests.
3. Automatic rollback and recovery drills.
4. Storage compaction, forgetting, archiving, and contradiction repair.
5. Dashboard and daily learning report.

**Exit criterion:** 30 days of operation with reproducible gains, bounded costs, no uncontrolled promotion, and successful recovery drills.

---

## Immediate next engineering task

The next task should **not** be another new subsystem. It should be a canonical consolidation sprint:

> Create a new `solomon-plc` repository from the Phase 3C branch, import deployment/auth improvements from the PLC branch, import Gabriel only as a disabled laboratory package, merge the 88 tests, add packaging and migrations, and produce a single local end-to-end test proving experience → retrieval → plan → sandbox execution → evidence → draft card → review → promotion → reuse.

Until that test exists, the system is a collection of promising cognitive components. Once that test exists and runs on SS1/SS2/SS3, Solomon becomes the first real version of the perpetual learning machine.

---

## Final assessment

### What Jules accomplished

Jules created a credible foundation rather than empty scaffolding. The memory system, review lifecycle, retrieval, graph, planner safeguards, security tests, deployment materials, and Gabriel concepts are all valuable. The work demonstrates that Solomon can be engineered as a learning system rather than merely prompted to “remember.”

### What must change now

Stop branching the architecture into isolated session archives. Stop equating generated code or synthetic benchmark output with learned capability. Stop allowing an experimental assimilation engine to define its own evidence and then approve itself.

From now forward, every capability must move through one chain:

```text
Experience → Evidence → Draft Knowledge/Skill → Independent Evaluation
→ Review → Versioned Promotion → Measured Reuse → Revision/Retirement
```

That chain is the machine.

### Destination

The destination is not an AI that knows everything. It is an AI that:
- notices what it does not know,
- chooses what is worth learning,
- learns through bounded experiments,
- proves what it learned,
- stores it in reusable form,
- applies it at the right time,
- measures whether it helped,
- corrects or forgets bad learning,
- and continually improves the learning process itself.

That is the perpetual learning machine Solomon is becoming.
