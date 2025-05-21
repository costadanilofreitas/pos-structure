from sqlite3 import Row

from sqliteutil import BaseRepository
from datetime import datetime

from typing import List

from ._Order import Order


class OrderRepository(BaseRepository):
    def __init__(self, conn):
        super(OrderRepository, self).__init__(conn)

    def get_paid_orders(self, business_period):
        # type: (datetime) -> List[Order]
        def mapper(row):
            # type: (Row) -> Order
            return Order(row[0], row[1], row[2], row[3], row[4], row[5])

        return self.execute(get_paid_orders_query, (business_period.strftime("%Y%m%d"), ), mapper)


get_paid_orders_query = """
select OrderId, StateId, TotalGross, TotalNet, DiscountAmount, coalesce(Tip, 0)
from Orders
where StateId = 5 and BusinessPeriod = ?
"""
