#!/usr/bin/python
# -*- coding: utf-8 -*-

from messagehandler import EventHandler
from msgbus import MBEasyContext
from FlaskServer import FlaskServer
from interactor import SalesReportInteractor


class ReportsApiEventHandler(EventHandler):
    def __init__(self, mbcontext, flask_server, sales_report_interactor):
        # type: (MBEasyContext, FlaskServer, SalesReportInteractor) -> None
        super(ReportsApiEventHandler, self).__init__(mbcontext)

        self.flask_server = flask_server
        self.sales_report_interactor = sales_report_interactor

    def get_handled_tokens(self):
        return []

    def handle_message(self, msg):
        raise NotImplementedError("handle_message should not be called")

    def handle_event(self, subject, evt_type, data, msg):
        raise NotImplementedError("handle_message should not be called")

    def terminate_event(self):
        self.flask_server.stop()
