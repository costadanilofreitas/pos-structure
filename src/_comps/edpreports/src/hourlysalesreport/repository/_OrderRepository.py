# encoding: utf-8
import datetime

from old_helper import BaseRepository
from ..model import Order


class OrderRepository(BaseRepository):

    def __init__(self, mbcontext, pos_list):
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list

    def get_sales_by_date(self, user_id, start_date, end_date):
        def inner_func(conn):
            start_date_formatted = datetime.datetime.strftime(start_date, "%Y-%m-%dT%H:%M:%S")
            end_date_formatted = datetime.datetime.strftime(end_date, "%Y-%m-%dT%H:%M:%S")

            query = self._OrdersQuery.format(user_id, start_date_formatted, end_date_formatted)

            orders = []
            for x in conn.select(query):
                orders.append(Order(x.get_entry("Timestamp"),
                                    x.get_entry("SaleType"),
                                    float(x.get_entry("Amount"))
                                    )
                              )
            return orders

        return self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

    _OrdersQuery = """\
    SELECT ocp.Value as Timestamp, st.TypeDescr as SaleType, o.TotalGross as Amount FROM Orders o
    INNER JOIN OrderCustomProperties ocp ON o.OrderId = ocp.OrderID
    INNER JOIN SaleType st ON o.SaleType = st.TypeId
    WHERE  o.stateid = 5 
        AND o.SessionId like '%user={0}%' 
        AND KEY = 'FISCALIZATION_DATE'
        AND ocp.value >= '{1}'
        AND ocp.value < '{2}'
    ORDER BY Timestamp
    """
