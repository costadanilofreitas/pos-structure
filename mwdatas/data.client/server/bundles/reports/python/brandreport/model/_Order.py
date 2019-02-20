from datetime import datetime
from typing import List
from _OrderTender import OrderTender


class OrderSate(object):
    Voided = 4
    Paid = 5


class Order(object):
    def __init__(self, order_id, date, state, total, tenders):
        # type: (int, datetime, int, float, List[OrderTender]) -> None
        self.order_id = order_id
        self.date = date
        self.state = state
        self.total = total
        self.tenders = tenders
