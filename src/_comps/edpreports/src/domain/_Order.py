from pos_model import OrderState
from typing import List  # noqa

from enum import Enum
from _OrderTender import OrderTender  # noqa


class Order(object):
    def __init__(self, state, total, tenders):
        # type: (OrderState, float, List[OrderTender]) -> None
        self.state = state
        self.total = total
        self.tenders = tenders

    class OrderSate(Enum):
        voided = 1
        paid = 2
