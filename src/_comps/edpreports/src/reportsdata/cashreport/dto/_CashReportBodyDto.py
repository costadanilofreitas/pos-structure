from typing import List  # noqa
from _CashReportBodyLineDto import CashReportBodyLineDto  # noqa


class CashReportBodyDto(object):
    def __init__(self, cash_report_body_lines_dto, report_type):
        # type:(List[CashReportBodyLineDto], unicode) -> None
        self.cash_report_body_lines_dto = cash_report_body_lines_dto  # type:(List[CashReportBodyLineDto])
        self.report_type = report_type
