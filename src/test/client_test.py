import eel
import unittest

from src.client.oqs_client import OQSClient

oqs_client = OQSClient(name="Robin", eel=eel)

class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_something_else(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
