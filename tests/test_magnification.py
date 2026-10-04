import unittest
import math
from src.domain.magnification import compute_scale, ease_toward

class TestMagnification(unittest.TestCase):
    def test_scale_at_distance_zero(self):
        scale = compute_scale(0, max_scale=2.0)
        self.assertEqual(scale, 2.0)

    def test_scale_at_large_distance(self):
        scale = compute_scale(1000, max_scale=2.0, radius=100)
        self.assertEqual(scale, 1.0)

    def test_monotonic_decrease(self):
        scale1 = compute_scale(10, max_scale=2.0, radius=100)
        scale2 = compute_scale(20, max_scale=2.0, radius=100)
        self.assertGreater(scale1, scale2)

    def test_easing_converges(self):
        scale = compute_scale(100, max_scale=2.0, radius=100)
        self.assertAlmostEqual(scale, 1.0, places=2)

if __name__ == '__main__':
    unittest.main()
