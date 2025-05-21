# -*- coding: utf-8 -*-

import logging
import os

from helper import config_logger, import_pydevd
from messagehandler import MessageHandler
from msgbus import MBEasyContext
import cfgtools

from rupture_event_handler import RuptureEventHandler
from rupture_events import RuptureEvents
from rupture_repository import RuptureRepository
from rupture_service import RuptureService
from services import CleanRuptureThread

LOADER_CFG = os.environ["LOADERCFG"]
REQUIRED_SERVICES = "Persistence|DeliveryPersistence"
SERVICE_NAME = "Ruptura"


def main():
    import_pydevd(LOADER_CFG, 9143)

    config_logger(LOADER_CFG, SERVICE_NAME)
    logger = logging.getLogger(SERVICE_NAME)
    config = cfgtools.read(LOADER_CFG)

    mb_context = MBEasyContext(SERVICE_NAME)

    rupture_repository = RuptureRepository(mb_context, logger)
    rupture_service = RuptureService(mb_context, logger, rupture_repository, config)
    event_handler = RuptureEventHandler(mb_context, logger, rupture_service)
    message_handler = MessageHandler(mb_context, SERVICE_NAME, SERVICE_NAME, REQUIRED_SERVICES, None)

    message_handler.set_event_handler(event_handler)
    message_handler.subscribe_non_reentrant_events([RuptureEvents.FullRuptureRequest, RuptureEvents.CleanRupture])

    if config.find_value("Rupture.CleanRuptureTimeWindow.Enabled", "false").lower() == "true":
        clean_rupture_thread = CleanRuptureThread(mb_context, config)
        clean_rupture_thread.start()

    message_handler.handle_events()


if __name__ == "__main__":
    main()
