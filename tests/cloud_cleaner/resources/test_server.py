from unittest import TestCase
from unittest.mock import Mock
from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources import Server


class ServerTest(TestCase):
    def test_init_with_name(self):
        config = CloudCleanerConfig(args=[])
        config.add_subparser = Mock()
        Server(config)
        config.add_subparser.assert_called_once_with(Server.type_name)
