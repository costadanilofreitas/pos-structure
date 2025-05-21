from report.command import AlignCommand

from .._CommandProcessor import CommandProcessor


class AlignCommandProcessor(CommandProcessor):
    def get_bytes(self, command):
        if not isinstance(command, AlignCommand):
            return ""
        
        ret = b"\x1b\x61"
        if command.alignment == AlignCommand.Alignment.left:
            ret += "\x00"
        elif command.alignment == AlignCommand.Alignment.center:
            ret += "\x01"
        elif command.alignment == AlignCommand.Alignment.right:
            ret += "\x02"
        else:
            return ""

        return ret
