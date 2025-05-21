import json

from application.interactor import VerifyAndRemoveBenefitsInteractor
from application.model import Configurations
from application.model.transactions import VerifyAndRemoveBenefitsUnitOfWork
from messagebus import DefaultToken, DataType, Message
from messageprocessorutil import UuidMessageProcessor


class VerifyAndRemoveBenefitsProcessor(UuidMessageProcessor):
    def __init__(self, configs, interactor):
        # type: (Configurations, VerifyAndRemoveBenefitsInteractor) -> None

        super(VerifyAndRemoveBenefitsProcessor, self).__init__()
        self.logger = configs.logger
        self.configs = configs
        self.interactor = interactor

    def parse_data(self, data):
        # type: (str) -> int

        data = json.loads(data)
        pos_id = int(data["pos_id"])

        return pos_id

    def call_business(self, pos_id):
        # type: (int) -> None

        try:
            self.interactor.repository.show_wait_screen(pos_id)

            uow = VerifyAndRemoveBenefitsUnitOfWork(pos_id=pos_id)

            self.logger.info("Verifying and removing not used benefits from orderId: {}; posId: {}"
                             .format(uow.order.id, pos_id))

            self.interactor.verify_and_remove(uow)
        finally:
            self.interactor.repository.hide_wait_screen(pos_id)

    def format_response(self, message_bus, message, event, request, response):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.string, ""))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        self.logger.exception(str(exception))
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
