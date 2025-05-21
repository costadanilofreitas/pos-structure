from datetime import datetime

from msgbus import MBEasyContext
from old_helper import BaseRepository
from persistence import Connection
from typing import List, Union
from voidedlinesreport.model import Line


class OrderRepository(BaseRepository):
    def __init__(self, mbcontext, pos_list):
        # type: (MBEasyContext, List[int]) -> None
        super(OrderRepository, self).__init__(mbcontext)
        self.pos_list = pos_list

    def get_voided_lines(self, report_pos, initial_date, end_date, operator_id):
        # type: (Union[str, None], datetime, datetime, Union[int, None]) -> List[Line]
        def inner_func(conn):
            # type: (Connection) -> List[Line]
            query = self._GetVoidedLinesQuery.format(initial_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

            results = [[int(x.get_entry(0)),
                       x.get_entry(1),
                       int(x.get_entry(2)),
                       float(x.get_entry(3)),
                       int(x.get_entry(4)),
                       int(x.get_entry(5)),
                       float(x.get_entry(6)),
                       x.get_entry(7)]
                       for x in conn.select(query)]

            all_lines = []
            for columns in results:
                order_id = columns[0]
                session_id = columns[1]
                authorizator = None
                line_number = columns[2]
                quantity = columns[3]
                part_code = columns[4]
                price_key = columns[5]
                price = columns[6]
                void_datetime = columns[7]

                operator = int(session_id.split("user=")[1].split(",")[0])
                void_datetime = datetime.strptime(void_datetime, "%Y-%m-%dT%H:%M:%S.%f")

                if operator_id and operator_id != operator:
                    continue

                all_lines.append(Line(order_id,
                                      operator,
                                      authorizator,
                                      line_number,
                                      quantity,
                                      part_code,
                                      price_key,
                                      void_datetime,
                                      price))

            return all_lines

        report_pos_list = self.pos_list if report_pos is None else report_pos
        return self.execute_in_all_databases_returning_flat_list(inner_func, report_pos_list)

    _GetVoidedLinesQuery = """
    SELECT DISTINCT
        a.OrderId, 
        a.SessionId,
        a.LineNumber,
        CASE
            WHEN a.PartCode == b.PartCode 
            THEN coalesce(a.LastOrderedQty, a.DefaultQty) 
            ELSE coalesce(a.LastOrderedQty, a.DefaultQty) * b.LastOrderedQty 
        END Qty, 	
        a.PartCode, 
        a.PriceKey, 
        a.DefaultUnitPrice,
        a.LastUpdate
    FROM (
        SELECT
            oi.OrderId, 
            o.SessionId, 
            oi.PartCode, 
            oi.PriceKey, 
            oi.LastOrderedQty, 
            oi.DefaultQty, 
            oi.LastUpdate, 
            oi.LineNumber,
            op.DefaultUnitPrice
        FROM Orders o
            JOIN OrderItem oi ON oi.OrderId = o.OrderId
            JOIN OrderPrice op ON op.OrderId = o.OrderId
        WHERE (oi.LastOrderedQty > 0 OR oi.DefaultQty > 0)
            AND oi.PriceKey IS NOT NULL
            AND oi.PriceKey = op.PriceKey
            AND o.StateId in (5, 8)
            AND strftime('%Y-%m-%d', oi.LastUpdate, 'localtime') >= '{0}' 
            AND strftime('%Y-%m-%d', oi.LastUpdate, 'localtime') <= '{1}'
        ) a
        JOIN OrderItem b ON b.OrderId = a.OrderId 
            AND b.LineNumber = a.LineNumber 
            AND b.Level = 0 
            AND b.LastOrderedQty IS NOT NULL"""
