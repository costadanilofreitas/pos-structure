from commons.dto import DefaultHeaderDto  # noqa
from ._CashReportBodyDto import CashReportBodyDto  # noqa


class CashReportDto(object):
    def __init__(self, header, body):
        # type: (DefaultHeaderDto, CashReportBodyDto) -> None
        self.header = header
        self.body = body
