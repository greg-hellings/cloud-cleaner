from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources import all_resources

import sys


def cloud_clean(args: list=sys.argv,
                config: CloudCleanerConfig=None):
    # Construct or configure cloud cleaner config
    if config is None:
        config = CloudCleanerConfig(args=args)
    else:
        config.set_args(args)
    # Register all the resource types and options with the configurator
    resources = {}
    for Resource in all_resources:
        resources[Resource.type_name] = Resource(config)
    config.parse_args()
