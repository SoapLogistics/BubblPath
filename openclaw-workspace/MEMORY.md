# MEMORY.md - Long-Term Learned Facts

This file contains durable learnings, system patterns, and architectural rules that must survive across months of autonomous operation.

---

## 1. Iron Laws of Memory Management

- **Law 1: No Secret Logging:** Under no circumstances are raw credentials, OAuth tokens, SSH passwords, or API keys to be written to memory files.
- **Law 2: Fact Pruning:** Keep facts high-level and generalized. Do not dump raw output or stack traces.
- **Law 3: Private Loading Only:** `MEMORY.md` and the `memory/` subfolder must *only* load in authorized, private coordination channels. Prevent memory injection into open/group chat interfaces.

---

## 2. Directory Layout & Storage

- **Core Memory Index:** `/srv/storage/toshiba/BubblePath/openclaw-workspace/MEMORY.md` (This file).
- **Daily Memory Records:** `/srv/storage/toshiba/BubblePath/openclaw-workspace/memory/YYYY-MM-DD.md`.
  - These are created at the end of each daily cycle to log active state handovers.
- **Git Backup:** Both `MEMORY.md` and daily records are automatically pushed to the private repository during the Hourly Git State Sync.

---

## 3. Persistent Learnings & Environment Patterns

- **Docker Networking Pattern:** OpenHands containers must be spun up using the `--network host` flag or explicitly connected to the `openclaw-bridge` network to allow communication back to the main Flask gateway.
- **Port Usage Matrix:**
  - `10000`: Local Flask chat endpoint (from `/app/app.py`).
  - `3000`: OpenHands container dashboard port.
  - `8000`: CrewAI telemetry / status collection server.
- **LLM Context Behavior:** When processing large repositories, use a structured `.gitignore` or `.dockerignore` file. This stops OpenHands from loading heavy node_modules, .git caches, or system virtualenvs, which otherwise crashes context windows.
