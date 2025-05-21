from domain import TransferRepository, Transfer
from old_helper import BaseRepository
from persistence import Connection

from typing import List  # noqa


class MwBusinessPeriodTransferRepository(TransferRepository, BaseRepository):
    def __init__(self, mbcontext):
        super(MwBusinessPeriodTransferRepository, self).__init__(mbcontext)

    def get_transfers(self, initial_date, end_date):
        def inner_func(conn):
            # type: (Connection) -> List[Transfer]
            query = self._TransfersByBusinessPeriod.format(initial_date.strftime("%Y%m%d"),
                                                           end_date.strftime("%Y%m%d"))

            return [Transfer(Transfer.Type(int(x.get_entry(0))), float(x.get_entry(1))) for x in conn.select(query)]

        return self.execute_with_connection(inner_func)

    _TransfersByBusinessPeriod = """
select Type, Amount
from Transfer where Period >= '{0}' and Period <= '{1}'"""
