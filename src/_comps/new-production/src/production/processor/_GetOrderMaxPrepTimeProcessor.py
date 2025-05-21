from messagebus import AckMessage, NakMessage
from messageprocessorutil import UuidMessageProcessor
from production.interactor import GetOrderMaxPrepTimeInteractor
from production.manager import ProductionManager
from production.model.request import GetOrderXmlRequest
from production.repository import ProductRepository


class GetOrderMaxPrepTimeProcessor(UuidMessageProcessor):
    def __init__(self, production_manager, product_repository):
        # type: (ProductionManager, ProductRepository) -> None
        super(GetOrderMaxPrepTimeProcessor, self).__init__()
        self.production_manager = production_manager
        self.product_repository = product_repository
        self.get_order_max_prep_time_interactor = GetOrderMaxPrepTimeInteractor(self.product_repository)

    def parse_data(self, data):
        return GetOrderXmlRequest(int(data))

    def call_business(self, request):
        production_order = self.production_manager.get_production_order(request.order_id)
        return self.get_order_max_prep_time_interactor.execute(production_order)

    def format_response(self, message_bus, message, event, input_obj, result):
        message_bus.reply_message(message, AckMessage(str(result).encode("utf-8")))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        exception_message = "Error obtaining order max prep time: {}".format(exception.message)
        message_bus.reply_message(message, NakMessage(exception_message))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        exception_message = "Error parsing received data: {}; Received data: {}".format(exception.message, data)
        message_bus.reply_message(message, NakMessage(exception_message))
