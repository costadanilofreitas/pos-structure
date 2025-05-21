from application.interactor import BurnVoucherInteractor
from application.model import AsyncUuidMessageProcessor
from application.model.configuration import Configurations
from messagebus import DefaultToken, DataType, Message


class BurnVoucherProcessor(AsyncUuidMessageProcessor):
    def __init__(self, configs, interactor):
        # type: (Configurations, BurnVoucherInteractor) -> None

        super(BurnVoucherProcessor, self).__init__()
        self.logger = configs.logger
        self.configs = configs
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> str

        return str(data)

    def call_business(self, benefit_id):
        # type: (str) -> None

        self.interactor.burn_benefit(benefit_id)

    def format_response(self, message_bus, message, event, request, response):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
