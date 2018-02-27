from unittest import TestCase
from unittest.mock import Mock, call
from argparse import ArgumentParser
from munch import munchify

from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources.fip import Fip


floating_ips = [
    # THESE ARE ATTACHED, AND SHOULDN'T BE DELETED, BY DEFAULT
    munchify({
        'attached': True,
        'fixed_ip_address': '191.168.1.1',
        'floating_ip_address': '10.0.0.1',
        'id': '1',
        'status': 'ACTIVE'
    }),
    munchify({
        'attached': True,
        'fixed_ip_address': '172.16.0.2',
        'floating_ip_address': '10.0.0.2',
        'id': '2',
        'status': 'ACTIVE'
    }),
    munchify({
        'attached': True,
        'fixed_ip_address': '192.168.10.22',
        'floating_ip_address': '8.9.10.3',
        'id': '3',
        'status': 'ACTIVE'
    }),
    # THESE ARE NOT ATTACHED AND SHOULD BE DELETED, BY DEFAULT
    munchify({
        'attached': False,
        'fixed_ip_address': '192.168.1.20',
        'floating_ip_address': '10.0.0.20',
        'id': '20',
        'status': 'DOWN'
    }),
    munchify({
        'attached': False,
        'fixed_ip_address': '172.16.0.21',
        'floating_ip_address': '10.0.0.21',
        'id': '21',
        'status': 'DOWN'
    }),
    munchify({
        'attached': False,
        'fixed_ip_address': '192.168.10.22',
        'floating_ip_address': '8.9.10.22',
        'id': '22',
        'status': 'DOWN'
    })
]


class TestFip(TestCase):
    def __test_with_calls(self, args, calls):
        shade = Mock()
        shade.list_floating_ips = Mock(return_value=floating_ips)
        shade.delete_floating_ip = Mock()
        calls = [call(i) for i in calls]
        config = CloudCleanerConfig(args=args)
        config.get_shade = Mock(return_value=shade)
        fip = Fip()
        fip.register(config)
        config.parse_args()
        fip.process()
        fip.clean()
        self.assertEqual(shade.delete_floating_ip.call_args_list, calls)

    def test_resource_type(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=["--os-auth-url",
                                                         "http://no.com",
                                                         "fip"])
        config.add_subparser = Mock()
        fip = Fip()
        fip.register(config)
        config.add_subparser.assert_called_once_with(Fip.type_name)

    def test_resource_handled_from_args(self):
        parser = ArgumentParser()
        config = CloudCleanerConfig(parser=parser, args=["--os-auth-url",
                                                         "httpp://no.com",
                                                         Fip.type_name])
        fip = Fip()
        # If config hasn't yet been registered, then there will be an error
        # from within this method, as intended
        with self.assertRaises(AttributeError):
            fip.process()
        fip.register(config)
        config.parse_args()
        self.assertEqual(Fip.type_name, config.get_resource())

    def test_default_filters_active(self):
        args = ["--os-auth-url", "http://no.com", "fip"]
        calls = ['20', '21', '22']
        self.__test_with_calls(args, calls)

    def test_force_delete_attached(self):
        args = ["--os-auth-url", "http://no.com", "fip", "--with-attached"]
        calls = ['1', '2', '3', '20', '21', '22']
        self.__test_with_calls(args, calls)

    def test_delete_by_subnet(self):
        args = ['--os-auth-url', 'http://no.com', 'fip', '--floating-subnet',
                '10.0.0.0/8']
        calls = ['20', '21']
        self.__test_with_calls(args, calls)

    def test_delete_by_static_subnet(self):
        args = ['--os-auth-url', 'http://no.com', 'fip', '--static-subnet',
                '192.168.0.0/16']
        calls = ['20', '22']
        self.__test_with_calls(args, calls)
