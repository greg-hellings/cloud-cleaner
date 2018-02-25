from cloud_cleaner.config import CloudCleanerConfig, date_format
from cloud_cleaner.resources.resource import Resource
from datetime import datetime, timezone
from munch import Munch


class Server(Resource):
    type_name = "server"

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.__shade = None
        self.__targets = []
        self._interval = None

    def register(self, config: CloudCleanerConfig):
        """

        :type parser: argparse.ArgumentParser
        """
        super(Server, self).register(config)
        _desc = "Regex to match the name of the servers"
        self._sub_config.add_argument("--name", "-n", help=_desc)
        _desc = "Minimum age (1d, 2w, 6m, 1y)"
        self._sub_config.add_argument("--age", "-a", help=_desc)

    def process(self):
        """
        Fetches the list of servers and processes them to filter out which
        ones ought to actually be deleted.

        :return: None
        """
        if self.__shade is None:
            self.__shade = self._config.get_shade()
        self._config.info("Connecting to OpenStack to retrieve server list")
        self.__targets = self.__shade.list_servers()
        self._config.debug("Found servers: ", [t.name for t in self.__targets])
        # Process for time
        self._interval = self.parse_interval(self._config.get_arg('age'))
        self.__targets = [t for t in self.__targets if self.__right_age(t)]
        self._config.debug("Parsed ages, servers remaining: ", [t.name for t in self.__targets])

    def clean(self):
        """
        Call delete on the list of servers left over after the process
        stage is completed.

        :return: None
        """
        if self.__shade is None:
            self.__shade = self._config.get_shade()
        for target in self.__targets:
            self.__shade.delete_server(target.id)

    def __right_age(self, target: Munch):
        system_age = datetime.strptime(target.created, date_format)
        system_age = system_age.replace(tzinfo=timezone.utc)
        self._config.info(target.id, self._now, system_age + self._interval)
        return self._now > (system_age + self._interval)
