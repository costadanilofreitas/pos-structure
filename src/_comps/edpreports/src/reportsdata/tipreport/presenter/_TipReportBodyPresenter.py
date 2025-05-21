from typing import List

from basereport import TableReport, ReportColumnDefinition, AlignTypes
from report import Presenter, Part
from report.command import RepeatCommand
from ..dto import TipReportBodyDto


class TipReportBodyPresenter(Presenter):
    def present(self, dto):
        # type: (TipReportBodyDto) -> List[TableReport]
        report_body = []

        detail_lines = [["$TIP_REPORT_OPERATOR", "$TIP_REPORT_TABLES", "$TIP_REPORT_ORDERS", "#CURRENCY_SYMBOL()", "$TIP_REPORT_TIP"]]
        for detail_line in dto.detail_line_list:
            detail_lines.append([
                detail_line.operator,
                detail_line.table_count,
                detail_line.order_count,
                "#NUMBER({})".format(detail_line.total_sold_amount),
                "#NUMBER({})".format(detail_line.tip_amount)
            ])

        report_body.append(TableReport(lines=detail_lines, column_definitions=a_item_column_definition()))

        report_body.extend([Part(commands=[RepeatCommand(38, "=")]), a_new_line()])

        totalized_line = [
            [
            "$TOTAL",
            dto.total_tables_count,
            dto.total_order_count,
            "#NUMBER({})".format(dto.total_sold_amount),
            "#NUMBER({})".format(dto.total_tip_amount)
            ]
        ]

        report_body.append(TableReport(lines=totalized_line, column_definitions=a_item_column_definition()))

        return report_body

def a_new_line():
    return Part("\n")


def a_item_column_definition():
    return [
        ReportColumnDefinition(width=8,
                               before_text="",
                               after_text="",
                               after_fill_text="",
                               align=AlignTypes.CENTER),
        ReportColumnDefinition(width=7,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.CENTER),
        ReportColumnDefinition(width=7,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.CENTER),
        ReportColumnDefinition(width=8,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.CENTER),
        ReportColumnDefinition(width=8,
                               fill_with_char="",
                               before_text="",
                               align=AlignTypes.CENTER)
    ]
