# PROJECT SOLOMON — JULES IMPLEMENTATION CAMPAIGN 01

**STATE INTEGRITY, CANONICAL MEMORY, DURABLE GOVERNANCE, CLOSED-LOOP LEARNING, AND RESIDENT CONTINUITY**

- **Executor:** Jules / Antigravity
- **Authority:** Mark Miller / Project Solomon
- **Repository last reported:** `/app`
- **Remote last reported:** `https://github.com/SoapLogistics/BubblPath`
- **Branch last reported:** `jules-13384773238309533918-912b2a35`
- **Last reported commit:** `4d4a01f739ea65d34e8ee2838c112785b50d1e7a`
- **Environment last reported:** `SANDBOX_DEV`
- **Current verified maturity:** Level 3/7 sandbox prototype
- **Campaign type:** Code-first implementation campaign
- **Expected result:** Material repository changes, expanded tests, clean evidence, and one functioning perpetual-learning cycle
- **Forbidden result:** Another inventory-only, audit-only, or repackaged-directive ZIP

---

## 0. EXECUTIVE COMMAND

The most recent Jules return did not execute the supplied repair order. The new ZIP:
- added a shortened copy of `PROJECT_SOLOMON_FULL_REPAIR_AND_PERPETUAL_LEARNING_COMPLETION_ORDER.md`;
- left the component registry unchanged;
- left the runtime identity unchanged;
- left both test outputs unchanged;
- left the Gabriel source unchanged;
- left the master audit unchanged;
- removed `fact_memory.log`;
- removed `governance_log.bin`;
- did not include `memory_atoms.db`;
- did not add implementation files;
- did not add tests;
- did not add migrations;
- did not create a clean commit;
- did not produce a closed-loop trace;
- did not implement residents;
- did not prove restart or recovery.

That is not completion of the order.

This campaign changes the mode of work:
> Do not write another inventory or audit until the implementation and test requirements in this campaign have been executed.

The only acceptable next ZIP contains:
- real source changes;
- real new tests;
- a clean commit;
- a full fresh test run;
- root-state immutability proof;
- a canonical database;
- durable governance;
- one real closed-loop learning cycle;
- resident checkpoint and restart proof;
- a complete evidence manifest.

*Documentation may accompany the implementation. Documentation may not substitute for it.*

---

## 1. CAMPAIGN OUTCOME

At the end of this campaign, Solomon must be able to perform this exact sequence:
1. Receive or observe a task failure.
2. Create a structured event.
3. Draft a non-empty learning candidate.
4. Reject duplicates.
5. Validate the candidate with real evidence.
6. Route the candidate through governance.
7. Activate the approved memory.
8. Index it.
9. Receive a similar task.
10. Retrieve the memory before planning.
11. Record how the memory changed the plan.
12. Execute the task.
13. Measure the outcome.
14. Update memory utility and confidence.
15. Select the next learning target.
16. Persist a checkpoint.
17. Stop the process.
18. Restart the process.
19. Resume without duplicating the task or memory.
20. Preserve the complete event and governance history.

*A single integration test must prove the entire sequence.*

---

## 2. NO-PAPERWORK RETURN RULE

The next returned archive is automatically rejected if all of the following are true:
- fewer than five production source files changed;
- fewer than ten new tests were added;
- no migration file exists;
- no new canonical database schema exists;
- no root-state isolation test exists;
- no governance append-only test exists;
- no closed-loop integration test exists;
- no resident framework exists;
- no fresh test output exists;
- Git status is not clean;
- no manifest hashes the evidence.

The following do *not* count as implementation:
- renaming an inventory;
- copying this directive;
- shortening this directive;
- changing maturity wording;
- deleting evidence files;
- omitting broken state;
- changing only Markdown;
- adding empty placeholder modules;
- adding skipped tests;
- adding tests that mock the entire closed loop;
- adding a static dashboard without a live backend;
- returning old test output.

---

## 3. REQUIRED IMPLEMENTATION BRANCH

Create a new branch from the current real commit:
```bash
git switch -c jules/solomon-state-core-closed-loop
```

Before modifying code:
- `mkdir -p evidence/campaign_01/00_before`
- `git rev-parse HEAD > evidence/campaign_01/00_before/commit.txt`
- `git status --porcelain > evidence/campaign_01/00_before/git_status.txt`
- `git diff --binary > evidence/campaign_01/00_before/working_tree.patch`

