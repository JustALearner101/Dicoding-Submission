import unittest
from utils.transform import transform

class TestTransform(unittest.TestCase):
    def test_transform(self):
        sample_data = [{"title": "T-Shirt", "price": "$25"}]
        transformed_data = transform(sample_data)

        self.assertIsInstance(transformed_data, list)
        self.assertEqual(transformed_data[0]["price"], 25)

if __name__ == "__main__":
    unittest.main()
