import datetime

from basereport import TableReport, ReportColumnDefinition, AlignTypes
from commons.dto import DefaultHeaderDto  # noqa


class DefaultHeaderFormatter(object):
    def __init__(self, translator):
        self.report_lines = []
        self.translator = translator
        self.translated_messages = {}

    def format_header(self, title, header_dto, pos_id):
        # type: (title, DefaultHeaderDto) -> []
        self.translated_messages = self.translator.translate_labels(["$STORE",
                                                                     "$POS",
                                                                     "$ALL",
                                                                     "$OPERATOR",
                                                                     "$PERIOD",
                                                                     "$CURRENT_DATE"
                                                                     ],
                                                                    pos_id)

        self._append_header_informations(header_dto, title)

        table_formatter = TableReport([
            ReportColumnDefinition(width=13, fill_with_char='.'),
            ReportColumnDefinition(width=25, before_text=': ')
        ])

        return table_formatter.format(self.report_lines)

    def _append_header_informations(self, header_dto, title):
        self._append_line_separator()
        self._append_title(title)
        self._append_store_pos(header_dto)
        self._append_operator(header_dto)
        self._append_period(header_dto)
        self._append_current_date()
        self._append_line_separator()

    def _append_line_separator(self):
        self.report_lines.append([ReportColumnDefinition(
            fill_with_char='='
        )])

    def _append_title(self, title):
        self.report_lines.append([ReportColumnDefinition(
            text=title,
            align=AlignTypes.CENTER
        )])

    def _append_store_pos(self, header_transfer_dto):
        title = self.translated_messages["$STORE"] + "/" + self.translated_messages["$POS"]
        pos = str(header_transfer_dto.pos) if header_transfer_dto.pos is not None else self.translated_messages["$ALL"]
        value = (str(header_transfer_dto.store) + "/" + pos)

        self.report_lines.append([title, value])

    def _append_operator(self, header_transfer_dto):
        title = self.translated_messages["$OPERATOR"]
        operator = str(header_transfer_dto.operator) if header_transfer_dto.pos is not None \
            else self.translated_messages["$ALL"]
        value = operator

        self.report_lines.append([title, value])

    def _append_period(self, header_transfer_dto):
        title = self.translated_messages["$PERIOD"]
        value = str(header_transfer_dto.period)

        self.report_lines.append([title, value])

    def _append_current_date(self):
        title = self.translated_messages["$CURRENT_DATE"]
        value = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        self.report_lines.append([title, value])
