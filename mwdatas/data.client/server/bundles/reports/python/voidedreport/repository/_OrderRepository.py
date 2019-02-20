# encoding: utf-8

import re
from datetime import datetime

from helper import BaseRepository
from helper import convert_from_utf_to_localtime
from msgbus import MBEasyContext
from persistence import Connection
from typing import List, Optional

from ..model import Order


class OrderRepository(BaseRepository):
    TypeRealDate = "RealDate"
    TypeBusinessPeriod = "BusinessPeriod"
    TypeSessionId = "SessionId"

    def __init__(self, mbcontext, pos_list):
        # type: (MBEasyContext, List[int]) -> None
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list

    def get_voided_orders_by_real_date(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_voided_orders(self.TypeRealDate, initial_date, end_date, operator_id, None, report_pos)

    def get_voided_orders_by_business_period(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_voided_orders(self.TypeBusinessPeriod, initial_date, end_date, operator_id, None, report_pos)

    def get_voided_orders_by_session_id(self, session_id):
        # type: (unicode) -> List[Order]
        return self._get_voided_orders(self.TypeSessionId, None, None, None, session_id, None)

    def _get_voided_orders(self, report_type, initial_date, end_date, operator_id, session_id, report_pos):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode], Optional[unicode]) -> List[Order]
        def inner_func(conn):
            # type: (Connection) -> List[Order]

            try:
                if report_type == self.TypeRealDate:
                    query = self._VoidedOrdersByRealDateQuery
                    date_format = "%Y-%m-%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))
                elif report_type == self.TypeBusinessPeriod:
                    query = self._VoidedOrdersByBusinessPeriodQuery
                    date_format = "%Y%m%d"
                    query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))
                else:
                    query = self._VoidedOrdersBySessionIdQuery
                    query = query.format(session_id)

                if report_type == self.TypeRealDate or report_type == self.TypeBusinessPeriod:
                    if operator_id is not None:
                        query += " and o.SessionId like '%user={0},%'".format(operator_id)

                order_with_payments = [(int(x.get_entry(0)),
                                        unicode(x.get_entry(1).split(" - ")[-1]),
                                        int(re.search(r"(?:user=)(.\d*)", x.get_entry(2)).group(1)),
                                        x.get_entry(3),
                                        convert_from_utf_to_localtime(datetime.strptime(x.get_entry(4), "%Y-%m-%dT%H:%M:%S.%f")),
                                        float(x.get_entry(5))) for x in conn.select(query)]

                all_orders = []  # type: List[Order]
                for order_tuple in order_with_payments:
                    order_id = order_tuple[0]
                    order_reason = order_tuple[1]
                    order_operator_id = order_tuple[2]
                    order_authorizer = order_tuple[3]
                    order_datetime = order_tuple[4]
                    order_total = order_tuple[5]

                    order = Order(order_id, order_reason, order_operator_id, order_authorizer, order_datetime, order_total)
                    all_orders.append(order)

                return all_orders
            except:
                return list({"error": "error"}.values())


        report_pos_list = self.pos_list if report_pos is None else (report_pos, )
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)


    _VoidedOrdersByRealDateQuery = \
"""select o.OrderId, coalesce(vrs.Value, 'Nao Populada') as VoidReason, o.SessionId, aut.Value as AuthenticationUser, osh.OrderDate as Timestamp, coalesce(o.TotalGross, 0) as TotalGross
    from Orders o
    left join (
        select OrderId, OrderDate 
        from (
            select OrderId, (max(Timestamp)) OrderDate
                from (
                    select OrderId, StateId, Timestamp 
                        from OrderStateHistory 
                        where strftime('%Y-%m-%d', Timestamp, 'localtime') > strftime('%Y-%m-%d', '{0}' , '-1 day') and strftime('%Y-%m-%d', Timestamp, 'localtime') < strftime('%Y-%m-%d', '{1}' , '+1 day')
                )
                where StateId = 4
                group by OrderId
        ) a where strftime('%Y-%m-%d', a.OrderDate, 'localtime') >= '{0}' and strftime('%Y-%m-%d', a.OrderDate, 'localtime') <= '{1}'
    ) osh on o.OrderId = osh.OrderId
    left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_DESCR'
    left join OrderCustomProperties aut on aut.OrderId = o.OrderId and aut.Key = 'AUTHENTICATION_USER'
    where o.StateId = 4 and osh.OrderDate is not null"""

    _VoidedOrdersByBusinessPeriodQuery = \
"""select o.OrderId, coalesce(vrs.Value, 'Nao Populada') as VoidReason, o.SessionId, aut.Value as AuthenticationUser, max(osh.Timestamp) as Timestamp, coalesce(o.TotalGross, 0) as TotalGross
    from Orders o
	left join OrderStateHistory osh on osh.OrderId = o.OrderId
	left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_DESCR'
	left join OrderCustomProperties aut on aut.OrderId = o.OrderId and aut.Key = 'AUTHENTICATION_USER'
	where o.BusinessPeriod >= '{0}' and o.BusinessPeriod <= '{1}' and o.StateId = 4 and osh.OrderDate is not null"""

    _VoidedOrdersBySessionIdQuery = \
"""select o.OrderId, coalesce(vrs.Value, 'Nao Populada') as VoidReason, o.SessionId, aut.Value as AuthenticationUser, max(osh.Timestamp) as Timestamp, coalesce(o.TotalGross, 0) as TotalGross
	from Orders o
	left join OrderStateHistory osh on osh.OrderId = o.OrderId
	left join OrderCustomProperties vrs on vrs.OrderId = o.OrderId and vrs.Key = 'VOID_REASON_DESCR'
	left join OrderCustomProperties aut on aut.OrderId = o.OrderId and aut.Key = 'AUTHENTICATION_USER'
	where o.SessionId = '{0}' and o.StateId = 4 and osh.OrderDate is not null"""
