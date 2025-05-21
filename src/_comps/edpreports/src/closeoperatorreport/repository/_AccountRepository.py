# encoding: utf-8
from old_helper import BaseRepository
from ..model import Account


class AccountRepository(BaseRepository):

    def __init__(self, mbcontext):
        super(AccountRepository, self).__init__(mbcontext)

    def get_all_transfers(self, session):
        def inner_func(conn):
            query = self._AccountQuery.format(session)
            transfers = []
            for x in conn.select(query):
                transfers.append(Account(int(x.get_entry("Type")),
                                         float(x.get_entry("Amount")),
                                         int(x.get_entry("TenderId")),
                                         x.get_entry("Timestamp"),
                                         x.get_entry("GLAccount")
                                         )
                                 )
            return transfers

        return self.execute_with_connection(inner_func)

    _AccountQuery = """\
    SELECT Type, Amount, TenderId, Timestamp, GLAccount
    FROM Transfer
    WHERE SessionId = '{}'
    """
