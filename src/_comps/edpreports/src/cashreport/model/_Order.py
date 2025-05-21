from datetime import datetime

from typing import List
from typing import Union

from _OrderTender import OrderTender


class OrderSate(object):
    Voided = 4
    Paid = 5


class Order(object):
    def __init__(self, order_id, date, state, total, donation, tenders, void_reason_id, discount, tip, sale_type, table_id, sector, delivery_originator):
        # type: (int, datetime, int, float, float, List[OrderTender], Union[int, None], float, float, int, str, Union[str, None], Union[str, None]) -> None
        self.order_id = order_id
        self.date = date
        self.state = state
        self.total = total
        self.donation = donation
        self.tenders = tenders
        self.void_reason_id = void_reason_id
        self.discount = discount
        self.tip = tip
        self.sale_type = sale_type
        self.table_id = table_id
        self.sector = sector
        self.delivery_originator = delivery_originator
