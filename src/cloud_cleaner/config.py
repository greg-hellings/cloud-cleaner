from argparse import ArgumentParser, _SubParsersAction

import os_client_config
import sys


class CloudCleanerConfig(object):
    def __init__(self,
                 parser: ArgumentParser=ArgumentParser(),
                 args: list=sys.argv):
        self.__cloud_config = os_client_config.OpenStackConfig()
        self.__cloud_config.register_argparse_arguments(parser, args)
        self.__parser = parser
        self.__sub_parsers = self.__parser.add_subparsers(dest="resource")
        self.__sub_parser_set = {}
        self.__args = args

    def add_subparser(self, name: str) -> _SubParsersAction:
        """
        Creates a subparser to match the name given by the user.
        Returns it to caller

        :param name: Name of the subparser to create
        :return: The subparser object
        """
        sub_parser = self.__sub_parsers.add_parser(name)
        self.__sub_parser_set[name] = sub_parser

    def set_args(self, args: list) -> CloudCleanerConfig:
        """
        Sets args for the current execution, in case there are any args that
        might have been altered or removed from the set by the first call

        :param args: The list of args to parse
        :return: this object
        """
        self.__args = args
        return self

    def parse_arguments(self) -> ArgumentParser:
        """
        Parse all arguments currently attached to this config object

        :return: Parsed arguments
        """
        return self.__parser.parse_args(self.__args)