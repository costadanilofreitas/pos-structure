# -*- coding: utf-8 -*-

from datetime import datetime

from application.model import CustomProperty, OrderItem, PickUpInfo, Tender
from typing import List, Dict, Optional


class RemoteOrder(object):
    def __init__(self):
        self.id = None                  # type: Optional[unicode]
        self.code = None                # type: Optional[unicode]
        self.created_at = None          # type: Optional[datetime]
        self.partner = None             # type: Optional[unicode]
        self.short_reference = None     # type: Optional[unicode]
        self.items = []                 # type: Optional[List[OrderItem]]
        self.tenders = []               # type: Optional[List[Tender]]
        self.custom_properties = {}     # type: Optional[Dict[unicode, CustomProperty]]
        self.pickup = None              # type: Optional[PickUpInfo]
        self.originator_id = None       # type: Optional[unicode]
        self.order_id = None            # type: Optional[unicode]
        self.discount_amount = None     # type: Optional[float]
        self.sub_total = None           # type: Optional[float]
