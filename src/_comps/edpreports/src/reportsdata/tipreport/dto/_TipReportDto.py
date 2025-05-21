from ._TipReportHeaderDto import TipReportHeaderDto
from ._TipReportBodyDto import TipReportBodyDto


class TipReportDto(object):
    def __init__(self, header, body):
        # type: (TipReportHeaderDto, TipReportBodyDto) -> None
        self.header = header
        self.body = body
