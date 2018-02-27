class StringMatcher(object):
    """
    Used in place where a regex would otherwise be used, but where a constant
    return value is desired, instead.
    """
    def __init__(self, value: bool):
        self.__value = value

    def match(self, *args) -> bool:
        return self.__value