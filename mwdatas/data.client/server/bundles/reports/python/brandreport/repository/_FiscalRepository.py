from helper import BaseRepository
from persistence import Connection
from typing import List, Tuple

from ..model import Order


class FiscalRepository(BaseRepository):
    def __init__(self, mbcontext):
        super(FiscalRepository, self).__init__(mbcontext)

    def get_card_brands(self, paid_orders):
        # type: (List[Order]) -> List[Tuple[unicode, int, float, int]]
        def inner_func(conn):
            # type: (Connection) -> List[Tuple[unicode, int, float, int]]
            order_list = map(lambda order: order.order_id, paid_orders)
            order_list = ','.join(map(str, order_list))
            query = self._CardBrandsQuery
            query = query.format(order_list)
            return [((x.get_entry(0)).decode('utf-8'), int(x.get_entry(1)), float(x.get_entry(2)), int(x.get_entry(3))) for x in conn.select(query)]

        return self.execute_with_connection(inner_func, None, "FiscalPersistence")

    _CardBrandsQuery = """SELECT
                          CASE WHEN bc.Descricao IS NOT NULL THEN bc.Descricao ELSE 'OUTROS' END AS Brand, pd.Type as Type, SUM(pd.Amount) as Amount, COUNT(pd.OrderId)
                          FROM fiscal.PaymentData pd
                          LEFT JOIN fiscal.BandeiraCartao bc on pd.Bandeira = bc.Bandeira
                          WHERE pd.Type IN (1,2) AND pd.OrderId IN ({0})
                          GROUP BY bc.Descricao, pd.Type
                          ORDER BY Type ASC, Amount DESC"""
