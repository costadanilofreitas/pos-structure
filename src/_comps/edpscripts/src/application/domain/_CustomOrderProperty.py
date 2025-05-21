
class CustomOrderProperty(object):
    def __init__(self, key, value):
        self.__key = key
        self.__value = value

    @property
    def key(self):
        # type: () -> str
        return self.__key

    @property
    def value(self):
        # type: () -> str
        return self.__value
