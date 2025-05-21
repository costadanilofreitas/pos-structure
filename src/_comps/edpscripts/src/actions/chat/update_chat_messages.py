# -*- coding: utf-8 -*-

from actions import mb_context, logger
from bustoken import TK_CHAT_GET_LAST_MESSAGES
from msgbus import FM_PARAM, TK_SYS_ACK, MBTimeout, MBException
from sysactions import action


@action
def update_chat_messages(_):
    try:
        msg = mb_context.MB_EasySendMessage("ChatController", TK_CHAT_GET_LAST_MESSAGES, FM_PARAM)
        if msg.token == TK_SYS_ACK:
            return msg.data
    except (MBTimeout, MBException) as _:
        logger.exception("Error retrieving last messages from ChatController")
    
    return False
