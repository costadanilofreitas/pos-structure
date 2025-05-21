from application.interactor import UserUpdaterInteractor
from application.model import AsyncUuidMessageProcessor
from messagebus import DefaultToken, DataType, Message
from typing import Any


class LoaderUpdaterProcessor(AsyncUuidMessageProcessor):
    def __init__(self, interactor):
        # type: (UserUpdaterInteractor) -> None

        super(LoaderUpdaterProcessor, self).__init__()
        self.interactor = interactor

    @staticmethod
    def parse_data(data):
        # type: (Any) -> Any

        restart_hv = data.lower() == "true" if data else "false"
        return restart_hv

    def call_business(self, restart_hv):
        # type: (Any) -> Any
        
        return self.interactor.update_loaders(True, restart_hv)

    @staticmethod
    def format_response(message_bus, message, event, _, response):
        reply_message = Message(DefaultToken.TK_SYS_ACK, DataType.param, response)
        if message:
            message_bus.reply_message(message, reply_message)
        elif event:
            message_bus.reply_event(event, reply_message)

    def format_exception(self, message_bus, message, event, _, exception):
        self._reply_exception(event, exception, message, message_bus)

    def format_parse_exception(self, message_bus, message, event, _, exception):
        self._reply_exception(event, exception, message, message_bus)

    @staticmethod
    def _reply_exception(event, exception, message, message_bus):
        reply_message = Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception))
        if message:
            reply_message = Message(DefaultToken.TK_SYS_NAK, DataType.param, str(type(exception).__name__))
            message_bus.reply_message(message, reply_message)
        elif event:
            message_bus.reply_event(event, reply_message)
