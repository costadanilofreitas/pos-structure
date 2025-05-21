# -*- coding: utf-8 -*-

from typing import Optional


class Tender(object):
    def __init__(self):
        self.type = None   # type: Optional[unicode]
        self.value = None  # type: Optional[float]
