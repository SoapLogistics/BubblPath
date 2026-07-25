import unittest
import math
from solomon_extreme_efficiency_toolkit import SolomonExtremeEfficiencyToolkit

class TestExtremeToolkit(unittest.TestCase):

    def test_fast_inverse_square_root(self):
        # The fast inverse square root gives an approximation
        number = 16.0
        exact = 1.0 / math.sqrt(number)
        approx = SolomonExtremeEfficiencyToolkit.fast_inverse_square_root(number)
        self.assertTrue(abs(exact - approx) < 0.05) # Within 5% error margin

    def test_varint_packing(self):
        val = 300
        packed = SolomonExtremeEfficiencyToolkit.pack_varint(val)
        unpacked, read = SolomonExtremeEfficiencyToolkit.unpack_varint(packed)
        self.assertEqual(val, unpacked)
        self.assertEqual(read, 2)

    def test_morton_encoding(self):
        x, y = 5, 9
        encoded = SolomonExtremeEfficiencyToolkit.morton_encode_2d(x, y)
        decoded_x, decoded_y = SolomonExtremeEfficiencyToolkit.morton_decode_2d(encoded)
        self.assertEqual(x, decoded_x)
        self.assertEqual(y, decoded_y)

    def test_boolean_packing(self):
        bools = [True, False, True, True, False, False, False, True, True]
        packed = SolomonExtremeEfficiencyToolkit.pack_boolean_list(bools)
        unpacked = SolomonExtremeEfficiencyToolkit.unpack_boolean_list(packed, len(bools))
        self.assertEqual(bools, unpacked)

    def test_sliding_window_truncate(self):
        text = "abcdefghij"
        truncated = SolomonExtremeEfficiencyToolkit.sliding_window_truncate(text, 5)
        self.assertEqual(truncated, "fghij")

if __name__ == '__main__':
    unittest.main()
