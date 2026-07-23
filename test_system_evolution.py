"""
Integration and Concurrency Load Tests for Solomon Perpetual Learning Machine System Evolution.
Verifies Review Gate Automation, Model Calibration, Multi-Process Concurrency routing with
thread-locks, Resource monitoring caps, worker transitions, and structured /metrics telemetry.
"""

import os
import json
import sqlite3
import threading
import concurrent.futures
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestSystemEvolution:
    """
    Validates evolution capabilities introduced in SOSS Phase 1 stabilization.
    """

    def test_review_gate_automation_and_revisions(self, client):
        """
        1. Promotes a card status from DRAFT -> APPROVED.
        2. Verifies status changes in SQLite and revisions log.
        """
        card_id = "SOK-TASK-QUANT-001"

        # Initial check - promote status
        payload = {
            "card_id": card_id,
            "status": "APPROVED",
            "content": "Verify that custom initializers are injected safely and execute cleanly."
        }
        response = client.post("/api/mnemosyne/review", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"
        assert data["new_status"] == "APPROVED"
        assert "promoted" in data["message"]

        # Fetch card to check status update in SQLite
        card = db.get_card(card_id)
        assert card["status"] == "APPROVED"
        assert card["content"] == "Verify that custom initializers are injected safely and execute cleanly."

        # Fetch revisions log
        response_rev = client.get(f"/api/mnemosyne/revisions?card_id={card_id}")
        assert response_rev.status_code == 200
        data_rev = response_rev.get_json()
        assert data_rev["status"] == "success"
        assert data_rev["total_revisions"] > 0

        first_rev = data_rev["revisions"][0]
        assert first_rev["card_id"] == card_id
        assert first_rev["status"] == "APPROVED"
        assert first_rev["content"] == "Verify that custom initializers are injected safely and execute cleanly."

    def test_local_model_calibration_compilation_and_simulation(self, client):
        """
        1. Compiles a calibration dataset directly from active SQLite database cards.
        2. Simulates Adaptive Mixed-Precision Bit Allocation (AMPBA).
        """
        # Compile calibration
        response_cal = client.post("/api/command-center/quantization/compile-calibration", json={"status_filter": "ACTIVE"})
        assert response_cal.status_code == 200
        data_cal = response_cal.get_json()
        assert data_cal["status"] == "success"
        assert data_cal["total_cards_compiled"] > 0
        assert "dataset" in data_cal

        # Simulate AMPBA
        payload_ampba = {
            "model_size_params": 7e9,
            "num_layers": 16,
            "target_ram_mb": 3500.0,
            "use_spinquant": True,
            "initial_outliers": 120
        }
        response_sim = client.post("/api/command-center/quantization/simulate-ampba", json=payload_ampba)
        assert response_sim.status_code == 200
        data_sim = response_sim.get_json()
        assert data_sim["status"] == "success"
        assert data_sim["model_metadata"]["num_layers"] == 16
        assert data_sim["hessian_mixed_precision_solver"]["feasible"] is True
        assert len(data_sim["hessian_mixed_precision_solver"]["allocations"]) == 16

    def test_multi_process_concurrency_load_routing(self, client):
        """
        Stress-tests /api/mnemosyne/route under high-concurrency requests to verify
        thread-safe locks prevent database corruption, lock contentions, or crashing.
        """
        concurrency_count = 20
        queries = [
            "How to allocate VRAM on high-throughput model routers?",
            "What are Hessian sensitivity traces rules?",
            "Derive declarative rules for SpinQuant outliers.",
            "Biscuit cookie recipe tutorial instructions.",
            "Run quantization simulation within active execution contexts."
        ]

        def call_routing_endpoint(idx):
            payload = {
                "query": queries[idx % len(queries)],
                "threshold": 0.20
            }
            # Inside thread, we use app.test_client() which is thread-safe
            with app.test_client() as thr_client:
                res = thr_client.post("/api/mnemosyne/route", json=payload)
                return res.status_code, res.get_json()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(call_routing_endpoint, i) for i in range(concurrency_count)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Assert all 20 threads completed with HTTP 200 and success status
        assert len(results) == concurrency_count
        for status_code, data in results:
            assert status_code == 200
            assert data["status"] == "success"
            assert "routing_decision" in data

    def test_resource_monitor_cap_verification(self, client):
        """
        Simulates severe memory pressure events to verify that the Infrastructure
        Resource Monitor intercepts processes exceeding the 1.5GB RAM cap and logs alerts.
        """
        # Exceed cap: 1650 MB > 1536 MB (1.5GB)
        payload = {"simulated_rss_mb": 1650.0}
        response = client.post("/api/quantization/simulate-memory-pressure", json=payload)
        assert response.status_code == 200
        data = response.get_json()
        assert data["status"] == "success"

        audit = data["audit_result"]
        assert audit["status"] == "CRITICAL_OVERLIMIT"
        assert audit["alert_triggered"] is True
        assert audit["active_rss_mb"] == 1650.0
        assert "CRITICAL LIMIT VIOLATION" in audit["message"]

        # Check logs/solomon_telemetry.log contains the warning
        log_filepath = "logs/solomon_telemetry.log"
        assert os.path.exists(log_filepath) is True
        with open(log_filepath, "r") as f:
            logs = f.read()
            assert "CRITICAL LIMIT VIOLATION" in logs

    def test_worker_modes_transitions_verification(self, client):
        """
        Verifies helper worker state query and transition REST APIs.
        """
        # Get worker modes
        response_get = client.get("/api/command-center/worker-modes")
        assert response_get.status_code == 200
        data_get = response_get.get_json()
        assert data_get["status"] == "success"
        assert "Gabriel" in data_get["worker_modes"]

        # Transition Gabriel to READ_WRITE
        payload_trans = {
            "worker_name": "Gabriel",
            "execution_mode": "READ_WRITE"
        }
        response_post = client.post("/api/command-center/worker-modes", json=payload_trans)
        assert response_post.status_code == 200
        data_post = response_post.get_json()
        assert data_post["status"] == "success"
        assert data_post["worker_name"] == "Gabriel"
        assert data_post["new_execution_mode"] == "READ_WRITE"

        # Query database directly to verify persistence
        modes = db.get_worker_modes()
        assert modes["Gabriel"] == "READ_WRITE"

    def test_telemetry_optimization_and_metrics(self, client):
        """
        Verifies /metrics returns SQL latencies and AST injection stats.
        Also runs mock injection to verify counter increments correctly.
        """
        # Fetch initial metrics
        response_init = client.get("/metrics")
        assert response_init.status_code == 200
        data_init = response_init.get_json()
        assert data_init["status"] == "healthy"
        assert "sql_metrics" in data_init
        assert "ast_fusion_statistics" in data_init

        initial_triggers = data_init["ast_fusion_statistics"]["total_injections_triggered"]

        # Run mock AST injection
        payload_ast = {
            "class_name": "ModelRouter",
            "method_name": "mock_evolution_probe",
            "source_code": "def mock_evolution_probe(self):\n    return 'evolution_stabilized'"
        }
        response_inject = client.post("/api/mnemosyne/ast-inject", json=payload_ast)
        assert response_inject.status_code == 200

        # Fetch updated metrics
        response_updated = client.get("/metrics")
        assert response_updated.status_code == 200
        data_updated = response_updated.get_json()

        updated_triggers = data_updated["ast_fusion_statistics"]["total_injections_triggered"]
        assert updated_triggers == initial_triggers + 1
        assert data_updated["ast_fusion_statistics"]["successful_injections"] > 0
