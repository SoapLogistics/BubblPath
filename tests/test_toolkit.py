import unittest
from solomon_efficiency_toolkit import SolomonEfficiencyToolkit

class TestToolkit(unittest.TestCase):
    def test_quantization_int8(self):
        tensor = [1.0, -2.0, 3.0, 4.0]
        q, scale, zp = SolomonEfficiencyToolkit.quantize_float_to_int8(tensor)
        self.assertTrue(all(0 <= x <= 255 for x in q))
        deq = SolomonEfficiencyToolkit.dequantize_int8_to_float(q, scale, zp)
        self.assertTrue(abs(deq[0] - 1.0) < 0.1)

    def test_rle(self):
        data = [1, 1, 1, 2, 2, 3]
        rle = SolomonEfficiencyToolkit.run_length_encode(data)
        self.assertEqual(rle, [3, 1, 2, 2, 1, 3])

    def test_fast_cosine(self):
        v1 = [1.0, 0.0]
        v2 = [1.0, 0.0]
        v3 = [0.0, 1.0]
        self.assertEqual(SolomonEfficiencyToolkit.fast_cosine_similarity(v1, v2), 1.0)
        self.assertEqual(SolomonEfficiencyToolkit.fast_cosine_similarity(v1, v3), 0.0)

if __name__ == '__main__':
    unittest.main()
