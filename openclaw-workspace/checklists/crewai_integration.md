# PROCEDURE CARD: CrewAI Orchestration & Multi-Agent Operational Checklist

- **Card ID:** PC-CA-01
- **Focus Area:** Multi-Agent Collaboration, Operational Research, Strategy, and Output Synthesis
- **Target Agent:** CrewAI (Sub-Agent Orchestration Framework)
- **Lifecycle Mode:** 24/7 Autonomous execution

---

## 1. Context & Purpose
This procedure card guides the OpenClaw coordinator through assembling, running, validating, and recovering CrewAI sessions. CrewAI must be engaged for complex workflows requiring multi-persona analysis, high-quality strategic reporting, document reviews, or structured workflow planning.

---

## 2. Operational Checklist

### Phase 1: Pre-Execution Requirements
Before invoking any CrewAI session, the OpenClaw coordinator must execute and confirm the following:
- [ ] **1.1 Configuration Validation:** Ensure the target crew config files (YAML or JSON formats defining agents, roles, backstories, and tasks) are present and structurally valid:
  ```bash
  python3 -c "import json, yaml; yaml.safe_load(open('/srv/storage/toshiba/BubblePath/openclaw-workspace/crews/research_crew.yaml'))"
  ```
- [ ] **1.2 Environment Check:** Ensure `CREWAI_TELEMETRY` and `OPENAI_API_KEY` are successfully exported.
- [ ] **1.3 Task Input Mapping:** Prepare the `inputs` payload. Every variable required by the task templates (e.g., `{topic}`, `{date}`) must be mapped with correct parameters in the tool call.

### Phase 2: Crew Assembly & Execution
Invoke the multi-agent session using the `crewai_run` tool.
- [ ] **2.1 Configuration Payload:** Format the tool request exactly as defined in `TOOLS.md`:
  ```json
  {
    "crew_config_path": "/srv/storage/toshiba/BubblePath/openclaw-workspace/crews/research_crew.yaml",
    "inputs": {
      "topic": "Microservices dependency health",
      "target_date": "2026-07-19"
    },
    "timeout": 300
  }
  ```
- [ ] **2.2 Monitoring Logs:** Follow the execution log of the crew agents to monitor thought processes and detect delegation loops:
  ```bash
  tail -f /srv/storage/toshiba/BubblePath/openclaw-workspace/logs/crewai_session.log
  ```
- [ ] **2.3 Resource Caps Monitoring:** Check memory consumption of the Python runner process to ensure it stays below the 1.5GB cap:
  ```bash
  ps aux | grep python3 | grep crewai
  ```

### Phase 3: Output Parsing & Schema Validation
Once the CrewAI session concludes:
- [ ] **3.1 Output Recovery:** Locate the final synthesized output. This is typically written to a markdown file or returned as a structured JSON object.
- [ ] **3.2 Schema Validation:** If a JSON schema was requested for the output, validate the parsed JSON structure:
  ```bash
  python3 -c "import json; data = json.load(open('crew_output.json')); assert 'summary' in data and 'recommendations' in data"
  ```
- [ ] **3.3 Actionable Decisions:** Extract key decisions or recommendations and write them into the daily progress log (`memory/YYYY-MM-DD.md`) so subsequent runs benefit from the research.

### Phase 4: Recovery, Timeouts & Resource Management
If the CrewAI execution fails, hangs, or experiences severe performance degradation:
- [ ] **4.1 Force Termination:** If the execution times out (>300 seconds), locate and terminate the orphaned Python sub-processes:
  ```bash
  kill $(pgrep -af "crewai" | awk '{print $1}') 2>/dev/null || true
  ```
- [ ] **4.2 Resource Reclamation:** Clean up temporary cached vectors or session history files from the CrewAI memory cache to prevent memory leaks:
  ```bash
  rm -rf ~/.crewai/cache/*
  ```
- [ ] **4.3 Backoff & Retry:** On failure, wait 60 seconds (incremental backoff) and attempt exactly one retry with a slightly simplified set of tasks or a smaller context payload.
- [ ] **4.4 Escalation:** If the retry fails or the crew config remains unparseable, transition the task state to `PAUSED_BLOCKED` and dispatch an alert to the operator.
