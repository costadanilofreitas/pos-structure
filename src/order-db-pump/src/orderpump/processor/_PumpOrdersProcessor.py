from messageprocessorutil import UuidMessageProcessor
from orderpump.interactor.pumporders import PumpAllOrdersInteractor


class PumpOrdersProcessor(UuidMessageProcessor):
    def __init__(self, pump_all_orders_interactor):
        # type: (PumpAllOrdersInteractor) -> None
        super(PumpOrdersProcessor, self).__init__()
        self.pump_all_orders_interactor = pump_all_orders_interactor

    def parse_data(self, data):
        return None

    def call_business(self, _):
        self.pump_all_orders_interactor.execute()

    def format_response(self, message_bus, message, event, _, result):
        return

    def format_exception(self, message_bus, message, event, _, exception):
        return

    def format_parse_exception(self, message_bus, message, event, data, exception):
        return
