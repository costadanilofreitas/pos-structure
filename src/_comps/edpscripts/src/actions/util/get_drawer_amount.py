from decimal import Decimal

import persistence
from sysactions import show_info_message
from systools import sys_log_exception

from .. import logger, mb_context


def get_drawer_amount(pos_id, period, session):
    logger.debug("--- get_drawer_amount START ---")
    conn = None
    try:
        conn = persistence.Driver().open(mb_context, dbname=str(pos_id))
        conn.transaction_start()
        # set the period
        logger.debug("--- get_drawer_amount DELETE ReportsPeriod ---")
        conn.query("DELETE FROM temp.ReportsPeriod")
        logger.debug("--- get_drawer_amount INSERT ReportsPeriod ---")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period, period))
        logger.debug("--- get_drawer_amount SELECT Transfer ---")
        cursor = conn.select("""SELECT T.Period AS Period,
           T.SessionId AS SessionId,
           SUM(CASE WHEN T.Type=1 THEN 1 ELSE 0 END) AS InitialFloatQty,
           tdsum(CASE WHEN T.Type=1 THEN T.Amount ELSE '0.00' END) AS InitialFloatAmount,
           SUM(CASE WHEN T.Type=2 THEN 1 ELSE 0 END) AS SkimQty,
           tdsum(CASE WHEN T.Type=2 THEN T.Amount ELSE '0.00' END) AS SkimAmount,
           SUM(CASE WHEN T.Type=3 THEN 1 ELSE 0 END) AS TransferInQty,
           tdsum(CASE WHEN T.Type=3 THEN T.Amount ELSE '0.00' END) AS TransferInAmount,
           SUM(CASE WHEN T.Type=4 THEN 1 ELSE 0 END) AS TransferOutQty,
           tdsum(CASE WHEN T.Type=4 THEN T.Amount ELSE '0.00' END) AS TransferOutAmount
            FROM
                Transfer T
            WHERE T.Period = '%s'
            AND T.SessionId = '%s'
            GROUP BY Period, SessionId""" % (period, session))

        row = cursor.get_row(0)
        if row is not None:
            initial_float = Decimal(row.get_entry("InitialFloatAmount") or 0)
            transfer_in_amount = Decimal(row.get_entry("TransferInAmount") or 0)
            skim_amount = Decimal(row.get_entry("SkimAmount") or 0)
            transfer_out_amount = Decimal(row.get_entry("TransferOutAmount") or 0)
        else:
            initial_float = 0
            transfer_in_amount = 0
            skim_amount = 0
            transfer_out_amount = 0

        logger.debug("--- get_drawer_amount SELECT Orders ---")
        cursor_cash_drawer = conn.select("""
        	SELECT
                   tdsub(tdsum(DA.SaleCashAmount),COALESCE(tdsum(DA.SaleCashChangeAmount), 0)) AS CashGrossAmount,
                   tdsum(DA.RefundCashAmount) AS RefundCashAmount
                FROM (
                    SELECT
                        substr(Orders.SessionID, instr(Orders.SessionID, 'period=')+7) AS BusinessPeriod,
                        Orders.SessionID AS SessionID,
                        Orders.OrderId AS OrderId,
                        tdsum(CASE WHEN (Orders.OrderType=0) THEN OrderTender.ChangeAmount ELSE '0.00' END) AS SaleChangeAmount,
                        tdsum(CASE WHEN (Orders.OrderType=0 AND OrderTender.TenderId=0) THEN OrderTender.ChangeAmount ELSE '0.00' END) AS SaleCashChangeAmount,
                        tdsum(CASE WHEN (Orders.OrderType=0 AND OrderTender.TenderId=0) THEN OrderTender.TenderAmount ELSE '0.00' END) AS SaleCashAmount,
                        COALESCE(tdsum(CASE WHEN (OrderTender.TenderId=0 AND Orders.OrderType=1) THEN tdsub(OrderTender.TenderAmount,COALESCE(OrderTender.ChangeAmount,'0')) ELSE '0.00' END),'0.00') AS RefundCashAmount,
                        COALESCE(tdsum(CASE WHEN (Orders.OrderType=0 AND OrderTender.TenderId=0) THEN OrderTender.TipAmount ELSE '0.00' END),'0.00') AS TipsCashAmount
                    FROM
                        orderdb.Orders Orders
                    JOIN
                        orderdb.OrderTender OrderTender
                        ON OrderTender.OrderId=Orders.OrderId
                    WHERE Orders.StateId=5 AND Orders.OrderType IN (0,1)
                    AND substr(Orders.SessionID, instr(Orders.SessionID, 'period=')+7) = '%s'
                    AND Orders.SessionID = '%s'
                    GROUP BY Orders.BusinessPeriod, Orders.SessionId, Orders.OrderId) AS DA""" % (period, session))

        row_cash_drawer = cursor_cash_drawer.get_row(0)
        cash_gross_amount = Decimal(row_cash_drawer.get_entry("CashGrossAmount") or 0)
        cash_refund_amount = Decimal(row_cash_drawer.get_entry("RefundCashAmount") or 0)
        logger.debug("--- get_drawer_amount SELECT OrderCustomProperties inner Orders---")
        cursor = conn.select("""SELECT COALESCE(SUM(ocp.Value), 0) AS DonatedAmount FROM OrderCustomProperties ocp 
                                INNER JOIN Orders o 
                                ON o.OrderId = ocp.OrderId 
                                WHERE ocp.Key = 'DONATION_VALUE' 
                                AND o.BusinessPeriod = '%s' 
                                AND o.SessionId = '%s'""" % (period, session))
        row = cursor.get_row(0)
        donated_amount = Decimal(row.get_entry("DonatedAmount") or 0)
        drawer_amount = initial_float + cash_gross_amount + transfer_in_amount + donated_amount - (cash_refund_amount + skim_amount + transfer_out_amount)
        drawer_amount = round(drawer_amount, 2)
    except Exception as ex:
        logger.exception("--- get_drawer_amount ---")
        sys_log_exception("get_drawer_amount Error")
        show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
        return
    finally:
        if conn:
            conn.close()
    logger.debug("--- get_drawer_amount END ---")
    return drawer_amount
