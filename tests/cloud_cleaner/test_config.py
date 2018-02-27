from unittest import TestCase
from cloud_cleaner.config import CloudCleanerConfig
from argparse import ArgumentParser
from logging import getLogger, WARNING, INFO, DEBUG


class TestConfig(TestCase):
    def test_set_args(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=[])
        config.add_subparser("item")
        config.set_args(["--os-auth-url", "http://no.com", "item"])
        config.parse_args()
        self.assertEqual("item", config.get_resource())
        log = getLogger("cloud_cleaner")
        self.assertEqual(log.getEffectiveLevel(), WARNING)

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

    def test_verbose_one(self):
        args = ["--os-auth-url", "http://no.com", "-v"]
        config = CloudCleanerConfig(args=args)
        config.parse_args()
        log = getLogger("cloud_cleaner")
        self.assertEqual(log.getEffectiveLevel(), INFO)

    def test_verbose_two(self):
        args = ["--os-auth-url", "http://no.com", "-vv"]
        config = CloudCleanerConfig(args=args)
        config.parse_args()
        log = getLogger("cloud_cleaner")
        self.assertEqual(log.getEffectiveLevel(), DEBUG)
