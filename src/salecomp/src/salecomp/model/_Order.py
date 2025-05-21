from datetime import datetime, date

from typing import List

from ._Line import Line
from ._OrderType import OrderType
from ._SaleType import SaleType
from ._State import State


class Order(object):
    def __init__(self,
                 id,
                 state,
                 type,
                 originator_id,
                 created_at,
                 business_period,
                 pod_type,
                 session_id,
                 price_lists,
                 price_basis,
                 sale_type,
                 lines):
        # type: (int, State, OrderType, int, datetime, date, str, str, List[str], str, SaleType, List[Line]) -> None
        self.id = id
        self.state = state
        self.type = type
        self.originator_id = originator_id
        self.created_at = created_at
        self.business_period = business_period
        self.pod_type = pod_type
        self.session_id = session_id
        self.price_lists = price_lists
        self.price_basis = price_basis
        self.sale_type = sale_type
        self.lines = lines
