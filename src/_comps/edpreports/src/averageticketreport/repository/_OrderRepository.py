# encoding: utf-8

from old_helper import BaseRepository


class OrderRepository(BaseRepository):

    def __init__(self, mbcontext, pos_list):
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list


    def get_paid_orders(self, business_period):
        def inner_func(conn):
            query = self._PaidOrdersQuery.format(business_period)
            orders = [[(x.get_entry(0), x.get_entry(1)) for x in conn.select(query)][0]]
            return orders

        return self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

    _PaidOrdersQuery = """\
SELECT SessionId, COUNT(*) AS orders
FROM orders
WHERE StateId = 5 AND BusinessPeriod = '{}'"""