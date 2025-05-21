from logging import Logger

from messagehandler import MessageHandler


class ProxyMessageHandler(MessageHandler):
    def __init__(self, comp_name, logger):
        # type: (str, Logger) -> None
        self.comp_name = comp_name
        self.logger = logger

    def handle_event(self, message_bus, event):
        pass

    def handle_message(self, message_bus, message):
        self.logger.info("Receiving message")
        resp = message_bus.send_message(self.comp_name, message)
        self.logger.info("Message forwarded")
        message_bus.reply_message(message, resp)
        self.logger.info("Message replied")
