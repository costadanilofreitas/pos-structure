from xml.etree import cElementTree as eTree

from application.interactor import OrderModifiedTotalInteractor
from application.model import AsyncUuidMessageProcessor
from messagebus import DefaultToken, DataType, Message, MessageBus, Event
from typing import Optional, Any


class OrderModifiedTotalProcessor(AsyncUuidMessageProcessor):
    
    def __init__(self, interactor):
        # type: (OrderModifiedTotalInteractor) -> None

        super(OrderModifiedTotalProcessor, self).__init__()
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> (str, str, eTree)

        order_picture = eTree.XML(data).find(".//Order")
        pos_id = order_picture.get("posId")
        order_id = order_picture.get("orderId")

        return pos_id, order_id, order_picture

    def call_business(self, params):
        # type: ((str, str, eTree)) -> None

        pos_id, order_id, order_picture = params
        return self.interactor.apply_benefit_tenders(pos_id, order_id, order_picture)

    def format_response(self, message_bus, message, event, request, response):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, Any) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, BaseException) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], bytes, BaseException) -> None
        
        message_bus.reply_event(event, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
