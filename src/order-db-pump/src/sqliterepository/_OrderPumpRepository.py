from sqlite3 import Row, Connection
from datetime import datetime

import orderpump.repository
from orderpump.model import OrderWithError
from sqliteutil import BaseRepository
from timeutil import Clock


class OrderPumpRepository(orderpump.repository.OrderPumpRepository, BaseRepository):
    def __init__(self, connection, clock):
        # type: (Connection, Clock) -> None
        super(OrderPumpRepository, self).__init__(connection)
        self.clock = clock

    def get_last_order_sent(self):
        return self.get_scalar("select OrderId from LastOrderSent")

    def set_last_order_processed(self, order_id):
        self.execute("update LastOrderSent set OrderId = ?", (order_id, ))

    def add_to_error(self, order_with_error):
        self.execute(add_to_error_query,
                     (order_with_error.order_id,
                      order_with_error.enabled,
                      order_with_error.retry_count,
                      order_with_error.next_retry,
                      False))

    def update_order_with_error(self, order_with_error):
        self.execute(update_order_with_error_query,
                     (order_with_error.enabled,
                      order_with_error.retry_count,
                      order_with_error.next_retry,
                      order_with_error.order_id))

    def get_orders_with_error(self):
        def mapper(row):
            # type: (Row) -> OrderWithError
            order_with_error = OrderWithError(row[0], self.clock)
            order_with_error.enabled = row[1]
            order_with_error.retry_count = row[2]
            order_with_error.next_retry = datetime.strptime(row[3], "%Y-%m-%d %H:%M:%S.%f")
            return order_with_error

        return self.execute(get_orders_with_error_query, mapper=mapper)

    def mark_as_sent(self, order_id):
        self.execute("update OrderWithError set Sent = true where OrderId = ?", (order_id, ))


add_to_error_query = """
insert into OrderWithError (OrderId, Enabled, RetryCount, NextRetry, Sent)
values
(?, ?, ?, ?, ?)
"""


update_order_with_error_query = """
update OrderWithError set Enabled = ?, RetryCount = ?, NextRetry = ?
where OrderId = ?
"""


get_orders_with_error_query = """
select OrderId, Enabled, RetryCount, NextRetry
from OrderWithError
where Sent = false AND Enabled = true AND DATETIME('now') > NextRetry
"""

