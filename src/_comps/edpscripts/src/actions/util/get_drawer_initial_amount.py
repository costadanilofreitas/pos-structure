import persistence
from systools import sys_log_exception

from .. import mb_context


def get_drawer_initial_amount(pos_id, session):
    conn = None
    try:
        conn = persistence.Driver().open(mb_context, pos_id)
        cursor = conn.select("select amount from transfer "
                             "where description = 'INITIAL_AMOUNT' and SessionId = '{}' "
                             "order by timestamp desc limit 1".format(session))

        if cursor.rows() > 0:
            for row in cursor:
                amount_data = float(row.get_entry(0) or 0.0)
                return amount_data

        return 0
    except:
        sys_log_exception("Error in consult initial amount")
    finally:
        if conn:
            conn.close()
