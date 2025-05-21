from application.interactor import GetCatalogVersionToApplyInteractor
from messagebus import Message, DefaultToken, DataType
from messageprocessorutil import UuidMessageProcessor


class GetCatalogVersionToApplyProcessor(UuidMessageProcessor):
    
    def __init__(self, interactor, event_name=None):
        # type: (GetCatalogVersionToApplyInteractor, str) -> None
        super(GetCatalogVersionToApplyProcessor, self).__init__(event_name)
        self.interactor = interactor

    def parse_data(self, data):
        return data or self._do_not_remove_this_function_bug_in_the_library()

    def call_business(self, obj):
        return self.interactor.get_catalog_version_to_apply()

    def format_response(self, message_bus, message, event, input_obj, result):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.param, result))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        exception_name = str(type(exception).__name__)
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, exception_name))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        return

    @staticmethod
    def _do_not_remove_this_function_bug_in_the_library():
        return ''
