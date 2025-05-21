# -*- coding: utf-8 -*-

from datetime import datetime

from application.apimodel import Item
from typing import List, Optional, Dict


class OrderStatus(object):
    Ok = "Ok"
    Warning = "Warning"
    Danger = "Danger"
    NotSet = "NotSet"


class Order(object):
    def __init__(self):
        self.id = None               # type: Optional[unicode]
        self.order_status = None     # type: Optional[int]
        self.remote_id = None        # type: Optional[unicode]
        self.customer_name = ""      # type: Optional[unicode]
        self.partner = None          # type: Optional[unicode]
        self.short_reference = None  # type: Optional[unicode]
        self.items = []              # type: Optional[List[Item]]
        self.receive_time = None     # type: Optional[datetime]
        self.pickup_time = None      # type: Optional[datetime]
        self.status = None           # type: Optional[unicode]
        self.originator_id = None    # type: Optional[unicode]
        self.city = None             # type: Optional[unicode]
        self.complement = None       # type: Optional[unicode]
        self.address = None          # type: Optional[unicode]
        self.neighborhood = None     # type: Optional[unicode]
        self.postal = None           # type: Optional[unicode]
        self.reference = None        # type: Optional[unicode]
        self.state = None            # type: Optional[unicode]
        self.total = None            # type: Optional[float]
        self.custom_properties = {}  # type: Optional[Dict[unicode: unicode]]
        self.business_period = None  # type: Optional[unicode]
