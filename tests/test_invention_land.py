import unittest
from solomon_invention_land import (
    PagedRingMemoryCone,
    SpeculativeRadixCone,
    QuantumMoERouterCone,
    SolomonInventionEngine
)

class TestInventionLand(unittest.TestCase):
    def test_paged_ring_memory(self):
        memory_cone = PagedRingMemoryCone(block_size=10, num_blocks=5)
        # Should push to ring
        self.assertTrue(memory_cone.push_chunk_to_ring(b"1234567890"))
        self.assertEqual(len(memory_cone.ring_pointers), 1)

        # Fill the remaining blocks
        for _ in range(4):
            self.assertTrue(memory_cone.push_chunk_to_ring(b"A"))

        # OOM check
        self.assertFalse(memory_cone.push_chunk_to_ring(b"B"))

        # Test shift topology
        original_last = memory_cone.ring_pointers[-1]
        memory_cone.shift_ring_pointers()
        self.assertEqual(memory_cone.ring_pointers[0], original_last)

        # Test free
        memory_cone.free_oldest_ring()
        self.assertEqual(len(memory_cone.ring_pointers), 4)
        self.assertEqual(len(memory_cone.free_stack), 1)

    def test_speculative_radix(self):
        cone = SpeculativeRadixCone()
        cone.train_success("what is your name", "my name is solomon")
        # Ensure drafting hits the ngram
        draft = cone.record_and_draft("what is your name")
        # We trained it 1 time, threshold is > 5 for a draft, so should return ""
        self.assertEqual(draft, "")

        for _ in range(6):
            cone.train_success("what is your name", "my name is solomon")

        draft2 = cone.record_and_draft("what is your name")
        self.assertEqual(draft2, "my name is solomon"[:50])

    def test_quantum_moe_router(self):
        router = QuantumMoERouterCone()

        # Short / low entropy -> hash
        self.assertEqual(router.route_request("hi"), "hash")

        # Medium length -> ngram
        ngram_prompt = "hello how are you doing today my friend"
        self.assertEqual(router.route_request(ngram_prompt), "ngram")

        # Test spline backoff evaluation
        backoff = router.calculate_spline_backoff(retry_count=5)
        self.assertTrue(backoff > 0)

        # Test simulated annealing (accepts lower latency)
        w = router.anneal_worker_count(current_workers=50, latency=100.0, step=1)
        self.assertIn(w, [49, 51])

    def test_invention_engine_integration(self):
        engine = SolomonInventionEngine()
        success = engine.ingest_http_request(b"test payload")
        self.assertTrue(success)

        draft, route = engine.process_prompt("this is a test prompt")
        self.assertEqual(route, "ngram")
        self.assertEqual(draft, "")

        engine.register_success("this is a test prompt", "hello world")
        self.assertEqual(engine.system_step, 1)

if __name__ == '__main__':
    unittest.main()
