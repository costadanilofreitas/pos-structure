from domain import Clock

from datetime import datetime


class RealClock(Clock):
    def get_current_date(self):
        return datetime.utcnow().date()

    def get_current_datetime(self):
        return datetime.utcnow()
