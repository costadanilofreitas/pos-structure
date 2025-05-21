# -*- coding: utf-8 -*-
from application.customexception._TranslatedException import TranslatedException
from application.model import ErrorStatus


class LogisticException(TranslatedException):
    def __init__(self, message, model=None):
        super(LogisticException, self).__init__(message, model)
        self.error_code = ErrorStatus.LOGISTIC_ERROR
