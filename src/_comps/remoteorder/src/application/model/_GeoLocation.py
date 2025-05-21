# -*- coding: utf-8 -*-

from typing import Optional


class GeoLocation(object):
    def __init__(self):
        self.latitude = None   # type: Optional[float]
        self.longitude = None  # type: Optional[float]
