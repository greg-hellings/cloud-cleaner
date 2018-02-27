from unittest import TestCase
from unittest.mock import Mock
from argparse import ArgumentParser

from cloud_cleaner.bin.entrypoint import cloud_clean
from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources import all_resources


class TestEntrypoint(TestCase):
    def test_cloud_cleaner_noopts(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=[])
        with self.assertRaises(KeyError):
            cloud_clean(["--os-auth-url", "http://no.com"], config)
        self.assertIsNone(config.get_resource())

    def test_cloud_cleaner_server(self):
        config = CloudCleanerConfig(args=[])
        all_resources["server"].process = Mock()
        all_resources["server"].clean = Mock()
        cloud_clean(args=["--os-auth-url", "http://no.com", "server",
                          "--name", "derp"], config=config)
        self.assertEqual("server", config.get_resource())
        self.assertEqual("derp", config.get_arg("name"))
        self.assertEqual(1, len(all_resources["server"].process.mock_calls))
        self.assertEqual(0, len(all_resources["server"].clean.mock_calls))

    def test_resource_type(self):
        all_resources["server"].process = Mock()
        all_resources["server"].clean = Mock()
        cloud_clean(args=["--os-auth-url", "http://no.com", "-f", "server"])
        self.assertEqual(1, len(all_resources["server"].process.mock_calls))
        self.assertEqual(1, len(all_resources["server"].clean.mock_calls))
