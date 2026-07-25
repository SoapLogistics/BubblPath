import unittest
from solomon_ultra_efficiency_toolkit import SolomonUltraEfficiencyToolkit

class TestUltraToolkit(unittest.TestCase):
    def test_fast_integer_sqrt(self):
        self.assertEqual(SolomonUltraEfficiencyToolkit.fast_integer_sqrt(144), 12)
        self.assertEqual(SolomonUltraEfficiencyToolkit.fast_integer_sqrt(145), 12) # Truncates

    def test_date_packing(self):
        y, m, d = 2023, 10, 25
        packed = SolomonUltraEfficiencyToolkit.pack_date_to_int(y, m, d)
        unpacked_y, unpacked_m, unpacked_d = SolomonUltraEfficiencyToolkit.unpack_int_to_date(packed)
        self.assertEqual(y, unpacked_y)
        self.assertEqual(m, unpacked_m)
        self.assertEqual(d, unpacked_d)

    def test_kadane(self):
        arr = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
        self.assertEqual(SolomonUltraEfficiencyToolkit.kadane_max_subarray_sum(arr), 6)

    def test_moores_voting(self):
        arr = [2, 2, 1, 1, 1, 2, 2]
        self.assertEqual(SolomonUltraEfficiencyToolkit.moores_voting_majority(arr), 2)

    def test_1bit_tensor_packing(self):
        tensor = [1.5, -0.5, 2.0, -1.0, 0.5, 3.0, -2.0, 1.0, -0.1]
        binarized = SolomonUltraEfficiencyToolkit.binarize_tensor(tensor)
        packed = SolomonUltraEfficiencyToolkit.pack_1bit_tensor(binarized)
        unpacked = SolomonUltraEfficiencyToolkit.unpack_1bit_tensor(packed, len(tensor))
        self.assertEqual(binarized, unpacked)

    def test_radix_sort(self):
        arr = [170, 45, 75, 90, 802, 24, 2, 66]
        sorted_arr = SolomonUltraEfficiencyToolkit.radix_sort_base10(arr)
        self.assertEqual(sorted_arr, sorted(arr))

if __name__ == '__main__':
    unittest.main()
