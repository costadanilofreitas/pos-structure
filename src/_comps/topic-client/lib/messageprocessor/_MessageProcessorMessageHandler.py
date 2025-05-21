import json

from typing import Dict, Optional
from messagebus import MessageBus, Event, Message, NakMessage
from messagehandler import MessageHandler

from ._MessageProcessor import MessageProcessor
from ._ApiRouter import ApiRouter
from ._ApiRequest import ApiRequest
from ._MessageProcessorExecutorFactory import MessageProcessorExecutorFactory


class MessageProcessorMessageHandler(MessageHandler):
    def __init__(self,
                 event_processors,
                 message_processors,
                 api_routers,
                 executor_factory,
                 logger=None):
        # type: (Optional[Dict[str, MessageProcessor]], Optional[Dict[int, MessageProcessor]], Optional[Dict[str, ApiRouter]], MessageProcessorExecutorFactory) -> None
        self.event_processors = event_processors
        self.message_processors = message_processors
        self.api_routers = api_routers
        self.executor_factory = executor_factory
        self.logger = logger

    def handle_event(self, message_bus, event):
        # type: (MessageBus, Event) -> None
        try:
            if self.event_processors is not None:
                if self._has_event_type(event) and self._event_type_is_in_event_processors(event):
                    self._create_executor_and_execute(message_bus, event, self._get_event_type_key(event))
                    return

                if self._event_subject_is_in_event_processors(event):
                    self._create_executor_and_execute(message_bus, event, self._get_subject_key(event))
                    return

            if self.api_routers is not None and event.subject in self.api_routers:
                api_request = self._create_api_request(event)
                api_router = self.api_routers[event.subject]
                message_processor = api_router.get_message_processor(api_request)
                if message_processor is None:
                    raise MessageProcessorMessageHandler.ApiRequestNotMapped(api_request)

                executor = self.executor_factory.build_executor(message_processor)
                executor.execute_processor(message_bus, None, event, api_request)
                return

            raise MessageProcessorMessageHandler.EventNotMapped(event.subject, event.event_type)
        except:
            if self.logger is not None:
                self.logger.exception("Exception while handling event")
            raise

    def _create_api_request(self, event):
        data = event.data
        if isinstance(data, ApiRequest):
            api_request = data
        elif isinstance(data, bytes):
            request = json.loads(data, encoding="utf-8")
            path_variables_names = self._get_path_variables_names(request["api_path"])
            path_variables = {}
            for path_variable in path_variables_names:
                if path_variable in request["query"]:
                    path_variables[path_variable] = request["query"][path_variable]
                    del request["query"][path_variable]

            query_variables = request["query"]

            api_request = ApiRequest(event.event_type,
                                     request["api_path"],
                                     path_variables,
                                     query_variables,
                                     request["headers"],
                                     request["body"])
        else:
            raise Exception("Invalid request type: " + str(type(data)))
        return api_request

    def handle_message(self, message_bus, message):
        # type: (MessageBus, Message) -> None
        try:
            if self.message_processors is not None and message.token in self.message_processors:
                executor = self.executor_factory.build_executor(self.message_processors[message.token])
                executor.execute_processor(message_bus, message, None, message.data)
            else:
                message_bus.reply_message(message, NakMessage())
        except:
            if self.logger is not None:
                self.logger.exception("Exception handling message")
            raise

    def _has_event_type(self, event):
        return event.event_type is not None

    def _event_type_is_in_event_processors(self, event):
        return self._get_event_type_key(event) in self.event_processors

    def _get_event_type_key(self, event):
        return event.subject + "_" + event.event_type

    def _event_subject_is_in_event_processors(self, event):
        return self._get_subject_key(event) in self.event_processors

    def _get_subject_key(self, event):
        return event.subject

    def _create_executor_and_execute(self, message_bus, event, event_key):
        message_processor = self.event_processors[event_key]
        executor = self.executor_factory.build_executor(message_processor)
        executor.execute_processor(message_bus, None, event, event.data)

    def _get_path_variables_names(self, api_path):
        # type: (unicode) -> List[unicode]
        ret = []

        index2 = 0
        while True:
            try:
                index1 = api_path.index("{", index2)
            except ValueError:
                return ret
            try:
                index2 = api_path.index("}", index1)
            except ValueError:
                return ret

            ret.append(api_path[index1 + 1:index2])

    class EventNotMapped(Exception):
        def __init__(self, subject, type):
            # type: (str, str) -> None
            self.subject = subject
            self.type = type

        def __str__(self):
            return "Event not mapped: {} - {}".format(self.subject, self.type)

        def __repr__(self):
            return "EventNotMapped('{}', '{}')".format(self.subject, self.type)

    class ApiRequestNotMapped(Exception):
        def __init__(self, api_request):
            # type: (ApiRequest) -> None
            self.api_request = api_request

        def __str__(self):
            return u"ApiRequest not mapped: {} - {}".format(self.api_request.method, self.api_request.api_path)

        def __repr__(self):
            return u"ApiRequest not mapped: {} - {}".format(self.api_request.method, self.api_request.api_path)
