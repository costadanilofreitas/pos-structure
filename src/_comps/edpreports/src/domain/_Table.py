from datetime import datetime

from typing import List

from ._TableOrder import TableOrder


class Table(object):
    def __init__(self):
        self.table_id = None  # type: str
        self.start_date = None  # type: datetime
        self.service_seats = 0  # type: int
        self.total_amount = 0.0  # type: float
        self.sub_total_amount = 0.0  # type: float
        self.total_per_seat = 0.0  # type: float
        self.total_discounts = 0.0  # type: float
        self.orders = []  # type: List[TableOrder]
        self.tip = 0.0  # type: float
        self.user_id = None  # type: str
        self.user_name = None  # type: str
