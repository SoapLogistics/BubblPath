#!/usr/bin/env python3
"""
Solomon Performance & Resource Profiling Tool.
Measures and prints startup times, mock request latencies, and database search queries with microsecond precision.
"""

import time
import sys
import os
import sqlite3
import random

# Ensure PYTHONPATH contains current directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def profile_startup():
    print("⏱️  Profiling Subsystem Startups...")

    # 1. Measure database connection time
    start = time.perf_counter()
    db_path = "solomon_hyper_memory.db"
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.close()
    db_time_ms = (time.perf_counter() - start) * 1000
    print(f"   - Database Initialization Time: {db_time_ms:.3f} ms")

    # 2. Measure BrainMap / Memory instantiation
    start = time.perf_counter()
    try:
        from core.solomon_quantized_memory import QuantizedBrainMap
        brain = QuantizedBrainMap()
        brain_time_ms = (time.perf_counter() - start) * 1000
        print(f"   - Quantized Brain Map Initialization: {brain_time_ms:.3f} ms")
    except Exception as e:
        print(f"   - Quantized Brain Map Initialization: ❌ Failed ({e})")
        brain_time_ms = 0.0

    return db_time_ms, brain_time_ms

def profile_queries():
    print("\n⏱️  Profiling Database Queries & Search Retrieval...")
    try:
        from core.solomon_quantized_memory import QuantizedBrainMap
        brain = QuantizedBrainMap()

        # Insert a few dummy nodes if empty
        stats = brain.get_stats()
        if stats.get("total_nodes", 0) == 0:
            brain.ingest(node_type="factual", content="The capital of France is Paris.", importance=0.9)
            brain.ingest(node_type="factual", content="Water boils at 100 degrees Celsius.", importance=0.8)
            brain.ingest(node_type="factual", content="Quantum computing uses qubits instead of bits.", importance=0.95)

        # Measure retrieval latency
        queries = ["Paris", "Water", "Quantum", "Nonexistent term to test miss latency"]
        total_time_ms = 0.0

        for q in queries:
            start = time.perf_counter()
            results = brain.recall(q, top_k=3)
            lat_ms = (time.perf_counter() - start) * 1000
            total_time_ms += lat_ms
            print(f"   - Query '{q}' Retrieval Latency: {lat_ms:.3f} ms (Matches: {len(results)})")

        avg_lat_ms = total_time_ms / len(queries)
        print(f"   - Average Retrieval Latency: {avg_lat_ms:.3f} ms")
        return avg_lat_ms
    except Exception as e:
        print(f"   - Retrieval profiling failed: {e}")
        return 0.0

def main():
    print("====================================================")
    print("🌟  Solomon Performance Maintenance & Profiler  🌟")
    print("====================================================")

    db_time, brain_time = profile_startup()
    avg_query_time = profile_queries()

    print("\n========================= SUMMARY =========================")
    print(f"  🏎️  DB Startup Latency:        {db_time:.3f} ms")
    print(f"  🧠  Brain Map Start Latency:   {brain_time:.3f} ms")
    print(f"  🔍  Avg Retrieval Latency:     {avg_query_time:.3f} ms")
    print("===========================================================")

if __name__ == "__main__":
    main()
