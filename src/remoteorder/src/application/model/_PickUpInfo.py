# -*- coding: utf-8 -*-

from datetime import datetime

from _Address import Address
from typing import Optional


class PickUpInfo(object):
    def __init__(self):
        self.time = None     # type: Optional[datetime]
        self.type = None     # type: Optional[unicode]
        self.company = None  # type: Optional[unicode]
        self.address = None  # type: Optional[Address]
