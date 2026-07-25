import unittest
from solomon_bleeding_edge_toolkit import SolomonBleedingEdgeToolkit

class TestBleedingEdgeToolkit(unittest.TestCase):
    def test_flash_attention_tiling(self):
        Bc, Br = SolomonBleedingEdgeToolkit.concept1_flash_attention_tiling(q_len=2048, k_len=2048, sram_size=65536)
        self.assertTrue(Bc > 0 and Br > 0)
        self.assertTrue(Bc <= 2048)
        self.assertTrue(Br <= 128) # Head dim constraint

    def test_moe_sparse_routing(self):
        inputs = [0.1, 0.5, -0.2, 0.8]
        top_experts = SolomonBleedingEdgeToolkit.concept2_moe_sparse_routing(inputs, num_experts=8, top_k=2)
        self.assertEqual(len(top_experts), 2)
        # Probabilities should sum to 1
        self.assertAlmostEqual(sum(prob for _, prob in top_experts), 1.0)

    def test_kan_b_spline(self):
        knots = [0.0, 1.0, 2.0, 3.0, 4.0]
        # Just verifying it executes without mathematical errors
        result = SolomonBleedingEdgeToolkit.concept4_kan_b_spline(1.5, knots, degree=2)
        self.assertTrue(isinstance(result, float))

    def test_quantum_simulated_annealing(self):
        # Should always accept lower energy
        self.assertTrue(SolomonBleedingEdgeToolkit.concept5_quantum_simulated_annealing(100.0, 50.0, 10.0))
        # At zero temp, should reject higher energy
        self.assertFalse(SolomonBleedingEdgeToolkit.concept5_quantum_simulated_annealing(50.0, 100.0, 0.0))

    def test_radix_tree_routing(self):
        trie = {
            "children": {
                "/api/v1/": {
                    "is_leaf": True,
                    "children": {}
                }
            }
        }
        self.assertTrue(SolomonBleedingEdgeToolkit.process2_radix_http_prefix_match("/api/v1/", trie))
        self.assertFalse(SolomonBleedingEdgeToolkit.process2_radix_http_prefix_match("/api/v2/", trie))

if __name__ == '__main__':
    unittest.main()
