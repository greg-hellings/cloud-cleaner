from unittest import TestCase
from unittest.mock import Mock
from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources import Server
from argparse import ArgumentParser


class ServerTest(TestCase):
    def test_init_with_name(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=[])
        config.add_subparser = Mock()
        server = Server()
        server.register(config)
        config.add_subparser.assert_called_once_with(Server.type_name)

    def test_parser_with_name(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser,
                                    args=["server", "--name", "test-.*"])
        server = Server()
        server.register(config)
        config.parse_args()
        self.assertEqual("test-.*", config.get_arg("name"))
        self.assertEqual(Server.type_name, config.get_resource())
