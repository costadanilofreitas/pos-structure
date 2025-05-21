from datetime import datetime  # noqa

from typing import List  # noqa
from typing import Union  # noqa

from _OrderTender import OrderTender  # noqa


class OrderSate(object):
    Voided = 4
    Paid = 5


class Order(object):
    def __init__(self, order_id, date, state, total, donation, tenders, void_reason_id, change_amount):
        # type: (int, datetime, int, float, float, List[OrderTender], Union[int, None], float) -> None
        self.order_id = order_id
        self.date = date
        self.state = state
        self.total = total
        self.donation = donation
        self.tenders = tenders
        self.void_reason_id = void_reason_id
        self.change_amount = change_amount
