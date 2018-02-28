"""
Contains CloudCleanerConfig for configuring the CLI options in this program
"""
import logging
import sys
from argparse import ArgumentParser
import os_client_config
from shade import OpenStackCloud


DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
DEFAULT_ARGUMENTS = sys.argv


class CloudCleanerConfig(object):  # pylint: disable=R0902
    """
    Contains config options for the entirety of this program, handles setting
    and parsing the global config options related to OpenStack. And also
    provides convenient interfaces for Resource type definitions to define
    their own sub-options and fetch back their parsed values.
    """
    def __init__(self, parser=None, args=None):
        if parser is None:
            parser = ArgumentParser()
        if args is None:
            args = DEFAULT_ARGUMENTS
        self.__cloud_config = os_client_config.OpenStackConfig()
        self.__cloud_config.register_argparse_arguments(parser, args)
        self.__parser = parser
        # Register global options
        _help = "Perform delete operations, don't just report them. " \
                "By default, the command executes a 'dry run'. Add this " \
                "switch to perform a full run."
        self.__parser.add_argument("--force", "-f",
                                   help=_help,
                                   action='store_true')
        _help = "Verbosity level. Add more times for more output "\
                "(up to 2 times)"
        self.__parser.add_argument("-v", "--verbose", help=_help,
                                   action='count', default=0)
        self.__sub_parsers = self.__parser.add_subparsers(dest="resource")
        self.__sub_parser_set = {}
        self.__args = args
        # Defined after options are parsed
        self.__options = None
        self.__cloud = None
        self.__shade = None
        self.__log = logging.getLogger("cloud_cleaner")
        self.__log.addHandler(logging.StreamHandler())

    def add_subparser(self, name):
        """
        Creates a subparser to match the name given by the user.
        Returns it to caller

        :param name: Name of the subparser to create
        :return: The subparser object
        """
        sub_parser = self.__sub_parsers.add_parser(name)
        self.__sub_parser_set[name] = sub_parser
        return sub_parser

    def set_args(self, args):
        """
        Sets args for the current execution, in case there are any args that
        might have been altered or removed from the set by the first call

        :param args: The list of args to parse
        :return: this object
        """
        self.__args = args
        return self

    def parse_args(self):
        """
        Parse all arguments currently attached to this config object

        :return: Parsed arguments
        """
        results = self.__parser.parse_args(self.__args)
        self.__options = vars(results)
        # Set logging level based on verbosity
        debug = self.get_arg('verbose')
        if debug == 0:
            self.__log.setLevel(logging.WARNING)
        if debug == 1:
            self.__log.setLevel(logging.INFO)
            self.__log.info("Setting logging level to info")
        if debug >= 2:
            self.__log.setLevel(logging.DEBUG)
            self.__log.info("Setting logging level to debug")
        self.info("Getting cloud connection")
        self.debug("Parsing cloud connection information")
        cloud = self.__cloud_config.get_one_cloud(argparse=results)
        self.__cloud = cloud
        self.debug("Constructing shade client")
        self.__shade = OpenStackCloud(self.__cloud)
        return results

    def get_arg(self, name):
        """
        Fetch the value of one of the command line arguments from the argparser

        :param name: The command line argument that is requested
        :return: The value of the name requested from
        """
        if name in self.__options.keys():
            return self.__options[name]
        return None

    def get_resource(self):
        """
        Get the name of the resource that is being requested

        :return: The string name of the resource selected from the command line
        """
        if self.__options is None:
            return None
        return self.__options['resource']

    def get_cloud(self):
        """
        Get the cloud that was specified by the command line options. Note that
        this should only be called after #parse_args is called, otherwise it
        will only return None.

        :return: Cloud option parsed, or None
        """
        return self.__cloud

    def get_shade(self):
        """
        Fetch the shade object attached to the cloud that has been configured
        for this run.

        :return: The shade object
        """
        return self.__shade

    # LOGGING FUNCTIONS
    def info(self, msg, *args):
        """Log at the info level"""
        self.__log.info("INFO: %s" % msg, *args)

    def debug(self, msg, *args):
        """Log at the debug level"""
        self.__log.debug("DEBUG: %s" % msg, *args)

    def warning(self, msg, *args):
        """Log at the warning level"""
        self.__log.warning("WARN: %s" % msg, *args)
