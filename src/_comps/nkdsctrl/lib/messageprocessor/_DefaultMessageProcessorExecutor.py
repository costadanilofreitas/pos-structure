from typing import Any, Optional, List
from messagebus import MessageBus, Message, Event

from ._MessageProcessor import MessageProcessor
from ._MessageProcessorCallback import MessageProcessorCallback


class DefaultMessageProcessorExecutor(object):
    def __init__(self, event_processor, callbacks=None):
        # type: (MessageProcessor, Optional[List[MessageProcessorCallback]]) -> None
        self.event_processor = event_processor
        self.callbacks = callbacks

    def execute_processor(self, message_bus, message, event, data):
        # type: (MessageBus, Optional[Message], Optional[Event], Any) -> None
        event_name = self.event_processor.get_processor_name()
        request_id = self.event_processor.generate_unique_id()

        self._process_begun(event_name, request_id, data)
        input_obj = None
        try:
            input_obj = self.event_processor.parse_data(data)
            self._input_parsed(event_name, request_id, input_obj)

            output_obj = self.event_processor.call_business(input_obj)
            self._business_called(event_name, request_id, input_obj, output_obj)
            self.event_processor.format_response(message_bus, message, event, input_obj, output_obj)
            self._process_finished(event_name, request_id, input_obj, output_obj)
        except BaseException as ex:
            if input_obj is not None:
                self.event_processor.format_exception(message_bus, message, event, input_obj, ex)
                self._unhandled_exception(event_name, request_id, input_obj, ex)
            else:
                self.event_processor.format_parse_exception(message_bus, message, event, data, ex)
                self._parse_exception(event_name, request_id, data, ex)

    def _process_begun(self, event_name, request_id, data):
        # type: (str, str, bytes) -> None
        if self.callbacks is not None:
            for callback in self.callbacks:
                callback.process_begun(event_name, request_id, data)

    def _input_parsed(self, event_name, request_id, input_obj):
        # type: (str, str, Any) -> None
        if self.callbacks is not None:
            for callback in self.callbacks:
                callback.input_parsed(event_name, request_id, input_obj)

    def _business_called(self, event_name, request_id, input_obj, output_obj):
        # type: (str, str, Any, Any) -> None
        if self.callbacks is not None:
            for callback in self.callbacks:
                callback.business_called(event_name, request_id, input_obj, output_obj)

    def _process_finished(self, event_name, request_id, input_obj, output_obj):
        # type: (str, str, Any, Any) -> None
        if self.callbacks is not None:
            for callback in self.callbacks:
                callback.process_finished(event_name, request_id, input_obj, output_obj)

    def _parse_exception(self, event_name, request_id, data, exception):
        # type: (str, str, bytes, BaseException) -> None
        if self.callbacks is not None:
            for callback in self.callbacks:
                callback.parse_exception(event_name, request_id, data, exception)

    def _unhandled_exception(self, event_name, request_id, input_obj, exception):
        # type: (str, str, Any, BaseException) -> None
        if self.callbacks is not None:
            for callback in self.callbacks:
                callback.unhandled_exception(event_name, request_id, input_obj, exception)
