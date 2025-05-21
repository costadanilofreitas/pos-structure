from datetime import datetime
from ._Clock import Clock


class RealClock(Clock):
    def now(self):
        return datetime.now()

    def utc_now(self):
        return datetime.utcnow()
