# encoding: utf-8
import os
import iso8601
from systools import sys_log_info, sys_log_debug, sys_log_exception, sys_log_error
from helper import BaseRepository
from msgbus import MBEasyContext
from ..model import Order, OrderItem
from persistence import Connection
from datetime import datetime, timedelta
from typing import List, Dict, Union, Optional
from pyscriptscache import cache as _cache


class OrderRepository(BaseRepository):

    def __init__(self, mbcontext, pos_list):
        # type: (MBEasyContext, List[int], unicode) -> None
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list

    def get_paid_orders_by_real_date(self, initial_date, end_date):
        # type: (datetime, datetime) -> List[Order]
        return self._get_paid_orders(initial_date, end_date, True)

    def get_paid_orders_by_business_period(self, initial_date, end_date):
        # type: (datetime, datetime) -> List[Order]
        return self._get_paid_orders(initial_date, end_date, False)

    def get_orders_items(self, paid_orders):
        # type: (List[Order]) -> List[OrderItem]
        def inner_func(conn):
            # type: (Connection) -> List[Order]
            query = self._OrderItemsQuery

            order_list = map(lambda order: order.order_id, sorted(paid_orders))
            order_list = ','.join(map(str, order_list))
            query = query.format(order_list)

            all_order_items = {}  # type: Dict[int, OrderItem]
            try:
                order_items = [(int(x.get_entry(0)), int(x.get_entry(1)), str(x.get_entry(2))) for x in conn.select(query)]

                for order_tuple in order_items:
                    pcode = order_tuple[0]
                    quantity = order_tuple[1]
                    item_id = order_tuple[2]

                    cache_unit_price, cache_add_price, cache_sub_price = 0, 0, 0

                    if _cache.get_best_price(item_id, str(pcode)):
                        cache_unit_price, cache_add_price, cache_sub_price = _cache.get_best_price(item_id, str(pcode))

                    if float(cache_unit_price or '0.00') != 0 or float(cache_add_price or '0.00') != 0:
                        if pcode not in all_order_items.keys():
                            order_item = OrderItem(u"", quantity, pcode, cache_unit_price)
                            all_order_items[pcode] = order_item
                        else:
                            all_order_items[pcode].quantity += quantity

                return list(all_order_items.values())
            except Exception as e:
                sys_log_error("get order error: %s" % str(e))
                return list({"error": "error"}.values())

        return self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

    def _get_paid_orders(self, initial_date, end_date, real_date):
        # type: (Optional[datetime], Optional[datetime], Optional[bool]) -> List[Order]
        def inner_func(conn):
            # type: (Connection) -> List[Order]

            try:
                if real_date:
                    query = self._PaidOrderByRealDate
                    date_format = "%Y-%m-%d"
                else:
                    query = self._PaidOrderByBusinessPeriod
                    date_format = "%Y%m%d"

                query = query.format(initial_date.strftime(date_format), end_date.strftime(date_format))

                all_orders = {}  # type: Dict[int, Order]
                order_with_payments = [(int(x.get_entry(0)),
                                        int(x.get_entry(1)),
                                        datetime.strptime(x.get_entry(2), "%Y%m%d"),
                                        float(x.get_entry(3)),
                                        int(x.get_entry(4)),
                                        float(x.get_entry(5))) for x in conn.select(query)]

                for order_tuple in order_with_payments:
                    order_id = order_tuple[0]
                    order_state = order_tuple[1]
                    order_date = order_tuple[2]

                    if order_id not in all_orders:
                        order = Order(order_id, order_date, order_state)
                        all_orders[order_id] = order

                return list(all_orders.values())
            except:
                return list()

        return self.execute_in_all_databases_returning_flat_list(inner_func, self.pos_list)

    _PaidOrderByBusinessPeriod = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, o.TotalGross, ot.TenderId, ot.TenderAmount - coalesce(ot.ChangeAmount, 0)
from Orders o
inner join OrderTender ot
on o.OrderId = ot.OrderId
where o.BusinessPeriod >= '{0}' and o.BusinessPeriod <= '{1}' and o.StateId = 5"""

    _PaidOrderByRealDate = \
"""select o.OrderId, o.StateId, o.BusinessPeriod, o.TotalGross, ot.TenderId, ot.TenderAmount - coalesce(ot.ChangeAmount, 0)
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
on o.OrderId = od.OrderId"""


    _OrderItemsQuery = """\
    SELECT * FROM (
    SELECT PartCode, SUM(OrderedQty) as SOMA, ItemId
    FROM
        (SELECT u.PartCode, CASE u.level WHEN '0' THEN u.OrderedQty ELSE t.OrderedQty * u.OrderedQty END OrderedQty, u.ItemId, u.OrderId
        FROM OrderItem t
        JOIN OrderItem u ON t.OrderId = u.OrderId AND t.LineNumber = u.LineNumber
        JOIN Orders s ON t.OrderId = s.OrderId
        WHERE s.StateId = 5 AND u.OrderId IN ({0}) AND t.Level = '0'  AND u.PriceKey IS NOT NULL) T
    GROUP BY PartCode, ItemId) where SOMA is not null
    """
