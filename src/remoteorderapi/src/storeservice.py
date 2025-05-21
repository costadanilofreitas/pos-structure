from msgbus import MBEasyContext, FM_STRING, TK_SYS_ACK
from bustoken import TK_REMOTE_ORDER_GET_STORE, TK_REMOTE_ORDER_OPEN_STORE, TK_REMOTE_ORDER_CLOSE_STORE, TK_REMOTE_STORE_ALREADY_OPEN, TK_REMOTE_STORE_ALREADY_CLOSED
from customexception import ValidationException


class StoreService(object):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        self.mbcontext = mbcontext

    def get_store(self):
        msg = self.mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_GET_STORE)
        if msg.token != TK_SYS_ACK:
            raise Exception("Error retrieving store: " + msg.data)

        return msg.data

    def open_store(self):
        msg = self.mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_OPEN_STORE)
        if msg.token == TK_REMOTE_STORE_ALREADY_OPEN:
            raise ValidationException("StoreAlreadyOpened", "Cannot open store because it is already open")

        if msg.token != TK_SYS_ACK:
            raise Exception("Error sending message: " + msg.data)

        return msg.data

    def close_store(self):
        msg = self.mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_CLOSE_STORE)
        if msg.token == TK_REMOTE_STORE_ALREADY_CLOSED:
            raise ValidationException("StoreAlreadyClosed", "Cannot close store because it is already closed")

        if msg.token != TK_SYS_ACK:
            raise Exception("Error sending message: " + msg.data)

        return msg.data
