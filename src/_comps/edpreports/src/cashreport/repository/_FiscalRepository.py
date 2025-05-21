from unicodedata import normalize

from old_helper import BaseRepository
from typing import List, Tuple
from persistence import Connection
from ..model import Order

BAND_DESCRIPTION_CACHE = None


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

        return self.execute_with_connection(inner_func, service_name="FiscalPersistence")

    _CardBrandsQuery = """SELECT
                          CASE WHEN bc.Descricao IS NOT NULL THEN bc.Descricao ELSE 'OUTROS' END AS Brand, pd.Type as Type, SUM(pd.Amount) as Amount, COUNT(pd.OrderId)
                          FROM fiscal.PaymentData pd
                          LEFT JOIN fiscal.BandeiraCartao bc on pd.Bandeira = bc.Bandeira
                          WHERE pd.Type IN (1,2) AND pd.OrderId IN ({0})
                          GROUP BY bc.Descricao, pd.Type
                          ORDER BY Type ASC, Amount DESC"""

    def get_brands_description(self):
        global BAND_DESCRIPTION_CACHE

        def inner_func(conn):
            query = "select bandeira, descricao from bandeiracartao"
            card_brands = {}
            for row in conn.select(query):
                card_brands[int(row.get_entry(0))] = _remove_accents(row.get_entry(1))
            return card_brands

        if not BAND_DESCRIPTION_CACHE:
            BAND_DESCRIPTION_CACHE = self.execute_with_connection(inner_func, service_name="FiscalPersistence")
        return BAND_DESCRIPTION_CACHE


def _remove_accents(text):
    return normalize('NFKD', unicode(text.decode('utf8'))).encode('ascii', 'ignore')
