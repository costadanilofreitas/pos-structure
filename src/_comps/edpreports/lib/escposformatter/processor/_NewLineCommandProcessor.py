from report.command import NewLineCommand

from .._CommandProcessor import CommandProcessor


class NewLineCommandProcessor(CommandProcessor):
    def get_bytes(self, command):
        if not isinstance(command, NewLineCommand):
            return ""

        return "\n"
