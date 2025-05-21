# -*- coding: utf-8 -*-

import json
import logging
from threading import Condition, Thread

from chatservice import ChatModelJsonEncoder, MessageParser
from chatservice.model import Message, Event
from chatservice.repository import MessageRepository
from msgbus import MBEasyContext
from typing import List

logger = logging.getLogger("ChatController")


class ChatService(object):
    def __init__(self, mb_context, message_repository, message_parser, retry_sync_time):
        # type: (MBEasyContext, MessageRepository, MessageParser, int) -> None
        self.mb_context = mb_context
        self.message_repository = message_repository
        self.message_parser = message_parser
        self.retry_sync_time = retry_sync_time

        self.thread_running = True
        self.thread_condition = Condition()
        self.resend_chat_messages = Thread(target=self._send_store_status_to_server)
        self.resend_chat_messages.daemon = True
        self.resend_chat_messages.start()

    def get_updates(self, message_data):
        # type: (str) -> List[Message]
        
        message_id = int(message_data)
        return self.message_repository.get_updates(message_id)

    def get_last_messages(self, quantity):
        # type: (str) -> List[Message]
        
        try:
            quantity = int(quantity)
        except ValueError:
            quantity = 50

        return self.message_repository.get_last_messages(quantity)

    def send_message(self, message_data):
        # type: (unicode) -> None
        message = self.message_parser.parse(message_data)
        ret = self.message_repository.save_new_messages_from_store([message])
        message.id = ret[0]
        data = json.dumps([message], encoding="utf-8", cls=ChatModelJsonEncoder)
        self.mb_context.MB_EasyEvtSend(Event.POS_CHAT_MESSAGE_NEW, "", data)

    def messages_received(self, messages_data):
        messages = self.message_parser.parse_sac_messages(messages_data)
        logger.debug("Founded messages: {0}".format(len(messages)))
        ack_messages = self.message_repository.save_new_messages_from_sac(messages)
        logger.debug("Founded confirmations: {0}".format(len(ack_messages)))
        data = json.dumps(ack_messages, encoding="utf-8", cls=ChatModelJsonEncoder)
        self.mb_context.MB_EasyEvtSend(Event.POS_CHAT_MESSAGE_ACK, "", data)

    def sac_ack_messages_received(self, messages_data):
        ack_messages = self.message_parser.parse_sac_ack_messages(messages_data)
        self.message_repository.mark_messages_received(ack_messages)

    def terminate(self):
        self.thread_running = False
        with self.thread_condition:
            self.thread_condition.notify_all()

        Thread.join(self.resend_chat_messages)

    def _send_store_status_to_server(self):
        while self.thread_running:
            messages = self.message_repository.get_messages_without_confirmation()
            if len(messages) > 0:
                data = json.dumps(messages, encoding="utf-8", cls=ChatModelJsonEncoder)
                self.mb_context.MB_EasyEvtSend(Event.POS_CHAT_MESSAGE_NEW, "", data)

            with self.thread_condition:
                self.thread_condition.wait(self.retry_sync_time)
