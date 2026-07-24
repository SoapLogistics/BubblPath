# TOOLS.md - Local Notes & Agent Integrations

This file documents the local tool inventory, security boundaries, and integration configurations for the **OpenClaw** workspace. It outlines the specific tool rules, API references, environment setups, and parameter mappings for coordinating **OpenHands** (for codebase/engineering tasks), **CrewAI** (for multi-agent research and task delegation), and **Open-Source Code Absorption & MCP Integration** within the 24/7 autonomous cycle.

---

## 1. Secrets and Environment Configurations

All sensitive keys and environment variables are externalized. Under no circumstances should raw API credentials be committed to the repository or written directly into workspace files.

- **Canonical Configuration Location:** `/srv/storage/toshiba/BubblePath/openclaw-workspace/.env` (or user home alternative: `~/.openclaw/.env`)
- **Required Variables:**
  - `OPENAI_API_KEY`: Secret key for LLM orchestration (e.g., `gpt-4o`, `gpt-3.5-turbo`).
  - `OPENHANDS_API_KEY`: Key/Token for interacting with the OpenHands remote workspace server.
  - `OPENHANDS_URL`: Endpoint for OpenHands API (e.g., `http://localhost:3000`).
  - `CREWAI_TELEMETRY`: Boolean (`true`/`false`) to manage CrewAI execution telemetry.

---

## 2. OpenClaw Core Tools

The following built-in tools are natively available to the OpenClaw agent.

### 2.1 File System Access (`file_ops`)
- **Purpose:** Read, write, list, and modify files within the `/srv/storage/toshiba/BubblePath/openclaw-workspace/` boundary.
- **Constraints:**
  - **Read Limit:** Max file size 1MB per read operation.
  - **Path Resolution:** Absolute paths outside of `/srv/storage/toshiba/` are strictly blocked unless explicit read/write privileges are enabled in `openclaw.json`.
  - **Write Gate:** All writes must be followed by immediate structural verification using a read-back check.

### 2.2 Bash Executor (`bash_run`)
- **Purpose:** Execute arbitrary terminal commands in the local sandbox.
- **Rules & Bounds:**
  - **Non-Interactive Only:** Interactive prompts (e.g., waiting for `y/n` inputs) will hang and time out after 60 seconds.
  - **Command Sanitization:** Destructive commands (`rm -rf /`, `mkfs`) are blocked.
  - **Stderr Capturing:** All stderr must be captured and logged for debugging purposes.

---

## 3. OpenHands Integration (Agentic Coding & Codebases)

**OpenHands** is the dedicated engineering partner agent. When a task requires deep repository investigation, system-level compilation, test suites execution, or multi-file code modifications, OpenClaw delegates execution to OpenHands.

### 3.1 Tool Signature: `openhands_run`
- See standard parameter properties in [`checklists/openhands_integration.md`](checklists/openhands_integration.md). OpenHands runs in a sandboxed Docker environment (`ghcr.io/all-in-a-day/openhands:latest`) and is capable of modifying files, setting up virtual environments, and executing unit tests safely.

---

## 4. CrewAI Integration (Multi-Agent Orchestration & Research)

**CrewAI** is leveraged for complex, parallelized workflows requiring multi-persona brainstorming, strategic planning, and report generation.

### 4.1 Tool Signature: `crewai_run`
- See details in [`checklists/crewai_integration.md`](checklists/crewai_integration.md). Generates high-signal insights and delegates research and strategic tasks to autonomous sub-agents with strict CPU (2 cores) and memory (1.5GB RAM) caps.

---

## 5. Solomon Open-Source Code Absorption & MCP Dynamic Integration

To achieve passive exponential growth, Solomon dynamically scans, downloads, and absorbs external open-source code and integrates it into its active runtime using the **Model Context Protocol (MCP)** or direct package installers.

### 5.1 Open-Source GitHub Discovery Tool (`github_search_and_clone`)
```json
{
  "name": "github_search_and_clone",
  "description": "Searches GitHub for the most popular open-source software, libraries, and tools related to a specific problem and clones them to a sandbox directory.",
  "parameters": {
    "type": "object",
    "properties": {
      "query": { "type": "string", "description": "Search keyword or topic (e.g., 'trading bot', 'lead generation scraper')." },
      "destination_path": { "type": "string", "description": "Local sandbox directory to clone the repository into." }
    },
    "required": ["query", "destination_path"]
  }
}
```

### 5.2 Dynamic Language Package Installer (`pypi_npm_install`)
```json
{
  "name": "pypi_npm_install",
  "description": "Installs Python (pip) or Node.js (npm) packages dynamically into the isolated agent environment.",
  "parameters": {
    "type": "object",
    "properties": {
      "manager": { "type": "string", "enum": ["pip", "npm"], "description": "The package manager to use." },
      "package_name": { "type": "string", "description": "The name of the open-source library to install." }
    },
    "required": ["manager", "package_name"]
  }
}
```

### 5.3 MCP Server Dynamic Orchestrator (`mcp_server_integrate`)
```json
{
  "name": "mcp_server_integrate",
  "description": "Spins up an external Model Context Protocol (MCP) server dynamically, allowing Solomon to instantly discover and utilize its tools.",
  "parameters": {
    "type": "object",
    "properties": {
      "server_command": { "type": "string", "description": "The bash command or script path to execute the MCP server (e.g., 'npx -y @modelcontextprotocol/server-postgres')." },
      "config_alias": { "type": "string", "description": "The alias/identifier to reference the new tools inside Solomon's session config." }
    },
    "required": ["server_command", "config_alias"]
  }
}
```
- **Automatic Tool Injection:** Once the MCP server starts, its available tool schemas are fetched dynamically and loaded into Solomon's system prompt list automatically, removing the need for manual python source adjustments.
