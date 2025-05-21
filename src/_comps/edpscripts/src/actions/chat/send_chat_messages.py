# -*- coding: utf-8 -*-

import json

from actions import mb_context, logger
from bustoken import TK_CHAT_SEND_MESSAGE
from msgbus import FM_PARAM, TK_SYS_ACK, MBTimeout, MBException
from sysactions import action


@action
def send_chat_messages(_, message):
    message_data = json.dumps(dict(text=message))
    try:
        msg = mb_context.MB_EasySendMessage("ChatController", TK_CHAT_SEND_MESSAGE, FM_PARAM, message_data)
        if msg.token == TK_SYS_ACK:
            return True
    except (MBTimeout, MBException) as _:
        logger.exception("Error sending message to ChatController")
    
    return False
