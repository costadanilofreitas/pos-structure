from typing import List

from report import Presenter  # noqa
from basereport import SimpleReport

from .builders import TableReportHeader, TableReportBody, ReportBuilder
from .dto import TableReportDto  # noqa


class TableReportPresenter(Presenter):
    def __init__(self, print_by, hide_unpriced_items):
        self.print_by = print_by
        self.hide_unpriced_items = hide_unpriced_items

    def present(self, dto):
        # type: (TableReportDto) -> SimpleReport

        report_builders = [
            TableReportHeader(dto.header),
            TableReportBody(dto.body, self.print_by, self.hide_unpriced_items)
        ]  # type: List[ReportBuilder]

        report = []
        for builder in report_builders:
            report.extend(builder.generate())

        return SimpleReport(report, 38)
