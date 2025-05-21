from messagebus import TokenCreator, TokenPriority
from messagehandler import MessageHandlerBuilder
from messageprocessor import MessageProcessorMessageHandler, DefaultMessageProcessorExecutorFactory, \
    LoggingProcessorCallback
from mobileposprinter.processor import PrnPrintProcessor

PERIPHERALS_GROUP = "6"
TK_PRN_PRINT = TokenCreator.create_token(TokenPriority.high, PERIPHERALS_GROUP, "101")


class MobilePosPrinterMessageHandlerBuilder(MessageHandlerBuilder):
    def __init__(self, pos_id, message_bus, logger):
        self.pos_id = pos_id
        self.message_bus = message_bus
        self.logger = logger

        self.message_handler = None

    def build_singletons(self):
        message_processor = {
            TK_PRN_PRINT: PrnPrintProcessor(self.pos_id, self.message_bus)
        }

        callbacks = [LoggingProcessorCallback(self.logger)]

        self.message_handler = MessageProcessorMessageHandler(None,
                                                              message_processor,
                                                              None,
                                                              DefaultMessageProcessorExecutorFactory(callbacks),
                                                              self.logger)

    def build_message_handler(self):
        return self.message_handler

    def destroy_message_handler(self, message_handler):
        pass

    def destroy_singletons(self):
        pass
