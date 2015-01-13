import os
import unittest


class BaseTestCase(unittest.TestCase):

    """Common stuff for tests."""

    data_dir = os.path.abspath(os.path.join(
        os.path.dirname(os.path.dirname(__file__)), 'examples'))

    def setUp(self):
        self.openfiles = []

    def tearDown(self):
        if self.openfiles:
            for f in self.openfiles:
                f.close()
