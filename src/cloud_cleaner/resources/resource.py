from cloud_cleaner.config import CloudCleanerConfig


class Resource(object):
    type_name = "resource"

    def __init__(self, config: CloudCleanerConfig):
        self._config = config
        self._sub_config = config.add_subparser(self.type_name)
