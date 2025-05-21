import datetime

from commons.dto import ReportColumnDefinition, AlignTypes
from commons.report import Formatter
from commons.util import TableReport
from reports_app.cashtransfersummary.dto import CashTransferSummaryDto  # noqa
from reports_app.cashtransfersummary.dto import CashTransferSummaryHeaderDto  # noqa


class CashTransferFormatter(Formatter):
    def __init__(self):
        self.report_lines = []
        self.translated_messages = []

    def format_report(self, cash_transfer_summary_dto, translator):
        # type: (CashTransferSummaryDto) -> None
        self.translated_messages = translator.translate_labels(["$CASH_OUT_TITLE",
                                                                "$CASH_IN_TITLE",
                                                                "$BUSINESS_DATE",
                                                                "$STORE",
                                                                "$POS",
                                                                "$OPERATOR",
                                                                "$AUTHORIZER",
                                                                "$CURRENT_DATE",
                                                                "$BUSINESS_DATE",
                                                                "$ENVELOPE_NUMBER",
                                                                "$VALUE"
                                                                ],
                                                               cash_transfer_summary_dto.cash_transfer_summary_header_dto.pos_id)

        report = self._append_header(cash_transfer_summary_dto.cash_transfer_summary_header_dto)
        report += self._append_body(cash_transfer_summary_dto.cash_transfer_summary_body_dto)

        report_bytes = report.decode("utf-8").encode("utf-8")
        return report_bytes

    def _append_header(self, cash_transfer_summary_header_dto):
        # type: (CashTransferSummaryHeaderDto) -> str
        self._append_line_separator()
        self._append_title(cash_transfer_summary_header_dto.cash_out)
        self._append_store_pos(cash_transfer_summary_header_dto.store_id, cash_transfer_summary_header_dto.pos_id)
        self._append_operator(cash_transfer_summary_header_dto.operator_id)
        self._append_current_date()
        self._append_business_date(cash_transfer_summary_header_dto.business_date)

        table_formatter = TableReport([
            ReportColumnDefinition(width=17, fill_with_char='.'),
            ReportColumnDefinition(width=21, before_text=': ')
        ])

        return table_formatter.format(self.report_lines)

    def _append_body(self, cash_transfer_summary_body_dto):
        self.report_lines = []

        self._append_empty_line()

        if cash_transfer_summary_body_dto.cash_out:
            self._append_authorizer(cash_transfer_summary_body_dto.authorizer)
            self._append_envelope_number(cash_transfer_summary_body_dto.envelope_number)

        self._append_value(cash_transfer_summary_body_dto.value)
        self._append_line_separator()

        table_formatter = TableReport([
            ReportColumnDefinition(width=17, fill_with_char='.'),
            ReportColumnDefinition(width=21, before_text=': ')
        ])

        return table_formatter.format(self.report_lines)

    def _append_line_separator(self):
        self.report_lines.append([ReportColumnDefinition(
            fill_with_char='='
        )])

    def _append_title(self, cash_in_cash_out):
        title = self.translated_messages["$CASH_OUT_TITLE"] if \
            (cash_in_cash_out == 'cash_out' or cash_in_cash_out is True) else self.translated_messages["$CASH_IN_TITLE"]

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

    def _append_business_date(self, business_date):
        self.report_lines.append([self.translated_messages["$BUSINESS_DATE"], business_date])

    def _append_empty_line(self):
        self.report_lines.append([ReportColumnDefinition(fill_with_char=' ')])

    def _append_authorizer(self, authorizer):
        self.report_lines.append([self.translated_messages["$AUTHORIZER"], str(authorizer)])

    def _append_envelope_number(self, envelope_number):
        self.report_lines.append([self.translated_messages["$ENVELOPE_NUMBER"], str(envelope_number)])

    def _append_value(self, value):
        self.report_lines.append([self.translated_messages["$VALUE"], ("R$ " + str(value))])
