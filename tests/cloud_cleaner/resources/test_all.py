from unittest import TestCase
from cloud_cleaner.resources import all_resources
from cloud_cleaner.resources.server import Server
from cloud_cleaner.resources.fip import Fip


class TestAll(TestCase):
    def test_all_is_right(self):
        self.assertIsInstance(all_resources["server"], Server)
        self.assertIsInstance(all_resources["fip"], Fip)
