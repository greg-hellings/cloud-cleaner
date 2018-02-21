from unittest import TestCase
from cloud_cleaner.resources import all_resources
from cloud_cleaner.resources.server import Server
from cloud_cleaner.resources.fip import Fip


class TestAll(TestCase):
    all_resources = [
        Server,
        Fip
    ]

    def test_all_is_right(self):
        self.assertEqual(all_resources, TestAll.all_resources)
