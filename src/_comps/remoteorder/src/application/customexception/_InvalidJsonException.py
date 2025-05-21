# -*- coding: utf-8 -*-

from application.customexception import InvalidOrderException
from application.model import ErrorStatus
from typing import Union


class InvalidJsonException(InvalidOrderException):
    def __init__(self, message, invalid_json=None):
        # type: (unicode, Union[unicode, None]) -> None
        super(InvalidJsonException, self).__init__()
        self.error_code = ErrorStatus.UNEXPECTED_ERROR
        self.message = message
        self.invalid_json = invalid_json

    def __str__(self):
        # type: () -> unicode
        return u"InvalidJsonException: " + self.message + u" " + self.invalid_json

    def __repr__(self):
        # type: () -> unicode
        return self.__str__()
