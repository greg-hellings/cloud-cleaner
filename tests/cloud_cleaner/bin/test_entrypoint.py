from sys import version_info
from unittest import TestCase
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock
from argparse import ArgumentParser
from keystoneauth1.exceptions import MissingRequiredOptions
from cloud_cleaner.bin.entrypoint import cloud_clean
from cloud_cleaner import config as config_module
from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources import ALL_RESOURCES


class TestEntrypoint(TestCase):
    def test_cloud_cleaner_noopts(self):
        parser = ArgumentParser()
        config_module.DEFAULT_ARGUMENTS = []
        config = CloudCleanerConfig(parser=parser)
        if version_info.major == 3:
            # Raised because no resource
            with self.assertRaises(MissingRequiredOptions):
                cloud_clean([], config)
        else:
            with self.assertRaises(SystemExit):
                cloud_clean([], config)
        self.assertIsNone(config.get_resource())

    def test_cloud_cleaner_server(self):
        config = CloudCleanerConfig(args=[])
        ALL_RESOURCES["server"].process = Mock()
        ALL_RESOURCES["server"].clean = Mock()
        cloud_clean(args=["--os-auth-url", "http://no.com", "server",
                          "--name", "derp"], config=config)
        self.assertEqual("server", config.get_resource())
        self.assertEqual("derp", config.get_arg("name"))
        self.assertEqual(1, len(ALL_RESOURCES["server"].process.mock_calls))
        self.assertEqual(0, len(ALL_RESOURCES["server"].clean.mock_calls))

    def test_resource_type(self):
        ALL_RESOURCES["server"].process = Mock()
        ALL_RESOURCES["server"].clean = Mock()
        cloud_clean(args=["--os-auth-url", "http://no.com", "-f", "server"])
        self.assertEqual(1, len(ALL_RESOURCES["server"].process.mock_calls))
        self.assertEqual(1, len(ALL_RESOURCES["server"].clean.mock_calls))
