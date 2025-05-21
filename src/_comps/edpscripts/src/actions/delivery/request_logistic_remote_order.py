# -*- coding: utf-8 -*-

from sysactions import action, show_messagebox
from bustoken import TK_REMOTE_ORDER_SEARCH_LOGISTIC
from msgbus import TK_SYS_ACK

from .. import mb_context
from model.customexception import LogisticRequestError


@action
def request_logistic_remote_order(pos_id, order_id=""):
    data = pos_id + "\0" + order_id
    search_logistic_token = TK_REMOTE_ORDER_SEARCH_LOGISTIC
    msg = mb_context.MB_EasySendMessage("RemoteOrder", search_logistic_token, data=data, timeout=10000)
    if msg.token == TK_SYS_ACK:
        show_messagebox(pos_id, "$LOGISTIC_SEARCHING")
        return
    
    raise LogisticRequestError("$LOGISTIC_SEARCHING_ERROR")
