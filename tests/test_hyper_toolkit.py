import unittest
from solomon_hyper_efficiency_toolkit import SolomonHyperEfficiencyToolkit

class TestHyperToolkit(unittest.TestCase):
    def test_power_of_two(self):
        self.assertTrue(SolomonHyperEfficiencyToolkit.check_power_of_two(1024))
        self.assertFalse(SolomonHyperEfficiencyToolkit.check_power_of_two(1023))
        self.assertEqual(SolomonHyperEfficiencyToolkit.next_power_of_two(1000), 1024)

    def test_ip_packing(self):
        ip = "192.168.1.1"
        packed = SolomonHyperEfficiencyToolkit.pack_ip_to_int(ip)
        unpacked = SolomonHyperEfficiencyToolkit.unpack_int_to_ip(packed)
        self.assertEqual(ip, unpacked)

    def test_gray_code(self):
        n = 42
        encoded = SolomonHyperEfficiencyToolkit.gray_code_encode(n)
        decoded = SolomonHyperEfficiencyToolkit.gray_code_decode(encoded)
        self.assertEqual(n, decoded)

    def test_zigzag_encoding(self):
        # tests signed int mapping
        n = -5
        encoded = SolomonHyperEfficiencyToolkit.zigzag_encode(n)
        decoded = SolomonHyperEfficiencyToolkit.zigzag_decode(encoded)
        self.assertEqual(n, decoded)

    def test_float32_reconstruction(self):
        val = -12.5
        s = SolomonHyperEfficiencyToolkit.extract_sign_bit(val)
        e = SolomonHyperEfficiencyToolkit.extract_exponent_bits(val)
        m = SolomonHyperEfficiencyToolkit.extract_mantissa_bits(val)
        reconstructed = SolomonHyperEfficiencyToolkit.build_custom_float32(s, e, m)
        self.assertEqual(val, reconstructed)

    def test_count_min_sketch(self):
        sketch = SolomonHyperEfficiencyToolkit.count_min_sketch_init(100, 3)
        SolomonHyperEfficiencyToolkit.count_min_sketch_add(sketch, "apple")
        SolomonHyperEfficiencyToolkit.count_min_sketch_add(sketch, "apple")
        count = SolomonHyperEfficiencyToolkit.count_min_sketch_estimate(sketch, "apple")
        self.assertEqual(count, 2)
        count_zero = SolomonHyperEfficiencyToolkit.count_min_sketch_estimate(sketch, "banana")
        self.assertEqual(count_zero, 0)

if __name__ == '__main__':
    unittest.main()
