from abc import abstractmethod
from typing import Optional
from messageprocessor import MessageProcessor
from uuid import uuid4


class UuidMessageProcessor(MessageProcessor):

    def __init__(self, event_name=None):
        # type: (Optional[str]) -> None
        if event_name is not None:
            self.event_name = event_name
        else:
            self.event_name = type(self).__name__

    def get_processor_name(self):
        # type: () -> str
        if self.event_name is not None:
            return self.event_name

        return self.__class__.__name__

    def generate_unique_id(self):
        # type: () -> str
        return str(uuid4())

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
