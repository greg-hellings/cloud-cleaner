"""Contains the Resource base class for CLI processing"""
import re
from datetime import datetime, timedelta
from pytz import utc


HOUR = re.compile(r'(\d+)h')
DAY = re.compile(r'(\d+)d')
WEEK = re.compile(r'(\d+)w')
MONTH = re.compile(r'(\d+)m')
YEAR = re.compile(r'(\d+)y')


# PyLint disabled because removing the (object) call here causes errors in
# python2.7. Once we drop support for that, we can then re-enable this lint
# line
class Resource(object):  # pylint: disable=R0205
    """
    Base class for all resources types. It handles basic registration of the
    type with a config object and a few simple helper methods for handling
    things like dates and times and the like.

    Sub-classes should override the "type_name" field as well as the methods
    "process" and "clean", minimally. See those methods for more information
    on what they should do.

    "type_name" defines the specific CLI sub-command that will be processed
    by the sub-classing type. Therefore, it should be a simple, CLI-friendly
    string.

    If the resource you are adding requires any additional options to
    configure its behavior, then overriding the "register" method will allow
    you to add CLI options to self._sub_config for handling those
    arguments.
    """
    type_name = "resource"

    def __init__(self, **kwargs):
        self._config = None
        self._sub_config = None
        if 'now' in kwargs.keys():
            self._now = kwargs['now']
        else:
            self._now = datetime.now(utc)

    def register(self, config):
        """
        Call to register options for this resource type with the provided
        config object.

        Override this method to implement the specific CLI arguments for
        the data type that is represented

        :param config: Config object to register resource type with
        :return: None
        """
        self._config = config
        self._sub_config = config.add_subparser(self.type_name)

    def process(self):  # pylint: disable=no-self-use
        """
        Override this method in base classes in order to perform the actual
        calls to OpenStack to fetch and filter the processed resources

        :return: None
        """
        raise UnimplementedError("Must override this method")

    def clean(self):  # pylint: disable=no-self-use
        """
        Override this method in base classes in order to perform the actual
        calls to OpenStack to clean up the processed resources

        :return: None
        """
        raise UnimplementedError("Must override this method")

    def parse_interval(self, interval):
        """
        Parse the given CLI argument interval into a usable timedelta type
        of object. This method understands suffixes for hours, days, weeks,
        months, and years.

        Note that this will only pick up the first such substring in the
        passed parameter.

        :param interval: A string representation of the interval
        :return: The timedelta object representing the interval
        """
        hours = self.__parse_interval(HOUR, interval)
        days = self.__parse_interval(DAY, interval)
        weeks = self.__parse_interval(WEEK, interval)
        months = self.__parse_interval(MONTH, interval)
        years = self.__parse_interval(YEAR, interval)
        return timedelta(days=(days+30*months+years*365),
                         weeks=weeks,
                         hours=hours)

    def prep_deletion(self):
        """
        Prepare the resource for deletion. The steps that this entails will
        vary greatly from resource to resource.

        """
        raise UnimplementedError("Must override this method")

    @classmethod
    def __parse_interval(cls, regex, interval):
        match = regex.match(interval)
        if match:
            return int(match.group(1))
        return 0

    def _get_conn(self):
        if self._config is None:
            return None
        return self._config.get_conn()


class UnimplementedError(Exception):
    """Error indicating called method needs to be overridden"""
