# -*- coding: utf-8 -*-

import os

import cfgtools
from messagehandler import MessageHandler
from msgbus import MBEasyContext
from helper import config_logger, import_pydevd

from ChatControllerEventHandler import ChatControllerEventHandler
from chatservice import ChatService, MessageParser
from chatservice.model import Event
from chatservice.repository import MessageRepository


def main():
    loader_cfg = os.environ["LOADERCFG"]
    service_name = "ChatController"
    required_services = "DeliveryPersistence"
    
    import_pydevd(loader_cfg, 9145)
    config_logger(loader_cfg, service_name)

    mb_context = MBEasyContext(service_name)
    message_handler = MessageHandler(mb_context, service_name, service_name, required_services, None)

    config = cfgtools.read(loader_cfg)
    sync_interval = int(config.find_value("ChatController.SyncInterval") or 10)
    
    message_repository = MessageRepository(mb_context)
    message_parser = MessageParser()
    
    chat_service = ChatService(mb_context, message_repository, message_parser, sync_interval)
    event_handler = ChatControllerEventHandler(mb_context, chat_service)

    message_handler.subscribe_reentrant_events([Event.SAC_CHAT_MESSAGE_NEW, Event.SAC_CHAT_MESSAGE_ACK])
    message_handler.set_event_handler(event_handler)

    message_handler.handle_events()


if __name__ == "__main__":
    main()
