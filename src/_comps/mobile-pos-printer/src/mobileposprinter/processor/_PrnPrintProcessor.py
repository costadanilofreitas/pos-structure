import base64

from messagebus import Message, DefaultToken, DataType, MessageBus, TokenPriority, TokenCreator, Event
from messageprocessorutil import UuidMessageProcessor

TK_POS_MODELSETCUSTOM = TokenCreator.create_token(TokenPriority.high, "5", "4")


class PrnPrintProcessor(UuidMessageProcessor):
    def __init__(self, pos_id, message_bus):
        # type: (int, MessageBus) -> None
        super(PrnPrintProcessor, self).__init__()

        self.pos_id = pos_id
        self.message_bus = message_bus

    def parse_data(self, data):
        return data

    def call_business(self, print_data):
        event_xml = """<Event subject="POS{}" type="MOBILE">
                           <MOBILE_PRINT>
                               {}
                           </MOBILE_PRINT>
                       </Event>""".format(self.pos_id, base64.b64encode(print_data))

        return Event("POS{}".format(self.pos_id), "MOBILE", event_xml)

    def format_response(self, message_bus, message, event, input_obj, result):
        message_bus.publish_event(result)
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_ACK, DataType.param))

    def format_exception(self, message_bus, message, event, input_obj, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))

    def format_parse_exception(self, message_bus, message, event, data, exception):
        message_bus.reply_message(message, Message(DefaultToken.TK_SYS_NAK, DataType.param, str(exception)))
