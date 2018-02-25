from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources import all_resources

import sys


def cloud_clean(args: list=sys.argv[1:],
                config: CloudCleanerConfig=None):
    # Construct or configure cloud cleaner config
    if config is None:
        config = CloudCleanerConfig(args=args)
    else:
        config.set_args(args)
    # Register all the resource types and options with the configurator
    for resource in all_resources.values():
        resource.register(config)
    config.parse_args()
    # Call the process method for the target resource type
    all_resources[config.get_resource()].process()
    if config.get_arg("force"):
        all_resources[config.get_resource()].clean()