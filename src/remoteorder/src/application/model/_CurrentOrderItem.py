# -*- coding: utf-8 -*-

from typing import Optional


class CurrentOrderItem(object):
    def __init__(self):
        self.order_id = None                    # type: Optional[int]
        self.line_number = None                 # type: Optional[int]
        self.item_id = None                     # type: Optional[unicode]
        self.level = None                       # type: Optional[int]
        self.part_code = None                   # type: Optional[int]
        self.ordered_quantity = None            # type: Optional[int]
        self.last_ordered_quantity = None       # type: Optional[int]
        self.included_quantity = None           # type: Optional[int]
        self.decremented_quantity = None        # type: Optional[int]
        self.price_key = None                   # type: Optional[unicode]
        self.discount_amount = None            # type: Optional[float]
        self.surcharge_amount = None           # type: Optional[float]
        self.only_flag = None                   # type: Optional[int]
        self.overwritten_unit_price = None      # type: Optional[float]
        self.default_qty = None                 # type: Optional[int]
