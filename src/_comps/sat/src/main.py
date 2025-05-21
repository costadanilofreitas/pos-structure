# -*- coding: utf-8 -*-
import cfgtools
import pyscripts

from old_helper import config_logger
from msgbus import MBEasyContext
from messagehandler import MessageHandler
from satprocessor import FakeSatProcessor, SatSynchProcessor
from eventhandler import SatEventHandler
from old_helper import read_swconfig

import sys
import os
debugPath = '../python/pycharm-debug.egg'
if os.path.exists(debugPath):
    try:
        sys.path.index(debugPath)
    except:
        sys.path.append(debugPath)
    import pydevd

# Use the line below in the function you want to debug
# pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True)
# UNTIL HERE

REQUIRED_SERVICES = ""


def main():
    # pydevd.settrace('localhost', port=9124, stdoutToServer=True, stderrToServer=True, suspend=False)
    config = cfgtools.read(os.environ["LOADERCFG"])
    is_fake = config.find_value("SatComponent.IsFake") == "True"
    comp_no = int(config.find_value("SatComponent.Number"))

    config_logger(os.environ["LOADERCFG"], 'SatProcessor')
    mbcontext = MBEasyContext("SAT%02d" % comp_no)
    pyscripts.mbcontext = mbcontext

    if is_fake:
        is_active_delay = float(config.find_value("SatComponent.IsActiveDelay"))
        process_delay = float(config.find_value("SatComponent.ProcessDelay"))
        is_mfe = config.find_value("SatComponent.IsMFE")
        sat_processor = FakeSatProcessor(is_active_delay, process_delay, is_mfe)
    else:
        sat_act_key = config.find_value("SatComponent.SatActKey")
        module_directory = config.find_value("SatComponent.ModuleDirectory")
        is_mfe = config.find_value("SatComponent.IsMFE") or ''
        is_mfe = is_mfe.lower() == "true"
        if is_mfe:
            mfe = config.find_group("SatComponent.MFE")
            integrador_inputdir = mfe.find_value("integrador_inputdir")
            integrador_outputdir = mfe.find_value("integrador_outputdir")
            temp_dir = mfe.find_value("temp_dir")
            error_dir = mfe.find_value("error_dir")
            chave_acesso_validador = mfe.find_value("chave_acesso_validador")
            chave_requisicao = mfe.find_value("chave_requisicao")
            estabelecimento = read_swconfig(mbcontext, "Store.idLoja")
            cnpj = mfe.find_value("cnpj")
            icms_base = mfe.find_value("icms_base")
            max_retries = mfe.find_value("max_retries") or 30
            sat_processor = SatSynchProcessor(sat_act_key, module_directory, is_mfe, integrador_inputdir,
                                              integrador_outputdir, temp_dir, error_dir, chave_acesso_validador, chave_requisicao,
                                              estabelecimento, cnpj, icms_base, max_retries)
        else:
            sat_processor = SatSynchProcessor(sat_act_key, module_directory, is_mfe)

    sat_event_handler = SatEventHandler(mbcontext, sat_processor)
    MessageHandler(mbcontext, "SAT%02d" % comp_no, "SAT", REQUIRED_SERVICES, sat_event_handler).handle_events()
