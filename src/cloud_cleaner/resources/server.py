from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources.resource import Resource


class Server(Resource):
    type_name = "server"

    def __init__(self, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        self.__shade = None

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
        if self.__shade is None:
            self.__shade = self._config.get_shade()
        servers = self.__shade.list_servers()
        for server in servers:
            print(server.name)
