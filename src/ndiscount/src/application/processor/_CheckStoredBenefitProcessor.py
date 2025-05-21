import json

from application.interactor import CheckStoredBenefitInteractor
from application.model import Configurations
from application.model.benefit import Benefit
from messagebus import DefaultToken, DataType, Message
from messageprocessorutil import UuidMessageProcessor


class CheckStoredBenefitProcessor(UuidMessageProcessor):

    def __init__(self, configs, interactor):
        # type: (Configurations, CheckStoredBenefitInteractor) -> None

        super(CheckStoredBenefitProcessor, self).__init__()
        self.logger = configs.logger
        self.configs = configs
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> Benefit

        parsed_data = json.loads(data)
        benefit_id = str(parsed_data.get("benefitId"))

        return benefit_id

    def call_business(self, benefit_id):
        # type: (str) -> bool

        return self.interactor.check_stored_benefit(benefit_id)

    def format_response(self, message_bus, message, event, request, response):
        if response:
            message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, response))
        else:
            message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.string, ""))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
