import json

from application.interactor import AddBenefitToApplyInteractor
from application.model import Configurations
from application.model.benefit import Benefit
from application.model.transactions import AddBenefitToApplyUnitOfWork
from messagebus import DefaultToken, DataType, Message
from messageprocessorutil import UuidMessageProcessor


class AddBenefitToApplyProcessor(UuidMessageProcessor):
    def __init__(self, configs, interactor):
        # type: (Configurations, AddBenefitToApplyInteractor) -> None
        super(AddBenefitToApplyProcessor, self).__init__()
        self.logger = configs.logger
        self.configs = configs
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> Benefit

        parsed_data = json.loads(data)
        pos_id = int(parsed_data.get("posId"))
        benefit_id = str(parsed_data.get("benefitId"))
        benefit = parsed_data.get("benefit", {})

        return pos_id, benefit, benefit_id

    def call_business(self, param):
        # type: ((int, dict, str)) -> None

        pos_id, raw_benefit, benefit_id = param

        if not raw_benefit:
            raw_benefit = self.interactor.get_benefit_from_database(benefit_id)
        benefit = Benefit.from_benefit_json(raw_benefit)

        uow = AddBenefitToApplyUnitOfWork(self.logger, pos_id, benefit, raw_benefit)

        self.logger.info("Adding benefit to orderId: {}; posId: {}; benefitId: {}"
                         .format(uow.order.id, uow.pos_id, benefit_id))
        self.interactor.apply(uow)

    def format_response(self, message_bus, message, event, request, response):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, ""))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
