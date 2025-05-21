from logging import Logger
from ._MessageProcessorCallback import MessageProcessorCallback


class LoggingProcessorCallback(MessageProcessorCallback):
    def __init__(self, logger):
        # type: (Logger) -> None
        self.logger = logger

    def process_begun(self, event_name, request_id, data):
        # type: (str, str, str) -> None
        try:
            converted_data = data.decode(u"utf-8")
        except:
            converted_data = u"could not convert data using utf-8"
        self.logger.info(u"{} - {} - Start handling. Data: {}".format(event_name, request_id, converted_data))

    def input_parsed(self, event_name, request_id, input_obj):
        self.logger.info(u"{} - {} - Input parsed handling".format(event_name, request_id))

    def business_called(self, event_name, request_id, input_obj, output_obj):
        pass

    def process_finished(self, event_name, request_id, input_obj, output_obj):
        self.logger.info(u"{} - {} - Successfully processed".format(event_name, request_id))

    def parse_exception(self, event_name, request_id, data, exception):
        self.logger.exception(u"{} - {} - Parse exception handling".format(event_name, request_id))

    def unhandled_exception(self, event_name, request_id, input_obj, exception):
        self.logger.exception(u"{} - {} - Unhandled exception handling".format(event_name, request_id))
