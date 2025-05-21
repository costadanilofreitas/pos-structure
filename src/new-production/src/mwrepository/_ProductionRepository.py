import base64
import cPickle as Pickle
from Queue import Queue, Empty
from threading import Thread

import production.repository
from mw_helper import BaseRepository
from persistence import Connection
from production.model import ProductionOrder
from typing import List


class ProductionRepository(BaseRepository, production.repository.ProductionRepository):
    def __init__(self, mb_context, logger):
        super(ProductionRepository, self).__init__(mb_context)
        self.logger = logger

        self.order_queue = Queue()
        self.running = True

        self.processor_thread = Thread(target=self.consume_queue)
        self.processor_thread.daemon = True
        self.processor_thread.start()

    def consume_queue(self):
        while self.running:
            order_id = None
            try:
                order_to_save = self.order_queue.get(True, 5)
                order_id = order_to_save.order_id
                self.save_order_async(order_to_save)
            except Empty:
                continue
            except BaseException as _:  # noqa
                self.logger.exception("Error saving order: {}".format(order_id))

    def stop(self):
        self.running = False

    def save_order(self, order):
        self.order_queue.put(order)

    def save_order_async(self, order):
        def func(conn):
            # type: (Connection) -> None
            order_data = base64.b64encode(Pickle.dumps(order, Pickle.HIGHEST_PROTOCOL))
            conn.query(insert_query.format(order.order_id, order_data, order.created_at, 0))

        self.execute_with_connection(func)

    def get_all_orders(self):
        def func(conn):
            # type: (Connection) -> List[ProductionOrder]
            orders = []
            for row in conn.select(select_query):
                order_data = base64.b64decode(row.get_entry(0))
                order = Pickle.loads(order_data)
                orders.append(order)

            return orders

        return self.execute_with_connection(func)

    def get_orders_to_purge(self, limit_date):
        def func(conn):
            # type: (Connection) -> List[int]
            orders = []
            formatted_limit_date = limit_date.strftime("%Y-%m-%dT%H:%M:%S")
            for row in conn.select(get_orders_to_purge_query.format(formatted_limit_date)):
                order_id = int(row.get_entry("OrderId"))
                orders.append(order_id)

            return orders

        return self.execute_with_connection(func)

    def purge_orders(self, orders):
        def func(conn):
            # type: (Connection) -> None
            orders_list = [str(order) for order in orders]
            query = purge_orders_query.format(",".join(orders_list))
            conn.query(query)

        return self.execute_with_connection(func)


insert_query = """
INSERT OR REPLACE INTO ProductionOrders
(OrderId, Object, CreatedAt, Purged)
VALUES
({}, '{}', '{}', {})
"""

select_query = """
SELECT Object FROM ProductionOrders WHERE PURGED = 0
"""

get_orders_to_purge_query = """
SELECT OrderId FROM ProductionOrders WHERE CreatedAt < '{}'
"""

purge_orders_query = """
DELETE FROM ProductionOrders WHERE OrderId IN ({})
"""
