import json

from application.interactor import ApplyBenefitsInteractor
from application.model import Configurations
from application.model.benefit import Benefit
from application.repository import NDiscountRepository
from messagebus import DefaultToken, DataType, Message
from messageprocessorutil import UuidMessageProcessor
from sysactions import get_model, get_posot


class ApplyBenefitsProcessor(UuidMessageProcessor):
    def __init__(self, configs, interactor):
        # type: (Configurations, ApplyBenefitsInteractor) -> None
        super(ApplyBenefitsProcessor, self).__init__()
        self.logger = configs.logger
        self.configs = configs
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> int

        data = json.loads(data)
        pos_id = int(data["pos_id"])

        return pos_id

    def call_business(self, param):
        # type: (int) -> None

        pos_id = param
        try:
            self.interactor.repository.show_wait_screen(pos_id)
            
            model = get_model(pos_id)
            pos_ot = get_posot(model)
            order = NDiscountRepository.get_order(pos_id)

            self.logger.info("Trying to apply benefits to orderId: {}; posId: {}".format(order.id, order.pos_id))

            benefits_to_apply = NDiscountRepository.get_benefits_to_apply(model)
            benefits_to_apply = [
                {
                    "promotion_tender_amount": x.get("promotion_tender_amount", 0),
                    "added_sale_lines": x.get("added_sale_lines", []),
                    "benefit": Benefit.from_benefit_json(json.loads(x.get("benefit", "{}"))),
                    "raw_benefit": x.get("benefit", "{}"),
                    "burnt_items": x.get("burnt_items", {})
                } for x in benefits_to_apply
            ]
            self.interactor.apply(pos_id, pos_ot, order, benefits_to_apply)
        finally:
            self.interactor.repository.hide_wait_screen(pos_id)

    def format_response(self, message_bus, message, event, request, response):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, str(response)))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
