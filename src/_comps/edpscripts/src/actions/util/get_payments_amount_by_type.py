import persistence
from systools import sys_log_exception

from .. import mb_context


def get_payments_amount_by_type(pos_id, session_id, payments_amount):
    conn = None

    try:
        conn = persistence.Driver().open(mb_context, str(pos_id))
        cursor = conn.select("""
            SELECT ot.TenderId, sum(ot.TenderAmount - COALESCE(ot.ChangeAmount, 0)) as Amount
            FROM OrderTender ot
            INNER JOIN Orders o ON o.OrderId = ot.OrderId
            WHERE sessionid = '{}' AND StateId = 5
            GROUP BY ot.TenderId""".format(session_id)
        )

        if cursor.rows() > 0:
            for row in cursor:
                if row.get_entry("TenderId") not in payments_amount:
                    payments_amount[row.get_entry("TenderId")] = float(row.get_entry("Amount") or 0.0)
                else:
                    current_amount = payments_amount[row.get_entry("TenderId")]
                    payments_amount[row.get_entry("TenderId")] = current_amount + float(row.get_entry("Amount") or 0.0)

    except Exception as _:
        sys_log_exception("Error getting ")
    finally:
        if conn:
            conn.close()

    return payments_amount
