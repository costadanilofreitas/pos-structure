# -*- coding: utf-8 -*-

from typing import Optional


class Store(object):
    def __init__(self):
        self.id = None      # type: Optional[int]
        self.name = None    # type: Optional[unicode]
        self.status = None  # type: Optional[unicode]
