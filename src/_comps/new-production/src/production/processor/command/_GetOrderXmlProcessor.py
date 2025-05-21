from messagebus import AckMessage, NakMessage
from messageprocessorutil import UuidMessageProcessor
from production.manager import ProductionManager
from production.model.request import GetOrderXmlRequest


class GetOrderXmlProcessor(UuidMessageProcessor):
    def __init__(self, production_manager):
        # type: (ProductionManager) -> None
        super(GetOrderXmlProcessor, self).__init__()
        self.production_manager = production_manager

    def parse_data(self, data):
        return GetOrderXmlRequest(int(data))

    def call_business(self, request):
        # type: (GetOrderXmlRequest) -> str
        return self.production_manager.get_order_xml(request.order_id)

    def format_response(self, message_bus, message, event, input_obj, result):
        message_bus.reply_message(message, AckMessage(result.encode("utf-8")))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, NakMessage(str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, NakMessage(str(exception)))
