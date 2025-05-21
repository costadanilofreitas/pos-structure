# -*- coding: utf-8 -*-

from datetime import datetime
from xml.etree import cElementTree as eTree

import sysactions
from msgbus import MBEasyContext
from old_helper import BaseRepository
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

    def get_discount_orders_by_real_date(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_discount_orders(self.TypeRealDate, initial_date, end_date, operator_id, None, report_pos)

    def get_discount_orders_by_business_period(self, initial_date, end_date, operator_id, report_pos):
        # type: (datetime, datetime, unicode, unicode) -> List[Order]
        return self._get_discount_orders(self.TypeBusinessPeriod, initial_date, end_date, operator_id, None, report_pos)

    def get_discount_orders_by_session_id(self, session_id):
        # type: (unicode) -> List[Order]
        return self._get_discount_orders(self.TypeSessionId, None, None, None, session_id, None)

    def _get_discount_orders(self, report_type, initial_date, end_date, operator_id, session_id, report_pos):
        # type: (unicode, Optional[datetime], Optional[datetime], Optional[unicode], Optional[unicode], Optional[unicode]) -> List[Order]
        def inner_func(conn):
            # type: (Connection) -> List[Order]

            date_format = "%Y%m%d"
            if operator_id is not None:
                current_session_id = "user={}".format(operator_id)
            else:
                current_session_id = session_id if session_id is not None and session_id != 'None' else ''

            if report_pos == self.TypeSessionId:
                query = self._DiscountOrdersBySessionIdQuery.format(session_id)
            else:
                if report_type == self.TypeBusinessPeriod:
                    query = self._DiscountOrdersByBusinessPeriodQuery
                else:
                    query = self._DiscountOrdersByRealDateQuery
                query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format), current_session_id)

            order_with_payments = [(x.get_entry(0),
                                    x.get_entry(1),
                                    x.get_entry(2),
                                    x.get_entry(3),
                                    x.get_entry(4),
                                    x.get_entry(5),
                                    x.get_entry(6)) for x in conn.select(query)]

            all_orders = []  # type: List[Order]
            for order_params in order_with_payments:
                empty_params = len([param for param in order_params if param is None]) > 0
                if empty_params:
                    continue

                order_id = int(order_params[0])
                discount_amount = float(order_params[1])
                total_gross = float(order_params[2])
                applied_date = datetime.strptime(order_params[3], "%Y-%m-%dT%H:%M:%S")
                operator = self.get_operator_name(order_params[4])
                authorizer = self.get_operator_name(order_params[5])

                order = Order(order_id, discount_amount, total_gross, applied_date, operator, authorizer)
                all_orders.append(order)

            return all_orders

        report_pos_list = self.pos_list if report_pos is None else (report_pos, )
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)

    @staticmethod
    def get_operator_name(operator_id):
        return eTree.XML(sysactions.get_user_information(int(operator_id))).find(".//user").get("LongName").upper()

    _DiscountOrdersByRealDateQuery = \
"""
    select 
        o.orderid, 
        o.discountamount,
        o.totalgross,
        ocp1.value as AppliedDate,
        ocp2.value as Operator,
        ocp3.value as Authorizer,
        ocp4.value as Method
    from orders o
    left join ordercustomproperties ocp1 on ocp1.orderid = o.orderid and ocp1.key = 'DISCOUNT_APPLY_DATETIME'
    left join ordercustomproperties ocp2 on ocp2.orderid = o.orderid and ocp2.key = 'DISCOUNT_APPLY_OPERATOR'
    left join ordercustomproperties ocp3 on ocp3.orderid = o.orderid and ocp3.key = 'DISCOUNT_APPLY_AUTHORIZER'
    left join ordercustomproperties ocp4 on ocp4.orderid = o.orderid and ocp4.key = 'DISCOUNT_APPLY_METHOD'
    inner join (
        select orderid, strftime('%Y%m%d', value, 'localtime') OrderDate
        from ordercustomproperties
        where key = 'FISCALIZATION_DATE' 
            and strftime('%Y%m%d', value, 'localtime') >= '{0}' 
            and strftime('%Y%m%d', value, 'localtime') <= '{1}'
    ) od on o.orderid = od.orderid
    where cast(o.discountamount as float) <> 0 
    and o.stateid = 5
    and o.sessionid like '%{2}%'
"""

    _DiscountOrdersByBusinessPeriodQuery = \
"""
    select 
        o.orderid, 
        o.discountamount,
        o.totalgross,
        ocp1.value as AppliedDate,
        ocp2.value as Operator,
        ocp3.value as Authorizer,
        ocp4.value as Method
    from orders o
    left join ordercustomproperties ocp1 on ocp1.orderid = o.orderid and ocp1.key = 'DISCOUNT_APPLY_DATETIME'
    left join ordercustomproperties ocp2 on ocp2.orderid = o.orderid and ocp2.key = 'DISCOUNT_APPLY_OPERATOR'
    left join ordercustomproperties ocp3 on ocp3.orderid = o.orderid and ocp3.key = 'DISCOUNT_APPLY_AUTHORIZER'
    left join ordercustomproperties ocp4 on ocp4.orderid = o.orderid and ocp4.key = 'DISCOUNT_APPLY_METHOD'
	where o.businessperiod >= '{0}' and o.businessperiod <= '{1}' 
        and o.stateid = 5
        and cast(o.discountamount as float) <> 0 
        and o.sessionid like '%{2}%'
"""

    _DiscountOrdersBySessionIdQuery = \
"""
    select 
        o.orderid, 
        o.discountamount,
        o.totalgross,
        ocp1.value as AppliedDate,
        ocp2.value as Operator,
        ocp3.value as Authorizer,
        ocp4.value as Method
    from orders o
    left join ordercustomproperties ocp1 on ocp1.orderid = o.orderid and ocp1.key = 'DISCOUNT_APPLY_DATETIME'
    left join ordercustomproperties ocp2 on ocp2.orderid = o.orderid and ocp2.key = 'DISCOUNT_APPLY_OPERATOR'
    left join ordercustomproperties ocp3 on ocp3.orderid = o.orderid and ocp3.key = 'DISCOUNT_APPLY_AUTHORIZER'
    left join ordercustomproperties ocp4 on ocp4.orderid = o.orderid and ocp4.key = 'DISCOUNT_APPLY_METHOD'
	where o.sessionid = '{0}' 
        and o.stateid = 5 
        and cast(o.discountamount as float) <> 0 
"""
