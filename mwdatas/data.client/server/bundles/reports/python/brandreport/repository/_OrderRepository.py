# encoding: utf-8
from datetime import datetime

from helper import BaseRepository
from msgbus import MBEasyContext
from persistence import Connection
from typing import List, Dict, Optional

from ..model import Order, OrderTender


class OrderRepository(BaseRepository):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"

    def __init__(self, mbcontext, pos_list):
        # type: (MBEasyContext, List[int]) -> None
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list

    def get_paid_orders_by_real_date(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_paid_orders(self.TypeRealDate, initial_date, end_date, operator_id, None, report_pos)

    def get_paid_orders_by_business_period(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_paid_orders(self.TypeBusinessPeriod, initial_date, end_date, operator_id, None, report_pos)

    def get_paid_orders_by_session_id(self, session_id):
        # type: (unicode) -> List[Order]
        return self._get_paid_orders(self.TypeSessionId, None, None, None, session_id, None)

    def _get_paid_orders(self, report_type, initial_date, end_date, operator_id, session_id, report_pos):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode]) -> List[Order]
        def inner_func(conn):
            # type: (Connection) -> List[Order]
            try:
                if report_type == self.TypeRealDate:
                    query = self._PaidOrdersByRealDateQuery
                    date_format = "%Y-%m-%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))
                elif report_type == self.TypeBusinessPeriod:
                    query = self._PaidOrderByBusinessPeriod
                    date_format = "%Y%m%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))
                else:
                    query = self._PaidOrderBySessionId
                    date_format = "%Y%m%d"
                    query = query.format(session_id)

                if report_type == self.TypeRealDate or self.TypeBusinessPeriod:
                    if operator_id is not None:
                        query += " and o.SessionId like '%user={0},%'".format(operator_id)

                all_orders = {}  # type: Dict[int, Order]
                order_with_payments = [(int(x.get_entry(0)),
                                        int(x.get_entry(1)),
                                        datetime.strptime(x.get_entry(2), date_format),
                                        float(x.get_entry(3)),
                                        int(x.get_entry(4)),
                                        float(x.get_entry(5))) for x in conn.select(query)]

                for order_tuple in order_with_payments:
                    order_id = order_tuple[0]
                    order_state = order_tuple[1]
                    order_date = order_tuple[2]
                    order_total = order_tuple[3]

                    if order_id in all_orders:
                        order = all_orders[order_id]
                    else:
                        order = Order(order_id, order_date, order_state, order_total, [])
                        all_orders[order_id] = order

                    tender_type = order_tuple[4]
                    tender_value = order_tuple[5]

                    order_tender = OrderTender(tender_type, tender_value)
                    order.tenders.append(order_tender)

                return list(all_orders.values())
            except Exception as _:
                return list()

        report_pos_list = self.pos_list if report_pos is None else (report_pos,)
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)

    _PaidOrdersByRealDateQuery = \
"""select o.OrderId, o.StateId, od.OrderDate, o.TotalGross, ot.TenderId, ot.TenderAmount - coalesce(ot.ChangeAmount, 0)
from Orders o
inner join OrderTender ot
on o.OrderId = ot.OrderId
inner join 
(
	-- Busca as Orders do dia que estamos interessadosh
	select OrderId, strftime('%Y-%m-%d', Value, 'localtime') OrderDate
	from OrderCustomProperties
	where key = 'FISCALIZATION_DATE' and strftime('%Y-%m-%d', Value, 'localtime') >= '{0}' and strftime('%Y-%m-%d', Value, 'localtime') <= '{1}'
) od
on o.OrderId = od.OrderId
where o.StateId = 5"""

    _PaidOrderByBusinessPeriod = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, o.TotalGross, ot.TenderId, ot.TenderAmount - coalesce(ot.ChangeAmount, 0)
from Orders o
inner join OrderTender ot
on o.OrderId = ot.OrderId
where o.BusinessPeriod >= '{0}' and o.BusinessPeriod <= '{1}' and o.StateId = 5"""

    _PaidOrderBySessionId = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, o.TotalGross, ot.TenderId, ot.TenderAmount - coalesce(ot.ChangeAmount, 0)
from Orders o
inner join OrderTender ot
on o.OrderId = ot.OrderId
where o.SessionId = '{0}' and o.StateId = 5"""