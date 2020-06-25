from typing import List
from ..model import OrderData
from old_helper import BaseRepository
from msgbus import MBEasyContext
from persistence import Connection
import base64


class OrderRetrieverRepository(BaseRepository):
    def __init__(self, mbcontext):
        # type: (MBEasyContext) -> None
        super(OrderRetrieverRepository, self).__init__(mbcontext)

    def get_order_data_list(self, initial_order_id, last_order_id):
        # type: (int, int) -> List[OrderData]
        def inner_func(conn):
            # type: (Connection) -> List[OrderData]
            if last_order_id is not None:
                query = self._RetrieveOrderQueryBetween.format(initial_order_id, last_order_id)
            else:
                query = self._RetrieveOrderQueryHigher.format(initial_order_id)

            ret = []
            for x in conn.select(query):
                try:
                    order_data = OrderData(int(x.get_entry(0)),
                                           int(x.get_entry(1)),
                                           base64.b64decode(x.get_entry(2)),
                                           base64.b64decode(x.get_entry(3)))
                    ret.append(order_data)
                except:
                    pass

            return ret

        return self.execute_with_connection(inner_func, service_name="FiscalPersistence")

    def get_last_order_id(self):
        # type: () -> int
        def inner_func(conn):
            # type: (Connection) -> int
            cursor = conn.select(self._LastOrderQuery)
            if cursor.rows() > 0:
                row_data = cursor.get_row(0).get_entry(0)
                if row_data is None:
                    return 0
                else:
                    return int(row_data)
            else:
                return 0

        return self.execute_with_connection(inner_func, service_name="FiscalPersistence")

    _RetrieveOrderQueryBetween = """SELECT OrderId, PosId, OrderPicture, XmlRequest 
FROM FiscalData
WHERE (SentToNfce = 1) AND (OrderId BETWEEN {0} AND {1})
ORDER BY OrderId"""

    _RetrieveOrderQueryHigher = """SELECT OrderId, PosId, OrderPicture, XmlRequest
FROM FiscalData
WHERE (SentToNfce = 1) AND (OrderId > {0})
ORDER BY OrderId"""

    _LastOrderQuery = """SELECT max(OrderId) FROM FiscalData"""
