from cloud_cleaner.resources.resource import Resource
from cloud_cleaner.config import CloudCleanerConfig


class Fip(Resource):
    type_name = "fip"

    def __init__(self, config: CloudCleanerConfig):
        super(Fip, self).__init__(config)
