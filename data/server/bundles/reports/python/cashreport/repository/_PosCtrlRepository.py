from helper import BaseRepository
from persistence import Connection


class PosCtrlRepository(BaseRepository):
    def __init__(self, mbcontext):
        super(PosCtrlRepository, self).__init__(mbcontext)

    def get_operators_qty(self, pos_id, business_period):
        # type: (int, unicode) -> int
        def inner_func(conn):
            # type: (Connection) -> int
            query = self._OperatorsQtyQuery
            query = query.format(pos_id, business_period)
            return int(conn.select(query).get_row(0).get_entry(0))

        return self.execute_with_connection(inner_func)

    _OperatorsQtyQuery = "SELECT count(*) from UserSession WHERE PosId='{0}' AND BusinessPeriod='{1}';"
