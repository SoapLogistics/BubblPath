# 🏛️ Project Solomon: Perpetual Learning Machine (SOSS Core)

Welcome to the definitive repository for the **Solomon Perpetual Learning Machine (SOSS Core)**. SOSS represents a governed, isolated, and highly performant cognitive substrate capable of learning from experiences, performing safe sandboxed experiments, and promoting approved workflows through cryptographically chained governance lanes.

---

## 🗺️ Subsystem Architecture & Map

```
                  ┌─────────────────────────────────────┐
                  │       Edge API Proxy (7420)         │
                  └──────────────────┬──────────────────┘
                                     │
                  ┌──────────────────▼──────────────────┐
                  │    Unified SOSS Gateway (18789/10k) │
                  └──────┬──────────────────────┬───────┘
                         │                      │
       ┌─────────────────▼─────────┐  ┌─────────▼─────────────────┐
       │   Mnemosyne Memory Sub    │  │   Gabriel Lab / Evolution │
       │  (solomon_hyper_memory.db)│  │ (Sandboxed AST Execution) │
       └───────────────────────────┘  └───────────────────────────┘
```

### 1. **SOSS Flask Core (`app.py`)**
-   **Role:** Exposes API routes, controls background tasks, and provides cognitive orchestration pathways.
-   **API Endpoints:**
    -   `/chat`, `/talk`: Interactive local response router and state query paths.
    -   `/api/memory/*`: Ingestion, hybrid sparse activation recall, and dream cycles.
    -   `/api/gabriel/*`: Dynamic capabilities compilation, evaluation, and AST injection gates.
    -   `/api/jules/*`: Patcher, dependency setups, and recursive corrections.

### 2. **Mnemosyne: Memory Substrate (`core/`)**
-   **Core Module:** `core/solomon_quantized_memory.py`
-   **Database:** `solomon_hyper_memory.db` (utilizes high-speed WAL mode with transaction thread safety).
-   **Design:** Vectorized ternary similarity dot products, Spreading Activation via sparse matrices (Hebbian updates), and decay consolidation modeling.

### 3. **Gabriel: Capability Assimilation (`gabriel_engine/`)**
-   **Core Modules:** `gabriel_engine/core/*`
-   **Design:** Safe AST-based static code analysis, license compliance filters, and sandboxed dynamic execution testing.

### 4. **Prometheus: Futures & Predictions (`services/`)**
-   **Core Module:** `services/solomon_futures_engine.py`
-   **Database:** `solomon_soss.db`
-   **Design:** Multi-dimensional Monte Carlo simulations with Gates A & B evaluation, Wilson confidence intervals, and sensitivity stress checks.

---

## 🛠️ Developer Experience (DX) Commands

We provide a single, unified CLI command utility for setting up, running, formatting, style checks, and system diagnostics:

```bash
# Setup: Installs dependencies and prepares environment
./scripts/solomon_dx.py setup

# Run tests: Executes all pytest verification suites
./scripts/solomon_dx.py test

# Format: Beautifully formats the codebase using Black
./scripts/solomon_dx.py format

# Lint: Checks code quality and compliance with Black & Flake8
./scripts/solomon_dx.py lint

# Run: Launches SOSS Flask core server locally on Port 10000
./scripts/solomon_dx.py run

# Health check: Instantly verifies required files, ports, and versions
./scripts/solomon_dx.py health-check
```

---

## 📈 System Maturity Status & Limitations

Solomon operates at **Level 4/7** maturity:
-   **Memory:** Vectorized and persistent on WAL SQLite.
-   **Governance:** Append-only SHA-256chained transaction audit trail logs with programmatic expirations, revocations, and verification checks.
-   **Safety:** Zero execution is performed outside the local sandbox, and any agentic behavior defaults to honest status notices when no adapter is configured.
