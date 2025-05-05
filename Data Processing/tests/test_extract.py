import unittest
from utils.extract import extract

class TestExtract(unittest.TestCase):
    def test_extract(self):
        data = extract()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        self.assertIn("title", data[0])
        self.assertIn("price", data[0])

if __name__ == "__main__":
    unittest.main()
