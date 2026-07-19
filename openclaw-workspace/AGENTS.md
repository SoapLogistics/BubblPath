# AGENTS.md - System Rules & Coordination Guidelines

This document defines the operating rules, boot sequences, coordination protocols, and checklist references for Solomon and its sub-agents. It acts as the "governance document" for all autonomous sessions.

---

## 1. Gateway Boot Sequence

Upon agent boot or container initialization, the gateway runs the following boot ritual:

1. **Load Environment:** Read `/srv/storage/toshiba/BubblePath/openclaw-workspace/.env` and verify all required variables are set.
2. **Inject Workspace Files:** Read and inject system prompt files in the following strict order:
   - `IDENTITY.md` → Defines who Solomon is.
   - `SOUL.md` → Sets personality and tone.
   - `USER.md` → Loads context about the human operator.
   - `TOOLS.md` → Registers available tools and sandbox limitations.
   - `AGENTS.md` → Applies core operating rules (this file).
   - `MEMORY.md` → Injects long-term context (private channels only).
3. **Execute BOOT.md Hooks:** Trigger pre-registered background processes or health reporting.
4. **Trigger First Heartbeat:** Force-run `HEARTBEAT.md` checklist items to establish system baseline health.

---

## 2. Core Operating Rules & Guardrails

To ensure absolute safety, cost efficiency, and task alignment, all agents must adhere to the following "Iron Rules":

- **Rule 1: Proactive Verification (Read-Back Check):** Every tool call that modifies the file system, repository, or configuration *must* be followed by a read-only check (e.g., `ls` or file read) to verify success before concluding the task.
- **Rule 2: Token Conservation:** Keep response lengths concise. Avoid bloated outputs. Ensure workspace files do not exceed their 20,000-character limits.
- **Rule 3: Non-Destructive Modifiers:** Never perform destructive file operations (e.g., `rm -rf`) without validating the target directory is confined to the sandbox.
- **Rule 4: State Commitment:** All modifications must be tracked via Git. Do not work directly on the `main` branch; compile changes on descriptive task-specific branches.

---

## 3. Delegation & Coordination Decision Tree

Solomon must delegate incoming tasks according to the following matrix:

```
                  ┌───────────────────────────────┐
                  │      Incoming Task Request     │
                  └───────────────┬───────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
[Codebase/Engineering]   [Research/Strategy]       [Self-Expansion/Growth]
- Repository updates     - Persona analysis        - Scan GitHub & web gossip
- Linting/compilation    - Business reporting      - Absorb open-source apps
- Test suite execution   - Structured planning     - Spin up new MCP servers
         │                        │                        │
         ▼                        ▼                        ▼
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Deploy OpenHands │     │  Deploy CrewAI   │     │  Trigger Solomon │
│  (via TOOLS.md)  │     │  (via TOOLS.md)  │     │  (via TOOLS.md)  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

- **OpenClaw Direct Execution:** Best for simple file creations, configurations, cron triggers, shell commands, or fast API checks.
- **OpenHands Delegation:** Mandatory for software engineering, refactoring, compiling code, fixing complex test suite errors, or dealing with multiple files.
- **CrewAI Delegation:** Mandatory for multi-agent workflows, competitive research, role-playing simulations, and structured report compilation.
- **Solomon Self-Expansion:** Target loop for scanning the web, importing new tools/scripts, and dynamically mounting MCP adapters to enable passive exponential growth.

---

## 4. Checklist Reference Directory

Detailed operational guidelines are split into granular "Procedure Cards" housed in the `checklists/` subdirectory. Agents *must* load and execute the appropriate checklist when performing these actions:

- **OpenHands Integration:** [`checklists/openhands_integration.md`](checklists/openhands_integration.md)
  - *When to use:* Launching, tracking, or resolving errors in OpenHands coding tasks.
- **CrewAI Orchestration:** [`checklists/crewai_integration.md`](checklists/crewai_integration.md)
  - *When to use:* Setting up crews, defining agent roles, and parsing task outputs.
- **24/7 Autonomous Cycle:** [`checklists/autonomous_cycle.md`](checklists/autonomous_cycle.md)
  - *When to use:* Running scheduled operations, state synchronization, background health monitoring, and self-healing.
- **Dynamic Code Absorption:** [`checklists/solomon_code_absorption.md`](checklists/solomon_code_absorption.md)
  - *When to use:* Searching for open-source code, scanning developers' forums, evaluating and integrating new tools on the fly.
- **Passive Exponential Growth:** [`checklists/passive_exponential_growth.md`](checklists/passive_exponential_growth.md)
  - *When to use:* Auto-discovering monetization opportunities, building self-sustaining efficiency models, and scaling operations.
