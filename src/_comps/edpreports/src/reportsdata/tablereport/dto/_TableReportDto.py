from ._TableReportHeaderDto import TableReportHeaderDto  # noqa
from ._TableReportBodyDto import TableReportBodyDto  # noqa


class TableReportDto(object):

    def __init__(self, header, body):
        # type: (TableReportHeaderDto, TableReportBodyDto) -> None
        self.header = header
        self.body = body
