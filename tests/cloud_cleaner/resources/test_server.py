from argparse import ArgumentParser

try:
    from unittest.mock import Mock, call
except ImportError:
    from mock import Mock, call

from datetime import datetime

import pytest
from munch import munchify
from pytz import utc

from cloud_cleaner.config import DATE_FORMAT, CloudCleanerConfig
from cloud_cleaner.resources import Server

CURRENT_TIME = datetime.strptime("2018-02-23T16:00:00Z", DATE_FORMAT)
CURRENT_TIME = CURRENT_TIME.replace(tzinfo=utc)
SAMPLE_USER = munchify({"email": None, "name": "test-user"})
SAMPLE_SERVERS = [
    # Server still being built out by OpenStack, should remain
    munchify(
        {
            "id": "1",
            "name": "test-server-1",
            "power_state": 0,
            "status": "BUILD",
            "created": "2018-02-23T16:00:00Z",
            "updated": "2018-02-23T16:05:00Z",
        }
    ),
    # A 3 day old server that should not be deleted (exactly 3d)
    munchify(
        {
            "id": "2",
            "name": "test-server-2",
            "power_state": 1,
            "status": "ACTIVE",
            "created": "2018-02-20T16:00:00Z",
            "updated": "2018-02-28T00:00:00Z",
        }
    ),
    # A much older server that definitely should be deleted
    munchify(
        {
            "id": "3",
            "name": "test-server-3",
            "power_state": 0,
            "status": "ACTIVE",
            "created": "2017-12-31T12:00:00Z",
            "updated": "2018-01-31T12:00:00Z",
        }
    ),
    # An older, errored server that should be deleted in some cases
    munchify(
        {
            "id": "4",
            "name": "server-pet-4",
            "power_state": 1,
            "status": "ERROR",
            "created": "2018-01-31T08:00:00Z",
            "updated": "2018-02-23T12:00:00Z",
        }
    ),
    # A new server that should be deleted (1 second over the 3d threshhold)
    munchify(
        {
            "id": "5",
            "name": "derp-server-5",
            "power_state": 0,
            "status": "ACTIVE",
            "created": "2018-02-20T15:59:59Z",
            "updated": "2018-02-22T04:17:42Z",
        }
    ),
    # A pet server that should remain
    munchify(
        {
            "id": "6",
            "name": "pet-server-6",
            "power_state": 1,
            "status": "ACTIVE",
            "created": "2016-01-01T01:00:00Z",
            "updated": "2018-01-01T02:07:34Z",
        }
    ),
]


@pytest.fixture
def conn(mocker):
    conn = mocker.Mock()
    conn.list_servers = mocker.Mock(return_value=SAMPLE_SERVERS)
    conn.get_user_by_id = mocker.Mock(return_value=SAMPLE_USER)
    conn.delete_server = mocker.Mock()
    return conn


@pytest.fixture
def args():
    return [
        "--os-auth-url",
        "http://no.com",
        "server",
        "--age",
        "3d",
        "--skip-name",
        "test-.*",
    ]


def __test_with_call_order(conn, args, calls):
    config = CloudCleanerConfig(args=args)
    config.get_conn = Mock(return_value=conn)
    calls = [call(c) for c in calls]
    server = Server(now=CURRENT_TIME)
    server.register(config)
    config.parse_args()
    server.prep_deletion()
    server.process()
    server.clean()
    assert conn.delete_server.call_args_list == calls


def test_email_with_calls(conn, args):
    config = CloudCleanerConfig(args=args)
    config.get_conn = Mock(return_value=conn)
    calls = ["4", "5"]
    calls = [call(c) for c in calls]
    server = Server(now=CURRENT_TIME)
    server.send_emails = Mock()
    server.register(config)
    config.parse_args()
    server.process()
    assert len(server.targets) == 2
    server.send_emails()
    assert conn.get_user_by_id.call_count == 2
    server.clean()
    assert conn.delete_server.call_args_list == calls


def test_email_with_delete(conn, args):
    config = CloudCleanerConfig(args=args)
    config.get_conn = Mock(return_value=conn)
    server = Server(now=CURRENT_TIME)
    server.send_emails = Mock()
    server.register(config)
    config.parse_args()
    server.prep_deletion()
    server.process()
    server.clean()
    server.process()
    server.send_emails()
    # Only server 4 should be deleted. As in the test above, servers 4 and
    # 5 fit the criteria, but this time around server 5 should be deleted,
    # and thus not considered for an email warning, whereas for server 4
    # nothing should change.
    assert conn.get_user_by_id.call_count == 1


def test_init_with_name():
    parser = ArgumentParser()
    config = CloudCleanerConfig(parser=parser, args=[])
    config.add_subparser = Mock()
    server = Server()
    server.register(config)
    config.add_subparser.assert_called_once_with(Server.type_name)


def test_parser_with_name():
    args = ["--os-auth-url", "http://no.com", "server", "--name", "test-.*"]
    parser = ArgumentParser()
    config = CloudCleanerConfig(parser=parser, args=args)
    server = Server()
    server.register(config)
    config.parse_args()
    assert "test-.*" == config.get_arg("name")
    assert Server.type_name == config.get_resource()


def test_delete_3_day_old_servers(conn):
    largs = ["--os-auth-url", "http://no.com", "server", "--age", "3d"]
    calls = ["3", "4", "5", "6"]
    __test_with_call_order(conn, largs, calls)


def test_delete_server_by_name(conn):
    largs = ["--os-auth-url", "http://no.com", "server", "--name", "test-.*"]
    calls = ["1", "2", "3"]
    __test_with_call_order(conn, largs, calls)


def test_name_and_age(conn):
    largs = [
        "--os-auth-url",
        "http://no.com",
        "server",
        "--age",
        "3d",
        "--skip-name",
        "pet-.*",
    ]
    calls = ["3", "4", "5"]
    __test_with_call_order(conn, largs, calls)
