import logging
import os

import cfgtools
from helper import config_logger, import_pydevd
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from messagehandlerbuilder import SaleCompMessageHandlerBuilder
from msgbus import MBEasyContext
from mwrepository import ProductRepository, OrderRepository


def main():
    import_pydevd(os.environ["LOADERCFG"], 9138, False)

    logger = logging.getLogger("SaleComp")

    config = cfgtools.read(os.environ["LOADERCFG"])
    proxy_comp_name = config.find_value("SaleComp.ProxyCompName")
    pos_number = config.find_value("SaleComp.PosNumber")
    proxy_comp_name += pos_number
    config_logger(os.environ["LOADERCFG"], "SaleComp{}".format(pos_number))

    mb_context = MBEasyContext("SALECTRLCOMP")
    message_bus = MbContextMessageBus(mb_context)

    message_handler = MbContextMessageHandler(
        message_bus,
        "ORDERMGR{}".format(pos_number),
        "SALECTRL",
        "Persistence",
        None)

    product_repository = ProductRepository(mb_context)
    order_repository = OrderRepository(mb_context)
    order = order_repository.get_order(4, 4)
    message_handler_builder = SaleCompMessageHandlerBuilder(proxy_comp_name, product_repository, logger)
    message_handler.event_handler_builder = message_handler_builder

    return message_handler.handle_events()
