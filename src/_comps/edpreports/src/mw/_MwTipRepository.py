from datetime import datetime
from sqlite3 import Connection

from domain import TipRepository, OperatorTip
from old_helper import BaseRepository
from typing import List


class MwTipRepository(TipRepository, BaseRepository):

    def get_tips_per_operator(self, start_date=None, end_date=None, operator=None):
        # type: (datetime, datetime, str) -> List[OperatorTip]
        def inner_func(conn):
            # type: (Connection) -> List[OperatorTip]
            query = self._TipsQuery.format(
                start_date.strftime("%Y-%m-%d %H:%M:%S"),
                end_date.strftime("%Y-%m-%d %H:%M:%S"),
                " AND oicp.Value = {0}".format(operator) if operator is not None else ""
            )

            return [OperatorTip(x.get_entry(0), int(x.get_entry(1)), float(x.get_entry(2)), float(x.get_entry(3))) for x in conn.select(query)]

        return self.execute_with_connection(inner_func)

    _TipsQuery = """
        SELECT oicp.Value,
               sp.ServiceId,
               p.DefaultUnitPrice,
               tip.tip
        FROM ServiceSplit sp
        INNER JOIN OrderItem oi ON sp.SplitOrderId = oi.OrderId
        AND sp.SplitLineNumber = oi.LineNumber
        AND oi.OrderedQty > 0
        INNER JOIN
          (SELECT sp.OrderId,
                  sp.LineNumber,
                  Value
           FROM ServiceSplit sp
           INNER JOIN OrderItemCustomProperties oicp ON sp.OrderId = oicp.OrderId
           AND sp.LineNumber = oicp.LineNumber
           AND oicp.Key = 'operator' {2}
        ) oicp ON sp.OrderId = oicp.OrderId
        AND sp.LineNumber = oicp.LineNumber
        INNER JOIN Price p ON oi.PriceKey = p.PriceKey
        INNER JOIN
          (SELECT o.OrderId,
                  max(Tip) / max(TotalGross) tip
           FROM TableService ts
           INNER JOIN ServiceSplit sp ON ts.serviceId = sp.ServiceId
           INNER JOIN Orders o ON sp.SplitOrderId = o.OrderId
           INNER JOIN ServiceTip st ON sp.ServiceId = st.ServiceId
           AND sp.SplitKey = st.SplitKey
           WHERE ts.StartTS >= '{0}' and ts.FinishedTS <= '{1}'
        GROUP BY o.OrderId) tip ON oi.OrderId = tip.OrderId
    """
