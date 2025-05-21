import salecomp.repository
from mwhelper import BaseRepository
from salecomp.model import Order, State, OrderType, SaleType, Line
from datetime import datetime, date
from pytz import timezone
from typing import Dict


class OrderRepository(salecomp.repository.OrderRepository, BaseRepository):
    def __init__(self, mb_context):
        super(OrderRepository, self).__init__(mb_context)
        self.sale_types = self.load_sale_types()  # type: Dict[int, SaleType]

    def get_order(self, pos_id, order_id):
        def inner_func(conn):
            cursor = conn.select(self.get_order_query.format(order_id))
            if cursor.rows() == 0:
                return None

            row = cursor.get_row(0)
            created_at = datetime.strptime(row.get_entry(5), "%Y-%m-%dT%H:%M:%S.%f")
            created_at.replace(tzinfo=timezone("UTC"))

            business_period_str = row.get_entry(6)
            business_period = date(int(business_period_str[0:4]),
                                   int(business_period_str[4:6]),
                                   int(business_period_str[6:8]))

            price_list_1 = row.get_entry(9)
            price_list_2 = row.get_entry(10)
            price_list_3 = row.get_entry(11)
            price_lists = []
            if price_list_1 is not None:
                price_lists.append(price_list_1)
            if price_list_2 is not None:
                price_lists.append(price_list_2)
            if price_list_3 is not None:
                price_lists.append(price_list_3)

            order = Order(id=int(row.get_entry(0)),
                          state=State(int(row.get_entry(1))),
                          type=OrderType(int(row.get_entry(2))),
                          originator_id=int(row.get_entry(3)[3:]),
                          sale_type=self.sale_types[int(row.get_entry(4))],
                          created_at=created_at,
                          business_period=business_period,
                          pod_type=row.get_entry(7),
                          session_id=row.get_entry(8),
                          price_lists=price_lists,
                          price_basis="G",
                          lines=[])

            lines = []
            for row in conn.select(self.get_order_lines_query.format(order_id)):
                lines.append(Line(line_number=int(row.get_entry(0)),
                                  item_id=row.get_entry(1),
                                  part_code=int(row.get_entry(2)),
                                  quantity=0 if row.get_entry(3) is None else int(row.get_entry(3)),
                                  lines=[]))

            active_lines, lines = self.separate_lines_with_item_id(lines, "1")
            root_lines = []
            for line in active_lines:
                root_lines.append(line)

            while len(active_lines) > 0:
                active_line = active_lines.pop()
                for line in lines[:]:
                    if line.item_id == active_line.get_line_code():
                        active_line.lines.append(line)
                        lines.remove(line)

            order.lines = root_lines
            return order

        return self.execute_with_connection(inner_func, str(pos_id))

    def add_line(self, line):
        pass

    def update_line(self, line):
        pass

    def delete_sons(self, line):
        pass

    def load_sale_types(self):
        def inner_func(conn):
            cursor = conn.select(self.load_sale_types_query)
            sale_types = {}
            for row in cursor:
                sale_type_id = int(row.get_entry(0))
                sale_types[sale_type_id] = SaleType(sale_type_id, row.get_entry(1))
            return sale_types

        return self.execute_with_connection(inner_func, "1")

    def separate_lines_with_item_id(self, lines, item_id):
        lines_with_item_id = []
        lines_without_item_id = []
        for line in lines:
            if line.item_id == item_id:
                lines_with_item_id.append(line)
            else:
                lines_without_item_id.append(line)
        return lines_with_item_id, lines_without_item_id

    get_order_query = \
"""select 
OrderId, 
StateId, 
OrderType, 
OriginatorId, 
SaleType,
CreatedAt, 
BusinessPeriod, 
DistributionPoint, 
SessionId, 
PriceListId1, 
PriceListId2, 
PriceListId3
from Orders
where OrderId = 4"""

    load_sale_types_query = \
"""select TypeId TypeDescr from SaleType"""

    get_order_lines_query = \
"""select LineNumber, ItemId, PartCode, OrderedQty FROM OrderItem where OrderId = {}"""
