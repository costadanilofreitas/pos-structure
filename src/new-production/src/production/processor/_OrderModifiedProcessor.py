import xml.sax
from cache_functions import UsersInfoCache

from messageprocessorutil import UuidMessageProcessor
from production.manager import ProductionManager
from production.model import ProductionOrder

from ._SystemOrderParser import SystemOrderParser


class OrderModifiedProcessor(UuidMessageProcessor):
    def __init__(self, production_manager, user_cache_thread=None):
        # type: (ProductionManager, UsersInfoCache) -> None
        super(OrderModifiedProcessor, self).__init__()
        self.production_manager = production_manager
        self.user_cache_thread = user_cache_thread

    def parse_data(self, data):
        handler = SystemOrderParser(user_cache_thread=self.user_cache_thread)
        xml.sax.parseString(data, handler)
        if handler.order.order_id == 0:
            return None
        return handler.order

    def call_business(self, order):
        # type: (ProductionOrder) -> None
        if order is not None:
            self.production_manager.order_modified(order)

    def format_response(self, message_bus, message, event, input_obj, result):
        # no response
        pass

    def format_exception(self, message_bus, message, event, input_obj, exception):
        # no response
        pass

    def format_parse_exception(self, message_bus, message, event, data, exception):
        # no response
        pass
