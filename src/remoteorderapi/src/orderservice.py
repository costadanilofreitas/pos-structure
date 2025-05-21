from msgbus import MBEasyContext, FM_STRING, TK_SYS_ACK
from bustoken import TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION, TK_REMOTE_ORDER_INVALID_ORDER_ID, \
    TK_REMOTE_ORDER_GET_STORED_ORDERS, TK_REMOTE_ORDER_REPRINT
from customexception import ValidationException
from threading import Lock


production_lock = Lock()


class OrderService(object):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        self.mbcontext = mbcontext

    def get_stored_orders(self):
        msg = self.mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_GET_STORED_ORDERS)
        if msg.token != TK_SYS_ACK:
            raise Exception("Error retrieving stored orders: " + msg.data)

        return msg.data

    def send_order_to_production(self, message_data):
        with production_lock:
            msg = self.mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION, format=FM_STRING, data=str(message_data))
            if msg.token == TK_REMOTE_ORDER_INVALID_ORDER_ID:
                raise ValidationException("InvalidOrderId", "The orderId sent was not found")

        if msg.token != TK_SYS_ACK:
            raise Exception("Error sending message: " + msg.data)

    def reprint_delivery_order(self, order_id, retransmit_id):
        msg = self.mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_REPRINT, format=FM_STRING, data='|'.join([str(order_id), str(retransmit_id)]))
        if msg.token != TK_SYS_ACK:
            raise Exception("Error sending message: " + msg.data)
