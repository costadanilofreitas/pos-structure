import datetime

from commons.dto import ReportColumnDefinition, AlignTypes
from commons.report import Formatter
from commons.util import TableReport
from reports_app.loginsummary.dto import LoginSummaryDto  # noqa
from reports_app.loginsummary.dto import LoginSummaryHeaderDto  # noqa


class LoginFormatter(Formatter):
    def __init__(self):
        self.report_lines = []
        self.translated_messages = []

    def format_report(self, login_summary_dto, translator):
        # type: (LoginSummaryDto) -> None
        self.translated_messages = translator.translate_labels(["$LOGIN",
                                                                "$STORE",
                                                                "$POS",
                                                                "$OPERATOR",
                                                                "$CURRENT_DATE",
                                                                "$BUSINESS_DATE",
                                                                "$LOGIN_TIME",
                                                                "$POS_TYPE",
                                                                "$AUTHORIZER",
                                                                "$INITIAL_VALUE"
                                                                ],
                                                               login_summary_dto.login_summary_header_dto.pos_id)

        report = self._append_header(login_summary_dto.login_summary_header_dto)
        report += self._append_body(login_summary_dto.login_summary_body_dto)

        report_bytes = report.decode("utf-8").encode("utf-8")
        return report_bytes

    def _append_header(self, login_summary_header_dto):
        # type: (LoginSummaryHeaderDto) -> str
        self._append_line_separator()
        self._append_title()
        self._append_store_pos(login_summary_header_dto.store_id, login_summary_header_dto.pos_id)
        self._append_operator(login_summary_header_dto.operator_id)
        self._append_current_date()
        self._append_business_date(login_summary_header_dto.business_date)

        table_formatter = TableReport([
            ReportColumnDefinition(width=17, fill_with_char='.'),
            ReportColumnDefinition(width=21, before_text=': ')
        ])

        return table_formatter.format(self.report_lines)

    def _append_body(self, login_summary_body_dto):
        self.report_lines = []

        self._append_empty_line()

        self._append_pos_type(login_summary_body_dto.pos_type)
        self._append_authorizer(login_summary_body_dto.authorizer)

        self._append_initial_value(login_summary_body_dto.initial_value)
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

    def _append_title(self):
        title = self.translated_messages["$LOGIN"]

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

    def _append_pos_type(self, pos_type):
        self.report_lines.append([self.translated_messages["$POS_TYPE"], str(pos_type)])

    def _append_initial_value(self, initial_value):
        self.report_lines.append([self.translated_messages["$INITIAL_VALUE"], ("R$ " + str(initial_value))])
