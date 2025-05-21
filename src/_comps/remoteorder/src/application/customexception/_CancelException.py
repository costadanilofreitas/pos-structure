# -*- coding: utf-8 -*-
from application.model import ErrorStatus
from _TranslatedException import TranslatedException


class CancelException(TranslatedException):
    def __init__(self, message, model=None):
        super(CancelException, self).__init__(message, model)
        self.error_code = ErrorStatus.INTERNAL_ERROR
