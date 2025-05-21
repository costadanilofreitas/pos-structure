# -*- coding: utf-8 -*-

from bustoken import TK_REMOTE_ORDER_SAVE_ORDER
from msgbus import TK_SYS_ACK

from .. import mb_context
from model.customexception import SaveDeliveryOrderError


def save_delivery_order(order_id):
    data = order_id
    msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_SAVE_ORDER, data=data, timeout=10000000)
    if msg.token == TK_SYS_ACK:
        return
    
    raise SaveDeliveryOrderError("$ERROR_SAVING_ORDER")
