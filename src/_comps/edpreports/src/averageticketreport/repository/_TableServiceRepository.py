# encoding: utf-8

from old_helper import BaseRepository


class TableServiceRepository(BaseRepository):

    def __init__(self, mbcontext):
        super(TableServiceRepository, self).__init__(mbcontext)

    def get_paid_ticket(self, business_period):
        def inner_func(conn):
            query = self._PaidTicketsQuery.format(business_period)
            users_average_ticket = [(x.get_entry(0), x.get_entry(1)) for x in conn.select(query)]
            return users_average_ticket
        return self.execute_with_connection(inner_func)

    _PaidTicketsQuery = """\
SELECT UserId, SUM(NumberOfSeats) AS seats
FROM TableService tb
WHERE BusinessPeriod = '{}' AND (OrderId IS NOT NULL OR TotalAmount IS NOT NULL)
GROUP BY UserId
"""
