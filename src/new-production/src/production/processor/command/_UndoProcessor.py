from production.command import CommandType
from production.model.request import UndoRequest

from ._CommandProcessor import CommandProcessor


class UndoProcessor(CommandProcessor):
    def get_command_type(self):
        return CommandType.undo

    def parse_data(self, data):
        return UndoRequest(data.split('\0')[0])
