from typing import List  # noqa

from _CashReportBodyLineDto import CashReportBodyLineDto  # noqa


class CashReportBodyDto(object):
    def __init__(self):
        self.operator_count = 0
        self.initial_float = CashReportBodyLineDto(0, 0.0)
        self.total_sales = CashReportBodyLineDto(0, 0.0)
        self.voids = CashReportBodyLineDto(0, 0.0)
        self.net_sales = CashReportBodyLineDto(0, 0.0)
        self.tender_breakdown = []  # type: List[CashReportBodyLineDto]
        self.cash_ins = CashReportBodyLineDto(0, 0.0)
        self.cash_outs = CashReportBodyLineDto(0, 0.0)
        self.value_in_drawer = 0.0
