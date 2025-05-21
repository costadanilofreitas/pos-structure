from xml.etree import cElementTree as eTree

from application.interactor import OrderModifiedVoidInteractor
from application.model import AsyncUuidMessageProcessor
from messagebus import DefaultToken, DataType, Message, MessageBus, Event
from typing import Optional, Any


class OrderModifiedVoidProcessor(AsyncUuidMessageProcessor):
    
    def __init__(self, interactor):
        # type: (OrderModifiedVoidInteractor) -> None

        super(OrderModifiedVoidProcessor, self).__init__()
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> eTree

        order_picture = eTree.XML(data).find(".//Order")
        pos_id = int(order_picture.get("posId"))

        return pos_id, order_picture

    def call_business(self, params):
        # type: ((int, eTree)) -> None

        pos_id, order_picture = params
        self.interactor.unlock_voided_benefit(pos_id, order_picture)

    def format_response(self, message_bus, message, event, request, response):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, Any) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, BaseException) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], bytes, BaseException) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
