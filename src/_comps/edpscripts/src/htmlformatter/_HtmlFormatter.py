from report import Formatter
from report.command import BoldCommand, NewLineCommand, AlignCommand, RepeatCommand


class HtmlFormatter(Formatter):
    def __init__(self):
        self.bold_start_index = -1
        self.bold_end_index = -1
        self.is_bold = False
        self.current_alignment = AlignCommand.Alignment.left

        self.current_line = ""
        self.body = ""

    def format(self, report):
        self.handle_new_line(report)

        for part in report.get_parts():
            if part.commands is not None:
                for command in part.commands:
                    if isinstance(command, BoldCommand):
                        self.handle_bold(command)
                    if isinstance(command, NewLineCommand):
                        self.handle_new_line(report)
                    if isinstance(command, AlignCommand):
                        self.current_alignment = command.alignment
                    if isinstance(command, RepeatCommand):
                        self.current_line += command.text * command.count

            if part.text is not None:
                if (part.commands is None or len(part.commands) == 0) and part.text == "\n":
                    self.handle_new_line(report)
                else:
                    self.current_line += part.text

        if self.current_line != "":
            self.handle_new_line(report)

        return self.body

    def handle_bold(self, command):
        if command.activate and not self.is_bold:
            self.bold_start_index = len(self.current_line)
            self.is_bold = True
        if not command.activate and self.is_bold:
            self.bold_end_index = len(self.current_line)
            self.is_bold = False

    def handle_new_line(self, report):
        formatted_text = self.create_formatted_text(self.current_line, report)
        self.add_line_to_body(formatted_text)
        self.current_line = ""

    def add_line_to_body(self, formatted_text):
        self.body += "<span style='font-family: monospace;font-size: 1.3em'>" + formatted_text + "</span>"
        self.body += "<br/>"

    def create_formatted_text(self, line, report):
        formatted_text = line
        if len(line) > report.get_width():
            formatted_text = line[0: report.get_width()]
        elif len(line) < report.get_width():
            if self.current_alignment == AlignCommand.Alignment.left:
                formatted_text += (" " * (report.get_width() - len(line)))
            elif self.current_alignment == AlignCommand.Alignment.right:
                formatted_text = (" " * (report.get_width() - len(line))) + formatted_text
            else:
                pre_space = int((report.get_width() - len(line)) / 2)
                post_space = report.get_width() - len(line) - pre_space
                formatted_text = (" " * pre_space) + formatted_text + (" " * post_space)
        before_bold = formatted_text
        bold_text = ""
        after_bold = ""
        if self.bold_start_index >= 0:
            if self.bold_end_index >= 0:
                before_bold = formatted_text[0: self.bold_start_index]
                bold_text = formatted_text[self.bold_start_index: self.bold_end_index]
                after_bold = formatted_text[self.bold_end_index:]

                self.bold_start_index = -1
                self.bold_end_index = -1

            else:
                before_bold = formatted_text[0: self.bold_start_index]
                bold_text = formatted_text[self.bold_start_index:]
                after_bold = ""

                self.bold_start_index = 0
        formatted_text = before_bold.replace(" ", "&nbsp;")
        if bold_text != "":
            formatted_text += "<span style='font-weight: bold;font-family: monospace;font-size: 1.3em'>" + bold_text.replace(" ", "&nbsp;") + "</span>"
        formatted_text += after_bold.replace(" ", "&nbsp;")

        return formatted_text
