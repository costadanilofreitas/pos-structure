from abc import abstractmethod

from messageprocessorutil import UuidMessageProcessor


class AsyncUuidMessageProcessor(UuidMessageProcessor):

    @abstractmethod
    def parse_data(self, data):
        pass

    @abstractmethod
    def call_business(self, obj):
        pass

    @abstractmethod
    def format_response(self, message_bus, message, event, input_obj, result):
        pass

    @abstractmethod
    def format_exception(self, message_bus, message, event, input_obj, exception):
        pass

    @abstractmethod
    def format_parse_exception(self, message_bus, message, event, data, exception):
        pass
