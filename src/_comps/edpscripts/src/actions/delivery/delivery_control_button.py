# -*- coding: utf-8 -*-

import json

import sysactions
from actions.delivery.close_delivery_store import close_delivery_store
from actions.delivery.get_store_status import get_remote_order_status
from actions.delivery.open_delivery_store import open_delivery_store
from bustoken import create_token, MSGPRT_LOW
from msgbus import FM_PARAM, TK_SYS_NAK

from .. import pos_config

TK_REMOTE_ORDER_CLOSE_STORE = create_token(MSGPRT_LOW, "37", "4")
TK_REMOTE_ORDER_OPEN_STORE = create_token(MSGPRT_LOW, "37", "5")


@sysactions.action
def delivery_control_button(pos_id):
    # type: (str) -> bool

    model = sysactions.get_model(pos_id)
    remote_store_status = json.loads(get_remote_order_status())
    store_is_opened = remote_store_status.get("isOpened")

    message, options = _get_display_text(model, store_is_opened)
    ret = sysactions.show_messagebox(pos_id, message, title="$DELIVERY", buttons=options)
    
    if ret == 1:
        return False

    user_id = sysactions.get_custom(model, "Last Manager ID")

    msg = sysactions.send_message("RemoteOrder",
                                  TK_REMOTE_ORDER_CLOSE_STORE if store_is_opened else TK_REMOTE_ORDER_OPEN_STORE,
                                  FM_PARAM,
                                  user_id)
    if msg.token == TK_SYS_NAK:
        sysactions.show_messagebox(pos_id, "$ERROR_CHANGING_REMOTE_ORDER_STORE_STATUS|{}".format(msg.data))
        return False
    
    if store_is_opened:
        success = close_delivery_store(pos_id, pos_config.store_id)
    else:
        success = open_delivery_store(pos_id, pos_config.store_id)
        
    if not success:
        sysactions.show_messagebox(pos_id, "$ERROR_CLOSING_DELIVERY_STORE")
        return False

    sysactions.show_messagebox(pos_id, "$REMOTE_ORDER_STORE_STATUS_CHANGED")
    return True


def _get_display_text(model, store_is_opened):
    if store_is_opened:
        options = "$STOP_DELIVERY|"
    else:
        options = "$START_DELIVERY|"
    options += "$CANCEL"
    status_message = sysactions.translate_message(model, "STORE_OPENED" if store_is_opened else "STORE_CLOSED")
    message = "$REMOTE_ORDER_STORE_STATUS_CHANGE|{}".format(status_message)
    return message, options
