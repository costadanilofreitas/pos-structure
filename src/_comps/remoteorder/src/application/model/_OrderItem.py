# -*- coding: utf-8 -*-

from typing import List


class OrderItem(object):
    def __init__(self, part_code=None, quantity=0, parts=None):
        # type: (unicode, int, List[OrderItem]) -> None
        self.part_code = part_code
        self.quantity = quantity
        self.product_name = None
        self.product_type = None
        self.price = None
        self.parts = parts
        if self.parts is None:
            self.parts = []
        self.comment = None
