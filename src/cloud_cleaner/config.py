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
        # Defined after options are parsed
        self.__options = None
        self.__cloud = None

    def add_subparser(self, name: str) -> _SubParsersAction:
        """
        Creates a subparser to match the name given by the user.
        Returns it to caller

        :param name: Name of the subparser to create
        :return: The subparser object
        """
        sub_parser = self.__sub_parsers.add_parser(name)
        self.__sub_parser_set[name] = sub_parser
        return sub_parser

    def set_args(self, args: list):
        """
        Sets args for the current execution, in case there are any args that
        might have been altered or removed from the set by the first call

        :param args: The list of args to parse
        :return: this object
        """
        self.__args = args
        return self

    def parse_args(self) -> ArgumentParser:
        """
        Parse all arguments currently attached to this config object

        :return: Parsed arguments
        """
        results = self.__parser.parse_args(self.__args)
        self.__options = vars(results)
        try:
            self.__cloud = self.__cloud_config.get_one_cloud(argparse=self.__options)
        except:
            # No cloud was specified on the command line
            self.__cloud = None
        return results

    def get_arg(self, name: str) -> any:
        """
        Fetch the value of one of the command line arguments from the argparser

        :param name: The command line argument that is requested
        :return: The value of the name requested from
        """
        return self.__options[name]

    def get_resource(self) -> str:
        """
        Get the name of the resource that is being requested

        :return: The string name of the resource selected from the command line
        """
        return self.__options['resource']

    def get_cloud(self):
        """
        Get the cloud that was specified by the command line options. Note that
        this should only be called after #parse_args is called, otherwise it
        will only return None.

        :return: Cloud option parsed, or None
        """
        return self.__cloud