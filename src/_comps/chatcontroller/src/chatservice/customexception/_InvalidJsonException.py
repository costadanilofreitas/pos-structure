# -*- coding: utf-8 -*-


class InvalidJsonException(Exception):
    def __init__(self, message, invalid_json=None):
        # type: (unicode, unicode) -> None
        self.message = message
        self.invalid_json = invalid_json

    def __str__(self):
        # type: () -> unicode
        return u"InvalidJsonException: " + self.message + u" " + self.invalid_json

    def __repr__(self):
        # type: () -> unicode
        return self.__str__()
