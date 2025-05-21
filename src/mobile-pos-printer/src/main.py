import os
import cfgtools
import logging

from msgbus import MBEasyContext
from messagehandlerbuilder import MobilePosPrinterMessageHandlerBuilder
from helper import config_logger, import_pydevd

from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler


def main():
    import_pydevd(os.environ["LOADERCFG"], 9129, False)
    config_logger(os.environ["LOADERCFG"], "MobilePosPrinter")

    logger = logging.getLogger("MobilePosPrinter")

    config = cfgtools.read(os.environ["LOADERCFG"])
    pos_id = int(config.find_value("MobilePosPrinter.PosId"))

    mb_context = MBEasyContext("MobilePosPrinter")
    message_bus = MbContextMessageBus(mb_context)
    message_handler_builder = MobilePosPrinterMessageHandlerBuilder(pos_id, message_bus, logger)
    message_handler = MbContextMessageHandler(
        message_bus,
        "printer{}".format(pos_id),
        "Printer",
        "POS{}".format(pos_id),
        message_handler_builder)
    return message_handler.handle_events()
