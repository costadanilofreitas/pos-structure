from report.command import AlignCommand, BoldCommand

from .._CommandProcessor import CommandProcessor


class BoldCommandProcessor(CommandProcessor):
    def get_bytes(self, command):
        if not isinstance(command, BoldCommand):
            return ""
        
        ret = b"\x45"
        if command.activate:
            ret += "\x00"
        else:
            ret += "\x01"

        return ret
