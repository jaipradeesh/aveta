import unittest
from collections import Counter
from gather_data import weighted_iter, bucket_zip


class TestGatherData(unittest.TestCase):

    test_str = "bbbbddeee"

    def test_weighted_iter(self):
        buckets = sorted(Counter(self.test_str).iteritems(),
                         key=lambda t: t[0])
        expected = list(self.test_str)
        actual = list(weighted_iter(buckets))
        self.assertEqual(actual, expected)

    def test_bucket_zip(self):
        srcs = [
            [1, 1, 2, 3], # source exhausts first
            xrange(100),  # buckets exhaust first
        ]
        for src in srcs:
            buckets = sorted(Counter(self.test_str).iteritems(),
                             key=lambda t: t[0])
            expected = list(zip(self.test_str, src))
            actual = list(bucket_zip(src, buckets))
            self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
