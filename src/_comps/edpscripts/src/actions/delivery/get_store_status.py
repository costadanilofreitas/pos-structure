import json

import bustoken
import sysactions
from msgbus import TK_SYS_ACK

from .. import logger, mb_context

TK_REMOTE_ORDER_GET_STORE_STATUS = bustoken.create_token(bustoken.MSGPRT_LOW, "37", "214")


@sysactions.action
def get_remote_order_status(_=None):
    default_response = json.dumps(dict(isOnline=False,
                                       isOpened=False,
                                       lastExternalContact=None,
                                       closedSince=None))
    try:
        msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_GET_STORE_STATUS, timeout=5 * 1000000)
        if msg.token == TK_SYS_ACK:
            return msg.data
        raise Exception("Could not retrieve remote order status")
    except Exception as e:
        logger.error(e)
        return default_response
