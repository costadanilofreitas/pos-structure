import json

from application.interactor import ApplyBenefitInteractor
from application.model import AsyncUuidMessageProcessor
from messagebus import DefaultToken, DataType, Message, MessageBus, Event
from typing import Optional, Any


class ApplyBenefitProcessor(AsyncUuidMessageProcessor):
    
    def __init__(self, interactor):
        # type: (ApplyBenefitInteractor) -> None

        super(ApplyBenefitProcessor, self).__init__()
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> str

        parsed_data = json.loads(data)
        pos_id = int(parsed_data.get("posId"))
        voucher_id = str(parsed_data.get("voucherId"))
        return pos_id, voucher_id

    def call_business(self, params):
        # type: ((int, str)) -> None

        pos_id, voucher_id = params
        self.interactor.apply_benefit(pos_id, voucher_id)

    def format_response(self, message_bus, message, event, request, response):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, Any) -> None
        
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, BaseException) -> None
        
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], bytes, BaseException) -> None
        
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
