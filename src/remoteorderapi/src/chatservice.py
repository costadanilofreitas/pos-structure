from msgbus import MBEasyContext, FM_PARAM, TK_SYS_ACK
from bustoken import TK_CHAT_GET_UPDATES, TK_CHAT_MARK_UPDATES_RECEIVED, TK_CHAT_SEND_MESSAGE, TK_CHAT_GET_LAST_MESSAGES, TK_CHAT_INVALID_REQUEST
from customexception import ValidationException


class ChatService(object):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        self.mbcontext = mbcontext

    def send_message(self, message_data):
        msg = self.mbcontext.MB_EasySendMessage("ChatController", TK_CHAT_SEND_MESSAGE, format=FM_PARAM, data=message_data)
        if msg.token == TK_CHAT_INVALID_REQUEST:
            raise ValidationException("InvalidJson", msg.data.decode("utf-8"))

        if msg.token != TK_SYS_ACK:
            raise Exception("Error sending message: " + msg.data)

    def get_updates(self, message_data):
        msg = self.mbcontext.MB_EasySendMessage("ChatController", TK_CHAT_GET_UPDATES, format=FM_PARAM, data=message_data)
        if msg.token != TK_SYS_ACK:
            raise Exception("Error sending message: " + msg.data)

        return msg.data

    def get_last_messages(self, message_data):
        msg = self.mbcontext.MB_EasySendMessage("ChatController", TK_CHAT_GET_LAST_MESSAGES, format=FM_PARAM, data=message_data)
        if msg.token != TK_SYS_ACK:
            raise Exception("Error sending message: " + msg.data)

        return msg.data

    def mark_unread_messages(self, message_data):
        msg = self.mbcontext.MB_EasySendMessage("ChatController", TK_CHAT_MARK_UPDATES_RECEIVED, format=FM_PARAM, data=message_data.encode("utf-8"))
        if msg.token != TK_SYS_ACK:
            raise Exception("Error sending message: " + msg.data)
