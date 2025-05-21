from typing import Optional


class Event(object):
    def __init__(self, subject, event_type=None, data=None, source=0, synchronous=False, timeout=-1):
        # type: (unicode, Optional[unicode], Optional[bytes], int, bool, int) -> None
        self.subject = subject
        self.event_type = event_type
        self.source = source
        self.data = data
        self.synchronous = synchronous
        self.timeout = timeout
        self.imp_message = None
