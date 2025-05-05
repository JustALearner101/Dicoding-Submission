import unittest
import os
from utils.load import load

class TestLoad(unittest.TestCase):
    def test_load(self):
        sample_data = [{"title": "T-Shirt", "price": 25}]
        load(sample_data, "test_output.csv")
        
        self.assertTrue(os.path.exists("test_output.csv"))

if __name__ == "__main__":
    unittest.main()
