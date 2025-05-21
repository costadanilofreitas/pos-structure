import json

from bustoken import TK_REMOTE_ORDER_GET_RUPTURED_ITEMS
from msgbus import FM_STRING, TK_SYS_NAK
from sysactions import send_message
from systools import sys_log_exception


def get_ruptured_products():
    ruptured_items = []
    try:
        msg = send_message("RemoteOrder", TK_REMOTE_ORDER_GET_RUPTURED_ITEMS, FM_STRING, "")
        if msg.token == TK_SYS_NAK:
            raise Exception()

        ruptured_items = json.loads(msg.data)
    except Exception as _:
        sys_log_exception("Error getting not ruptured items")

    return ruptured_items