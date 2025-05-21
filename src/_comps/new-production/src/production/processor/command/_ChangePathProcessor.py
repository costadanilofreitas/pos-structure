from abc import ABCMeta

from messagebus import AckMessage, NakMessage
from messageprocessorutil import UuidMessageProcessor
from production.command import ChangePathCommand
from production.manager import ProductionManager


class ChangePathProcessor(UuidMessageProcessor):
    __metaclass__ = ABCMeta

    def __init__(self, production_manager):
        # type: (ProductionManager) -> None
        super(ChangePathProcessor, self).__init__()
        self.production_manager = production_manager

    def call_business(self, request):
        change_path_command = ChangePathCommand(request.path, request.enabled)
        self.production_manager.handle_command(change_path_command)

    def format_response(self, message_bus, message, event, input_obj, result):
        message_bus.reply_message(message, AckMessage())

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, NakMessage())

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, NakMessage())
