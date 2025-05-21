from messageprocessorutil import UuidMessageProcessor
from messagebus import NakMessage, AckMessage
from production.manager import ProductionManager


class PurgeOrdersProcessor(UuidMessageProcessor):
    def __init__(self, production_manager):
        # type: (ProductionManager) -> None
        super(PurgeOrdersProcessor, self).__init__()
        self.production_manager = production_manager
    
    def parse_data(self, _):
        return ''

    def call_business(self, obj):
        self.production_manager.purge_all_orders()

    def format_response(self, message_bus, message, event, input_obj, result):
        message_bus.reply_message(message, AckMessage())

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, NakMessage())

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, NakMessage())
