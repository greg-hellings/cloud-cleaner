from unittest import TestCase
from unittest.mock import Mock
from argparse import ArgumentParser

from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources.fip import Fip


class TestFip(TestCase):
    def test_resource_type(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=["fip"])
        config.add_subparser = Mock()
        Fip(config)
        config.add_subparser.assert_called_once_with(Fip.type_name)

    def test_resource_handled_from_args(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=[Fip.type_name])
        Fip(config)
        config.parse_args()
        self.assertEqual(Fip.type_name, config.get_resource())
