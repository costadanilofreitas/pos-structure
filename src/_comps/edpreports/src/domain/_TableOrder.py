from ._TableOrderSaleLine import TableOrderSaleLine  # noqa
from ._OrderStateEnum import OrderStateEnum  # noqa
from typing import List  # noqa


class TableOrder(object):

    def __init__(self, order_id, order_state, total_amount, total_after_discount, total_tender, discount_amount,
                 sales_line, split_key, tip):
        # type: (str, OrderStateEnum, float, float, float, float, List[TableOrderSaleLine], str, float) -> None
        self.order_id = order_id
        self.order_state = order_state
        self.total_amount = total_amount
        self.total_after_discount = total_after_discount
        self.total_tender = total_tender
        self.discount_amount = discount_amount
        self.sales_line = sales_line
        self.split_key = split_key
        self.tip = tip
