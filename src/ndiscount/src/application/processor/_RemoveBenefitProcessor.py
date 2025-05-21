import json

from application.interactor import RemoveBenefitInteractor
from application.model import InvalidMessageContentException, Configurations
from application.model.benefit import Benefit
from application.model.order import Order
from messagebus import DefaultToken, DataType, Message
from messageprocessorutil import UuidMessageProcessor
from sysactions import get_posot, get_model, get_current_order


class RemoveBenefitProcessor(UuidMessageProcessor):
    def __init__(self, configs, interactor):
        # type: (Configurations, RemoveBenefitInteractor) -> None

        super(RemoveBenefitProcessor, self).__init__()
        self.logger = configs.logger
        self.configs = configs
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> Benefit

        data = json.loads(data)
        benefit_ids = data["benefit"]
        pos_id = int(data["pos_id"])

        return pos_id, benefit_ids

    def call_business(self, param):
        # type: ((int, Order, list)) -> None

        pos_id, benefit_ids = param

        try:
            self.interactor.repository.show_wait_screen(pos_id)

            model = get_model(pos_id)
            pos_ot = get_posot(model)
            order_id = get_current_order(model).get("orderId")

            self.logger.info("Trying to remove benefits to orderId: {}; posId: {}; benefitIds: {}"
                             .format(order_id, pos_id, benefit_ids))

            if benefit_ids is None:
                self.interactor.remove_all_benefits(model, pos_ot)
            elif isinstance(benefit_ids, basestring):
                self.interactor.remove_benefit_by_id(pos_id, model, pos_ot, benefit_ids)
            elif isinstance(benefit_ids, list):
                for benefit_id in benefit_ids:
                    self.interactor.remove_benefit_by_id(pos_id, model, pos_ot, benefit_id)
            else:
                raise InvalidMessageContentException()
        finally:
            self.interactor.repository.hide_wait_screen(pos_id)

    def format_response(self, message_bus, message, event, request, response):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, ""))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
