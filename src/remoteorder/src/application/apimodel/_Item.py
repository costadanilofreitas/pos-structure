# -*- coding: utf-8 -*-

from typing import List


class ProductType(object):
    PRODUCT = "Product"
    OPTION = "Option"
    COMBO = "Combo"


class Item(object):
    def __init__(self):
        self.part_code = 0              # type: int
        self.context = ""               # type: unicode
        self.product_name = ""          # type: unicode
        self.product_type = "Product"   # type: unicode
        self.quantity = 0               # type: int
        self.price = 0.0                # type: float
        self.default_quantity = 0       # type: int
        self.sons = []                  # type: List[Item]
