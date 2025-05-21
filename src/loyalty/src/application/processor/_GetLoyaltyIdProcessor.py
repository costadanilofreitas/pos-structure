from application.interactor import GetLoyaltyIdInteractor
from application.model import AsyncUuidMessageProcessor
from application.model.configuration import Configurations
from messagebus import DefaultToken, DataType, Message
from typing import Dict


class GetLoyaltyIdProcessor(AsyncUuidMessageProcessor):
    def __init__(self, configs, interactor):
        # type: (Configurations, GetLoyaltyIdInteractor) -> None

        super(GetLoyaltyIdProcessor, self).__init__()
        self.logger = configs.logger
        self.configs = configs
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> Dict

        return str(data)

    def call_business(self, loyalty_customer_id):
        # type: (str) -> None

        return self.interactor.get_loyalty_id(loyalty_customer_id)

    def format_response(self, message_bus, message, event, request, response):
        if response:
            message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))
        else:
            message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
