# -*- coding: utf-8 -*-
from application.model import ErrorStatus


class PaymentException(Exception):
    def __init__(self, message, i18n_tag=""):
        super(PaymentException, self).__init__(message)
        self.error_code = ErrorStatus.INTERNAL_ERROR
        self.message = message
        self.i18n_tag = i18n_tag
