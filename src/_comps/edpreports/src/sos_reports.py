# -*- coding: utf-8 -*-
import time
from cStringIO import StringIO
from decimal import Decimal as D
# Our modules
from systools import sys_log_error
from reports import mbcontext
from msgbus import TK_POS_GETPOSLIST, TK_SYS_NAK
from persistence import Driver as DBDriver


COLS = 38
SEPARATOR = ("=" * COLS)
SINGLE_SEPARATOR = ("-" * COLS)
DATE_TIME_FMT = "%d/%m/%Y %H:%M:%S"
DATE_FMT = "%d/%m/%Y"
ZERO = D("0.00")


def _cut(s):
    return s[:COLS] if (len(s) > COLS) else s


def _center(s):
    s = _cut(s)
    miss = COLS - len(s)
    if miss == 0:
        return s
    left = miss / 2
    return (" " * left) + s


def _join(dic1, dic2):
    d = dict(dic1)
    d.update(dic2)
    return d


def diffdates(d1, d2):
    # Date format: %Y-%m-%d %H:%M:%S
    dt1, _, us = d1.partition(".")
    dt2, _, us = d2.partition(".")
    return (time.mktime(time.strptime(dt2, "%Y-%m-%dT%H:%M:%S")) - time.mktime(time.strptime(dt1, "%Y-%m-%dT%H:%M:%S")))


def speedOfService(pos_id, period, pos, store_id="", *args):
    if pos == '0':
        # get a pos list
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token == TK_SYS_NAK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        pos_list = sorted(map(int, msg.data.split("\0")))
    else:
        pos_list = [pos]

    slot = {}
    cont = {}

    pos_error_list = []
    for pos_id in pos_list:
        orders = {}
        conn = None
        try:
            # Opens the database connection
            conn = DBDriver().open(mbcontext, service_name="Persistence", dbname=str(pos_id))

            # Get the data
            orig_id = "POS%04d" % int(pos_id)
            cursor = conn.select('''
SELECT Orders.Orderid AS OrderId, SessionId,
CASE WHEN OrderStateHistory.Stateid IN (1, 6) THEN "START" WHEN OrderStateHistory.Stateid IN (2, 4, 5) THEN "END" END AS State,
CASE WHEN OrderStateHistory.Stateid IN (1, 6) THEN MIN(Timestamp) ELSE MAX(Timestamp) END AS Time
FROM OrderStateHistory
JOIN Orders ON Orders.OrderId = OrderStateHistory.OrderId
WHERE OrderStateHistory.StateId IN (1, 2, 4, 5, 6) AND
BusinessPeriod = '%(period)s' AND
OriginatorId = '%(orig_id)s'
GROUP BY Orders.Orderid, OrderStateHistory.Stateid''' % locals())

            # TODO: Quando uma venda for InProgess->Stored->Recalled->Paid estamos contando apenas Recalled->Paid
            for row in cursor:
                order_id, session_id, state, timestamp = map(row.get_entry, ("OrderId", "SessionId", "State", "Time"))

                user_id = session_id.split(",")[1].replace("user=", "")
                if order_id not in orders:
                    orders[order_id] = {}
                orders[order_id]['USER'] = user_id

                if state == "START":
                    orders[order_id]['START'] = user_id = timestamp
                if state == "END":
                    orders[order_id]['END'] = user_id = timestamp
        except Exception as e:
            pos_error_list.append(pos_id)
            sys_log_error("Error openning database for POS %s - %s" % (pos_id, e.message))
        finally:
            if conn:
                # Close database connection
                conn.close()

        for key in orders:
            order = orders[key]
            if 'START' in order and 'END' in order:
                seconds = diffdates(order['START'], order['END'])

                user = order['USER']
                if user in slot.keys():
                    slot[user] += seconds
                    cont[user] += 1
                else:
                    slot[user] = seconds
                    cont[user] = 1

    slot_total = 0
    cont_total = 0
    for operator in slot.keys():
        slot_total += slot[operator]
        cont_total += cont[operator]

        tmp = slot[operator] / cont[operator]
        slot[operator] = tmp

    if cont_total != 0:
        tmp = slot_total / cont_total
    else:
        tmp = 0

    slot_total = tmp

    # create string I/O to append the report info
    report = StringIO()
    if not report:
        return

    #         11        21        31      |
    # 12345678901234567890123456789012345678
    #
    # ======================================
    #       Relatorio Speed of Service
    #   Data/hora.....: 03/26/2009 13:06:12
    #   Dia Util......: 03/26/2009
    #   POS ..........: 01
    # ======================================
    # Operador                         Tempo
    # --------------------------------------
    # 326                               0:00
    # ======================================

    store_id = store_id.zfill(5)
    # titulo
    if pos == '0':
        pos_list = "Todos"
    title = _center("Relatorio Speed of Service")
    current_datetime = time.strftime(DATE_TIME_FMT)
    business_period = "%02d/%02d/%04d" % (int(period[6:8]), int(period[4:6]), int(period[:4]))
    report.write(
        """%(SEPARATOR)s
%(title)s
  Loja..........: %(store_id)s
  Data/hora.....: %(current_datetime)s
  Dia Util......: %(business_period)s
  POS...........: %(pos_list)s
""" % _join(globals(), locals()))
    if len(pos_error_list) > 0:
        report.write("  POS Erro......: %s\n" % pos_error_list)
    report.write("%s\n" % SEPARATOR)
    report.write("Operador         Vendas          Tempo\n")
    report.write("%s\n" % SINGLE_SEPARATOR)

    # imprime as linhas do relatorio
    for operator in slot.keys():
        report.write("%s" % operator)

        width = 23 - len(operator)
        tmp = str(cont[operator])
        report.write("%s" % tmp.rjust(width))

        width = 15
        tmp = time.strftime('%H:%M:%S', time.gmtime(slot[operator]))
        report.write("%s\n" % tmp.rjust(width))

    report.write("%s\n" % SEPARATOR)

    report.write("TOTAL")
    width = 23 - len("TOTAL")
    tmp = str(cont_total)
    report.write("%s" % tmp.rjust(width))
    width = 15
    tmp = time.strftime('%H:%M:%S', time.gmtime(slot_total))
    report.write("%s\n" % tmp.rjust(width))

    report.write("%s\n" % SEPARATOR)

    return report.getvalue()
