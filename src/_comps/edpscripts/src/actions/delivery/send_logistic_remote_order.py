# -*- coding: utf-8 -*-

from sysactions import action, show_confirmation, show_messagebox, StopAction
from bustoken import TK_REMOTE_ORDER_SEND_ORDER_TO_LOGISTIC
from msgbus import TK_SYS_ACK

from .. import mb_context
from model.customexception import SendLogisticError


@action
def send_logistic_remote_order(pos_id, order_id=""):
    confirmation = show_confirmation(pos_id, "$LOGISTIC_SEND_CONFIRMATION")
    if not confirmation:
        raise StopAction()

    data = pos_id + "\0" + order_id
    logistic_send_order_token = TK_REMOTE_ORDER_SEND_ORDER_TO_LOGISTIC
    msg = mb_context.MB_EasySendMessage("RemoteOrder", logistic_send_order_token, data=data, timeout=10000000)
    if msg.token == TK_SYS_ACK:
        show_messagebox(pos_id, "$LOGISTIC_SENT")
        return
    
    raise SendLogisticError("$LOGISTIC_SENT_ERROR")
