from mebuhi.event.impl import EventManager, IdleCleaner
from mebuhi.http import FlaskAdapter
from mebuhi.http.processor import SendMessageProcessor, StartListenProcessor, ListenProcessor
from messagebus import TokenCreator, TokenPriority
from messagehandler import MessageHandlerBuilder
from simplehttprouter import Route

from ._MebuhiMessageHandler import MebuhiMessageHandler

PERIPHERALS_GROUP = "6"
TK_PRN_PRINT = TokenCreator.create_token(TokenPriority.high, PERIPHERALS_GROUP, "101")


class MebuhiMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self, message_bus, idle_timeout, bump_timeout, cleaner_interval, host, port, logger):
        self.message_bus = message_bus
        self.idle_timeout = idle_timeout
        self.bump_timeout = bump_timeout
        self.cleaner_interval = cleaner_interval
        self.host = host
        self.port = port
        self.logger = logger
        self.message_handler = None
        self.flask_adapter = None
        self.idle_cleaner = None

    def build_singletons(self):
        event_manager = EventManager(self.message_bus, self.idle_timeout, self.bump_timeout, self.logger)
        send_message_processor = SendMessageProcessor(self.message_bus, self.logger)
        start_listen_processor = StartListenProcessor(event_manager, self.logger)
        listen_processor = ListenProcessor(event_manager, self.logger)
        self.flask_adapter = FlaskAdapter({
            Route("GET", "/mwapp/events/listen"): listen_processor.handle,
            Route("GET", "/mwapp/events/start"): start_listen_processor.handle,
            Route("POST", "/mwapp/services/{serviceType}/{serviceName}"): send_message_processor.handle,
            Route("GET", "/mwapp/services/{serviceType}/{serviceName}/"): send_message_processor.handle
        }, self.logger)
        self.flask_adapter.start("MebuhiFlaskApp", self.host, self.port)

        self.idle_cleaner = IdleCleaner(event_manager, self.cleaner_interval, self.logger)
        self.idle_cleaner.start()

        self.message_handler = MebuhiMessageHandler(event_manager)

    def build_message_handler(self):
        return self.message_handler

    def destroy_message_handler(self, message_handler):
        return

    def destroy_singletons(self):
        self.idle_cleaner.stop()
        self.flask_adapter.stop()
