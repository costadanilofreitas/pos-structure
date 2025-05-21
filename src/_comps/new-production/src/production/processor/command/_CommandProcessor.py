from abc import ABCMeta, abstractmethod

from messagebus import AckMessage, NakMessage
from messageprocessorutil import UuidMessageProcessor
from production.box import ViewBox
from production.command import Command, CommandType
from production.model.request import ChangeProdStateRequest
from typing import List, Dict


class CommandProcessor(UuidMessageProcessor):
    __metaclass__ = ABCMeta

    def __init__(self, view_boxes):
        # type: (List[ViewBox]) -> None
        super(CommandProcessor, self).__init__()
        self.view_boxes = {}  # type: Dict[str, ViewBox]
        for box in view_boxes:
            self.view_boxes[box.get_view_name()] = box

    def call_business(self, request):
        # type: (ChangeProdStateRequest) -> None
        if request.view not in self.view_boxes:
            return None

        view_box = self.view_boxes[request.view]
        view_box.handle_view_command(Command(self.get_command_type(), request))

    def format_response(self, message_bus, message, event, input_obj, result):
        message_bus.reply_message(message, AckMessage())

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, NakMessage())

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, NakMessage())

    @abstractmethod
    def get_command_type(self):
        # type: () -> CommandType
        raise NotImplementedError()
