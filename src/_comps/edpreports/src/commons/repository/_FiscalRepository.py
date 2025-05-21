from helper import BaseRepository
from persistence import Connection  # noqa
from typing import List, Tuple  # noqa

from reports_app.cashreport.dto import Order  # noqa


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

    _CardBrandsQuery = """select
                          case when bc.Descricao is not null then bc.Descricao else 'OUTROS' end as Brand, pd.Type as Type, sum(pd.Amount) as Amount, count(pd.OrderId)
                          from fiscal.PaymentData pd
                          left join fiscal.BandeiraCartao bc on pd.Bandeira = bc.Bandeira
                          where pd.Type in (1,2) and pd.OrderId in ({0})
                          group by bc.Descricao, pd.Type
                          order by Type asc, Amount desc;"""
