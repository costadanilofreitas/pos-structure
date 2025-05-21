import json
from typing import Any

from application.interactor import GetAndLockVoucherInteractor
from application.model import AsyncUuidMessageProcessor
from application.model.configuration import Configurations
from messagebus import DefaultToken, DataType, Message


class GetAndLockVoucherProcessor(AsyncUuidMessageProcessor):
    def __init__(self, configs, interactor):
        # type: (Configurations, GetAndLockVoucherInteractor) -> None

        super(GetAndLockVoucherProcessor, self).__init__()
        self.logger = configs.logger
        self.configs = configs
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> Any

        parsed_data = json.loads(data)
        pos_id = int(parsed_data.get("posId"))
        voucher_id = str(parsed_data.get("voucherId"))
        return pos_id, voucher_id

    def call_business(self, params):
        # type: ((int, str)) -> str

        pos_id, voucher_id = params
        
        return self.interactor.get_and_lock_voucher(pos_id, voucher_id)

    def format_response(self, message_bus, message, event, request, response):
        if response:
            message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))
        else:
            message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
