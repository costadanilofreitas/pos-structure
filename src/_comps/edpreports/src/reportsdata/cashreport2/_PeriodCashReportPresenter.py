from commons.dto import ReportColumnDefinition, AlignTypes
from commons.util import TableReport
from typing import List, Union  # noqa
from reports_app.cashreport2.dto import CashReportDto  # noqa
from report import Part, Presenter, SimpleReport
from report import PartGenerator  # noqa
from report.command import RepeatCommand, AlignCommand


class PeriodCashReportPresenter(Presenter):
    def present(self, dto):
        report = [
            Part(commands=[RepeatCommand(38, "=")]), Part("\n"),
            Part("$PERIOD_CASH_REPORT_{}".format(dto.header.report_type),
                 [AlignCommand(AlignCommand.Alignment.center)]), Part("\n")
        ]

        column_definitions = [
            ReportColumnDefinition(width=17,
                                   fill_with_char=".",
                                   before_text="  ",
                                   after_text="",
                                   after_fill_text=":",
                                   align=AlignTypes.LEFT),
            ReportColumnDefinition(width=22,
                                   fill_with_char=" ",
                                   before_text=" ",
                                   align=AlignTypes.LEFT)
        ]

        pos_label = "$ALL"
        if dto.header.pos is not None:
            pos_label = str(dto.header.pos)

        operator_label = "$ALL"
        if dto.header.operator_id is not None:
            operator_label = "{} - {}".format(dto.header.operator_id, dto.header.operator_name)

        lines = [
            ["$STORE_POS", "{} / {}".format(dto.header.store_code, pos_label)],
            ["$OPERATOR", operator_label],
            ["$PERIOD", "#DATE({})-#DATE({})"
                .format(dto.header.initial_date.isoformat(), dto.header.end_date.isoformat())],
            ["$DATE", "#DATETIME({})".format(dto.header.generated_time.isoformat())]
        ]
        header = TableReport(lines=lines, column_definitions=column_definitions)
        report.append(header)

        report.extend([
            Part(commands=[RepeatCommand(38, "=")]), Part("\n")
        ])

        column_definitions = [
            ReportColumnDefinition(width=18,
                                   fill_with_char=" ",
                                   before_text="",
                                   after_text="",
                                   align=AlignTypes.LEFT),
            ReportColumnDefinition(width=8,
                                   fill_with_char=" ",
                                   before_text="",
                                   align=AlignTypes.LEFT),
            ReportColumnDefinition(width=4,
                                   fill_with_char=" ",
                                   before_text=" ",
                                   align=AlignTypes.LEFT),
            ReportColumnDefinition(width=8,
                                   fill_with_char=" ",
                                   before_text=" ",
                                   align=AlignTypes.LEFT)
        ]

        lines = [["$DESCRIPTION", "$QTY", "", "$TOTAL"]]
        body_header = TableReport(lines=lines, column_definitions=column_definitions)

        report.append(body_header)

        column_definitions = [
            ReportColumnDefinition(width=18,
                                   fill_with_char=".",
                                   before_text="",
                                   after_text="",
                                   after_fill_text=":",
                                   align=AlignTypes.LEFT),
            ReportColumnDefinition(width=8,
                                   fill_with_char=" ",
                                   before_text="[",
                                   after_text="]",
                                   align=AlignTypes.RIGHT),
            ReportColumnDefinition(width=4,
                                   fill_with_char=" ",
                                   before_text="",
                                   after_text="",
                                   align=AlignTypes.RIGHT),
            ReportColumnDefinition(width=8,
                                   fill_with_char=" ",
                                   before_text="",
                                   after_text="",
                                   align=AlignTypes.RIGHT)
        ]

        lines = [
            self.create_report_line("$INITIAL_BALANCE", dto.body.initial_float),
            ["$OPERATORS", str(dto.body.operator_count), "", ""],
            self.create_report_line("$TOTAL_SALES", dto.body.total_sales),
            self.create_report_line("$VOIDS", dto.body.voids),
            self.create_report_line("$NET_SALES", dto.body.net_sales)
        ]

        for tender in dto.body.tender_breakdown:
            lines.append(self.create_report_line("  $TENDER_{}".format(tender.detail), tender))

        lines.extend([
            self.create_report_line("$CASH_OUTS", dto.body.cash_outs),
            self.create_report_line("$CASH_INS", dto.body.cash_ins),
            ["$VALUE_IN_DRAWER", "", "#CURRENCY_SYMBOL()", "#NUMBER({0:.6f})".format(dto.body.value_in_drawer)]
        ])

        report.append(TableReport(lines=lines, column_definitions=column_definitions))

        report.append(Part(commands=[RepeatCommand(38, "=")]))
        return SimpleReport(report)

    def create_report_line(self, label, report_line):
        return [label,
                str(report_line.quantity),
                "#CURRENCY_SYMBOL()",
                "#NUMBER({0:.6f})".format(report_line.value)]
