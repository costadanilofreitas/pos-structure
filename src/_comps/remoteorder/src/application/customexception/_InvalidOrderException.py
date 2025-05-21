# -*- coding: utf-8 -*-
from application.model import ErrorStatus


class InvalidOrderException(Exception):
    def __init__(self):
        self.error_code = ErrorStatus.MENU_ERROR
        self.message = ""
        self.i18n_tag = ""
        

