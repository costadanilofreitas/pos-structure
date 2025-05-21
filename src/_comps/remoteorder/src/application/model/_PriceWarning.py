# -*- coding: utf-8 -*-

from typing import Optional


class PriceWarning(object):
    def __init__(self):
        self.remote_order_id = None         # type: Optional[unicode]
        self.remote_order_items_value = 0   # type: Optional[float]
        self.local_order_items_value = 0    # type: Optional[float]
