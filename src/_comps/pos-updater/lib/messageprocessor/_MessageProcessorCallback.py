from abc import ABCMeta, abstractmethod
from typing import Any


class MessageProcessorCallback(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def process_begun(self, event_name, request_id, data):
        # type: (str, str, str) -> None
        raise NotImplementedError()

    @abstractmethod
    def input_parsed(self, event_name, request_id, input_obj):
        # type: (str, str, Any) -> None
        raise NotImplementedError()

    @abstractmethod
    def business_called(self, event_name, request_id, input_obj, output_obj):
        # type: (str, str, Any, Any) -> None
        raise NotImplementedError()

    @abstractmethod
    def process_finished(self, event_name, request_id, input_obj, output_obj):
        # type: (str, str, Any, BaseException) -> None
        raise NotImplementedError()

    @abstractmethod
    def parse_exception(self, event_name, request_id, data, exception):
        # type: (str, str, str, BaseException) -> None
        raise NotImplementedError()

    @abstractmethod
    def unhandled_exception(self, event_name, request_id, input_obj, exception):
        # type: (str, str, Any, BaseException) -> None
        raise NotImplementedError()
