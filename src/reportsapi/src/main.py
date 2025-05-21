# -*- coding: utf-8 -*-

import os
import sys

import cfgtools
import sysactions
from old_helper import config_logger, read_swconfig
from messagehandler import MessageHandler
from msgbus import MBEasyContext

import FlaskServer
from ReportsApiEventHandler import ReportsApiEventHandler
from interactor import SalesReportInteractor

debug_path = '../python/pycharm-debug.egg'
if os.path.exists(debug_path):
    try:
        sys.path.index(debug_path)
    except ValueError:
        sys.path.append(debug_path)
    # noinspection PyUnresolvedReferences
    import pydevd


def main():
    # pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True, suspend=False)

    config_logger(os.environ["LOADERCFG"], 'ReportsApi')

    required_services = "Persistence|Reports|StoreWideConfig"

    config = cfgtools.read(os.environ["LOADERCFG"])
    allowed_urls = config.find_values("ReportsApi.AllowedUrls")
    port = config.find_value("ReportsApi.Port")

    if allowed_urls is None:
        allowed_urls = []

    mbcontext = MBEasyContext("ReportsApi")
    sysactions.mbcontext = mbcontext

    message_handler = MessageHandler(mbcontext,
                                     "ReportsApi",
                                     "ReportsApi",
                                     required_services,
                                     None)

    store_id = read_swconfig(mbcontext, "Store.Id")

    sales_report_interactor = SalesReportInteractor(store_id)
    FlaskServer.sales_report_interactor = sales_report_interactor
    FlaskServer.set_allowed_urls(allowed_urls)
    flask_server = FlaskServer.FlaskServer(port)
    flask_server.start()

    event_handler = ReportsApiEventHandler(mbcontext, flask_server, sales_report_interactor)
    message_handler.event_handler = event_handler

    message_handler.handle_events()
