import logging
import os

import cfgtools
from helper import import_pydevd, config_logger
from mbcontextmessagehandler import MbContextMessageBus, MbContextMessageHandler
from messagehandlerbuilder import NKDSCtrlMessageHandlerBuilder
from model import Kds, KdsView
from msgbus import MBEasyContext
from typing import List


def main():
    import_pydevd(os.environ["LOADERCFG"], 9135, False)
    config_logger(os.environ["LOADERCFG"], "NKDSCTRL")

    logger = logging.getLogger("NKDSCTRL")
    logger.setLevel(logging.DEBUG)
    proxy_comp_name = "KdsController"

    mb_context = MBEasyContext("NKDSCTRL")
    message_bus = MbContextMessageBus(mb_context)

    message_handler = MbContextMessageHandler(message_bus, "NKDSCTRL", "NKDSCTRL", "ProductionSystem", None)
    config = cfgtools.read(os.environ["LOADERCFG"])
    kds_views = get_kds_views(config)
    kds_list = get_kds_list(config, kds_views)

    message_handler_builder = NKDSCtrlMessageHandlerBuilder(proxy_comp_name, kds_list, message_bus, logger)
    message_handler.event_handler_builder = message_handler_builder

    return message_handler.handle_events()


def get_kds_views(config):
    # type: (cfgtools.Group) -> List[KdsView]
    views = []
    view_config = config.find_group("Views")
    if not view_config:
        return []

    for view_config_group in view_config.groups:
        views.append(KdsView(view_config_group))

    return views


def get_kds_list(config, kds_views):
    # type: (cfgtools.Group, List[KdsView]) -> List[Kds]
    kds_list = []
    kds_config = config.find_group("KDS")
    if not kds_config:
        return []
    for kds_config_group in kds_config.groups:
        kds_list.append(Kds(kds_config_group, kds_views))

    return kds_list
