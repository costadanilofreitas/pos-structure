# -*- coding: utf-8 -*-

import json

import sysactions
from bustoken import TK_REMOTE_ORDER_VOID_REMOTE_ORDER
from custom_sysactions import user_authorized_to_execute_action
from msgbus import TK_SYS_NAK
from systools import sys_log_exception

from .. import mb_context


@sysactions.action
@user_authorized_to_execute_action
def do_void_remote_order(pos_id, remote_id):
    try:
        error_message = None
        msg = mb_context.MB_EasySendMessage('RemoteOrder',
                                            TK_REMOTE_ORDER_VOID_REMOTE_ORDER,
                                            data=str(remote_id),
                                            timeout=10000 * 1000)
        if msg.token == TK_SYS_NAK:
            error_message = msg.data
            if not error_message:
                model = sysactions.get_model(pos_id)
                error_message = sysactions.translate_message(model, "UNKNOWN_ERROR")
        
        return error_message

    except Exception as _:
        sys_log_exception("Error voiding delivery order")
        raise
