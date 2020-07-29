import unittest
import re

def extract_datetime(target_string):
    patterns = [r"(\d\d\d\d)_(\d\d)_(\d\d)",
        r"(\d\d\d\d)-(\d\d)-(\d\d)"
    ]
    year = ""
    month = ""
    day = ""

    for pattern in patterns:
        found = re.findall(pattern, target_string)
        if len(found) <= 0:
            continue
        return found[0][0], found[0][1], found[0][2]
    raise Exception

class TestModule(unittest.TestCase):
    def setUp(self):
        pass

    def test_normal1(self):
        year, month, day = extract_datetime("xodifeoih2020-02-16asfsaf")
        self.assertEqual(year, "2020")
        self.assertEqual(month, "02")
        self.assertEqual(day, "16")

    def test_normal2(self):
        year, month, day = extract_datetime("xodifeoih2020_02_16asfsaf")
        self.assertEqual(year, "2020")
        self.assertEqual(month, "02")
        self.assertEqual(day, "16")

    def test_normal3(self):
        year, month, day = extract_datetime("2020_02_16")
        self.assertEqual(year, "2020")
        self.assertEqual(month, "02")
        self.assertEqual(day, "16")

if __name__ == "__main__":
    a, b, c = extract_datetime("2020_02_16")