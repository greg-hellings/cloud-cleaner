"""
Entry-point methods for CLI commands
"""
import sys
from cloud_cleaner.config import CloudCleanerConfig
from cloud_cleaner.resources import ALL_RESOURCES


def cloud_clean(args=sys.argv[1:],  # pylint: disable=W0102
                config=None):
    """
    Entrypoint for the cloud-clean CLI interface

    :param args: Command line arguments passed from user
    :param config: The config object to be used
    :return: None
    """
    # Construct or configure cloud cleaner config
    if config is None:
        config = CloudCleanerConfig(args=args)
    else:
        config.set_args(args)
    # Register all the resource types and options with the configurator
    for resource in ALL_RESOURCES.values():
        resource.register(config)
    config.parse_args()
    # Call the process method for the target resource type
    print("Options parsed, fetching resources")
    ALL_RESOURCES[config.get_resource()].process()
    if config.get_arg("force"):
        print("Resources fetched, cleaning")
        ALL_RESOURCES[config.get_resource()].clean()
    else:
        print("No changes made, force option not enabled")
