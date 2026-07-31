# PROJECT SOLOMON — COMPLETE REALITY INVENTORY

## 1. ENVIRONMENT AND ACCESS INVENTORY
* **Machine:** devbox
* **Kernel:** Linux devbox 6.8.0 #1 SMP PREEMPT_DYNAMIC
* **CPU:** Intel(R) Xeon(R) Processor @ 2.30GHz, 4 cores
* **RAM:** 7.8Gi Total, 7.3Gi Free
* **Disks:** /dev/vdb (98G, 1% used)
* **Mount:** overlayfs on /
* **Python Version:** Python 3.12.3
* **Docker Version:** 29.2.1
* **Users:** root, jules (current user running everything)

## 2. REPOSITORY INVENTORY
* **Working Tree:** Clean, checked out on `jules-1495918050171085004-39cbe6a9`.
* **Commit:** `32eb8c9e8882e6936fd8a597085e61eb288438ed`
* **Recommendation:** The current branch should become the source of truth, but will require CI/CD standardisation since testing passes locally only with manually installed missing dependencies (`openai`, `duckduckgo_search`, `flask`, `sqlalchemy`, etc.).

## 3. COMPLETE FILE AND DIRECTORY MAP
* `/app` is the root
* `core/`:
  * `solomon_quantized_memory.py` (Unified Memory system)
  * `solomon_web_crawler.py` (Duckduckgo search)
  * `solomon_local_llm.py` (Simulated LLM layer for specific queries)
* `services/`:
  * `solomon_futures_engine.py` (Futures Monte Carlo Engine)
  * `live_data_ingestion.py` (Mock Geopolitical Data Ingestion)
  * `renewable_worker.py` (Background queue worker)
  * `solomon_learning_writeback.py` (Learning interface)
* `backend/`: Future UI integration paths (`futures_dashboard_backend.py`)
* `solomon_api/`: `engine_registry.json` is the sole source of truth for all modules in `services/`, `backend/`, and `scripts/`.
* `tests/`: 23 tests, mostly green after dependencies are fixed.
* `scripts/`: `run_daily_scan.py` (Futures scan generator)
* `gabriel_engine/`: Assorted dynamic loading capabilities.

## 4. PYTHON MODULE INVENTORY
* See SOLOMON_INVENTORY_EVIDENCE/all_python.txt.
* Highlights:
  * `core/solomon_local_llm.py` simulates LLM behavior manually based on string checks, not an actual model loading weights.
  * `services/live_data_ingestion.py` has no actual live API keys; uses the web crawler in simulated mode to generate fake candidates.
  * `app.py` has the Flask entry points.

## 5. MAJOR ENGINE AND SUBSYSTEM INVENTORY
* **Futures Engine** (`services/solomon_futures_engine.py`): VERIFIED PARTIAL. Runs simulations locally, tests run but have bugs on thresholds in current state. Does not connect to live market data (using `live_data_ingestion.py` which falls back to web searches).
* **Solomon Local LLM** (`core/solomon_local_llm.py`): EXPERIMENTAL / MOCK. No model loaded. Pure keyword-based script routing.
* **Gabriel Engine**: VERIFIED PARTIAL. Endpoints exist in `app.py`. Tests pass. Uses code injection and basic evaluation.

## 6. ENTRY POINT INVENTORY
* `app.py`: Main Flask application, binds to 10000.
* `scripts/run_daily_scan.py`: Scheduled job script for Futures scanning.

## 7. RUNNING PROCESS INVENTORY
* Mostly standard bash, no long-running Solomon processes active beside test runs.

## 11. DATABASE INVENTORY
* SQLite databases are primarily transient or created ad-hoc for learning records.

## 13. MODEL AND AI PROVIDER INVENTORY
* OpenAI imported in `app.py` but actual generation handled through `gabriel_loop` and `core/solomon_local_llm.py`. Local LLM uses if/else keyword matching rather than inference.

## 17. TEST INVENTORY
* 23 tests present. Many fail on clean checkout because:
  * `requirements.txt` is missing dependencies (`openai`, `duckduckgo_search`, `pydantic`, `flask`, `sqlalchemy`, `numpy`, `scipy`).
  * `engine_registry.json` fails `test_engine_registry.py` because `services/live_data_ingestion.py` and `services/renewable_worker.py` are unregistered.
  * `tests/futures/test_threshold_logic.py` fails due to test setup bugs and hardcoded thresholds vs probabilistic nature of Monte Carlo.

## 21. SECURITY CONTROL INVENTORY
* Some `exec()` and `eval()` identified in code generation paths (e.g., `CleanRoomBuilder`, test suite).
* No active authentication on the Flask routes.

## 27. DUPLICATION INVENTORY
* Root level `solomon_quantized_memory.py` vs `core/solomon_quantized_memory.py` (Note: core has one, root has one as well!). Root version should probably be deleted as `core/` is the standard.

## 32. CHANGE-RISK INVENTORY
* `engine_registry.json` is highly fragile. Adding new files without registering them breaks tests.
* `solomon_local_llm.py` is hardcoded to tests (if you change string checks, tests fail).

## 35. FINAL EXECUTIVE SUMMARY
* **What Project Solomon actually is today:** A collection of Python scripts orchestrating mock services, some web crawling, and dynamic AST code generation. The system lacks live intelligence, relying heavily on fallback keyword mechanisms.
* **Safe to clean immediately:** Dependency installation in a standard `requirements.txt`. Removal of redundant files.
