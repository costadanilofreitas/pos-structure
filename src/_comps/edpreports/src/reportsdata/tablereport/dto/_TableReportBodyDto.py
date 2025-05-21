from ._TableReportOrderDto import TableReportOrderDto  # noqa
from typing import List


class TableReportBodyDto(object):
    def __init__(self):
        self.total_amount = 0.0  # type: float
        self.sub_total_amount = 0.0  # type: float
        self.discount_amount = 0.0  # type: float
        self.total_after_discount = 0.0  # type: float
        self.total_tender = 0.0  # type: float
        self.total_per_seat = 0.0  # type: float
        self.orders = []  # type: List[TableReportOrderDto]
        self.service_seats = 0  # type: int
        self.order_id = None  # type: str
        self.tip = None  # type: float
