from report.command import FontCommand

from .._CommandProcessor import CommandProcessor


class FontCommandProcessor(CommandProcessor):
    def get_bytes(self, command):
        if not isinstance(command, FontCommand):
            return ""

        esc = b'\x1b'
        _set_font = lambda n: esc + b'\x4d' + n

        if command.font == FontCommand.Font.A:
            ret = _set_font(b'\x00')
        elif command.font == FontCommand.Font.B:
            ret = _set_font(b'\x01')
        else:
            return ""

        return ret
