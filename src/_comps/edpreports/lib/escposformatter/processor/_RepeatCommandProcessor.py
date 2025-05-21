from escposformatter import CommandProcessor
from report.command import RepeatCommand


class RepeatCommandProcessor(CommandProcessor):
    def get_bytes(self, command):
        if not isinstance(command, RepeatCommand):
            return ""

        return command.text*command.count
