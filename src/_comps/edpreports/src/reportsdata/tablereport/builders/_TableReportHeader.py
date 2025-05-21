from typing import List

from basereport import TableReport, ReportColumnDefinition, AlignTypes
from report import Part
from report.command import AlignCommand, RepeatCommand, FontCommand
from ._ReportBuilder import ReportBuilder
from ..dto import TableReportHeaderDto


class TableReportHeader(ReportBuilder):
    def __init__(self, table_report_header_dto):
        # type: (TableReportHeaderDto) -> None
        self.table_report_header_dto = table_report_header_dto

    def generate(self):
        # type: () -> List[Part]
        report_header = [
            Part(commands=[FontCommand(FontCommand.Font.A)]),
            Part("$TABLE_NUMBER {}".format(self.table_report_header_dto.table_id),
                 [AlignCommand(AlignCommand.Alignment.center)]),
            a_new_line(),
            Part("$OPERATOR_LABEL {}".format(self.table_report_header_dto.user_name[:20]),
                 [AlignCommand(AlignCommand.Alignment.center)]),
            a_new_line(),
            Part("$SEATS_NUMBER {}".format(self.table_report_header_dto.service_seats),
                 [AlignCommand(AlignCommand.Alignment.center)]),
            a_new_line(),
            a_new_line(),
            TableReport(lines=[["$START_HOUR", self._start_hour()]], column_definitions=a_time_column_definition()),
            TableReport(lines=[["$TOTALED_HOUR", self._totaled_hour()]], column_definitions=a_time_column_definition()),
            a_new_line(),
            Part(commands=[RepeatCommand(38, "=")]),
            a_new_line(),

        ]
        return report_header


    def _start_hour(self):
        return "#DATETIME({})".format(self.table_report_header_dto.start_date.isoformat())

    def _totaled_hour(self):
        return "#DATETIME({})".format(self.table_report_header_dto.totaled_date.isoformat())


def a_new_line(commands=None):
    return Part("\n", commands=commands)


def a_time_column_definition():
    return [
        ReportColumnDefinition(width=13,
                               fill_with_char=" ",
                               before_text="",
                               align=AlignTypes.LEFT),
        ReportColumnDefinition(width=25,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.RIGHT)

    ]