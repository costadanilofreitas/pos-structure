# -*- coding: utf-8 -*-
import sysactions

from actions.void.do_void_remote_order import do_void_remote_order
from custom_sysactions import user_authorized_to_execute_action
from systools import sys_log_exception


@sysactions.action
@user_authorized_to_execute_action
def do_ask_void_remote_order(pos_id, remote_id):
    try:
        message = "$CONFIRM_VOID_ORDER"
        confirmation = sysactions.show_messagebox(pos_id, message,
                                                  title="$TABLE_INFO", timeout=720000, buttons="$OK|$CANCEL")
        if confirmation == 1:
            return False

        error_message = do_void_remote_order(pos_id, remote_id)
        if not error_message:
            sysactions.show_messagebox(pos_id, "$REMOTE_ORDER_VOIDED_SUCCESS")
        else:
            sysactions.show_messagebox(pos_id, error_message)

    except Exception as ex:
        sys_log_exception("Error voiding delivery order")
        sysactions.show_messagebox(pos_id, "$ERROR_VOIDING_REMOTE_ORDER|{}".format(ex))
