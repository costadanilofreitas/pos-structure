from datetime import datetime

from ._TagEventType import TagEventType


class TagEvent(object):
    def __init__(self, tag, action, date):
        # type: (str, TagEventType, datetime) -> None
        self.tag = tag
        self.action = action
        self.date = date
