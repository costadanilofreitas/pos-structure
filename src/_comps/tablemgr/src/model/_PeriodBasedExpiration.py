from memorycache import CacheExpiration
from datetime import datetime, timedelta


class PeriodBasedExpiration(CacheExpiration):
    def __init__(self, period_in_minutes):
        super(CacheExpiration, self).__init__()
        self.periodInMinutes = period_in_minutes
        self.expiration_date = datetime.now() - timedelta(days=1)

    def is_expired(self):
        return datetime.now() > self.expiration_date

    def renew(self):
        self.expiration_date = datetime.now() + timedelta(minutes=self.periodInMinutes)
