from commons.dto import ReportColumnDefinition, AlignTypes
from commons.report import Formatter
from commons.util import TableReport, DefaultHeaderFormatter
from reports_app.cashreport.dto import CashReportDto  # noqa


class CashReportFormatter(Formatter):
    def __init__(self):
        super(CashReportFormatter, self).__init__()
        self.translated_messages = {}

    def format_report(self, cash_report_dto, translator):
        # type: (CashReportDto) -> None
        self.translated_messages = translator.translate_labels(["$CASH_REPORT_BY_REAL_DATE_REPORT_TITLE",
                                                                "$CASH_REPORT_BY_BUSINESS_PERIOD_REPORT_TITLE",
                                                                "$CASH_REPORT_BY_XML_REPORT_TITLE",
                                                                "$CASH_REPORT_BY_SESSION_ID_REPORT_TITLE",
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
                                                               cash_report_dto.pos_id)

        report = self._append_header(cash_report_dto, translator)
        report += self._append_body(cash_report_dto)
        report_bytes = report.decode("utf-8").encode("utf-8")
        return report_bytes

    def _append_body(self, cash_report_dto):
        report_body_lines = []

        self._append_report_body_title(report_body_lines)
        self._append_body_items(cash_report_dto, report_body_lines)
        self._append_line_separator(report_body_lines)
        return self._format_body(report_body_lines)

    @staticmethod
    def _append_line_separator(report_body_lines):
        report_body_lines.append([ReportColumnDefinition(
            fill_with_char='='
        )])

    @staticmethod
    def _format_body(report_body_lines):
        table_formatter = TableReport([
            ReportColumnDefinition(text='', width=17, fill_with_char='.', align=AlignTypes.LEFT),
            ReportColumnDefinition(text=': [', width=3),
            ReportColumnDefinition(text='', width=4, fill_with_char='', before_text='', after_text='',
                                   align=AlignTypes.RIGHT),
            ReportColumnDefinition(text='] R$', width=4),
            ReportColumnDefinition(text='', width=10, fill_with_char='', before_text='', after_text='',
                                   align=AlignTypes.RIGHT)
        ])
        return table_formatter.format(report_body_lines)

    def _append_body_items(self, cash_report_dto, report_body_lines):
        for line in cash_report_dto.report_body_dto.cash_report_body_lines_dto:
            self._append_transfers_info(line, report_body_lines)

    def _append_transfers_info(self, report_item, report_body_lines):
        line_type = self.translated_messages["" if report_item.name is None else report_item.name].upper()
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

    def _append_header(self, cash_report_dto, translator):
        default_header_formatter = DefaultHeaderFormatter(translator)
        if cash_report_dto.report_header_dto.report_type == 'report_by_real_date':
            title = self.translated_messages["$CASH_REPORT_BY_REAL_DATE_REPORT_TITLE"]
        if cash_report_dto.report_header_dto.report_type == 'report_by_business_period':
            title = self.translated_messages["$CASH_REPORT_BY_BUSINESS_PERIOD_REPORT_TITLE"]
        if cash_report_dto.report_header_dto.report_type == 'report_by_session_id':
            title = self.translated_messages["$CASH_REPORT_BY_SESSION_ID_REPORT_TITLE"]
        if cash_report_dto.report_header_dto.report_type == 'report_by_xml':
            title = self.translated_messages["$CASH_REPORT_BY_XML_REPORT_TITLE"]

        return default_header_formatter.format_header(title, cash_report_dto.report_header_dto, cash_report_dto.pos_id)

    def _append_report_body_title(self, report_body_lines):
        report_body_lines.append([
            ReportColumnDefinition(text=self.translated_messages["$TYPE"], width=17),
            ReportColumnDefinition(text='', width=3),
            ReportColumnDefinition(text=self.translated_messages["$QTY"], width=4, align=AlignTypes.RIGHT),
            ReportColumnDefinition(text='', width=4),
            ReportColumnDefinition(text=self.translated_messages["$VALUE"] + '(R$)', width=10, align=AlignTypes.RIGHT)
        ])
