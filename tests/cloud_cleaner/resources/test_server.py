from unittest import TestCase
from unittest.mock import Mock, call
from cloud_cleaner.config import CloudCleanerConfig, date_format
from cloud_cleaner.resources import Server
from argparse import ArgumentParser
from munch import munchify
from datetime import datetime, timezone


current_time = datetime.strptime('2018-02-23T16:00:00Z', date_format)
current_time = current_time.replace(tzinfo=timezone.utc)
sample_servers = [
    # Server still being built out by OpenStack, should remain
    munchify({
        'id':  '1',
        'name': 'test-server-1',
        'power_state': 0,
        'status': 'BUILD',
        'created': '2018-02-23T16:00:00Z',
        'updated': '2018-02-23T16:05:00Z'
    }),
    # A 3 day old server that should not be deleted (exactly 3d)
    munchify({
        'id': '2',
        'name': 'test-server-2',
        'power_state': 1,
        'status': 'ACTIVE',
        'created': '2018-02-20T16:00:00Z',
        'updated': '2018-02-28T00:00:00Z'
    }),
    # A much older server that definitely should be deleted
    munchify({
        'id': '3',
        'name': 'test-server-3',
        'power_state': 0,
        'status': 'ACTIVE',
        'created': '2017-12-31T12:00:00Z',
        'updated': '2018-01-31T12:00:00Z'
    }),
    # An older, errored server that should be deleted in some cases
    munchify({
        'id': '4',
        'name': 'server-pet-4',
        'power_state': 1,
        'status': 'ERROR',
        'created': '2018-01-31T08:00:00Z',
        'updated': '2018-02-23T12:00:00Z'
    }),
    # A new server that should be deleted (1 second over the 3d threshhold)
    munchify({
        'id': '5',
        'name': 'derp-server-5',
        'power_state': 0,
        'status': 'ACTIVE',
        'created': '2018-02-20T15:59:59Z',
        'updated': '2018-02-22T04:17:42Z'
    }),
    # A pet server that should remain
    munchify({
        'id': '6',
        'name': 'pet-server-6',
        'power_state': 1,
        'status': 'ACTIVE',
        'created': '2016-01-01T01:00:00Z',
        'updated': '2018-01-01T02:07:34Z',
    })
]
# setup mocks
shade = Mock()
shade.list_servers = Mock(return_value=sample_servers)
shade.delete_server = Mock()


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
                                    args=["--os-auth-url", "http://no.com",
                                          "server", "--name", "test-.*"])
        server = Server()
        server.register(config)
        config.parse_args()
        self.assertEqual("test-.*", config.get_arg("name"))
        self.assertEqual(Server.type_name, config.get_resource())

    def test_delete_3_day_old_servers(self):
        config = CloudCleanerConfig(args=["--os-auth-url", "http://no.com",
                                          "server", "--age", "3d"])
        config.get_shade = Mock(return_value=shade)
        calls = [call('3'), call('4'), call('5'), call('6')]
        server = Server(now=current_time)
        server.register(config)
        config.parse_args()
        server.process()
        server.clean()
        shade.delete_server.assert_has_calls(calls, any_order=True)
