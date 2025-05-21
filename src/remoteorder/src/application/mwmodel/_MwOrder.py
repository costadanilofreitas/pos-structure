# -*- coding: utf-8 -*-

from typing import List, Optional, Dict

from application.mwmodel import MwOrderItem, MwOrderCustomProperty


class MwOrderStatus(object):
    IN_PROGRESS = 1
    STORED = 2
    TOTALED = 3
    VOIDED = 4
    PAID = 5
    RECALLED = 6


class MwOrder(object):
    def __init__(self):
        self.id = None               # type: Optional[int]
        self.status = None           # type: Optional[int]
        self.order_items = []        # type: Optional[List[MwOrderItem]]
        self.custom_properties = {}  # type: Optional[Dict[unicode: MwOrderCustomProperty]]
        self.total = None            # type: Optional[float]
        self.business_period = None  # type: Optional[unicode]
