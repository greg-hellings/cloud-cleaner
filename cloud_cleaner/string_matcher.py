"""Filler class for regex comparisons"""


class StringMatcher:  # pylint: disable=too-few-public-methods
    """
    Used in place where a regex would otherwise be used, but where a constant
    return value is desired, instead.
    """

    def __init__(self, value):
        self.__value = value

    def match(self, *args):  # pylint: disable=unused-argument
        """
        Ignores parameters and returns configured value.

        :param args: Ignored
        :return: Value configured in constructor
        """
        return self.__value
