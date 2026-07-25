import unittest
from solomon_cutting_edge_toolkit import SolomonCuttingEdgeToolkit

class TestCuttingEdgeToolkit(unittest.TestCase):
    def test_paged_attention_allocator(self):
        pool = SolomonCuttingEdgeToolkit.concept1_paged_attention_allocator(4096, 10)
        self.assertEqual(len(pool["free_blocks"]), 10)

        # Test writing data directly into the pool (zero GC logic)
        success = SolomonCuttingEdgeToolkit.opt1_zero_gc_page_allocation(pool, "req_1", b"test data payload")
        self.assertTrue(success)
        self.assertEqual(len(pool["free_blocks"]), 9)
        self.assertIn("req_1", pool["logical_to_physical"])

    def test_speculative_ngram_cache(self):
        history = "how are you today i am fine how are you doing"
        cache = SolomonCuttingEdgeToolkit.concept2_speculative_decoding_ngram(history, 3)
        self.assertIn(("how", "are"), cache)
        self.assertEqual(cache[("how", "are")]["you"], 2)

    def test_bitnet_xnor_gemm(self):
        # Two packed bit arrays
        a = bytearray([0b10101010])
        b = bytearray([0b11001100])
        # xnor: ~(10101010 ^ 11001100) = ~(01100110) = 10011001 -> 4 set bits
        dot = SolomonCuttingEdgeToolkit.concept3_bitnet_xnor_gemm(a, b, 8)
        self.assertEqual(dot, 4)

    def test_ring_attention_pointers(self):
        buffers = [bytearray(b"A"), bytearray(b"B"), bytearray(b"C")]
        SolomonCuttingEdgeToolkit.opt4_zero_copy_ring_shift(buffers)
        self.assertEqual(buffers[0], bytearray(b"C"))
        self.assertEqual(buffers[1], bytearray(b"A"))
        self.assertEqual(buffers[2], bytearray(b"B"))

if __name__ == '__main__':
    unittest.main()
