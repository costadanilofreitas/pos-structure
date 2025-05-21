# -*- coding: utf-8 -*-

import json
import logging

from bustoken import TK_CHAT_GET_UPDATES, TK_CHAT_SEND_MESSAGE, TK_CHAT_MARK_UPDATES_RECEIVED, \
    TK_CHAT_INVALID_REQUEST, TK_CHAT_GET_LAST_MESSAGES
from chatservice import ChatService, ChatModelJsonEncoder
from chatservice.model import Event
from messagehandler import EventHandler
from msgbus import MBEasyContext, FM_PARAM, MBMessage, TK_SYS_NAK, TK_SYS_ACK
from chatservice.customexception import InvalidJsonException

logger = logging.getLogger("ChatController")


class ChatControllerEventHandler(EventHandler):
    def __init__(self, mb_context, chat_service):
        # type: (MBEasyContext, ChatService) -> None
        
        super(ChatControllerEventHandler, self).__init__(mb_context)
        self.chat_service = chat_service

    def get_handled_tokens(self):
        return [TK_CHAT_GET_UPDATES, TK_CHAT_SEND_MESSAGE, TK_CHAT_MARK_UPDATES_RECEIVED, TK_CHAT_GET_LAST_MESSAGES]

    def handle_message(self, msg):
        # type: (MBMessage) -> None
        
        try:
            logger.debug("Message received: {}; Data: {}".format(msg.token, msg.data))
            
            if msg.token == TK_CHAT_GET_UPDATES:
                messages = self.chat_service.get_updates(msg.data)
                messages_json = json.dumps(messages, encoding="utf-8", cls=ChatModelJsonEncoder)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_PARAM, data=messages_json)
                
            elif msg.token == TK_CHAT_GET_LAST_MESSAGES:
                messages = self.chat_service.get_last_messages(msg.data)
                messages_json = json.dumps(messages, encoding="utf-8", cls=ChatModelJsonEncoder)
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_ReplyMessage(msg, format=FM_PARAM, data=messages_json)
                
            elif msg.token == TK_CHAT_SEND_MESSAGE:
                try:
                    self.chat_service.send_message(msg.data)
                except InvalidJsonException as ex:
                    msg.token = TK_CHAT_INVALID_REQUEST
                    self.mbcontext.MB_ReplyMessage(msg, format=FM_PARAM, data=repr(ex.message).encode("utf-8"))
                msg.token = TK_SYS_ACK
                self.mbcontext.MB_EasyReplyMessage(msg)
        except Exception as ex:
            logger.exception("Error processing message: {}".format(msg.token))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, format=FM_PARAM, data=repr(ex).encode("utf-8"))

    def handle_event(self, subject, evt_type, data, msg):
        # type: (unicode, unicode, str, MBMessage) -> None
        
        logger.debug("Event received: {}; Data: {}".format(subject, data))
        
        try:
            if subject == Event.SAC_CHAT_MESSAGE_NEW:
                self.chat_service.messages_received(data)
                
            elif subject == Event.SAC_CHAT_MESSAGE_ACK:
                self.chat_service.sac_ack_messages_received(data)
        except Exception as _:
            logger.exception("Error handling event: {}".format(subject))

    def terminate_event(self):
        self.chat_service.terminate()
