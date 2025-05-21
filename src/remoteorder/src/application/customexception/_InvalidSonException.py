# -*- coding: utf-8 -*-

from application.customexception import InvalidOrderException
from application.model import ErrorStatus


class InvalidSonException(InvalidOrderException):
    def __init__(self, order_validation_error, localized_message):
        # type: (unicode, unicode) -> None
        super(InvalidSonException, self).__init__()
        self.order_validation_error = order_validation_error
        self.message = self.localized_message = localized_message
        self.error_code = ErrorStatus.MENU_ERROR

    def __str__(self):
        # type: () -> unicode
        return u"OrderValidationException " + self.order_validation_error + ": " + self.localized_message

    def __repr__(self):
        return self.__str__()
