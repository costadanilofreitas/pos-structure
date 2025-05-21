import os
import cfgtools

import FlaskServer

from msgbus import MBEasyContext
from helper import import_pydevd
from messagehandler import MessageHandler
from RemoteOrderApiEventHandler import RemoteOrderApiEventHandler
from orderservice import OrderService
from chatservice import ChatService
from storeservice import StoreService


def main():
    import_pydevd(os.environ["LOADERCFG"], 9140)

    required_services = "RemoteOrder"

    config = cfgtools.read(os.environ["LOADERCFG"])
    allowed_urls = config.find_values("RemoteOrderApi.AllowedUrls") or []
    port = config.find_value("RemoteOrderApi.Port")

    mbcontext = MBEasyContext("RemoteOrderApi")
    message_handler = MessageHandler(mbcontext, "RemoteOrderApi", "RemoteOrderApi", required_services, None)

    order_service = OrderService(mbcontext)
    FlaskServer.order_service = order_service

    store_service = StoreService(mbcontext)
    FlaskServer.store_service = store_service

    chat_service = ChatService(mbcontext)
    FlaskServer.chat_service = chat_service

    FlaskServer.set_allowed_urls(allowed_urls)

    flask_server = FlaskServer.FlaskServer(port)
    flask_server.start()

    event_handler = RemoteOrderApiEventHandler(mbcontext, flask_server)

    message_handler.set_event_handler(event_handler)
    message_handler.handle_events()
