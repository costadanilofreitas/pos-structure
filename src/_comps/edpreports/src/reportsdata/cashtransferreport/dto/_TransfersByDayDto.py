import datetime  # noqa

from _Transfer import Transfer  # noqa


class TransfersByDayDto(object):
    def __init__(self, day, transfers_by_date):
        # type:(datetime, [Transfer]) -> None
        self.day = day
        self.transfers_by_date = transfers_by_date
