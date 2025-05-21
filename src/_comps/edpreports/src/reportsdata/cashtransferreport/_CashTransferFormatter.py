from commons.dto import ReportColumnDefinition, AlignTypes
from commons.report import Formatter
from commons.util import TableReport, DefaultHeaderFormatter
from reports_app.cashtransferreport.dto import CashTransferReportDto  # noqa


class CashTransferFormatter(Formatter):
    def __init__(self):
        super(CashTransferFormatter, self).__init__()
        self.translated_messages = {}

    def format_report(self, cash_transfer_report_dto, translator):
        # type: (CashTransferReportDto) -> None
        self.translated_messages = translator.translate_labels(["$CASH_OUT_TITLE",
                                                                "$CASH_IN_TITLE",
                                                                "$BUSINESS_DAY",
                                                                "$STORE",
                                                                "$POS",
                                                                "$OPERATOR",
                                                                "$PERIOD",
                                                                "$CURRENT_DATE",
                                                                "$TYPE",
                                                                "$OP",
                                                                "$HOUR",
                                                                "$VALUE",
                                                                "$MANAGER_MENU",
                                                                "$LOGOUT",
                                                                "$LOGIN",
                                                                "$MANAGER_MENU_CASH_TRANSFER_REPORT"
                                                                ],
                                                               cash_transfer_report_dto.pos_id)

        report = self._append_header(cash_transfer_report_dto, translator)
        report += self._append_body(cash_transfer_report_dto)
        report_bytes = report.decode("utf-8").encode("utf-8")
        return report_bytes

    def _append_body(self, cash_transfer_report_dto):
        report_body_lines = []

        self._append_transfers_title(report_body_lines)
        self._append_transfers(cash_transfer_report_dto, report_body_lines)
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
            ReportColumnDefinition(text='', width=15, fill_with_char='', before_text='', after_text='',
                                   align=AlignTypes.LEFT),
            ReportColumnDefinition(text='', width=7, fill_with_char='', before_text='', after_text='',
                                   align=AlignTypes.LEFT),
            ReportColumnDefinition(text='', width=6, fill_with_char='', before_text='', after_text='',
                                   align=AlignTypes.LEFT),
            ReportColumnDefinition(text='', width=10, fill_with_char='', before_text='', after_text='',
                                   align=AlignTypes.RIGHT)
        ])
        return table_formatter.format(report_body_lines)

    def _append_transfers(self, cash_transfer_report_dto, report_body_lines):
        for all_transfers in cash_transfer_report_dto.all_transfers_dto:
            self._append_transfers_date(all_transfers, report_body_lines)

            for transfer in all_transfers.transfers_by_date:
                self._append_transfers_info(transfer, report_body_lines)

    def _append_transfers_info(self, transfer, report_body_lines):
        report_body_lines.append(
            [self.translated_messages[transfer.transfer_type].upper(),
             transfer.transfer_operator,
             transfer.transfer_date.strftime("%H:%M"),
             (str(transfer.transfer_value))])

    @staticmethod
    def _append_transfers_date(transfers_by_day, report_body_lines):
        report_body_lines.append([ReportColumnDefinition(
            text=transfers_by_day.day,
            fill_with_char='-',
            before_text=' ',
            after_text=' ',
            align=AlignTypes.CENTER
        )])

    def _append_header(self, cash_transfer_report_dto, translator):
        default_header_formatter = DefaultHeaderFormatter(translator)
        if cash_transfer_report_dto.header_transfer_dto.report_type == 'cash_out':
            title = "{} ({})".format(self.translated_messages["$CASH_OUT_TITLE"],
                                     self.translated_messages["$BUSINESS_DAY"].upper())
        else:
            title = "{} ({})".format(self.translated_messages["$CASH_IN_TITLE"],
                                     self.translated_messages["$BUSINESS_DAY"].upper())

        return default_header_formatter.format_header(
            title, cash_transfer_report_dto.header_transfer_dto, cash_transfer_report_dto.pos_id)

    def _append_transfers_title(self, report_body_lines):
        report_body_lines.append([self.translated_messages["$TYPE"],
                                  self.translated_messages["$OP"],
                                  self.translated_messages["$HOUR"],
                                  self.translated_messages["$VALUE"] + "(R$)"])
