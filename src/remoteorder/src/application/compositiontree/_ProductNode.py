# -*- coding: utf-8 -*-

from typing import Optional


class ProductNode(object):
    def __init__(self, part_code, type, default_qty, min_qty, max_qty, current_qty, price):
        # type: (Optional[unicode], Optional[unicode], Optional[int], Optional[int], Optional[int], Optional[int], Optional[float]) -> None
        self.part_code = part_code
        self.type = type
        self.default_qty = default_qty
        self.min_qty = min_qty
        self.max_qty = max_qty
        self.current_qty = current_qty
        self.unit_price = None
        self.added_unit_price = None
        self.name = None
        self.comment = None
        self.enabled = True
        self.price = price

    def __str__(self):
        return "{{partCode: {0}, type: {1}, default_qty: {2}, min_qty: {3}, max_qty: {4}, current_qty = {5}, enabled = {6}, price = {7} }}"\
            .format(self.part_code, self.type, self.default_qty, self.min_qty, self.max_qty, self.current_qty, self.enabled, self.price)

    def __repr__(self):
        return self.__str__()
