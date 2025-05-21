# -*- coding: utf-8 -*-

from application.model import DispatchedEvents
from msgbus import MBEasyContext


class WarningType(object):
    PriceWarning = "PriceWarning"


class WarningEmitter(object):
    def __init__(self, mb_context):
        # type: (MBEasyContext) -> None
        self.mb_context = mb_context
        self.event_dispatcher = DispatchedEvents(mb_context)

    def emit_warn(self, warning_type, warning_detail):
        # type: (unicode, unicode) -> None
        if warning_type == WarningType.PriceWarning:
            self.event_dispatcher.send_event(DispatchedEvents.PosPriceWarning, "", warning_detail.encode("utf-8"))
