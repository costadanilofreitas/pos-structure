from messageprocessorutil import UuidMessageProcessor


class OrderModifiedIgnoredTypesProcessor(UuidMessageProcessor):
    def __init__(self):
        # type: () -> None
        super(OrderModifiedIgnoredTypesProcessor, self).__init__()

    def parse_data(self, data):
        return None

    def call_business(self, _):
        return None

    def format_response(self, message_bus, message, event, input_obj, result):
        # no response
        pass

    def format_exception(self, message_bus, message, event, input_obj, exception):
        # no response
        pass

    def format_parse_exception(self, message_bus, message, event, data, exception):
        # no response
        pass
