import os
import sys

import cfgtools
from helper import config_logger, import_pydevd
from messagehandler import MessageHandler
from msgbus import MBEasyContext

from eventhandler import FingerPrintReaderEventHandler, FingerPrintReaderCallback
from fingerprintreader import DigitalPersonaFingerPrintReader, DatabaseEnrolledUsersRepository

REQUIRED_SERVICES = ""


def main():
    import_pydevd(os.environ["LOADERCFG"], 9128)

    config_logger(os.environ["LOADERCFG"], 'FingerPrintReader')

    config = cfgtools.read(os.environ["LOADERCFG"])
    mbcontext = MBEasyContext("FingerPrintReader")

    module_directory = config.find_value("FingerPrinterReader.ModuleDirectory")
    number = int(config.find_value("FingerPrinterReader.Number"))
    enrolled_users_cache_expiration = int(config.find_value("FingerPrinterReader.EnrolledUsersCacheExpiration"))
    threshold = int(config.find_value("FingerPrinterReader.Threshold"))
    finger_print_timeout = int(config.find_value("FingerPrinterReader.FingerPrintTimeout"))

    finger_print_reader_callback = FingerPrintReaderCallback(mbcontext)
    enrolled_users_repository = DatabaseEnrolledUsersRepository(mbcontext, enrolled_users_cache_expiration)
    finger_print_reader = DigitalPersonaFingerPrintReader(enrolled_users_repository, finger_print_reader_callback, threshold, finger_print_timeout, module_directory)
    finger_print_event_handler = FingerPrintReaderEventHandler(mbcontext, finger_print_reader)

    MessageHandler(mbcontext, "FingerPrintReader{0}".format(number), "FingerPrintReader", REQUIRED_SERVICES, finger_print_event_handler).handle_events()
