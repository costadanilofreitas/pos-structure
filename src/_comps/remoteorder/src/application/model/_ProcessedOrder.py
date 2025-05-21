# -*- coding: utf-8 -*-

from application.model import OrderItem
from typing import List


class ProcessedOrder(object):
    def __init__(self, remote_order_id, local_order_id, items):
        # type: (int, int, List[OrderItem]) -> None
        self.remote_order_id = remote_order_id
        self.local_order_id = local_order_id
        self.items = items
        self.has_error = False
        self.code = ''
        self.error_message = ''
