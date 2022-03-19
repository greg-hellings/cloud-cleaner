from unittest import TestCase

from cloud_cleaner.resources import ALL_RESOURCES
from cloud_cleaner.resources.fip import Fip
from cloud_cleaner.resources.server import Server


class TestAll(TestCase):
    def test_all_is_right(self):
        self.assertIsInstance(ALL_RESOURCES["server"], Server)
        self.assertIsInstance(ALL_RESOURCES["fip"], Fip)