Back up all known state:
- `mkdir -p evidence/campaign_01/00_before/state_backup`

Locate and back up:
- `memory_atoms.db`
- `solomon_soss.db`
- `solomon_brain_map.bin`
- `governance_log.bin`
- `fact_memory.log`
- all checkpoint files
- all SQLite WAL/SHM files

For every state artifact, record:
- absolute path, size, SHA-256, modified time, role, reader modules, writer modules, and write: `evidence/campaign_01/00_before/state_manifest.json`

*Do not delete any existing state until it has been backed up and its disposition is documented.*

---

## 4. WORKSTREAM A — CENTRAL CONFIGURATION AND PATH CONTROL

### A.1 Goal
No production module and no test may use a hard-coded state path.

### A.2 Create package structure
Create:
```text
core/config/
  __init__.py
  paths.py
  settings.py
  validation.py
```

### A.3 `core/config/paths.py`
Implement an immutable path model. Reject `..` traversal, symlink escapes, and require paths inside the configured root.

### A.4 `core/config/settings.py`
Implement validated settings with environment priorities.

### A.5 Replace hard-coded paths
Replace direct usage with settings or path objects.

### A.6 Tests
Add corresponding testing and audit scripts.

---

## 5. WORKSTREAM B — TEST ISOLATION AND ROOT-STATE IMMUTABILITY

### B.1 Goal
Running all tests must not modify any production or repository-root state file.

---

## 6. WORKSTREAM C — CANONICAL DATABASE

### C.1 Goal
One relational database becomes the authoritative state store.

---

## 7. WORKSTREAM D — LEARNING DOMAIN MODEL

### D.1 Goal
Create one coherent learning model rather than disconnected writeback functions.

---

## 8. WORKSTREAM E — DURABLE GOVERNANCE

### E.1 Goal
Replace `governance_log.bin` as the authoritative record with an append-only hash chain.

---

## 9. WORKSTREAM F — RETRIEVAL BEFORE PLANNING

### F.1 Goal
Prove that memory retrieval occurs before final planning.

---

## 10. WORKSTREAM G — OUTCOME-LINKED MEMORY UPDATE

### G.1 Goal
A memory becomes more or less useful based on actual task results.

---

## 11. WORKSTREAM H — NEXT LEARNING TARGET SELECTOR

### H.1 Goal
After a cycle, Solomon selects the next highest-value bounded learning target.

---

## 12. WORKSTREAM I — REAL CLOSED-LOOP INTEGRATION TEST

### I.1 Goal
This is the campaign’s central acceptance test. Prove the entire learning loop from event through activation and reuse.

---

## 13. WORKSTREAM J — RESIDENT FRAMEWORK

### J.1 Goal
Create one durable resident loop with lease, checkpointing, and sleep yields.

---

## 14. WORKSTREAM K — GUARDIAN RESIDENT

### K.1 Goal
Check database integrity, disk space, and monitor loop heartbeats.

---

## 15. WORKSTREAM L — JULES CONVERGENCE RESIDENT

### L.1 Goal
Scan for structural drift, duplicate files, and missing test files.

---

## 16. WORKSTREAM M — VALIDATION SERVICE

### M.1 Goal
Provide type-appropriate validation proof records for all candidates.

---

## 17. WORKSTREAM N — SECURE EXISTING GABRIEL ENGINE

### N.1 Goal
Close AST path boundaries, dynamic loader traverses, and require capability permissions.

---

## 18. WORKSTREAM O — SECURE GATEWAY AND WRITEBACK

### O.1 Goal
Enforce authentication, input validation, error trace shielding, and signature verifications.

---

## 19. WORKSTREAM P — FRESH TEST BASELINE

### P.1 Expand suite
Expand tests to at least 75 total passing tests.

---

## 20. WORKSTREAM Q — BACKUP AND RESTORE

### Q.1 Goal
Verify online SQLite backups and recovery drills.

---

## 21. WORKSTREAM R — SERVICE ENTRY POINT

### R.1 Goal
Define clean startup, shutdown, and lifecycle order.

---

## 22. WORKSTREAM S — PROCESS RESTART PROOF

### S.1 Goal
Show continuous cycle progression across process restarts.

---

## 23. WORKSTREAM T — COMPONENT REGISTRY UPDATE

Update registry statuses strictly following physical scans.

---

## 24. REQUIRED COMMIT PLAN & ACCEPTANCE GATES

Follow the sequential commit structures and achieve all 14 Acceptance Gates.
