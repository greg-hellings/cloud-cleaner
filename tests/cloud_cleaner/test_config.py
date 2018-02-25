from unittest import TestCase
from cloud_cleaner.config import CloudCleanerConfig
from argparse import ArgumentParser


class TestConfig(TestCase):
    def test_set_args(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=[])
        config.add_subparser("item")
        config.set_args(["--os-auth-url", "http://no.com", "item"])
        config.parse_args()
        self.assertEqual("item", config.get_resource())

    def test_subcommand_incorrect(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=["notfound"])
        config.add_subparser("found")
        # ArgumentError raises SystemExit internally, apparently
        with self.assertRaises(SystemExit):
            config.parse_args()

    def test_get_cloud_is_none(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=[])
        self.assertIsNone(config.get_cloud())
