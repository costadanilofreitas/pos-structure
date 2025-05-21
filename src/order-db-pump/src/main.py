import logging
import os
import os.path

import cfgtools
from helper import config_logger, import_pydevd
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from messagehandlerbuilder import OrderDbPumpMessageHandlerBuilder, ConfigKey
from msgbus import MBEasyContext
from mwrepository import OrderPictureRepository, ProductRepository


def main():
    import_pydevd(os.environ["LOADERCFG"], 9151, False)
    config_logger(os.environ["LOADERCFG"], "OrderDbPump")
    logger = logging.getLogger("OrderDbPump")

    cfg = cfgtools.read(os.environ["LOADERCFG"])

    mb_context = MBEasyContext("OrderDbPump")
    message_bus = MbContextMessageBus(mb_context)

    order_picture_repository = OrderPictureRepository(message_bus)
    product_repository = ProductRepository(mb_context)

    config = {
        ConfigKey.store_id: cfg.find_value("OrderDbPump/StoreId"),
        ConfigKey.pump_url: cfg.find_value("OrderDbPump/PumpUrl"),
        ConfigKey.api_key: cfg.find_value("OrderDbPump/ApiKey"),
        ConfigKey.order_picture_repository: order_picture_repository,
        ConfigKey.product_repository: product_repository,
        ConfigKey.logger: logger,
        ConfigKey.order_pump_db_path: cfg.find_value("OrderDbPump/DbFilePath"),
        ConfigKey.batch_size: int(cfg.find_value("OrderDbPump/BatchSize"))
    }
    if "{BUNDLEDIR}" in config[ConfigKey.order_pump_db_path]:
        config[ConfigKey.order_pump_db_path] = config[ConfigKey.order_pump_db_path]\
            .replace("{BUNDLEDIR}", os.environ["BUNDLEDIR"]) \
            .replace("/./", os.sep) \
            .replace("//", os.sep)\
            .replace("/", os.sep)

    message_handler_builder = OrderDbPumpMessageHandlerBuilder(config, logger)
    message_handler = MbContextMessageHandler(message_bus,
                                              "OrderDbPump",
                                              "OrderDbPump",
                                              "Persistence",
                                              message_handler_builder)
    message_handler.subscribe_non_reentrant_events("PumpOrders")
    return message_handler.handle_events()
