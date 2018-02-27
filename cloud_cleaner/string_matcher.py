"""Filler class for regex comparisons"""


class StringMatcher(object):  # pylint: disable=too-few-public-methods
    """
    Used in place where a regex would otherwise be used, but where a constant
    return value is desired, instead.
    """
    def __init__(self, value: bool):
        self.__value = value

    def match(self, *args) -> bool:  # pylint: disable=unused-argument
        """
        Ignores parameters and returns configured value.

        :param args: Ignored
        :return: Value configured in constructor
        """
        return self.__value
