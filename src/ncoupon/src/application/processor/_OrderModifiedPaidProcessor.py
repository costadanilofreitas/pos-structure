from xml.etree import cElementTree as eTree

from application.interactor import OrderModifiedPaidInteractor
from application.model import AsyncUuidMessageProcessor
from messagebus import DefaultToken, DataType, Message, MessageBus, Event
from typing import Optional, Any


class OrderModifiedPaidProcessor(AsyncUuidMessageProcessor):
    
    def __init__(self, interactor):
        # type: (OrderModifiedPaidInteractor) -> None

        super(OrderModifiedPaidProcessor, self).__init__()
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> eTree

        order_picture = eTree.XML(data).find(".//Order")
        pos_id = int(order_picture.get("posId"))

        return pos_id, order_picture

    def call_business(self, params):
        # type: ((int, eTree)) -> None

        pos_id, order_picture = params
        return self.interactor.burn_paid_benefit(pos_id, order_picture)

    def format_response(self, message_bus, message, event, request, response):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, Any) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, BaseException) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], bytes, BaseException) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
