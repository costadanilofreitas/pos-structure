from ._TableReportSaleLineDto import TableReportSaleLineDto  # noqa
from typing import List  # noqa


class TableReportOrderDto(object):

    def __init__(self):
        self.order_id = None
        self.total_amount = 0.0
        self.total_after_discount = 0.0
        self.total_tender = 0.0
        self.discount_amount = 0.0
        self.sales_line_list = []  # type: List[TableReportSaleLineDto]
        self.split_key = None  # type: str
        self.tip = 0.0
