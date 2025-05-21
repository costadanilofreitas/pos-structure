# -*- coding: utf-8 -*-

from typing import Optional


class CustomProperty(object):
    def __init__(self):
        self.key = None    # type: Optional[unicode]
        self.value = None  # type: Optional[unicode]
