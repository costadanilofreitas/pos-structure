from messagebus import AckMessage, NakMessage
from messageprocessorutil import UuidMessageProcessor
from production.manager import ProductionManager
from production.model.request import GetOrderXmlRequest
from production.view import OrderXml


class GetOrderXmlProcessor(UuidMessageProcessor):
    def __init__(self, production_manager):
        # type: (ProductionManager) -> None
        super(GetOrderXmlProcessor, self).__init__()
        self.production_manager = production_manager
        self.order_xml = OrderXml()

    def parse_data(self, data):
        return GetOrderXmlRequest(int(data))

    def call_business(self, request):
        production_order = self.production_manager.get_production_order(request.order_id)
        if production_order is None:
            return None
        return self.order_xml.to_xml(production_order)

    def format_response(self, message_bus, message, event, input_obj, order_xml):
        if order_xml is None:
            message_bus.reply_message(message, NakMessage("order not found"))
            return

        message_bus.reply_message(message, AckMessage(order_xml))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        exception_message = "Error retrieving order xml: {}".format(exception)
        message_bus.reply_message(message, NakMessage(exception_message))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        exception_message = "Error parsing received data: {}; Received data: {}".format(exception, data)
        message_bus.reply_message(message, NakMessage(exception_message))
