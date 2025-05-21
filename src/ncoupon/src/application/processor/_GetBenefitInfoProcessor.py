import json

from application.interactor import GetBenefitInfoInteractor
from application.model import AsyncUuidMessageProcessor
from messagebus import DefaultToken, DataType, Message, MessageBus, Event
from typing import Optional, Any


class GetBenefitInfoProcessor(AsyncUuidMessageProcessor):
    
    def __init__(self, interactor):
        # type: (GetBenefitInfoInteractor) -> None

        super(GetBenefitInfoProcessor, self).__init__()
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> str

        parsed_data = json.loads(data)
        pos_id = int(parsed_data.get("posId"))
        benefit_id = str(parsed_data.get("voucherId"))
        return pos_id, benefit_id

    def call_business(self, params):
        # type: ((int, str)) -> str

        pos_id, benefit_id = params
        return self.interactor.get_benefit_info(pos_id, benefit_id)

    def format_response(self, message_bus, message, event, request, response):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, Any) -> None
        
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, BaseException) -> None
        
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], bytes, BaseException) -> None
        
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
