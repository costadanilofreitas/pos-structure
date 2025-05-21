from unicodedata import normalize

from report import Formatter

from _CommandFactory import CommandFactory

ESC = b'\x1b'


class EscPosFormatter(Formatter):
    def __init__(self, encoding="cp860", command_factory=None):
        # type: (str, CommandFactory) -> None
        self.encoding = encoding
        self.command_factory = command_factory

    def format(self, report):
        body = self.create_report_body(report.get_parts())
        if body == "":
            return body

        content = self._get_page_command() + body
        return EscPosFormatter._remove_accents(content).encode(self.encoding)

    def create_report_body(self, parts):
        body = ""
        for part in parts:
            if part.commands is not None:
                for command in part.commands:
                    body += self.command_factory.get_processor(command).get_bytes(command)
            if part.text is not None:
                body += part.text
        return body

    def _get_page_command(self):
        if self.encoding == "cp850":
            return ESC + 't' + '\x02'
        else:
            return ESC + 't' + '\x03'

    @staticmethod
    def _remove_accents(text):
        return normalize('NFKD', unicode(text)).encode('ASCII', 'ignore')
