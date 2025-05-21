import cfgtools
from msgbus import MBEasyContext
from messagehandler import MessageHandler
from scanner import ScannerEventHandler, Scanner
from old_helper import config_logger
import logging
import os
import sys

REQUIRED_SERVICES = "FiscalPersistence"

def main():
    config = cfgtools.read(os.environ["LOADERCFG"])
    config_logger(os.environ["LOADERCFG"], 'scanner')
    logger = logging.getLogger("scanner")

    try:
        mbcontext = MBEasyContext("scanner")
        com_port = config.find_value("scanner_config.port")
        baud_rate = config.find_value("scanner_config.baud_rate")

        scanner_uploader = Scanner(mbcontext, com_port, baud_rate)

        scanner_event_handler = ScannerEventHandler(mbcontext, scanner_uploader)
        scanner_event_handler.daemon = True

        messsage_handler = MessageHandler(mbcontext, "scanner", "scanner", REQUIRED_SERVICES, scanner_event_handler)

        scanner_uploader.start()
        messsage_handler.handle_events()

    except Exception as e:
        logger.info('[Scanner] Exception >>>>>>>>>>> {}'.format(e))