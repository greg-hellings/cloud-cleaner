from unittest import TestCase
from unittest.mock import Mock
from argparse import ArgumentParser

from cloud_cleaner.bin.entrypoint import cloud_clean
from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources import all_resources
from cloud_cleaner.resources.server import Server


class TestEntrypoint(TestCase):
    def test_cloud_cleaner_noopts(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=[])
        cloud_clean([], config)
        self.assertIsNone(config.get_resource())

    def test_cloud_cleaner_server(self):
        config = CloudCleanerConfig(args=[])
        cloud_clean(args=["server", "--name", "derp"], config=config)
        self.assertEqual("server", config.get_resource())
        self.assertEqual("derp", config.get_arg("name"))