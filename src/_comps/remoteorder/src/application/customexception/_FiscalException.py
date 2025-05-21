# -*- coding: utf-8 -*-
from application.model import ErrorStatus


class FiscalException(Exception):
    def __init__(self, message, i18n_tag=""):
        super(FiscalException, self).__init__(message)
        self.error_code = ErrorStatus.FISCAL_ERROR
        self.message = message
        self.i18n_tag = i18n_tag
