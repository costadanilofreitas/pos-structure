import json

import sysactions
from bustoken import TK_RUPTURA_GET_DISABLED, TK_RUPTURA_GET_ENABLED
from msgbus import TK_SYS_NAK, FM_STRING


def get_disabled_products():
    msg = sysactions.send_message("Ruptura", TK_RUPTURA_GET_DISABLED, FM_STRING, "UI")

    if msg.token == TK_SYS_NAK:
        raise Exception()

    return json.loads(msg.data)


def get_enabled_products():
    msg = sysactions.send_message("Ruptura", TK_RUPTURA_GET_ENABLED, FM_STRING, "UI")

    if msg.token == TK_SYS_NAK:
        raise Exception()

    return json.loads(msg.data)
