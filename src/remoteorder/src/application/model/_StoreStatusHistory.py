# -*- coding: utf-8 -*-

from typing import Optional


class StoreStatusHistory(object):
    def __init__(self):
        self.id = 0           # type: Optional[int]
        self.status = None    # type: Optional[unicode]
        self.operator = None  # type: Optional[unicode]
