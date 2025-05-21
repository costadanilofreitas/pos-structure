# -*- coding: utf-8 -*-

from sysactions import show_confirmation, StopAction, action, show_messagebox
from bustoken import TK_REMOTE_ORDER_CANCEL_LOGISTIC
from msgbus import TK_SYS_ACK

from .. import mb_context
from model.customexception import LogisticCancelError


@action
def cancel_logistic_remote_order(pos_id, order_id=""):
    confirmation = show_confirmation(pos_id, "$LOGISTIC_CANCEL_CONFIRMATION")
    if not confirmation:
        raise StopAction()

    data = pos_id + "\0" + order_id

    msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_CANCEL_LOGISTIC, data=data, timeout=10000000)
    if msg.token == TK_SYS_ACK:
        show_messagebox(pos_id, "$LOGISTIC_CANCELED")
        return
    
    raise LogisticCancelError("$LOGISTIC_CANCELLED_ERROR")
