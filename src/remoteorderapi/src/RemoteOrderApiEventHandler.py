# -*- coding: utf-8 -*-
from messagehandler import EventHandler
from msgbus import MBEasyContext
from FlaskServer import FlaskServer


class RemoteOrderApiEventHandler(EventHandler):
    def __init__(self, mbcontext, flask_server):
        # type: (MBEasyContext, FlaskServer) -> None
        super(RemoteOrderApiEventHandler, self).__init__(mbcontext)

        self.flask_server = flask_server

    def get_handled_tokens(self):
        return []

    def handle_message(self, msg):
        raise NotImplementedError("handle_message should not be called")

    def handle_event(self, subject, evt_type, data, msg):
        raise NotImplementedError("handle_message should not be called")

    def terminate_event(self):
        self.flask_server.stop()
