# encoding: utf-8
from old_helper import BaseRepository

from ..model import OrderTender


class OrderRepository(BaseRepository):

    def __init__(self, mbcontext, pos_list):
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list

    def get_paid_orders_by_tender_type(self, session_id):
        def inner_func(conn):
            query = self._PaidOrdersTotalAmountSumQuery.format(session_id)
            orders = []
            for x in conn.select(query):
                orders.append(OrderTender(x.get_entry("TenderId"),
                                          x.get_entry("TypeDescr"),
                                          float(x.get_entry("TenderAmount") or 0.0)))
            return orders

        return self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

    _PaidOrdersTotalAmountSumQuery = """SELECT ot.TenderId, st.TypeDescr, SUM(COALESCE(TenderAmount, 0) - COALESCE(ChangeAmount, 0)) AS TenderAmount
                                        FROM Orders o
                                        INNER JOIN OrderTender ot ON o.OrderId = ot.OrderId
                                        INNER JOIN SaleType st ON o.SaleType = st.TypeId
                                        WHERE o.StateId = 5 AND o.SessionId = '{}'
                                        GROUP BY st.TypeId, ot.TenderId"""
