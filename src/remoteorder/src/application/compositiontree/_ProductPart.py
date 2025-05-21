# -*- coding: utf-8 -*-

from typing import Optional


class ProductPart(object):
    def __init__(self):
        self.parent_part_code = None  # type: Optional[unicode]
        self.part_code = None         # type: Optional[unicode]
        self.default_qty = None       # type: Optional[int]
        self.min_qty = None           # type: Optional[int]
        self.max_qty = None           # type: Optional[int]
