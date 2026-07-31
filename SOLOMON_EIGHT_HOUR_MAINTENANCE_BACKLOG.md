# Maintenance Backlog
1. Consolidate `requirements.txt` to include missing libraries (`openai`, `duckduckgo_search`, `pydantic`, `flask`, `sqlalchemy`, `numpy`, `scipy`).
2. Remove root-level `solomon_quantized_memory.py` after ensuring `/core` acts as single source.
3. Fix test failures related to `engine_registry.json` constraints for background queue workers.
4. Replace `datetime.utcnow()` with timezone-aware `datetime.now(datetime.UTC)` across the repo to remove warnings.
5. Standardize `engine_registry.json` validation via CI hooks rather than failing unit tests mid-run, or register the newly created components.
