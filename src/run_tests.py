import unittest

from test.test_oqs_client import TestOQSClient

loader = unittest.TestLoader()
start_dir = 'test'
suite = loader.discover(start_dir)

runner = unittest.TextTestRunner()
runner.run(suite)