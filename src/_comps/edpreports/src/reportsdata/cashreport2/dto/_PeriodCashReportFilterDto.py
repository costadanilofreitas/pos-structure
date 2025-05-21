from ._CashReportFilterDto import CashReportFilterDto

from typing import Optional  # noqa
from datetime import datetime  # noqa


class PeriodCashReportFilterDto(CashReportFilterDto):
    def __init__(self, pos_id, report_type, initial_date, end_date, pos=None, operator_id=None):
        # type: (int, str, datetime, datetime, Optional[int], Optional[int]) -> None
        super(PeriodCashReportFilterDto, self).__init__(report_type)
        self.pos_id = pos_id
        self.initial_date = initial_date
        self.end_date = end_date
        self.pos = pos
        self.operator_id = operator_id
