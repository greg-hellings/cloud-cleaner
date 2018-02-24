from cloud_cleaner.resources.resource import Resource
from cloud_cleaner.config import CloudCleanerConfig


class Fip(Resource):
    type_name = "fip"

    def register(self, config: CloudCleanerConfig):
        super(Fip, self).register(config)
