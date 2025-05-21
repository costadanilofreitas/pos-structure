from domain import OrderRepository, Order, OrderTender
from old_helper import BaseRepository
from persistence import Connection

from typing import Dict, List  # noqa


class MwBusinessPeriodOrderRepository(OrderRepository, BaseRepository):
    def __init__(self, mbcontext):
        super(MwBusinessPeriodOrderRepository, self).__init__(mbcontext)

    def get_order(self, initial_date, end_date, pos, operator):
        def inner_func(conn):
            # type: (Connection) -> List[Order]
            query = self.build_query(initial_date, end_date, pos, operator)
            return self.execute_query(conn, query)

        return self.execute_with_connection(inner_func)

    @staticmethod
    def build_query(initial_date, end_date, pos, operator):
        query = MwBusinessPeriodOrderRepository.business_period_query \
            .format(initial_date.strftime("%Y%m%d"),
                    end_date.strftime("%Y%m%d"))
        if pos is not None:
            query += " and o.SessionId like '%pos={}%'".format(pos)
        if operator is not None:
            query += " and o.SessionId like '%user={}%'".format(operator)
        return query

    @staticmethod
    def execute_query(conn, query):
        order_with_payments = [(int(x.get_entry(0)),
                                int(x.get_entry(1)),
                                float(x.get_entry(2)),
                                int(x.get_entry(3)),
                                float(x.get_entry(4))) for x in conn.select(query)]

        all_orders = {}  # type: Dict[int, Order]
        for order_tuple in order_with_payments:
            order_id = order_tuple[0]
            order_state = order_tuple[1]
            order_total = order_tuple[2]
            tender_type = order_tuple[3]
            tender_value = order_tuple[4]

            if order_id in all_orders:
                order = all_orders[order_id]
            else:
                order = Order(Order.OrderSate(order_state), order_total, [])
                all_orders[order_id] = order

            order_tender = OrderTender(str(tender_type), tender_value)
            order.tenders.append(order_tender)
        return list(all_orders.values())

    business_period_query = """
select o.OrderId, o.StateId, o.TotalGross, ot.TenderId, ot.TenderAmount
from Orders o
inner join OrderTender ot
on o.OrderId = ot.OrderId
where o.BusinessPeriod >= '{0}' and o.BusinessPeriod <= '{1}' and o.StateId in (4, 5)"""
