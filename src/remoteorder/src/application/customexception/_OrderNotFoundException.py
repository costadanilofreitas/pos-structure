# -*- coding: utf-8 -*-
from application.model import ErrorStatus


class OrderNotFoundException(Exception):
    def __init__(self, remote_order_id, message):
        Exception.__init__(self, message)
        self.remote_order_id = remote_order_id
        self.message = message
        self.error_code = ErrorStatus.ORDER_NOT_FOUND
