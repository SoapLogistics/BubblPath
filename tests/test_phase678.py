import pytest
from solomon_core.soss.ast_injector import ASTInjector
from solomon_memory.graph.engine import MnemosyneEngine
from solomon_memory.db_manager import DatabaseManager
from solomon_core.efficiency.quantization import QuantizationOptimizer, EfficiencyMetrics
import os

def test_ast_injector(tmp_path):
    # Setup dummy script
    script_path = tmp_path / "dummy.py"
    script_path.write_text("def target_func():\n    return 'old'\n")

    new_code = "def target_func():\n    return 'new'\n"

    # Inject
    success = ASTInjector.inject_and_reload(str(script_path), "target_func", new_code)
    assert success is True

    # Verify file change
    content = script_path.read_text()
    assert "return 'new'" in content
    assert "return 'old'" not in content

def test_mnemosyne_semantic_search():
    # Setup isolated DB for test
    db = DatabaseManager(":memory:")
    # Reset thread local connection to force new in-memory DB
    if hasattr(db.local, "connection"):
        del db.local.connection
        # Re-initialize schema for new memory DB
        db._initialize_schema()

    engine = MnemosyneEngine(db)

    # Vectors (simplified to 2D for test)
    # v1 and v3 are similar (pointing same direction)
    v1 = [1.0, 0.0]
    v2 = [0.0, 1.0] # orthogonal
    v3 = [0.9, 0.1]

    engine.store_memory("semantic", "fact A", v1)
    engine.store_memory("semantic", "fact B", v2)
    engine.store_memory("episodic", "fact C", v3)

    # Search for something similar to v1
    results = engine.semantic_search([1.0, 0.0], top_k=2)
    assert len(results) == 2
    assert results[0]['content'] == "fact A" # sim 1.0
    assert results[1]['content'] == "fact C" # sim ~0.99

    # Filter by layer
    results_filtered = engine.semantic_search([1.0, 0.0], layer="episodic")
    assert len(results_filtered) == 1
    assert results_filtered[0]['content'] == "fact C"

def test_quantization_optimizer():
    opt = QuantizationOptimizer()

    m1 = EfficiencyMetrics()
    m1.tokens_used = 1000
    opt.record_task_cost("research", m1, True)

    m2 = EfficiencyMetrics()
    m2.tokens_used = 250
    opt.record_task_cost("research", m2, True)

    # Cost went from 1000 -> 250, LROI is 4.0
    assert opt.calculate_lroi("research") == 4.0
