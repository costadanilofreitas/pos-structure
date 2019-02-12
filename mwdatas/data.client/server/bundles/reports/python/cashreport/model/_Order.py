from datetime import datetime

from typing import List
from typing import Union

from _OrderTender import OrderTender


class OrderSate(object):
    Voided = 4
    Paid = 5


class Order(object):
    def __init__(self, order_id, date, state, total, donation, tenders, void_reason_id):
        # type: (int, datetime, int, float, float, List[OrderTender], Union[int, None]) -> None
        self.order_id = order_id
        self.date = date
        self.state = state
        self.total = total
        self.donation = donation
        self.tenders = tenders
        self.void_reason_id = void_reason_id
