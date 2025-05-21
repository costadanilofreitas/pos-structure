from abc import abstractmethod
from typing import Optional, Any

from messagebus import MessageBus, Message, Event
from messageprocessorutil import UuidMessageProcessor


class AsyncUuidMessageProcessor(UuidMessageProcessor):

    @abstractmethod
    def parse_data(self, data):
        # type: (str) -> Any
        
        pass

    @abstractmethod
    def call_business(self, obj):
        # type: (Any) -> None
        
        pass

    @abstractmethod
    def format_response(self, message_bus, message, event, input_obj, result):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, Any) -> None
        
        pass

    @abstractmethod
    def format_exception(self, message_bus, message, event, input_obj, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], Any, BaseException) -> None
        
        pass

    @abstractmethod
    def format_parse_exception(self, message_bus, message, event, data, exception):
        # type: (MessageBus, Optional[Message], Optional[Event], bytes, BaseException) -> None
        
        pass
