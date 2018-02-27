from cloud_cleaner.config import CloudCleanerConfig
from datetime import datetime, timezone, timedelta
import re


class Resource(object):
    type_name = "resource"

    def __init__(self, *args, **kwargs):
        self._config = None
        self._sub_config = None
        if 'now' in kwargs.keys():
            self._now = kwargs['now']
        else:
            self._now = datetime.now(timezone.utc)
        self.__hour = re.compile(r'(\d+)h')
        self.__day = re.compile(r'(\d+)d')
        self.__week = re.compile(r'(\d+)w')
        self.__month = re.compile(r'(\d+)m')
        self.__year = re.compile(r'(\d+)y')

    def register(self, config: CloudCleanerConfig):
        """
        Call to register options for this resource type with the provided
        config object

        :param config: Config object to register resource type with
        :return: None
        """
        self._config = config
        self._sub_config = config.add_subparser(self.type_name)

    def process(self):
        raise UnimplementedError("Must override this method")

    def clean(self):
        raise UnimplementedError("Must override this method")

    def parse_interval(self, interval: str) -> timedelta:
        hours = self.__parse_interval(self.__hour, interval)
        days = self.__parse_interval(self.__day, interval)
        weeks = self.__parse_interval(self.__week, interval)
        months = self.__parse_interval(self.__month, interval)
        years = self.__parse_interval(self.__year, interval)
        return timedelta(days=(days+30*months+years*365),
                         weeks=weeks,
                         hours=hours)

    def __parse_interval(self, regex, interval: str):
        match = regex.match(interval)
        if match:
            return int(match.group(1))
        return 0

    def _get_shade(self):
        if self._config is None:
            return None
        return self._config.get_shade()


class UnimplementedError(Exception):
    def __init__(self, msg: str):
        super(UnimplementedError, self).__init__(msg)
