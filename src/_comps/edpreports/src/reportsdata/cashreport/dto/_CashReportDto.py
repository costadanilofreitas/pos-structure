from commons.dto import DefaultHeaderDto  # noqa
from _CashReportBodyDto import CashReportBodyDto  # noqa


class CashReportDto(object):
    def __init__(self, report_header_dto, report_body_dto, pos_id):
        # type: (DefaultHeaderDto, CashReportBodyDto, int) -> None
        self.report_header_dto = report_header_dto
        self.report_body_dto = report_body_dto
        self.pos_id = pos_id
