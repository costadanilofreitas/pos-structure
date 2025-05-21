# -*- coding: utf-8 -*-
from application.model import ErrorStatus


class StoreClosedException(Exception):
    def __init__(self):
        # type: () -> None
        self.error_code = ErrorStatus.STORE_IS_CLOSED
        self.message = "$STORE_IS_CLOSED"
