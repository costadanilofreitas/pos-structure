# -*- coding: utf-8 -*-

import os

import cfgtools
import pyscripts
from helper import config_logger, import_pydevd
from messagehandler import MessageHandler
from msgbus import MBEasyContext
from old_helper import read_swconfig

from eventhandler import SitefEventHandler, SitefCallback

REQUIRED_SERVICES = "StoreWideConfig"
LOADER_CFG = os.environ["LOADERCFG"]


def main():
    import_pydevd(LOADER_CFG, 9155)

    config = cfgtools.read(LOADER_CFG)
    pos_id = int(config.find_value("SitefConfig.PosId"))

    config_logger(LOADER_CFG, "Sitef")
    mbcontext = MBEasyContext("Sitef%02d" % pos_id)

    pyscripts.mbcontext = mbcontext

    config = cfgtools.read(LOADER_CFG)
    is_fake = config.find_value("SitefConfig.IsFake") == "True"
    is_mobile = config.find_value("SitefConfig.IsMobile") == "True"

    if is_fake:
        from fakesitef import FakeSitefProcessor
        sitef_processor = FakeSitefProcessor()
    elif is_mobile:
        from mobilesitef import MobileSitefProcessor
        sitef_processor = MobileSitefProcessor(mbcontext)
    else:
        from syncsitef import SynchSitefProcessor
        sitef_callback = SitefCallback(mbcontext)
        sitef_processor = SynchSitefProcessor(mbcontext, sitef_callback.callback)

    sitef_event_handler = SitefEventHandler(mbcontext, sitef_processor)
    sitef_message_handler = MessageHandler(mbcontext, "Sitef%02d" % pos_id, "Sitef", REQUIRED_SERVICES, sitef_event_handler)

    if not is_fake and not is_mobile:
        from syncsitef import TestSitefProcessor, SitefServiceFinder
        id_loja = read_swconfig(mbcontext, "Store.idLoja")
        ip_sitef = read_swconfig(mbcontext, "Store.IpSitef").split("\0")
        timeout = int(read_swconfig(mbcontext, "Store.SiTefTimeout"))
        sleep_time = int(config.find_value("SitefConfig.SearchTime") or 300)

        sitef_test_processor = TestSitefProcessor(id_loja)
        sitef_service_finder = SitefServiceFinder(mbcontext, sitef_test_processor, sleep_time, ip_sitef, id_loja, pos_id)
        sitef_processor.config(id_loja, ip_sitef, timeout, sitef_service_finder)

    sitef_message_handler.handle_events()
