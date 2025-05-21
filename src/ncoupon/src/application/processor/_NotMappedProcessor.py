from application.model import AsyncUuidMessageProcessor


class NotMappedProcessor(AsyncUuidMessageProcessor):

    def __init__(self):
        # type: () -> None

        super(NotMappedProcessor, self).__init__()

    def parse_data(self, data):
        return

    def call_business(self, obj):
        return

    def format_response(self, message_bus, message, event, input_obj, result):
        return

    def format_exception(self, message_bus, message, event, input_obj, exception):
        return

    def format_parse_exception(self, message_bus, message, event, data, exception):
        return

