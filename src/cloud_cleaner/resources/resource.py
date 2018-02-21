from cloud_cleaner.config import CloudCleanerConfig


class Resource(object):
    type_name = "resource"

    def __init__(self):
        self._config = None
        self._sub_config = None

    def register(self, config: CloudCleanerConfig):
        """
        Call to register options for this resource type with the provided
        config object

        :param config: Config object to register resource type with
        :return: None
        """
        self._config = config
        self._sub_config = config.add_subparser(self.type_name)
