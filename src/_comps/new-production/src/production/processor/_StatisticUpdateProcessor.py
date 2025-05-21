import json

from messagebus import NakMessage, AckMessage
from messageprocessorutil import UuidMessageProcessor
from production.manager import ProductionManager


class StatisticUpdateProcessor(UuidMessageProcessor):
    def __init__(self, production_manager):
        # type: (ProductionManager) -> None
        super(StatisticUpdateProcessor, self).__init__()
        self.production_manager = production_manager

    def parse_data(self, _):
        pass

    def call_business(self, _):
        return self.production_manager.statistics or {}

    def format_response(self, message_bus, message, event, input_obj, result):
        message_bus.reply_message(message, AckMessage(json.dumps(result)))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, NakMessage(exception.message))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, NakMessage(exception.message))
