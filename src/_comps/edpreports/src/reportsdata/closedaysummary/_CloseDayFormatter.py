import datetime

from commons.dto import ReportColumnDefinition, AlignTypes
from commons.report import Formatter
from commons.util import TableReport
from reports_app.closedaysummary.dto import CloseDaySummaryDto  # noqa
from reports_app.closedaysummary.dto import CloseDaySummaryHeaderDto  # noqa


class CloseDayFormatter(Formatter):
    def __init__(self):
        self.report_lines = []
        self.translated_messages = []

    def format_report(self, close_day_summary_dto, translator):
        # type: (CloseDaySummaryDto) -> None
        self.translated_messages = translator.translate_labels(
            ["$CLOSE_DAY",
             "$STORE",
             "$POS",
             "$OPERATOR",
             "$CURRENT_DATE",
             "$BUSINESS_DATE",
             "$OPEN_DAY",
             "$AUTHORIZER",
             "$TYPE",
             "$QTY",
             "$VALUE",
             "$INITIAL_BALANCE",
             "$SALES",
             "$VOIDED_ORDERS",
             "$DISCOUNTS",
             "$DONATIONS",
             "$LIQUID_SALES",
             "$TENDER_TYPES",
             "$CASH_OUT",
             "$CASH_IN",
             "$VALUE_IN_DRAWER"
             ],
            close_day_summary_dto.close_day_summary_header_dto.pos_id)

        report = self._append_header(close_day_summary_dto.close_day_summary_header_dto,
                                     close_day_summary_dto.close_day_summary_body_dto)
        report += self._append_body(close_day_summary_dto.close_day_summary_body_dto)

        report_bytes = report.decode("utf-8").encode("utf-8")
        return report_bytes

    def _append_header(self, close_day_summary_header_dto, close_day_summary_body_dto):
        # type: (CloseDaySummaryHeaderDto, CloseDaySummaryBodyDto) -> str
        self._append_line_separator()
        self._append_title()
        self._append_store_pos(close_day_summary_header_dto.store_id, close_day_summary_header_dto.pos_id)
        self._append_operator(close_day_summary_header_dto.operator_id)
        self._append_current_date()
        self._append_business_date(close_day_summary_header_dto.business_date)
        self._append_empty_line()

        self._append_open_day_time(close_day_summary_body_dto.open_day_time)
        self._append_authorizer(close_day_summary_body_dto.authorizer)

        table_formatter = TableReport([
            ReportColumnDefinition(width=17, fill_with_char='.'),
            ReportColumnDefinition(width=21, before_text=': ')
        ])

        return table_formatter.format(self.report_lines)

    def _append_body(self, close_day_summary_body_dto):
        self.report_lines = []

        self._append_line_separator()

        self._append_report_body_title(self.report_lines)
        self._append_body_items(close_day_summary_body_dto, self.report_lines)
        self._append_line_separator()
        return self._format_body(self.report_lines)

    def _append_line_separator(self):
        self.report_lines.append([ReportColumnDefinition(
            fill_with_char='='
        )])

    def _append_title(self):
        title = self.translated_messages["$CLOSE_DAY"]

        self.report_lines.append([ReportColumnDefinition(
            text=title,
            align=AlignTypes.CENTER
        )])

    def _append_store_pos(self, store_id, pos_id):
        self.report_lines.append([self.translated_messages["$STORE"] + "/" + self.translated_messages["$POS"],
                                  (str(store_id) + '/' + str(pos_id))])

    def _append_operator(self, operator_id):
        self.report_lines.append([self.translated_messages["$OPERATOR"], str(operator_id)])

    def _append_current_date(self):
        self.report_lines.append([self.translated_messages["$CURRENT_DATE"],
                                  datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")])

    def _append_open_day_time(self, open_day_time):
        self.report_lines.append([self.translated_messages["$OPEN_DAY"], str(open_day_time)])

    def _append_business_date(self, business_date):
        self.report_lines.append([self.translated_messages["$BUSINESS_DATE"], business_date])

    def _append_empty_line(self):
        self.report_lines.append([ReportColumnDefinition(fill_with_char=' ')])

    def _append_authorizer(self, authorizer):
        self.report_lines.append([self.translated_messages["$AUTHORIZER"], str(authorizer)])

    def _append_body_items(self, logout_summary_body_dto, report_body_lines):
        for line in logout_summary_body_dto.report_body:
            self._append_transfers_info(line, report_body_lines)

    def _append_transfers_info(self, report_item, report_body_lines):
        line_type = self.translated_messages["" if report_item.name is None else report_item.name]
        separator_1 = "" if report_item.quantity is None else ": ["

        if report_item.quantity is None:
            quantity = ""
            separator_1 = ":  "
        else:
            quantity = str(report_item.quantity)

        if report_item.value is None and report_item.quantity is None:
            separator_2 = ""
        elif report_item.quantity is None:
            separator_2 = "  R$"
        elif report_item.value is None:
            separator_2 = "]   "
        else:
            separator_2 = "] R$"

        if report_item.value is None:
            value = ""
        else:
            value = str(report_item.value)

        report_body_lines.append([line_type,
                                  separator_1,
                                  quantity,
                                  separator_2,
                                  value])

    def _append_report_body_title(self, report_body_lines):
        report_body_lines.append([
            ReportColumnDefinition(text=self.translated_messages["$TYPE"], width=17),
            ReportColumnDefinition(width=3),
            ReportColumnDefinition(text=self.translated_messages["$QTY"], width=4, align=AlignTypes.RIGHT),
            ReportColumnDefinition(width=4),
            ReportColumnDefinition(text=self.translated_messages["$VALUE"] + "(R$)", width=10, align=AlignTypes.RIGHT)
        ])

    @staticmethod
    def _format_body(report_body_lines):
        table_formatter = TableReport([
            ReportColumnDefinition(width=17, fill_with_char='.'),
            ReportColumnDefinition(text=': [', width=3),
            ReportColumnDefinition(width=4, align=AlignTypes.RIGHT),
            ReportColumnDefinition(text='] R$', width=4),
            ReportColumnDefinition(text='', width=10, align=AlignTypes.RIGHT)
        ])
        return table_formatter.format(report_body_lines)
