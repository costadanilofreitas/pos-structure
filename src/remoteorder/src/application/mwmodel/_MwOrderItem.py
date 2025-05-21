# -*- coding: utf-8 -*-

from typing import List, Optional


class MwOrderItem(object):
    def __init__(self):
        self.line_number = None  # type: Optional[int]
        self.context = None      # type: Optional[unicode]
        self.part_code = None    # type: Optional[int]
        self.level = None        # type: Optional[int]
        self.quantity = None     # type: Optional[int]
        self.default_qty = None  # type: Optional[int]
        self.price = None        # type: Optional[float]
        self.parent = None       # type: Optional[MwOrderItem]
        self.sons = []           # type: Optional[List[MwOrderItem]]
