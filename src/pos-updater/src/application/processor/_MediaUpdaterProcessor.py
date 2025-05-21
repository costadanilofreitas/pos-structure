from typing import Any

from application.interactor import MediaUpdaterInteractor
from application.model import AsyncUuidMessageProcessor
from messagebus import DefaultToken, DataType, Message


class MediaUpdaterProcessor(AsyncUuidMessageProcessor):
    def __init__(self, interactor):
        # type: (MediaUpdaterInteractor) -> None

        super(MediaUpdaterProcessor, self).__init__()
        self.interactor = interactor

    def parse_data(self, data):
        # type: (Any) -> Any
        return data or self._do_not_remove_this_function_bug_in_the_library()

    def call_business(self, _):
        # type: (Any) -> Any
        return self.interactor.update_media()

    @staticmethod
    def format_response(message_bus, message, _, __, response):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.param, response))

    @staticmethod
    def format_exception(message_bus, message, _, __, exception):
        reply_message = Message(DefaultToken.TK_SYS_NAK, DataType.param, str(type(exception).__name__))
        message_bus.reply_message(message, reply_message)

    @staticmethod
    def format_parse_exception(message_bus, message, _, __, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    @staticmethod
    def _do_not_remove_this_function_bug_in_the_library():
        return ''
