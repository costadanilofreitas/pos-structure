# -*- coding: utf-8 -*-

import os
import cfgtools
import pyscripts

from msgbus import MBEasyContext
from messagehandler import MessageHandler
from eventhandler import CapptaEventHandler, CapptaCallback
from old_helper import config_logger, read_swconfig
from debug_helper import import_pydevd
from cappta import FakeCapptaProcessor, SynchCapptaProcessor

REQUIRED_SERVICES = "StoreWideConfig"
LOADER_CFG = os.environ["LOADERCFG"]


def main():
    import_pydevd(LOADER_CFG, 9122)

    config = cfgtools.read(LOADER_CFG)
    comp_no = int(config.find_value("CapptaConfig.PosId"))

    config_logger(LOADER_CFG, 'Cappta')
    mbcontext = MBEasyContext("Sitef%02d" % comp_no)
    pyscripts.mbcontext = mbcontext

    config = cfgtools.read(LOADER_CFG)
    is_fake = (config.find_value("CapptaConfig.IsFake") or "false").lower() == "true"
    env = int(config.find_value("CapptaConfig.Environment") or 2)
    module_directory = config.find_value("CapptaConfig.ModuleDirectory")
    pos_id = config.find_value("CapptaConfig.PosId")
    cnpj = config.find_value("CapptaConfig.CnpjLoja")
    auth_key = config.find_value("CapptaConfig.ChaveAutenticacao")

    if is_fake:
        cappta_processor = FakeCapptaProcessor()
    else:
        cappta_callback = CapptaCallback(mbcontext)
        cappta_processor = SynchCapptaProcessor(pos_id, cnpj, auth_key, module_directory, cappta_callback.callback, env)

    cappta_event_handler = CapptaEventHandler(mbcontext, cappta_processor)
    cappta_message_handler = MessageHandler(mbcontext, "Sitef%02d" % comp_no, "Cappta", REQUIRED_SERVICES, cappta_event_handler)

    cappta_message_handler.handle_events()
