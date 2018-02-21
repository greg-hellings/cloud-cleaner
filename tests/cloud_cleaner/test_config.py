from unittest import TestCase
from cloud_cleaner.config import CloudCleanerConfig


class TestConfig(TestCase):
    def test_add_subcommand(self):
        magic_name = "test_resource"
        magic_value = "bar"
        config = CloudCleanerConfig(args=[])
        test_parser = config.add_subparser(magic_name)
        config.set_args([magic_name, "--foo", magic_value])
        results
