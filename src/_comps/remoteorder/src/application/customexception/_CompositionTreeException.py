# -*- coding: utf-8 -*-

from application.customexception import ValidationException


class CompositionTreeException(ValidationException):
    def __init__(self, error_code, localized_error_message):
        super(CompositionTreeException, self).__init__(error_code, localized_error_message)
