import logging
import os

import cfgtools
from helper import config_logger, import_pydevd
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from messagehandlerbuilder import MebuhiMessageHandlerBuilder
from msgbus import MBEasyContext


def main():
    import_pydevd(os.environ["LOADERCFG"], 9130, False)
    config_logger(os.environ["LOADERCFG"], "mebuhi")

    config = cfgtools.read(os.environ["LOADERCFG"])
    idle_timeout = float(config.find_value("Mebuhi.IdleTimeout", "10"))
    bump_timeout = float(config.find_value("Mebuhi.BumpTimeout", "600"))
    cleaner_interval = float(config.find_value("Mebuhi.CleanerInterval", "60"))
    server_log_level = config.find_value("Mebuhi.InternalServerLogLevel", "ERROR")
    host = config.find_value("Mebuhi.Http.Host", "localhost")
    port = config.find_value("Mebuhi.Http.Port", "9494")

    logger = logging.getLogger("mebuhi")

    server_logger = logging.getLogger('werkzeug')
    server_logger.handlers = logger.handlers
    if server_log_level == "DEBUG":
        server_logger.setLevel(logging.DEBUG)
    elif server_log_level == "INFO":
        server_logger.setLevel(logging.INFO)
    elif server_log_level == "WARN":
        server_logger.setLevel(logging.WARN)
    elif server_log_level == "WARNING":
        server_logger.setLevel(logging.WARNING)
    else:
        server_logger.setLevel(logging.ERROR)

    mb_context = MBEasyContext("mebuhi")
    message_bus = MbContextMessageBus(mb_context)

    message_handler_builder = MebuhiMessageHandlerBuilder(message_bus,
                                                          idle_timeout,
                                                          bump_timeout,
                                                          cleaner_interval,
                                                          host,
                                                          port,
                                                          logger)
    message_handler = MbContextMessageHandler(
        message_bus,
        "mebuhi",
        "mebuhi",
        "",
        message_handler_builder)

    return message_handler.handle_events()
