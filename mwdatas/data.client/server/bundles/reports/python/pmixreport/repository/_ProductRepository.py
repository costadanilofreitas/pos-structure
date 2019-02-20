# encoding: utf-8
import os
import iso8601
from helper import BaseRepository
from msgbus import MBEasyContext
from ..model import OrderItem
from persistence import Connection
from typing import List, Dict, Union, Optional


class ProductRepository(BaseRepository):

    def __init__(self, mbcontext):
        # type: (MBEasyContext, List[int], unicode) -> None
        super(ProductRepository, self).__init__(mbcontext)

    def get_order_items_names(self, order_items):
        # type: (List[OrderItem]) -> List[OrderItem]
        def inner_func(conn):
            # type: (Connection) -> List[OrderItem]
            query = self._ProductNamesQuery
            pcodes_list = map(lambda order_item: order_item.pcode, order_items)
            pcodes_list = ','.join(map(str, pcodes_list))
            query = query.format(pcodes_list)
            product_names = [(int(x.get_entry(0)), x.get_entry(1)) for x in conn.select(query)]
            for product_tuple in product_names:
                for order_item in order_items:
                    if product_tuple[0] == order_item.pcode:
                        order_item.name = product_tuple[1]
            return order_items
        return self.execute_with_connection(inner_func)

    _ProductNamesQuery = """\
SELECT *
FROM Product
WHERE ProductCode IN ({0})
"""