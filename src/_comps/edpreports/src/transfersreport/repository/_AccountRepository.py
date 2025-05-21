# encoding: utf-8
from old_helper import BaseRepository
from ..model import Account


class AccountRepository(BaseRepository):

    def __init__(self, mbcontext):
        super(AccountRepository, self).__init__(mbcontext)

    def get_transfers_by_period(self, period, transfer_type):
        def inner_func(conn):
            query = self._AccountQuery.format(period, transfer_type)
            transfers = []
            for x in conn.select(query):
                transfers.append(Account(float(x.get_entry("Amount")),
                                         x.get_entry("Timestamp"),
                                         x.get_entry("GLAccount")
                                         )
                                 )
            return transfers

        return self.execute_with_connection(inner_func)

    _AccountQuery = """\
    SELECT *, strftime('%s',timestamp) as ID 
    FROM Transfer 
    WHERE period='{}' AND TYPE = '{}'
    """
