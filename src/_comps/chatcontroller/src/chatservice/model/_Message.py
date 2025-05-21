# -*- coding: utf-8 -*-

from datetime import datetime

from typing import Optional


class MessageFrom(object):
    SAC = "Sac"
    STORE = "Store"


class Message(object):
    def __init__(self):
        self.id = None  # type: Optional[int]
        self.message_from = None  # type: Optional[unicode]
        self.created_time = None  # type: Optional[datetime]
        self.received_time = None  # type: Optional[datetime]
        self.server_id = None  # type: Optional[unicode]
        self.text = None  # type: Optional[unicode]
