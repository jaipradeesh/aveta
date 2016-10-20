import unittest
import sys

sys.path.append("..")

from motion import clamp_speed, equalize_speeds, MotionController

class TestMotionController(unittest.TestCase):
    def test_clamp_speed(self):
        self.assertEqual(clamp_speed(0), 0)
        self.assertEqual(clamp_speed(-255), -255)
        self.assertEqual(clamp_speed(255), 255)
        self.assertEqual(clamp_speed(-256), -255)
        self.assertEqual(clamp_speed(256), 255)
        self.assertEqual(clamp_speed(-1000), -255)
        self.assertEqual(clamp_speed(1000), 255)
    
    def test_equalize_speeds(self):
        cases = (
            ((12, 14), (13, 13)),
            ((42, 42), (42, 42)),
            ((-50, 12), (-19, -19)),
        )
        for (x1, y1), (x2, y2) in cases:
            self.assertEqual(equalize_speeds(x1, y1),
                             (x2, y2))


if __name__ == '__main__':
    unittest.main()
