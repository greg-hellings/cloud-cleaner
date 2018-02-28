"""Contains implementation of the Server class"""
import re
from datetime import datetime
from pytz import utc
from cloud_cleaner.config import DATE_FORMAT
from cloud_cleaner.resources.resource import Resource
from cloud_cleaner.string_matcher import StringMatcher


class Server(Resource):
    """
    Performs processing and cleansing of instances of servers from the
    configured OpenStack endpoints
    """
    type_name = "server"

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.__targets = []
        self._interval = None
        # Default objects that pass through all instances without filtering
        self.__skip_name = StringMatcher(False)
        self.__name = StringMatcher(True)

    def register(self, config):
        """

        :type parser: argparse.ArgumentParser
        """
        super(Server, self).register(config)
        _desc = "Regex to match the name of the servers"
        self._sub_config.add_argument("--name", "-n", help=_desc)
        _desc = "Regex to match for servers to ignore"
        self._sub_config.add_argument("--skip-name", "-s", dest="skip_name",
                                      help=_desc)
        _desc = "Minimum age (1d, 2w, 6m, 1y)"
        self._sub_config.add_argument("--age", "-a", help=_desc)

    def process(self):
        """
        Fetches the list of servers and processes them to filter out which
        ones ought to actually be deleted.

        :return: None
        """
        shade = self._get_shade()
        self._config.info("Connecting to OpenStack to retrieve server list")
        self.__targets = shade.list_servers()
        self._config.info("Found %d servers" % len(self.__targets))
        self.__debug_targets()
        # Process for time
        self.__process_dates()
        self._config.info("%d servers passed age test" % len(self.__targets))
        # Process for name
        self.__process_names()
        self._config.info("%d servers passed name test" % len(self.__targets))

    def __debug_targets(self):
        for target in self.__targets:
            self._config.debug("   *** " + target.name)

    def clean(self):
        """
        Call delete on the list of servers left over after the process
        stage is completed.

        :return: None
        """
        shade = self._get_shade()
        self._config.info("Deleting %d servers" % len(self.__targets))
        for target in self.__targets:
            self._config.debug("Deleting %s" % target.id)
            shade.delete_server(target.id)
            print("Deleted %s" % target.name)

    def __process_dates(self):
        """
        Process out all the items from this system that are not targeted based
        on the age of the server

        :return: None
        """
        age = self._config.get_arg('age')
        if age is not None:
            self._config.debug("Parsing dates")
            self._interval = self.parse_interval(self._config.get_arg('age'))
            self._config.debug("Working with age %s" % (self._interval,))
            self.__targets = list(filter(self.__right_age, self.__targets))
            self._config.debug("Parsed ages, servers remaining: ")
            self.__debug_targets()
        else:
            self._config.debug("No age provided")

    def __process_names(self):
        skip_name = self._config.get_arg("skip_name")
        if skip_name is not None:
            self.__skip_name = re.compile(skip_name)
        name = self._config.get_arg('name')
        if name is not None:
            self.__name = re.compile(name)
        if name is not None or skip_name is not None:
            self._config.debug("Parsing names")
            self.__targets = list(filter(self.__right_name, self.__targets))
            self._config.debug("Parsed names, servers remaining: ")
            self.__debug_targets()
        else:
            self._config.debug("No name restrictions provided")

    def __right_name(self, target):
        return not self.__skip_name.match(target.name) and \
               self.__name.match(target.name)

    def __right_age(self, target):
        system_age = datetime.strptime(target.created, DATE_FORMAT)
        system_age = system_age.replace(tzinfo=utc)
        return self._now > (system_age + self._interval)
