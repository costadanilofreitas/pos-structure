# -*- coding: utf-8 -*-

import datetime
import locale
import time
import json
import ast
import re
import cfgtools
import os

from xml.etree import cElementTree as etree
from cStringIO import StringIO
from collections import defaultdict
from decimal import Decimal as D
from unicodedata import normalize

import sysactions
from systools import sys_log_error, sys_log_exception, sys_parsefilepath
from reports import dbd, mbcontext, Report
from msgbus import TK_POS_GETPOSLIST, TK_SYS_NAK, TK_SYS_ACK
from sysdefs import eft_commands as eft
from operator import itemgetter
from brandreport import BrandReport
from brandreport.repository import OrderRepository as BrandOrderRepository,\
                                   FiscalRepository as BrandFiscalRepository,\
                                   TenderRepository as BrandTenderRepository
from cashreport import CashReport
from cashreport.repository import \
    OrderRepository,\
    AccountRepository,\
    TenderRepository,\
    FiscalRepository,\
    PosCtrlRepository,\
    TableRepository, \
    ProductRepository as CashProductRepository
from typing import Optional, Union
from utils import get_store_id
from voidedlinesreport import VoidedLinesReport
from voidedlinesreport.repository import \
    OrderRepository as VoidedLinesOrderRepository, \
    UsersRepository as VoidedLinesUsersRepository
from pmixreport import PMixReport
from pmixreport.repository import ProductRepository, OrderRepository as PmixOrderRepository
from voidedreport import VoidedReport
from voidedreport.repository import OrderRepository as VoidedOrderRepository
from averageticketreport import AverageTicketReport
from averageticketreport.repository import TableServiceRepository as AverageTicketTableServiceRepository,\
                                           OrderRepository as AverageTicketOrderRepository
from closeoperatorreport import CloseOperatorReport
from closeoperatorreport.repository import OrderRepository as CloseOperatorOrderRepository
from closeoperatorreport.repository import ProductRepository as CloseOperatorProductRepository
from closeoperatorreport.repository import AccountRepository as CloseOperatorAccountRepository
from transfersreport import TransfersReport
from transfersreport.repository import AccountRepository as TransferAccountRepository

from discountreport import DiscountReport
from discountreport.repository import OrderRepository as DiscountOrderRepository


sysactions.mbcontext = mbcontext

COLS = 38
SEPARATOR = ("=" * COLS)
SINGLE_SEPARATOR = ("-" * COLS)
DATE_TIME_FMT = "%d/%m/%Y %H:%M:%S"
DATE_FMT = "%d/%m/%Y"
CONSOLIDATED = True
ZERO = D("0.00")


def _join(dic1, dic2):
    d = dict(dic1)
    d.update(dic2)
    return d


def _manager_report_header(title, posid, oper_id, bus_period):
    title = _center(title)
    current_datetime = time.strftime(DATE_TIME_FMT)
    formatted_store_id = get_store_id().zfill(5) + "\n"

    if len(bus_period) == 8:
        business_period = "%02d/%02d/%04d" % (int(bus_period[6:8]), int(bus_period[4:6]), int(bus_period[:4]))
    else:
        business_period = "%s (Dia Fechado)" % (bus_period)

    if int(oper_id) == 0:
        oper_id = "Todos"
    else:
        if len(oper_id) == 1:
            oper_id = "0%s" % (oper_id)

    return (
        """%(SEPARATOR)s
%(title)s
  Loja..........: %(formatted_store_id)s
  Data/hora.....: %(current_datetime)s
  Data Negocio..: %(business_period)s
  ID Operador...: %(oper_id)02s (POS # %(posid)02d)
""" % _join(globals(), locals()))


def _cut(s):
    return s[:COLS] if (len(s) > COLS) else s


def _center(s):
    s = _cut(s)
    miss = COLS - len(s)
    if miss == 0:
        return s
    left = miss / 2
    return (" " * left) + s


def _fmt_number(number, decimalPlaces=2, decimalSep='.', thousandsSep=','):
    # Gets sign
    sign = '-' if number < 0 else ''
    number = abs(number)

    # Splits on decimals
    number, dec = ("%.*f" % (decimalPlaces, number)).split('.')

    # Adds thousands separators
    if thousandsSep:
        sepPos = len(number) - 3
        while sepPos >= 1:
            number = number[:sepPos] + thousandsSep + number[sepPos:]
            sepPos -= 3

    # Adds decimals separator
    if decimalSep:
        number += (decimalSep + dec)

    return sign + number


def cash(posid, period, operatorid, store_wide, posnumbers, report_type="0", session_id="", manager_user="", *args):
    report = StringIO()
    posnumbers = posnumbers.split('|') if posnumbers else []
    store_wide = (store_wide.lower() == "true")

    if report_type == "sales_report":
        report_type = "Relatorio de Vendas"

    elif report_type == "logoffuser":
        report_type = "Logout Operador"

    elif report_type == "cashier_flash":
        report_type = "Relatorio Surpresa"

    elif report_type == "end_of_day":
        report_type = "Fechamento do Dia"

    if store_wide:
        report_type = "%s (Loja)" % (report_type)
    else:
        posnumbers = [posid]

    manager_user = None if manager_user in ["None", ""] else manager_user
    report.write(_manager_report_header(report_type, int(posid), manager_user or operatorid, period))

    operators = []
    voided_item_qty, voided_item_amount = (0, 0)
    transfer_in_qty, transfer_in_amount, transfer_out_qty, transfer_out_amount, skim_qty, skim_amount, donated_qty, donated_amount = (0, 0, 0, 0, 0, 0, 0, 0)
    paid_qty, net_sales, voided_net_coupon, initialfloat, initial_coupon, total_coupon, total_declared = (0, 0, 0, 0, 0, 0, 0)
    voided_coupon_qtd, gross_sales, voided_gross_coupon, refund_gross_amount, refund_net_amount, refund_qty_count = (0, 0, 0, 0, 0, 0)
    waste_gross_amount, waste_net_amount, waste_qty_count, tax_sales = (0, 0, 0, 0)
    # creditcard_amount, giftcard_amount, cash_refund_amount, cash_gross_amount = (0, 0, 0, 0)
    cash_refund_amount, cash_gross_amount = (0, 0)
    #giftcard_sales_qty, giftcard_sales_amount, giftcard_refunds_qty, giftcard_refunds_amount, giftcard_paidOrders = (0, ZERO, 0, ZERO, 0)
    donations_amount, donations_refunds_amount, donations_qty = (ZERO, ZERO, 0)
    total_discount_amount = ZERO
    total_tip, cash_tips, refunded_tips, voided_tips = (0, 0, 0, 0)

    pos_included = []
    any_data = False
    discountInfos = defaultdict(lambda: {"Descr": "", "Qty": 0, "Amt": ZERO})
    tenderInfos = defaultdict(lambda: {"TenderId": "", "TenderDescr": "", "TenderTotal": ZERO})
    #giftcardInfos = defaultdict(lambda: {"Qty": 0, "Amt": ZERO})
    donationInfos = defaultdict(lambda: {"Descr": "", "Qty": 0, "Amt": ZERO})
    list_orderid_fiscal = []
    is_print_flag_card = False

    for posno in posnumbers:
        pos_included.append(posno)

        # create database connection
        conn = None
        try:
            try:
                conn = dbd.open(mbcontext, dbname=str(posno))
            except:
                sys_log_exception("Excecao abrindo conexao com pos: " + str(posno))
                continue

            # reserve a database connection
            conn.transaction_start()

            # set the period
            conn.query("DELETE FROM temp.ReportsPeriod")
            conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period, period))

            if (report_type == "Relatorio Surpresa") and int(operatorid):
                # Retrieve only the latest session id (eLanes ticket #15)
                cursor = conn.select("SELECT SessionId FROM posctrl.UserSession WHERE BusinessPeriod='%s' AND PosId=%s AND OperatorId=%s ORDER BY OpenTime DESC LIMIT 1" % (period, posid, operatorid))
                if cursor.rows():
                    session_id = cursor.get_row(0).get_entry(0)

            # select temporary table
            if session_id:
                cursor = conn.select("SELECT * from temp.CASHView WHERE BusinessPeriod='%s' AND SessionId='%s';" % (period, session_id))
            elif int(operatorid):
                cursor = conn.select("SELECT * from temp.CASHView WHERE PosId='%s' AND BusinessPeriod='%s' AND OperatorId='%s';" % (posno, period, operatorid))
            else:
                cursor = conn.select("SELECT * from temp.CASHView WHERE PosId='%s' AND BusinessPeriod='%s';" % (posno, period))

            # for col in cursor.get_names():
            #     report.write("%*s "%(25, col))
            # report.write("\n")

            # for row in cursor:
            #     for entry in row:
            #        report.write("%*s "%(25, entry))
            #     report.write("\n")
            for row in cursor:
                any_data = True
                operator_id = row.get_entry("OperatorId")  # ID Operador
                operator_name = row.get_entry("OperatorName")  # Operator Name

                # Get the Initial Coupon for the Day
                if row.get_entry("InitialOrderId"):
                    initial_coupon = min((initial_coupon, int(row.get_entry("InitialOrderId"))))

                # List all operators # for the Day
                operators.append(row.get_entry("OperatorId"))

                # Sum all initial float for the Day
                initialfloat = initialfloat + D(row.get_entry("InitialFloat"))

                # Sum all gross sales for the Day
                gross_sales = gross_sales + D(row.get_entry("PaidGrossAmt"))

                # Sum all net sales for the Day
                net_sales = net_sales + D(row.get_entry("PaidNetAmt"))

                # Sum all paid quantities for the Day
                paid_qty = paid_qty + int(row.get_entry("PaidCount"))

                # Sum all gross voided sales for the day
                voided_gross_coupon = voided_gross_coupon + D(row.get_entry("VoidGrossAmt"))

                # Sum all net voided sales for the day
                voided_net_coupon = voided_net_coupon + D(row.get_entry("VoidNetAmt"))

                # Sum all voided quantities for the day
                voided_coupon_qtd = voided_coupon_qtd + int(row.get_entry("VoidCount"))

                # Sum all coupon quantities (transactions) for the day
                total_coupon = total_coupon + int(row.get_entry("TransactCount"))

                # Get the last order ID (coupon number) for the Day
                # if row.get_entry("FinalOrderId"):
                #     final_coupon = int(row.get_entry("FinalOrderId"))

                # Sum all refund gross amount for the Day
                refund_gross_amount = refund_gross_amount + D(row.get_entry("RefundGrossAmt"))

                # Sum all refund net amount for the Day
                refund_net_amount = refund_net_amount + D(row.get_entry("RefundNetAmt"))

                # Sum all refund quantities for the Day
                refund_qty_count = refund_qty_count + int(row.get_entry("RefundCount"))

                # Sum all waste gross amount for the Day
                waste_gross_amount = waste_gross_amount + D(row.get_entry("WasteGrossAmt"))

                # Sum all waste net amount for the Day
                waste_net_amount = waste_net_amount + D(row.get_entry("WasteNetAmt"))

                # Sum all waste quantities for the Day
                waste_qty_count = waste_qty_count + int(row.get_entry("WasteCount"))

                # Sum all CASH refund amounts
                cash_refund_amount += D(row.get_entry("CashRefundAmount") or 0)

                # Sum all CASH gross sales amounts
                cash_gross_amount += D(row.get_entry("CashGrossAmount") or 0)

                # Get the Initial GT(Gran Total) Gross
                # if row.get_entry("InitialPOSForeverTotalGross"):
                #     initial_GT_gross = D(row.get_entry("InitialPOSForeverTotalGross"))

                # Sum all voided items quantities for the Day
                if row.get_entry("ReducedItemsQty"):
                    voided_item_qty = voided_item_qty + int(row.get_entry("ReducedItemsQty"))

                # Sum all voided items amount for the Day
                if row.get_entry("ReducedAmount"):
                    voided_item_amount = voided_item_amount + D(row.get_entry("ReducedAmount"))

                # Sum all Transfer IN quantities for the Day
                if row.get_entry("TransferInQty"):
                    transfer_in_qty = transfer_in_qty + int(row.get_entry("TransferInQty"))

                # Sum all Transfer IN Amount for the Day
                if row.get_entry("TransferInAmount"):
                    transfer_in_amount = transfer_in_amount + D(row.get_entry("TransferInAmount"))

                # Sum all Transfer OUT quantities for the Day
                if row.get_entry("TransferOutQty"):
                    transfer_out_qty = transfer_out_qty + int(row.get_entry("TransferOutQty"))

                # Sum all Transfer OUT Amount for the Day
                if row.get_entry("TransferOutAmount"):
                    transfer_out_amount = transfer_out_amount + D(row.get_entry("TransferOutAmount"))

                # Sum all Skim quantities for the Day
                if row.get_entry("SkimQty"):
                    skim_qty = skim_qty + int(row.get_entry("SkimQty"))

                # Sum all Skim Amount for the Day
                if row.get_entry("SkimAmount"):
                    skim_amount = skim_amount + D(row.get_entry("SkimAmount"))

                if row.get_entry("DiscountSessionInfo"):
                    discountInfo = eval(row.get_entry("DiscountSessionInfo"))
                    for discount in discountInfo:
                        consolidated = discountInfos[discount["Code"]]
                        amt = D(discount["Amt"])
                        consolidated["Descr"] = discount["Descr"]
                        consolidated["Qty"] += int(discount["Qty"])
                        consolidated["Amt"] += amt
                        total_discount_amount += amt

                if row.get_entry("TenderSessionInfo"):
                    tenderInfo = eval(row.get_entry("TenderSessionInfo"))
                    for tender in tenderInfo:
                        consolidated = tenderInfos[tender["TenderId"]]
                        consolidated["TenderId"] = tender["TenderId"]
                        consolidated["TenderDescr"] = tender["TenderDescr"]
                        consolidated["TenderTotal"] += D(tender["TenderTotal"])


                # Gift Cards
                #giftcard_sales_qty += int(row.get_entry("GiftCardSales") or 0)
                #giftcard_sales_amount += D(row.get_entry("GiftCardsAmount") or 0)
                #giftcard_refunds_qty += int(row.get_entry("GiftCardRefunds") or 0)
                #giftcard_refunds_amount += D(row.get_entry("GiftCardsRefundsAmount") or 0)
                #giftcard_paidOrders += int(row.get_entry("PaidOrdersWithGiftCard") or 0)
                #giftCardsActivityInfo = row.get_entry("GiftCardsActivityInfo")

                #if giftCardsActivityInfo:
                #    for gcInfo in eval(giftCardsActivityInfo):
                #        giftcardInfos[gcInfo["Type"]]["Qty"] += int(gcInfo["Qty"])
                #        giftcardInfos[gcInfo["Type"]]["Amt"] += D(gcInfo["Amt"])

            # Select declared cash information
            cursor = conn.select("""SELECT
                        COALESCE(sum(tr.amount), 0) AS "Declared"
                     FROM posctrl.UserSession us
                      LEFT JOIN account.Transfer tr ON us.SessionId = tr.SessionId AND tr.Description = 'DECLARED_AMOUNT'
                     WHERE tr.Period = %s AND tr.PosId = %s %s;""" % (period, posno, '' if int(operatorid) == 0 else ('AND us.OperatorId = %s' % operatorid)))

            for row in cursor:
                total_declared += D(row.get_entry('Declared'))

            # Select the donations information
            if session_id:
                where_clause = "WHERE O.BusinessPeriod='%s' AND U.SessionId='%s'" % (period, session_id)
            elif int(operatorid):
                where_clause = "WHERE U.PosId='%s' AND O.BusinessPeriod='%s' AND U.OperatorId='%s'" % (posno, period, operatorid)
            else:
                where_clause = "WHERE U.PosId='%s' AND O.BusinessPeriod='%s'" % (posno, period)

            sql = """
            SELECT
            ProductCode AS DonationCode,
            ProductName AS DonationName,
            tdsum(CASE WHEN X.IsRefund THEN '0.00' ELSE TotalPrice END) AS DonatedAmount,
            tdsum(CASE WHEN X.IsRefund THEN TotalPrice ELSE '0.00' END) AS RefundedAmount,
            sum(DonatedQty) AS DonatedQty
            FROM (
                SELECT
                    OI.PartCode AS ProductCode,
                    tdsum(tdmul(COALESCE(OI.OverwrittenUnitPrice, PR.DefaultUnitPrice, '0.00'), OI.OrderedQty)) AS TotalPrice,
                    P.ProductName AS ProductName,
                    (CASE WHEN O.OrderType=0 THEN 1 ELSE 0 END) AS DonatedQty,
                    (CASE WHEN O.OrderType=1 THEN 1 ELSE 0 END) AS IsRefund
                FROM orderdb.Orders O
                JOIN orderdb.OrderItem OI
                    ON OI.OrderId=O.OrderId AND O.StateId=5 AND OI.OrderedQty>0
                JOIN productdb.ProductCustomParams PCP
                    ON OI.PartCode=PCP.ProductCode AND LOWER(PCP.CustomParamId)='familygroup' AND LOWER(PCP.CustomParamValue)='donation'
                JOIN productdb.Product P
                    ON P.ProductCode=OI.PartCode
                JOIN posctrl.UserSession U
                    ON O.BusinessPeriod=U.BusinessPeriod AND O.SessionId=U.SessionId
                LEFT JOIN productdb.Price PR
                    ON PR.PriceKey=OI.PriceKey
                %(where_clause)s AND O.OrderType IN (0,1)
                GROUP BY OI.OrderId,OI.PartCode
            ) X
            GROUP BY X.ProductCode
            """ % ({"where_clause": where_clause})

            cursor = conn.select(sql)
            for row in cursor:
                consolidated = donationInfos[str(row.get_entry("DonationCode"))]
                consolidated["Descr"] = str(row.get_entry("DonationName"))
                consolidated["Qty"] += int(row.get_entry("DonatedQty"))
                consolidated["Amt"] += D(row.get_entry("DonatedAmount"))
                donations_qty += int(row.get_entry("DonatedQty"))
                donations_amount += D(row.get_entry("DonatedAmount"))
                donations_refunds_amount += D(row.get_entry("RefundedAmount"))

            if session_id:
                cursor = conn.select("""SELECT COALESCE(COUNT(ocp.value), 0) AS DonatedQty, COALESCE(SUM(ocp.Value), 0) AS DonatedAmount FROM OrderCustomProperties ocp 
                                        INNER JOIN Orders o 
                                        ON o.OrderId = ocp.OrderId 
                                        WHERE ocp.Key = 'DONATION_VALUE' 
                                        AND o.BusinessPeriod = '%s' 
                                        AND o.SessionId = '%s'""" % (period, session_id))
            else:
                cursor = conn.select("""SELECT COALESCE(COUNT(ocp.value), 0) AS DonatedQty, COALESCE(SUM(ocp.Value), 0) AS DonatedAmount FROM OrderCustomProperties ocp 
                                        INNER JOIN Orders o 
                                        ON o.OrderId = ocp.OrderId 
                                        WHERE ocp.Key = 'DONATION_VALUE' 
                                        AND o.BusinessPeriod = '%s'""" % period)
            row = cursor.get_row(0)

            donated_amount = D(row.get_entry("DonatedAmount") or 0)
            donated_qty = D(row.get_entry("DonatedQty") or 0)

        finally:
            if conn:
                conn.close()

        # create database connection
        conn = None
        try:
            conn = dbd.open(mbcontext, dbname=str(posno))

            # reserve a database connection
            conn.transaction_start()

            originatorid = "POS%04d" % int(posno)

            if int(operatorid):
                sql = """SELECT OT.OrderId, O.OrderType, O.StateId, OT.OrderTenderId, COALESCE(OT.TipAmount,'0.00') AS TipAmount, TT.TenderId, TT.TenderDescr
                     FROM orderdb.OrderTender OT
                     JOIN productdb.TenderType TT ON TT.TenderId=OT.TenderId
                     JOIN orderdb.Orders O ON O.OrderId=OT.OrderId
                     WHERE O.BusinessPeriod='%s'
                     AND O.OriginatorId = '%s'
                     AND O.StateId IN (5,4)
                     AND O.SessionId LIKE '%%user=%s%%'
                    """ % (period, originatorid, operatorid)
            else:
                sql = """SELECT OT.OrderId, O.OrderType, O.StateId, OT.OrderTenderId, COALESCE(OT.TipAmount,'0.00') AS TipAmount, TT.TenderId, TT.TenderDescr
                     FROM orderdb.OrderTender OT
                     JOIN productdb.TenderType TT ON TT.TenderId=OT.TenderId
                     JOIN orderdb.Orders O ON O.OrderId=OT.OrderId
                     WHERE O.BusinessPeriod='%s'
                     AND O.OriginatorId = '%s'
                     AND O.StateId IN (5,4)
                    """ % (period, originatorid)

            if session_id:
                sql += "AND O.SessionId = '%s'" % session_id

            cursor = conn.select(sql)

            for row in cursor:
                list_orderid_fiscal.append(row.get_entry("OrderId"))

                if int(row.get_entry("OrderType")) == 0 and int(row.get_entry("StateId")) == 5:
                    total_tip += D(row.get_entry("TipAmount"))
                    if row.get_entry("TenderId") == "0":
                        cash_tips += D(row.get_entry("TipAmount"))
                elif int(row.get_entry("OrderType")) == 0 and int(row.get_entry("StateId")) == 4:
                    voided_tips += D(row.get_entry("TipAmount"))
                elif int(row.get_entry("OrderType")) == 1 and int(row.get_entry("StateId")) == 5:
                    refunded_tips += D(row.get_entry("TipAmount"))

        finally:
            if conn:
                conn.close()

    # Tax calculation
    tax_sales = (gross_sales - net_sales)

    if is_print_flag_card:
        fiscal_conn, cursor_card, card_flags = None, None, None
        try:
            sql = """SELECT
                CASE WHEN bc.Descricao IS NOT NULL THEN bc.Descricao ELSE 'OUTROS' END as desc,
                pd.Type as type,
                sum(pd.Amount) as amout
            FROM fiscal.PaymentData pd
            LEFT JOIN fiscal.BandeiraCartao bc on pd.Bandeira = bc.Bandeira
            WHERE pd.Type IN (1,2) AND pd.OrderId IN {0}
            GROUP BY bc.Descricao, pd.Type""".format('(' + ', '.join((str(n) for n in list_orderid_fiscal)) + ')')

            fiscal_conn = dbd.open(mbcontext, service_name="FiscalPersistence")
            cursor_card = fiscal_conn.select(sql)
            card_flags = [dict([(cursor_card.get_name(col_id), row.get_entry(col_id)) for col_id in range(cursor_card.cols())]) for row in cursor_card]
        except:
            sys_log_exception("Excecao get flags")
        finally:
            if fiscal_conn:
                fiscal_conn.close()

    # eLanes requested to remove GC sold and donations amount from Gross and Net Sales
    #gross_sales -= (giftcard_sales_amount + donations_amount)
    #net_sales -= (giftcard_sales_amount + donations_amount)

    # eLanes ticket #37 (Gross and Net description) - Add discounts to gross sales
    #gross_sales += total_discount_amount
    gross_sales += voided_gross_coupon

    # eLanes ticket #22 (Changes on reporting of refunds) - remove refunds from net sales and tax
    refund_tax_amount = (refund_gross_amount - refund_net_amount)
    net_sales -= refund_net_amount
    tax_sales -= refund_tax_amount

    # eLanes ticket #39 (Refund of Donations or Gift Cards should not decrease Gross or Net Sales)
    #net_sales += (giftcard_refunds_amount + donations_refunds_amount)

    # eLanes ticket #71 (Refund Net and Gross should include only product oriented Refunds)
    #refund_gross_amount -= (giftcard_refunds_amount + donations_refunds_amount)
    #refund_net_amount -= (giftcard_refunds_amount + donations_refunds_amount)
    #refund_qty_count -= giftcard_refunds_qty
    temp_pos_list = "POS incluidos...: "+" ".join(posnumbers)
    report.write("%s\n" % (SEPARATOR))
    report.write(temp_pos_list[:COLS])
    if len(temp_pos_list) > COLS:
        report.write("\n             %s" % temp_pos_list[COLS:2*COLS-18])
    if len(temp_pos_list) > 2*COLS-18:
        report.write("\n             %s" % temp_pos_list[2 * COLS - 18:3 * COLS - 36])
    report.write("\n%s\n" % (SEPARATOR))

    # Check if there is any data to print
    if not any_data:
        # report.write(_center("Dados nao encontrados para o operador # %s\n" % (operatorid)))
        report.write(_center("Sem dados para o movimento\n"))
        report.write("%s\n" % (SEPARATOR))
        return report.getvalue()

    def add_line(descr, qty=None, amount=None, info=None):
        DESCR = 17
        if amount is not None:
            amount = _fmt_number(float(amount))

        descr = descr[0:DESCR]

        if len(descr) < DESCR:
            descr += '.' * (DESCR - len(descr))

        if qty is not None:
            line = "%s: [%4s] " % (descr, qty)
        else:
            line = "%s: " % (descr)

        if amount is not None:
            if qty is None:
                line += "       "
            remain = COLS - len(line) - 3
            line += "R$ %*s\n" % (remain, amount)
        elif info is not None:
            remain = COLS - len(line)
            line += "%*.*s\n" % (remain, remain, info)
        else:
            line += "\n"

        report.write(line)

    # Starting Printing
    report.write("Descricao         Qtd         Total\n")

    # Initial Float
    add_line("Balanco Inicial", None, initialfloat)

    if int(operatorid) == 0:
        # Operators (Quantity)
        add_line("Operadores", len(operators), None)
    else:
        # ID Operador
        add_line("ID Operador", info=operator_id)
        # Operator Name
        add_line("Nome Operador", info=operator_name)

    # Initial Coupon Number
    # report.write("Initial Order ID...: %17s\n"%(initial_coupon))

    # Final Coupon Number
    # report.write("Final Order ID.....: %17s\n"%(final_coupon))

    # Total Transactions Count (Quantity)
    add_line("Total Pedidos", info=total_coupon)

    # Initial GT (Gran Total) Gross
    # report.write("Initial GT Gross...: $ %15.2f\n"%(initial_GT_gross))

    # Gross Sales
    add_line("Vendas", None, gross_sales)

    # Final/Current GT (Gran Total) Gross
    # final_GT_gross = initial_GT_gross + gross_sales
    # report.write("Curr/Final GT Gross: $ %15.2f\n"%(final_GT_gross))

    # Voided (Coupons) Gross Amount
    add_line("Cancelamentos", voided_coupon_qtd, voided_gross_coupon)

    # Voided (Coupons) Net Amount
    # add_line("Cancelamentos Liquido", None, voided_net_coupon)

    # Tax Sales Amount
    # add_line("Impostos de Venda", None, tax_sales)

    # Net Sales Amount
    add_line("Venda Liquida", None, net_sales + tax_sales)

    # Paid Quantity
    add_line("Pedidos Pagos", info=paid_qty)

    # TenderSessionInfo - get the information of specific tenders
    add_line("Total Recebido")
    for tenderid, tender in sorted(tenderInfos.items()):
        amt, descr = map(tender.get, ("TenderTotal", "TenderDescr"))
        if descr == 'CARTAO CREDITO' and is_print_flag_card:
            descr = "  " + descr
            add_line(descr, None, amt)
            for flag in filter(lambda x : x.get('type') == '1', card_flags):
                add_line("    " + flag.get('desc'), None, flag.get('amout'))
        elif descr == 'CARTAO DEBITO' and is_print_flag_card:
            descr = "  " + descr
            add_line(descr, None, amt)
            for flag in filter(lambda x : x.get('type') == '2', card_flags):
                add_line("    " + flag.get('desc'), None, flag.get('amout'))
        else:
            descr = "  " + descr
            add_line(descr, None, amt)

    # add_line("Informacoes Gift cards")

    # Quantity Orders paid with Gift Card
    #add_line("  Pedidos pagos", info=giftcard_paidOrders)

    # Gift Card Sold Quantity and amount
    #add_line("  Vendido", giftcard_sales_qty, giftcard_sales_amount)

    # Gift Card Refunds Quantity and amount
    #add_line("  Reembolso", giftcard_refunds_qty, giftcard_refunds_amount)

    #for gcType, gcInfo in giftcardInfos.iteritems():
    #    gcDescr = ""
    #    if gcType == eft.EFT_GIFTACTIVATE:
    #        gcDescr = "  Ativacao"
    #    elif gcType == eft.EFT_GIFTREDEEM:
    #        gcDescr = "  Resgate"
    #    elif gcType == eft.EFT_GIFTADDVALUE:
    #        gcDescr = "  Incremento"
    #    if gcDescr:
    #        add_line(gcDescr, gcInfo["Qty"], gcInfo["Amt"])#

    # Donations information
    '''
    add_line("Doacoes", donations_qty, donations_amount)
    add_line("  Reembolso", None, donations_refunds_amount)
    for donation in donationInfos.itervalues():
        add_line("  " + donation["Descr"], donation["Qty"], donation["Amt"])

    # Refund Gross Amount
    add_line("Reembolso Bruto", refund_qty_count, refund_gross_amount)

    # Refund Net Amount
    add_line("Reembolso Liquido", None, refund_net_amount)

    # Waste Gross Amount
    # add_line("Waste Gross", waste_qty_count, waste_gross_amount)

    # Waste Net Amount
    # add_line("Waste Net", None, waste_net_amount)
    '''
    # Voided Items
    # add_line("Voided Items", voided_item_qty, voided_item_amount)

    # Skims
    add_line("Sangria", skim_qty, skim_amount)
    add_line("Suprimentos", transfer_in_qty, transfer_in_amount)
    add_line("Doacoes", donated_qty, donated_amount)

    # Tip amount
    '''
    add_line("Valor Gorjetas", None, total_tip)
    add_line("  Gorjeta em Dinheiro", None, cash_tips)
    add_line("  Outros", None, (total_tip - cash_tips))
    '''
    # Transfer In Quantity
    # add_line("Transfer In", transfer_in_qty, transfer_in_amount)

    # Transfer Out Quantity
    # add_line("Transfer Out", transfer_out_qty, transfer_out_amount)

    # Drawer amount (needs to be reviewed by specific tender types)
    drawer_amount = initialfloat + cash_gross_amount + transfer_in_amount + donated_amount - (cash_refund_amount + skim_amount + transfer_out_amount)
    add_line("Valor na Gaveta", None, drawer_amount)

    #total_cash_tenders = cash_gross_amount - cash_refund_amount
    #total_overshort = total_declared - drawer_amount

    #add_line("Deposito Banco", None, float(float(total_cash_tenders if total_cash_tenders > 0 else 0) + float(total_overshort)))
    '''
    add_line("DESCONTOS")

    # DiscountSessionInfo - get the information of discounts from current operator or all operators
    for code, discount in sorted(discountInfos.items()):
        amt, descr, qty = map(discount.get, ("Amt", "Descr", "Qty"))
        add_line(" " + descr, qty, amt)
    '''
    report.write("%s\n" % (SEPARATOR))

    return report.getvalue()


new_pos_list = None
fiscal_sent_dir = None
delivery_originator_relation = None


def new_cash_report(date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, store_id, business_period=None, codigo_centro=None, close_time=None, is_table_service='False', only_body='False', only_payments='False'):
    global new_pos_list, fiscal_sent_dir, delivery_originator_relation

    if date_type != "JsonBusinessPeriod" and new_pos_list is None:
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token != TK_SYS_ACK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        new_pos_list = sorted(map(int, msg.data.split("\0")))

    if fiscal_sent_dir is None:
        config = cfgtools.read(os.environ["LOADERCFG"])
        fiscal_sent_dir = sys_parsefilepath(config.find_value("CashReport.FiscalSentDir").strip())
    if delivery_originator_relation is None:
        config = cfgtools.read(os.environ["LOADERCFG"])
        delivery_originator_relation = config.find_values("CashReport.DeliveryOriginatorRelation")

    order_repository = OrderRepository(mbcontext, new_pos_list, fiscal_sent_dir)
    account_repository = AccountRepository(mbcontext)
    tender_repository = TenderRepository(mbcontext)
    fiscal_repository = FiscalRepository(mbcontext)
    pos_ctrl_repository = PosCtrlRepository(mbcontext)
    table_repository = TableRepository(mbcontext)
    product_repository = CashProductRepository(mbcontext)

    operator_id = str(int(0 if operator_id in (None, 'None') else operator_id))
    if operator_id == '0':
        operator_id = None

    report_pos = str(int(0 if report_pos in (None, 'None') else report_pos))
    if report_pos == '0':
        report_pos = None

    is_table_service = is_table_service.lower() == 'true' if type(is_table_service) == str else is_table_service
    only_body = only_body.lower() == 'true' if type(only_body) == str else only_body
    only_payments = only_payments.lower() == 'true' if type(only_payments) == str else only_payments

    cash_report = CashReport(order_repository, account_repository, tender_repository, fiscal_repository, pos_ctrl_repository, table_repository, product_repository, store_id, delivery_originator_relation)
    initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d") if date_type != "SessionId" else None
    end_date = datetime.datetime.strptime(end_date, "%Y%m%d") if date_type != "SessionId" else None
    pos_id = int(pos_id)
    voided_lines = get_voided_lines(report_pos, initial_date, end_date, operator_id) if date_type != "SessionId" else None

    if date_type == "RealDate":
        report = cash_report.generate_cash_report_by_real_date(pos_id, report_pos, initial_date, end_date, operator_id, voided_lines, is_table_service=is_table_service, only_body=only_body, session_id=session_id, only_payments=only_payments)
    elif date_type == "BusinessPeriod":
        report = cash_report.generate_cash_report_by_business_period(pos_id, report_pos, initial_date, end_date, operator_id, voided_lines, is_table_service=is_table_service, only_body=only_body, only_payments=only_payments)
    elif date_type == "SessionId":
        report = cash_report.generate_cash_report_by_session_id(pos_id, session_id, voided_lines, is_table_service=is_table_service, only_body=only_body, only_payments=only_payments)
    elif date_type == "JsonBusinessPeriod":
        report = cash_report.generate_cash_report_by_real_date(pos_id, report_pos, initial_date, end_date, operator_id, voided_lines, business_period, codigo_centro, close_time, only_body=only_body, only_payments=only_payments)
    else:
        report = cash_report.generate_cash_report_by_xml(pos_id, initial_date, end_date, is_table_service=is_table_service, only_body=only_body, only_payments=only_payments)

    return report


def generate_voided_lines_report(report_pos, initial_date, end_date, only_body=False, operator_id=None):
    # type: (str, str, str, Optional[bool], Optional[Union[str, None]]) -> unicode
    try:
        report_pos = None if report_pos in ["", "0", "None", None] else [int(report_pos)]
        operator_id = None if operator_id in ["", "0", "None", None] else int(operator_id)
        only_body = only_body.lower() == "true" if only_body else False
        initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d")
        end_date = datetime.datetime.strptime(end_date, "%Y%m%d")

        order_repository = VoidedLinesOrderRepository(mbcontext, _get_pos_list())
        users_repository = VoidedLinesUsersRepository(mbcontext)
        voided_lines_report = VoidedLinesReport(order_repository, users_repository, get_store_id())
        report = voided_lines_report.generate_voided_lines_report(report_pos,
                                                                  initial_date,
                                                                  end_date,
                                                                  only_body,
                                                                  operator_id)

        return report
    except Exception as _:
        sys_log_exception("Error on [generate_voided_lines_report]")
        raise


def get_voided_lines(report_pos, initial_date, end_date, operator_id=None):
    try:
        operator_id = int(operator_id) if operator_id else None
        order_repository = VoidedLinesOrderRepository(mbcontext, _get_pos_list())
        users_repository = VoidedLinesUsersRepository(mbcontext)
        voided_lines_report = VoidedLinesReport(order_repository, users_repository, get_store_id())
        voided_lines = voided_lines_report.get_voided_lines(report_pos, initial_date, end_date, operator_id)
        return voided_lines
    except Exception as _:
        sys_log_exception("Error on [generate_voided_lines_report]")
        raise


def _get_pos_list():
    global new_pos_list

    if new_pos_list is None:
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token != TK_SYS_ACK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        new_pos_list = sorted(map(int, msg.data.split("\0")))

    return new_pos_list


def generate_paid_order_cash_report_by_date(initial_date, end_date):
    global new_pos_list, fiscal_sent_dir

    if new_pos_list is None:
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token != TK_SYS_ACK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        new_pos_list = sorted(map(int, msg.data.split("\0")))

    if fiscal_sent_dir is None:
        config = cfgtools.read(os.environ["LOADERCFG"])
        fiscal_sent_dir = sys_parsefilepath(config.find_value("CashReport.FiscalSentDir").strip())

    order_repository = OrderRepository(mbcontext, new_pos_list, fiscal_sent_dir)
    tender_repository = TenderRepository(mbcontext)
    cash_report = CashReport(order_repository, None, tender_repository, None, None, None, None, None)
    formatted_initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d")
    formatted_end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
    orders = cash_report.generate_paid_order_cash_report_by_date(formatted_initial_date, formatted_end_date)

    order_id_and_totals = [{"orderId": str(order.order_id), "total": order.total} for order in orders]

    return json.dumps(order_id_and_totals)


def sales_by_brand(date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, store_id):
    # type: (unicode, int, unicode, unicode, unicode, unicode, unicode, unicode) -> str
    global new_pos_list, fiscal_sent_dir

    if new_pos_list is None:
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token != TK_SYS_ACK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        new_pos_list = sorted(map(int, msg.data.split("\0")))

    order_repository = BrandOrderRepository(mbcontext, new_pos_list)
    fiscal_repository = BrandFiscalRepository(mbcontext)
    tender_repository = BrandTenderRepository(mbcontext)

    operator_id = str(int(0 if operator_id in (None, 'None') else operator_id))
    if operator_id == '0':
        operator_id = None

    report_pos = str(int(0 if report_pos in (None, 'None') else report_pos))
    if report_pos == '0':
        report_pos = None

    flag_report = BrandReport(order_repository, fiscal_repository, tender_repository, get_store_id())
    if date_type == "RealDate":
        initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d")
        end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
        report = flag_report.generate_brand_report_by_real_date(pos_id, report_pos, initial_date, end_date, operator_id)
    elif date_type == "BusinessPeriod":
        initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d")
        end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
        report = flag_report.generate_brand_report_by_business_period(pos_id, report_pos, initial_date, end_date, operator_id)
    else:
        report = flag_report.generate_brand_report_by_session_id(pos_id, session_id)

    return report


def voided_orders_report(date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, store_id):
    # type: (unicode, int, unicode, unicode, unicode, unicode, unicode, unicode) -> str
    global new_pos_list, fiscal_sent_dir

    if new_pos_list is None:
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token != TK_SYS_ACK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        new_pos_list = sorted(map(int, msg.data.split("\0")))

    order_repository = VoidedOrderRepository(mbcontext, new_pos_list)

    operator_id = str(int(0 if operator_id in (None, 'None') else operator_id))
    if operator_id == '0':
        operator_id = None

    report_pos = str(int(0 if report_pos in (None, 'None') else report_pos))
    if report_pos == '0':
        report_pos = None

    voided_report = VoidedReport(order_repository, get_store_id())
    if date_type == "RealDate":
        initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d")
        end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
        report = voided_report.generate_voided_report_by_real_date(pos_id, report_pos, initial_date, end_date, operator_id)
    elif date_type == "BusinessPeriod":
        initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d")
        end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
        report = voided_report.generate_voided_report_by_business_period(pos_id, report_pos, initial_date, end_date, operator_id)
    else:
        report = voided_report.generate_voided_report_by_session_id(pos_id, session_id)

    return report


def discount_report(date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, store_id, business_period=None, codigo_centro=None, close_time=None, is_table_service='False'):
    global new_pos_list, fiscal_sent_dir

    order_repository = DiscountOrderRepository(mbcontext, _get_pos_list())
    report_generator = DiscountReport(order_repository, get_store_id())

    report = ""
    if date_type == "SessionId":
        report = report_generator.generate_discount_report_by_session_id(pos_id, session_id)
    else:
        initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d")
        end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
        report_pos = _convert_report_pos(report_pos)
        operator_id = _convert_operator_id(operator_id)

        if date_type == "RealDate":
            report = report_generator.generate_discount_report_by_real_date(pos_id,
                                                                            report_pos,
                                                                            initial_date,
                                                                            end_date,
                                                                            operator_id)
        elif date_type == "BusinessPeriod":
            report = report_generator.generate_discount_report_by_business_period(pos_id,
                                                                                  report_pos,
                                                                                  initial_date,
                                                                                  end_date,
                                                                                  operator_id)

    return report


def _convert_report_pos(report_pos):
    report_pos = str(int(0 if report_pos in (None, 'None') else report_pos))
    if report_pos == '0':
        report_pos = None
    return report_pos


def _convert_operator_id(operator_id):
    operator_id = str(int(0 if operator_id in (None, 'None') else operator_id))
    if operator_id == '0':
        operator_id = None
    return operator_id


def new_pmix_report(date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, store_id, report_model):
    # type: (unicode, int, str, unicode, unicode, unicode, unicode, unicode, str) -> str
    global new_pos_list

    if new_pos_list is None:
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token != TK_SYS_ACK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        new_pos_list = sorted(map(int, msg.data.split("\0")))

    if report_pos == '0':
        order_repository = PmixOrderRepository(mbcontext, new_pos_list)
    else:
        order_repository = PmixOrderRepository(mbcontext, [int(report_pos)])
    product_repository = ProductRepository(mbcontext)

    pmix_report = PMixReport(order_repository, product_repository, get_store_id(), operator_id)
    initial_date = datetime.datetime.strptime(initial_date, "%Y%m%d")
    end_date = datetime.datetime.strptime(end_date, "%Y%m%d")
    if date_type == "RealDate":
        report = pmix_report.generate_pmix_report_by_real_date(pos_id, initial_date, end_date, report_model, operatorid=operator_id)
    else:
        report = pmix_report.generate_pmix_report_by_business_period(pos_id, initial_date, end_date, report_model, operatorid=operator_id)

    return report


def pmix_order_items(initial_date, end_date, store_id, operator_id):
    # type: (unicode, unicode, unicode) -> List[OrderItem]
    global new_pos_list

    if new_pos_list is None:
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token != TK_SYS_ACK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        new_pos_list = sorted(map(int, msg.data.split("\0")))

    order_repository = PmixOrderRepository(mbcontext, new_pos_list)
    product_repository = ProductRepository(mbcontext)

    pmix_report = PMixReport(order_repository, product_repository, get_store_id(), operator_id)

    initial_date = datetime.datetime.strptime(initial_date, "%Y-%m-%d %H:%M:%S.%f")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S.%f")

    report = pmix_report.generate_pmix_order_items(initial_date, end_date)

    return json.dumps(map(lambda x: x.__dict__, report))


def close_operator_report(pos_id, period, operator_id, pos_list, session_id, cash_report=None, authorizer=None):
    global new_pos_list

    if new_pos_list is None:
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token != TK_SYS_ACK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        new_pos_list = sorted(map(int, msg.data.split("\0")))

    close_operator_report_generator = CloseOperatorReport(CloseOperatorOrderRepository(mbcontext, new_pos_list),
                                                          CloseOperatorProductRepository(mbcontext),
                                                          CloseOperatorAccountRepository(mbcontext),
                                                          get_store_id())

    initial_date = end_date = period
    cash_report = new_cash_report("SessionId", pos_id, None, initial_date, end_date, operator_id, session_id, get_store_id(), only_body=True)
    return close_operator_report_generator.generate_close_operator_report(pos_id, operator_id, period, session_id, cash_report, authorizer)


def cash_over_short_report(posid, business_period, pos, *args):

    def generate_tender_info(conn, posno, period, session_id=None):
        tender_info = {
            0: {
                "TenderTotal": 0,
                "tickets": 0,
                "transfer_in": 0,
                "transfer_out": 0,
                "cash_refund": 0
            }
        }

        # set the period
        conn.query("DELETE FROM temp.ReportsPeriod")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period, period))

        # select temporary table
        if session_id:
            sql = "SELECT * from temp.CASHView WHERE SessionId='%s';" % (session_id)
        else:
            sql = "SELECT * from temp.CASHView WHERE PosId='%s';" % (posno)

        cursor = conn.select(sql)
        transfer_in_amount = D(0)
        transfer_out_amount = D(0)
        cash_refund_amount = D(0)

        for row in cursor:
            # Sum all Transfer IN Amount for the Day
            if row.get_entry("TransferInAmount"):
                transfer_in_amount = transfer_in_amount + D(row.get_entry("TransferInAmount"))

            # Sum all Transfer OUT Amount for the Day
            if row.get_entry("TransferOutAmount"):
                transfer_out_amount = transfer_out_amount + D(row.get_entry("TransferOutAmount"))

            if row.get_entry("CashRefundAmount"):
                cash_refund_amount = cash_refund_amount + D(row.get_entry("CashRefundAmount"))

            if row.get_entry("TenderSessionInfo"):
                sales = eval(row.get_entry("TenderSessionInfo"))
                for sale in sales:
                    tender_id = sale['TenderId']
                    if tender_id in tender_info:
                        tender_info[tender_id]['TenderTotal'] += D(sale['TenderTotal'])
                        tender_info[tender_id]['tickets'] += 1
                    else:
                        tender_info[tender_id] = {
                            'TenderTotal': D(sale['TenderTotal']),
                            'tickets': int(sale['PaidQty']),
                        }

        tender_info[0]["transfer_in"] = transfer_in_amount
        tender_info[0]["transfer_out"] = transfer_out_amount
        tender_info[0]["cash_refund"] = cash_refund_amount

        return tender_info

    if pos == '0':
        # get a pos list
        msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
        if msg.token == TK_SYS_NAK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        poslist = sorted(map(int, msg.data.split("\0")))
    else:
        poslist = [pos]

    report = StringIO()

    conn = None
    StoreId = ""

    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        conn.transaction_start()
        cursor = conn.select("SELECT KeyValue FROM storecfg.Configuration WHERE KeyPath = 'Store.Id'")
        for row in cursor:
            StoreId = row.get_entry(0)
            break
    finally:
        if conn:
            conn.close()

    title = _center("Relatorio Resumido")
    current_datetime = time.strftime(DATE_TIME_FMT)
    business_day = time.strptime(business_period, "%Y%m%d")
    business_day = time.strftime(DATE_FMT, business_day)

    report.write("%s\n" % SEPARATOR)
    report.write("%s\n" % title)
    report.write("%s\n" % SEPARATOR)
    report.write("Data/hora...: %s\n" % current_datetime)
    report.write("Dia Util....: %s\n" % business_day)
    report.write("%s\n" % (SEPARATOR))
    report.write("ID Loja.:%s                  Valor\n" % (StoreId))
    report.write("%s\n" % SINGLE_SEPARATOR)

    total_calculated = D(0)
    total_declared = D(0)
    total_cash_tenders = D(0)

    for posid in poslist:
        sql = """SELECT
                    COALESCE(sum(us.InitialFloat), 0) AS "InitialFloat",
                    COALESCE(sum(tr.amount), 0) AS "Declared"
                 FROM posctrl.UserSession us
                 LEFT JOIN account.Transfer tr ON us.SessionId = tr.SessionId AND tr.Description = 'DECLARED_AMOUNT'
                 WHERE us.BusinessPeriod = %s AND us.PosId = %s;""" % (business_period, posid)

        conn = None

        try:
            conn = dbd.open(mbcontext, dbname=str(posid))
            conn.transaction_start()
            cursor = conn.select(sql)

            for row in cursor:
                initial_float, float_declared = map(row.get_entry, ('InitialFloat', 'Declared'))
                tender_info = generate_tender_info(conn, posid, business_period)
                cash_tenders = tender_info[0]["TenderTotal"]
                transfer_in = tender_info[0]["transfer_in"]
                transfer_out = tender_info[0]["transfer_out"]
                cash_refund = tender_info[0]["cash_refund"]
                total_calculated = total_calculated + (cash_tenders + D(initial_float) + D(transfer_in) - D(transfer_out) - D(cash_refund))
                total_declared = total_declared + D(float_declared)
                total_cash_tenders = (total_cash_tenders + D(cash_tenders)) - D(cash_refund)
        finally:
            if conn:
                conn.close()

    total_overshort = total_declared - total_calculated

    report.write("Dinheiro Calculado:        R$%6.2f\n" % (float(total_calculated)))
    report.write("Dinheiro Declarado:        R$%6.2f\n" % (float(total_declared)))
    report.write("%s\n" % SINGLE_SEPARATOR)
    report.write("Sobra / Falta:             R$%6.2f\n" % (float(total_overshort)))
    report.write("Total de Dinheiro Pago:    R$%6.2f\n" % (float(total_cash_tenders)))
    report.write("%s\n" % SINGLE_SEPARATOR)
    report.write("Deposito Banco:            R$%6.2f\n" % float(float(total_cash_tenders if total_cash_tenders > 0 else 0) + float(total_overshort)))
    report.write("%s\n" % SINGLE_SEPARATOR)

    subtitle = _center("DETALHAMENTO SOBRA / FALTA")
    report.write("%s\n" % (SEPARATOR))
    report.write("%s\n" % subtitle)
    report.write("%s\n" % (SEPARATOR))

    for posid in poslist:
        sql = """ SELECT us.OperatorName,
                  us.PosId,
                  strftime("%%H:%%M", us.OpenTime) AS "Check-in",
                  strftime("%%H:%%M", us.CloseTime) AS "Check-out",
                  us.InitialFloat AS "InitialFloat",
                  tr.amount AS "Declared",
                  tr.SessionId AS "SessionId"
                  FROM posctrl.UserSession us
                  LEFT JOIN account.Transfer tr ON us.SessionId = tr.SessionId AND tr.Description = 'DECLARED_AMOUNT'
                  WHERE us.BusinessPeriod = '%s'
                  AND us.PosId = '%s'
                  GROUP BY us.SessionId, us.OperatorName, us.PosId;""" % (business_period, posid)

        conn = None

        try:
            conn = dbd.open(mbcontext, dbname=str(posid))
            conn.transaction_start()
            cursor = conn.select(sql)

            for row in cursor:
                OpName, PosId, Checkin, Checkout, InitialFloat, Declared, SessionId = map(row.get_entry, ('OperatorName', 'PosId', 'Check-in', 'Check-out', 'InitialFloat', 'Declared', 'SessionId'))
                tender_info = generate_tender_info(conn, PosId, business_period, session_id=SessionId)
                cash_tenders = tender_info[0]["TenderTotal"]
                transfer_in = tender_info[0]["transfer_in"]
                transfer_out = tender_info[0]["transfer_out"]
                cash_refund = tender_info[0]["cash_refund"]
                total_calculated = cash_tenders + D(InitialFloat) + D(transfer_in) - (D(transfer_out) + D(cash_refund))

                if not Declared:
                    Declared = D(0)

                total_overshort = D(Declared) - total_calculated
                report.write("%s / %s\n" % (OpName, PosId))
                report.write("%s\n" % SINGLE_SEPARATOR)
                report.write("Periodo: %s - %s\n" % (Checkin, Checkout))
                report.write("Dinheiro Calculado:        R$%6.2f\n" % (float(total_calculated)))
                report.write("Dinheiro Declarado:        R$%6.2f\n" % (float(Declared)))
                report.write("Sobra / Falta:             R$%6.2f\n" % (float(total_overshort)))
                report.write("\n")
                report.write("%s\n" % SINGLE_SEPARATOR)
        finally:
            if conn:
                conn.close()

    return report.getvalue()


def cash_over_short_op_report(posid, business_period, userid, *args):

    def generate_tender_info(conn, posno, period, session_id=None):
        tender_info = {
            0: {
                "TenderTotal": 0,
                "tickets": 0,
                "transfer_in": 0,
                "transfer_out": 0,
                "cash_refund": 0
            }
        }

        # set the period
        conn.query("DELETE FROM temp.ReportsPeriod")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period, period))

        # select temporary table
        if session_id:
            cursor = conn.select("SELECT * from temp.CASHView WHERE BusinessPeriod='%s' AND SessionId='%s';" % (period, session_id))
        else:
            cursor = conn.select("SELECT * from temp.CASHView WHERE PosId='%s' AND BusinessPeriod='%s';" % (posno, period))

        transfer_in_amount = D(0)
        transfer_out_amount = D(0)
        cash_refund_amount = D(0)

        for row in cursor:
            # Sum all Transfer IN Amount for the Day
            if row.get_entry("TransferInAmount"):
                transfer_in_amount = transfer_in_amount + D(row.get_entry("TransferInAmount"))

            # Sum all Transfer OUT Amount for the Day
            if row.get_entry("TransferOutAmount"):
                transfer_out_amount = transfer_out_amount + D(row.get_entry("TransferOutAmount"))

            if row.get_entry("CashRefundAmount"):
                cash_refund_amount = cash_refund_amount + D(row.get_entry("CashRefundAmount"))

            if row.get_entry("TenderSessionInfo"):
                sales = eval(row.get_entry("TenderSessionInfo"))
                for sale in sales:
                    tender_id = sale['TenderId']
                    if tender_id in tender_info:
                        tender_info[tender_id]['TenderTotal'] += D(sale['TenderTotal'])
                        tender_info[tender_id]['tickets'] += 1
                    else:
                        tender_info[tender_id] = {
                            'TenderTotal': D(sale['TenderTotal']),
                            'tickets': int(sale['PaidQty']),
                        }

        tender_info[0]["transfer_in"] = transfer_in_amount
        tender_info[0]["transfer_out"] = transfer_out_amount
        tender_info[0]["cash_refund"] = cash_refund_amount

        return tender_info

    report = StringIO()
    title = _center("RELATORIO DE SOBRA / FALTA")
    current_datetime = time.strftime(DATE_TIME_FMT)
    business_day = time.strptime(business_period, "%Y%m%d")
    business_day = time.strftime(DATE_FMT, business_day)

    report.write("%s\n" % SEPARATOR)
    report.write("%s\n" % title)
    report.write("%s\n" % SEPARATOR)
    report.write("Data/hora...: %s\n" % current_datetime)
    report.write("Dia Util....: %s\n" % business_day)
    report.write("%s\n" % (SEPARATOR))

    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        conn.transaction_start()

        sql = """ SELECT us.OperatorName,
          us.PosId,
          strftime("%%H:%%M", us.OpenTime) AS "Check-in",
          strftime("%%H:%%M", us.CloseTime) AS "Check-out",
          us.InitialFloat AS "InitialFloat",
          tr.amount AS "Declared",
          tr.SessionId AS "SessionId"
          FROM posctrl.UserSession us
          LEFT JOIN account.Transfer tr ON us.SessionId = tr.SessionId AND tr.Description = 'DECLARED_AMOUNT'
          WHERE us.BusinessPeriod = '%s'
          AND us.PosId = '%s'
          AND us.OperatorId = '%s'
          GROUP BY us.SessionId, us.OperatorName, us.PosId;""" % (business_period, posid, userid)

        cursor = conn.select(sql)
        if not cursor:
            return

        for row in cursor:
            OpName, PosId, Checkin, Checkout, InitialFloat, Declared, SessionId = map(row.get_entry, ('OperatorName', 'PosId', 'Check-in', 'Check-out', 'InitialFloat', 'Declared', 'SessionId'))
            tender_info = generate_tender_info(conn, PosId, business_period, session_id=SessionId)
            cash_tenders = tender_info[0]["TenderTotal"]
            transfer_in = tender_info[0]["transfer_in"]
            transfer_out = tender_info[0]["transfer_out"]
            cash_refund = tender_info[0]["cash_refund"]
            total_calculated = cash_tenders + D(InitialFloat) + D(transfer_in) - (D(transfer_out) + D(cash_refund))
            total_overshort = D(Declared) - total_calculated

            report.write("%s / %s\n" % (OpName, PosId))
            report.write("%s\n" % SINGLE_SEPARATOR)
            report.write("Periodo: %s - %s\n" % (Checkin, Checkout))
            report.write("Dinheiro Calculado:        R$%6.2f\n" % (float(total_calculated)))
            report.write("Dinheiro Declarado:        R$%6.2f\n" % (float(Declared)))
            report.write("Sobra / Falta:             R$%6.2f\n" % (float(total_overshort)))
            report.write("Deposito Banco:            R$%6.2f\n" % float(float(cash_tenders if cash_tenders > 0 else 0) + float(total_overshort)))
            report.write("\n")
            report.write("%s\n" % SINGLE_SEPARATOR)

    finally:
        if conn:
            conn.close()

    return report.getvalue()


def transfer_report(pos_id, operator_id, transfer_type, amount, period, envelope_number, print_operator_copy):
    transfer = TransfersReport(TransferAccountRepository(mbcontext), get_store_id())
    return transfer.generate_transfers_report(pos_id, operator_id, transfer_type, amount, period, envelope_number,
                                              print_operator_copy)


def transfer_report_by_period(pos_id, operator_id, transfer_type, period, *args):
    transfer = TransfersReport(TransferAccountRepository(mbcontext), get_store_id())
    return transfer.generate_transfers_report_by_period(pos_id, operator_id, transfer_type, period)


def productListReport(posid, period, show_inactive="true"):
    show_inactive = True if (show_inactive.lower() == "true") else False
    conn = None
    try:
        conn = dbd.open(mbcontext)
        sql = """
        SELECT P.ProductCode as ProductCode,
               P.ProductName as ProductName,
               COALESCE(PR.DefaultUnitPrice, '0.00') as Price
        FROM
            productdb.Product P
        JOIN productdb.ProductKernelParams PKP ON PKP.ProductCode=P.ProductCode
        LEFT JOIN
            productdb.Price PR
            ON  PR.ProductCode=P.ProductCode AND
                PR.Context IN (
                    SELECT DISTINCT ProductCode
                    FROM productdb.ProductKernelParams
                    WHERE ProductType=3
                ) AND
                DATE('%s-%s-%s') BETWEEN PR.ValidFrom AND PR.ValidThru
        WHERE
            P.ProductCode NOT IN (SELECT DISTINCT ClassCode FROM productdb.ProductClassification)
            AND PKP.Enabled IN (1, %s)
        GROUP BY ProductCode, Price
        ORDER BY P.ProductCode
        """ % (period[:4], period[4:6], period[6:8], ('0' if show_inactive else "NULL"))

        cursor = conn.select(sql)
        report = StringIO()

        if show_inactive:
            title = "Lista de Produtos (Todos os itens)"
        else:
            title = "Lista de Produtos (Apenas ativos)"

        report.write(_manager_report_header(title, int(posid), 0, period))
        report.write("%s\n" % (SEPARATOR))
        report.write("\n")
        #             12345678901234567890123456789012345678
        report.write("  Codigo Descricao            Preco\n")

        for row in cursor:
            code, descr, price = map(row.get_entry, ("ProductCode", "ProductName", "Price"))
            report.write("%8s %-20.20s  R$ %-7.7s\n" % (code, descr, _fmt_number(float(price))))

        report.write("%s\n" % (SEPARATOR))
        report.write("\n")
    finally:
        if conn:
            conn.close()

    return report.getvalue()


def dayOpen_report(posid, period, posnumbers, store_wide="false", operator=""):

    report = StringIO()

    operator = 0 if operator in ["None", ""] else operator

    title = "Abertura do Dia (Loja)" if store_wide.lower() == "true" else "Abertura do Dia"
    report.write(_manager_report_header(title, int(posid), operator, period))

    report.write("\n")

    temp_pos_list = "POS incluidos...: "+" ".join(posnumbers.split('|'))
    report.write("%s\n" % (SEPARATOR))
    report.write(temp_pos_list[:COLS])
    if len(temp_pos_list) > COLS:
        report.write("\n                  %s" % temp_pos_list[COLS:2*COLS-18])
    if len(temp_pos_list) > 2*COLS-18:
        report.write("\n                  %s" % temp_pos_list[2 * COLS - 18:2 * COLS - 36])
    report.write("\n%s\n" % (SEPARATOR))
    return report.getvalue()


def login_operator_report(posid, opera_id, opera_name, initial_float, period, autorized_by):
    report = StringIO()
    report.write(_manager_report_header("Login Operador", int(posid), opera_id, period))
    report.write("%s\n" % (SEPARATOR))
    report.write("\n")
    report.write("Nome do Operador...: %16s\n" % (opera_name[:16]))
    report.write("ID Operador........: %16s\n" % (opera_id))
    report.write("Autorizado por.....: %16s\n" % (autorized_by))
    report.write("Balanco Inicial....: R$ %13.2f\n" % (float(initial_float)))

    report.write("\n")
    report.write("%s\n" % (SEPARATOR))

    return report.getvalue()


def eftRefundReport(posid, operatorid, description, period, xml_response, *args):
    # parameter amount removed, changed to get the report amount from the XML response

    xml_response = etree.XML(xml_response)

    # create string I/O to append the report info
    report = StringIO()
    report.write(_manager_report_header(description, int(posid), operatorid, period))
    report.write("%s\n" % (SEPARATOR))
    report.write("\n")

    intSeqNum = xml_response.findtext("ServerResponse/RESPONSE/INTRN_SEQ_NUM")
    troutD = xml_response.findtext("ServerResponse/RESPONSE/TROUTD")
    aut_Code = xml_response.findtext("ServerResponse/RESPONSE/AUTH_CODE")
    payMedia = xml_response.findtext("ServerResponse/RESPONSE/PAYMENT_MEDIA")
    tranSeqNum = xml_response.findtext("ServerResponse/RESPONSE/TRANS_SEQ_NUM")
    trans_date = xml_response.findtext("ServerResponse/RESPONSE/TRANS_DATE")
    trans_time = xml_response.findtext("ServerResponse/RESPONSE/TRANS_TIME")

    # changed to get the report amount from the XML response
    amount = xml_response.findtext("ServerResponse/RESPONSE/TRANS_AMOUNT")

    # Starting Printing

    # EFT Refund Report
    report.write("%-20s.: R$ %12.2f\n" % (description, float(amount)))
    report.write("Internal Seq. Num....: %15s\n" % (intSeqNum))
    report.write("Numero Sequencial....: %15s\n" % (troutD))
    report.write("Codigo Autorizacao...: %15s\n" % (aut_Code))
    report.write("Meio de Pagamento....: %15s\n" % (payMedia))
    report.write("Seq Num Transacao....: %15s\n" % (tranSeqNum))
    report.write("Data Transacao.......: %15s\n" % (trans_date))
    report.write("Hora Transacao.......: %15s\n" % (trans_time))

    report.write("\n")
    report.write("%s\n" % (SEPARATOR))

    return report.getvalue()


def timePunchReport(xml_TP, *args):
    punchIn = ""
    punchOut = ""
    breakIn = ""
    breakOut = ""
    punchIn = ""
    breakPenalty = -1
    breakPenaltyTypes = {
        0: "N",
        1: "Y",
        -1: "",
    }
    globalTotal = 0

    def printLine():
        dayTotLocal = datetime.timedelta(microseconds=0)
        if not punchIn and not breakOut:  # not In
            return dayTotLocal.seconds

        if punchIn and breakIn:              # tot for first period
            dayTotLocal = breakIn - punchIn

        if breakOut and punchOut:            # tot for second period
            dayTotLocal += (punchOut - breakOut)

        if not breakIn and not breakOut:     # not found a lunch period
            if punchOut:
                dayTotLocal = punchOut - punchIn

        totalSeconds = int(dayTotLocal.seconds + (dayTotLocal.days * 24 * 3600))
        workedHours = totalSeconds / 3600
        workedMinutes = (totalSeconds - (workedHours * 3600)) / 60
        report.write("%5s %5s %5s %5s %5s %s %s\n"
                     % (punchIn.strftime("%m/%d") if punchIn else breakOut.strftime("%m/%d"),
                        "" if not punchIn else punchIn.strftime("%H:%M"),
                        "" if not breakIn else breakIn.strftime("%H:%M"),
                        "" if not breakOut else breakOut.strftime("%H:%M"),
                        "" if not punchOut else punchOut.strftime("%H:%M"),
                        "%02dh%02dm" % (workedHours, workedMinutes),
                        breakPenaltyTypes.get(breakPenalty, "")))

        return dayTotLocal.seconds + (dayTotLocal.days * 24 * 3600)

    def printTot():
        partTotal = printLine()
        totalSeconds = int(globalTotal + partTotal)
        if totalSeconds:
            workedHours = totalSeconds / 3600
            workedMinutes = (totalSeconds - (workedHours * 3600)) / 60
            line = "Worked: %02d hours, %02d minutes" % (workedHours, workedMinutes)
            report.write("%+*s\n" % (COLS, line))

    # getting information to report
    msg_xml = etree.XML(xml_TP)
    periodBegin = msg_xml.get("periodBegin")
    periodEnd = msg_xml.get("periodEnd")
    operatorId = msg_xml.get("operatorId")

    #          1         2         3       |
    # 12345678901234567890123456789012345678
    #
    # ======================================
    #          Time Punch Report
    #   Data/hora.....: 03/28/2009 13:06:12
    #   Period Begin..: 03/26/2009
    #   Period End....: 04/03/2009
    #   Users.........: All
    # ======================================
    #  UserName
    # mm/dd In    lunch       Out   W.day  P
    # --------------------------------------
    # Jonh Robert
    # 03/28 10:00 12:00 13:00 16:06 05h06m Y
    # 03/29 10:05 12:00 13:00 15:50 04h45m N
    # 03/29 20:05             22:00 02h05m
    # 03/30 10:07 12:00 13:00 16:08 05h01m N
    # 03/31  9:57 12:00 13:00 16:00 05h03m Y
    # 04/01 10:02 12:00 13:00 16:02 05h00m Y
    # 04/02 10:05 12:00 13:00 16:02 04h57m Y
    # 04/03 10:03 12:00 13:00 16:04 05h01m N
    #           Worked: 44 hours, 53 minutes
    # ======================================

    # create string I/O to append the report info
    report = StringIO()
    title = _center("Time Punch Report")
    current_datetime = datetime.datetime.now().strftime(DATE_TIME_FMT)

    if operatorId == "0":
        operator = "Todos"
    else:
        operator = operatorId

    beginDate = datetime.datetime.strptime(periodBegin, "%Y%m%d").strftime(DATE_FMT)
    endDate = datetime.datetime.strptime(periodEnd, "%Y%m%d").strftime(DATE_FMT)

    report.write(
        """%(SEPARATOR)s
%(title)s
  Data/hora......: %(current_datetime)s
  Periodo Inicial: %(beginDate)s
  Periodo Final..: %(endDate)s
  ID Operador....: %(operator)s
""" % _join(globals(), locals()))

    report.write("%s\n" % (SEPARATOR))
    report.write("UserName\n")
    report.write("mm/dd In    lunch       Out   W.day  P\n")

    userLast = ""
    periodLast = ""

    for line in msg_xml.findall("entry"):
        period = line.get("Period")
        userId = line.get("UserId")
        userName = (line.get("LongName")).encode("UTF-8")
        type = int(line.get("Type"))
        dt = datetime.datetime.strptime(line.get("Datetime"), "%Y-%m-%dT%H:%M:%S")
        date = dt.strftime("%m/%d")

        if period != periodLast:
            periodLast = period
            globalTotal += printLine()
            punchIn = ""
            punchOut = ""
            breakIn = ""
            breakOut = ""
            breakPenalty = -1

        if userId != userLast:
            printTot()
            globalTotal = 0
            punchIn = ""
            punchOut = ""
            breakIn = ""
            breakOut = ""
            breakPenalty = -1
            report.write("%s\n" % (SINGLE_SEPARATOR))
            report.write("%s\n" % (userName))
            userLast = userId

        if type == 0 and punchIn:
            globalTotal += printLine()
            punchIn = ""
            punchOut = ""
            breakIn = ""
            breakOut = ""
            breakPenalty = -1

        if type == 0:
            breakPenalty = int(line.get("BreakPenalty", "-1"))
            punchIn = dt

        if type == 1:
            breakIn = dt

        if type == 2:
            breakOut = dt

        if type == 3:
            punchOut = dt
            globalTotal += printLine()
            punchIn = ""
            punchOut = ""
            breakIn = ""
            breakOut = ""
            punchIn = ""
            breakPenalty = -1

    printTot()
    globalTotal = 0
    punchIn = ""
    punchOut = ""
    breakIn = ""
    breakOut = ""
    breakPenalty = -1

    report.write("%s\n" % (SEPARATOR))

    return report.getvalue()


def giftcardReport(posid, period, *args):
    conn = None
    try:
        conn = dbd.open(mbcontext)
        cursor = conn.select("Select Type,Timestamp,Amount,AuthNumber,CardNumber from account.GiftCardActivity WHERE Period='%s' ORDER BY Type;" % period)

        #         11        21        31      |
        # 12345678901234567890123456789012345678
        # ======================================
        #            Gift Card Report
        #   Data/hora.....: 03/28/2009 13:06:12
        #   Period........: 03/26/2009
        # ======================================
        #  Timestamp                 Amount
        #  CardNumber          AuthNumber
        # --------------------------------------
        #  GiftCard Activation
        #  2009-04-08t17:40:03       $ 123456.89
        #  1234567890123456789 12345678901234567
        #  2009-04-08t17:40:03       $ 123456.89
        #  1234567890123456789 12345678901234567
        # ======================================

        # create string I/O to append the report info
        report = StringIO()
        title = _center("Relatorio Gift Card")
        current_datetime = datetime.datetime.now().strftime(DATE_TIME_FMT)
        business_period = "%02d/%02d/%04d" % (int(period[4:6]), int(period[6:8]), int(period[:4]))

        report.write(
            """%(SEPARATOR)s
    %(title)s
      Data/hora.....: %(current_datetime)s
      Periodo.......: %(business_period)s
    """ % _join(globals(), locals()))

        report.write("%s\n" % (SEPARATOR))
        report.write(" Timestamp                      Amount\n")
        report.write(" CardNumber                 AuthNumber\n")
        report.write("%s\n" % (SINGLE_SEPARATOR))

        lastType = ""
        for row in cursor:
            gcType, gcTimestamp, gcAmount, gcAuthNumber, gcCardNumber = map(row.get_entry, ("Type", "Timestamp", "Amount", "AuthNumber", "CardNumber"))
            gcType = int(gcType)
            gcTimestamp = datetime.datetime.strptime(gcTimestamp[:19], "%Y-%m-%dT%H:%M:%S").strftime(DATE_TIME_FMT)
            if lastType != gcType:
                gcDescr = ""
                if gcType == eft.EFT_GIFTACTIVATE:
                    gcDescr = "GiftCard Activation"
                if gcType == eft.EFT_GIFTREDEEM:
                    gcDescr = "GiftCard Redemption"
                if gcType == eft.EFT_GIFTADDVALUE:
                    gcDescr = "GiftCard Increment"
                if gcDescr:
                    report.write("%s\n" % gcDescr)
                lastType = gcType
            if gcDescr:  # if Type is valid
                report.write(" %19s      R$ %9.2f\n" % (gcTimestamp, float(gcAmount)))
                report.write(" %19s %+14s\n" % (gcCardNumber or "", gcAuthNumber or ""))

        if not lastType:
            report.write(" Data nao encontrada\n")

        report.write("%s\n" % (SEPARATOR))

        return report.getvalue()
    finally:
        if conn:
            conn.close()


def employeesClockedInReport(posid, business_day, timesheets, *args):
    def get_formatted_timesheets(timesheets):
        timepunchs = {}
        for timepunch in timesheets['result']:
            job = timepunch['employee']['job']
            employee = timepunch['employee']
            employee_id = employee['employee_id']
            punch_in = timepunch['punch_in']
            punch_in['punch_time'] = datetime.datetime.strptime(punch_in['punch_time'], '%Y-%m-%dT%H:%M:%S')

            punch_in['adj_worked_secs'] = timepunch['adj_worked_secs']
            punch_in['break_intended'] = timepunch['break_intended']

            if 'punch_out' in timepunch and timepunch['punch_out']:
                punch_out = timepunch['punch_out']
                punch_out['punch_time'] = datetime.datetime.strptime(punch_out['punch_time'], '%Y-%m-%dT%H:%M:%S')
                punchs = [punch_in, punch_out]
            else:
                punchs = [punch_in, ]

            if job in timepunchs:
                if employee_id in timepunchs[job]:
                    timepunchs[job][employee_id]['punchs'].extend(punchs)
                    timepunchs[job][employee_id]['punchs'].sort(key=lambda x: x['punch_time'])
            else:
                timepunchs[job] = {}
                timepunchs[job][employee_id] = {'timepunch': timepunch, 'punchs': punchs}

        return timepunchs

    def report_add_header(report, title, business_day):
        title = _center(title)
        business_day = datetime.datetime.strptime(business_day, '%Y-%m-%d').strftime(DATE_FMT)
        operator = "Todos"

        report.write("""%(SEPARATOR)s
%(title)s
  Data/hora.....: %(business_day)s
  ID Operador...: %(operator)s
""" % _join(globals(), locals()))

        report.write("%s\n" % (SEPARATOR))
        report.write("Usuario\n")
        report.write("mm/dd In    lunch       Out   W.day  P\n\n")

    def report_add_job(report, job):
        report.write("%s\n" % job)
        report.write("--------------------------------------\n")

    def report_add_employee(report, employee):
        report.write("%s\n" % employee['name'])

    def report_add_punch(report, punchs, show_break_intent):
        def format_punchs_line(punchs_times):
            if len(punchs_times) == 1:
                punchs_times.append('                 ')
            elif len(punchs_times) == 2:
                punchs_times.insert(1, '     ')
                punchs_times.insert(2, '     ')
            elif len(punchs_times) == 3:
                punchs_times.append('     ')

        def format_adj_worked_secs(seconds):
            weeks = seconds / (7 * 24 * 60 * 60)
            days = seconds / (24 * 60 * 60) - 7 * weeks
            hours = seconds / (60 * 60) - 7 * 24 * weeks - 24 * days
            minutes = seconds / 60 - 7 * 24 * 60 * weeks - 24 * 60 * days - 60 * hours
            return datetime.time(hours, minutes).strftime('%Hh%Mm')

        if punchs:
            punch_date = punchs[0]['punch_time'].strftime('%m/%d')
            punchs_times = [punch['punch_time'].strftime('%H:%M') for punch in punchs]
            format_punchs_line(punchs_times)
            punchs_times = ' '.join(punchs_times)
            if show_break_intent:
                break_intent = 'Y' if punchs[0]['break_intended'] else 'N'
            else:
                break_intent = ' '

            adj_worked_secs = datetime.timedelta()

            for i in range(0, len(punchs), 2):
                if len(punchs) > i + 1:
                    adj_worked_secs += (punchs[i + 1]['punch_time'] - punchs[i]['punch_time'])

            adj_worked_secs = format_adj_worked_secs(adj_worked_secs.seconds)

            report.write("%5s %s %6s %1s\n" % (punch_date, punchs_times, adj_worked_secs, break_intent))

    import json
    timesheets = json.loads(timesheets)
    timesheets = get_formatted_timesheets(timesheets)

    report = StringIO()
    report_add_header(report, "Employees Clocked In", business_day)

    for job in timesheets:
        report_add_job(report, job)

        for employee_id in timesheets[job]:
            timepunch = timesheets[job][employee_id]['timepunch']
            employee = timepunch['employee']
            punchs = timesheets[job][employee_id]['punchs']
            report_add_employee(report, employee)

            show_break_intent = True
            for i in range(0, len(punchs), 4):
                report_add_punch(report, punchs[i:i + 4], show_break_intent)
                show_break_intent = False

            report.write("\n")

    return report.getvalue()


def laborReport(period, *args):
    # get the pos list
    msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
    if msg.token == TK_SYS_NAK:
        sys_log_error("Could not retrieve PosList")
        raise Exception("Could not retrieve PosList")

    poslist = sorted(map(int, msg.data.split("\0")))
    report = Report()

    # Report segments (date+time slot)
    segments_order = []
    segments = defaultdict(lambda: {"day": "", "time": "", "start_time": "", "end_time": "", "sales": ZERO, "laborHours": ZERO})

    for posid in poslist:
        conn = None
        try:
            try:
                conn = dbd.open(mbcontext, dbname=str(posid))
            except:
                if conn:
                    conn.close()
                continue
            conn.transaction_start()
            cursor = conn.pselect("laborReportStartEnd", period=period)
            start, end = None, None

            for row in cursor:
                start, end = row.get_entry("StartDateTime"), row.get_entry("EndDateTime")

            if start:
                if not end:
                    end = start

                # Compute the time difference between start and end
                date_start = datetime.datetime.strptime(start[:10], "%Y-%m-%d")
                date_end = datetime.datetime.strptime(end[:10], "%Y-%m-%d")
                delta = (date_end - date_start)

                # Build the list of dates that the report spawns trhu
                dates = ",".join([(date_start + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)])
                cursor = conn.pselect("laborReportSales", period=period, reportStart=start, reportEnd=end, PreparedStringTable=dates)

                if not segments_order:
                    # Keep a sorted list of segments that will be used to generate the report in the correct order
                    segments_order = [row.get_entry("TimestampStart") for row in cursor]
                else:
                    # Must review the segments order on every pos id
                    pos_segments = [row.get_entry("TimestampStart") for row in cursor]
                    for segment in pos_segments:
                        if segment not in segments_order:
                            segments_order.append(segment)

                for row in cursor:
                    segment = segments[row.get_entry("TimestampStart")]

                    if not segment["day"]:
                        segment["day"] = row.get_entry("Day")
                        segment["time"] = row.get_entry("Hour") + ":" + row.get_entry("MinuteStart")
                        segment["start_time"] = datetime.datetime.strptime(row.get_entry("TimestampStart")[:16], "%Y-%m-%d %H:%M")
                        segment["end_time"] = datetime.datetime.strptime(row.get_entry("TimestampEnd")[:16], "%Y-%m-%d %H:%M") + datetime.timedelta(minutes=1)

                    segment["sales"] += D(row.get_entry("SalesAmount"))
        finally:
            if conn:
                conn.close()

    # Get the time-punch data to calculate labor hours
    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(posid))
        cursor = conn.select("""
            SELECT
                T.UserId AS UserId,
                DATETIME(T.Datetime,'localtime') AS Datetime,
                T.Type AS Type,
                COALESCE(U.PayRate, '0.00') AS PayRate
            FROM punch.TimePunch T
            LEFT JOIN users.Users U ON U.UserId=T.UserId
            WHERE period=%s ORDER BY UserId,Datetime
        """ % period)

        userid, ts_in, ts_out, payrate = None, None, None, ZERO
        working_times = []  # List of working times (start, end, payrate)

        for row in cursor:
            if userid is not None and userid != row.get_entry("UserId"):
                # This means that the last userid was punched-in, but never punched-out
                working_times.append((ts_in, None, payrate))
                userid, ts_in, ts_out, payrate = None, None, None, ZERO

            punch_type = int(row.get_entry("Type"))

            if punch_type in (0, 2):
                # PUNCH-IN
                userid = row.get_entry("UserId")
                payrate = D(row.get_entry("PayRate"))
                ts_in = datetime.datetime.strptime(row.get_entry("Datetime")[:19], "%Y-%m-%d %H:%M:%S")
            elif userid is not None and punch_type in (1, 3):
                # PUNCH-OUT
                ts_out = datetime.datetime.strptime(row.get_entry("Datetime")[:19], "%Y-%m-%d %H:%M:%S")
                working_times.append((ts_in, ts_out, payrate))
                userid, ts_in, ts_out, payrate = None, None, None, ZERO

        # Check for the last row
        if userid is not None:
            working_times.append((ts_in, None, payrate))

        '''
        def get_labor(start_time, end_time):
            """Retrieve labor hours and cost for a time segment."""
            labor_seconds = 0
            labor_cost = ZERO

            for punch_start, punch_end, payrate in working_times:
                if punch_start < end_time and (punch_end is None or punch_end >= start_time):
                    # Compute this as worked time
                    start = max([start_time, punch_start])
                    end = min([end_time, punch_end or end_time])
                    delta = (end - start)
                    labor_seconds += delta.seconds
                    # Calculate the labor cost for this part of the segment
                    hours = D(delta.seconds) / D('3600.00')
                    cost = (hours * payrate).quantize(D(".01"))
                    labor_cost += cost

            labor_hours = labor_seconds / 3600.0
            return labor_hours, labor_cost
        '''

        # Generate the report output
        title = _center("Relatorio de Trabalho")
        business_period = datetime.datetime.strptime(period, "%Y%m%d").strftime(DATE_FMT)
        current_datetime = datetime.datetime.now().strftime(DATE_TIME_FMT)

        report.writeln("""%(SEPARATOR)s
%(title)s
  Data/hora.....: %(current_datetime)s
  Period........: %(business_period)s
%(SEPARATOR)s""" % _join(globals(), locals()))

        report.writeln("DATA")
        #               12345678901234567890123456789012345678
        #                14:35 23,456.78 23,456.78  10.5  100%
        # report.writeln("  HORA        PS        CS    LH    L%")
        report.writeln("  HORA        PS        CS")

        last_day = None
        total_sales = ZERO
        total_labor_hours = 0.0
        total_labor_cost = ZERO

        for key in segments_order:
            segment = segments[key]
            if segment["day"] != last_day:
                report.writeln(datetime.datetime.strptime(segment["day"], "%Y-%m-%d").strftime(DATE_FMT))
                last_day = segment["day"]

            total_sales += segment["sales"]

            '''
            labor_hours, labor_cost = get_labor(segment["start_time"], segment["end_time"])
            total_labor_hours += labor_hours
            total_labor_cost += labor_cost
            labor_hours = "%.1f" % (labor_hours)

            if segment["sales"] > 0:
                labor_percentage = labor_cost / segment["sales"] * D("100")
                labor_percentage = "%d%%" % int(labor_percentage)
            else:
                labor_percentage = "-"

            s = " %5.5s %9.9s %9.9s  %4.4s  %4.4s" % (segment["time"], _fmt_number(segment["sales"]), _fmt_number(total_sales), labor_hours, labor_percentage)
            '''

            s = " %5.5s %9.9s %9.9s" % (segment["time"], _fmt_number(segment["sales"]), _fmt_number(total_sales))
            report.writeln(s)

        # Write the "Total: line"
        report.writeln("")

        '''
        if total_sales > 0:
            total_labor_percentage = total_labor_cost / total_sales * D("100")
            total_labor_percentage = "%d%%" % int(total_labor_percentage)
        else:
            total_labor_percentage = "-"

        total_labor_hours = "%.1f" % (total_labor_hours)
        s = "TOTAL:           %9.9s %5.5s  %4.4s" % (_fmt_number(total_sales), total_labor_hours, total_labor_percentage)
        '''

        s = "TOTAL:           %9.9s" % (_fmt_number(total_sales))

        report.writeln(s)
        report.writeln(SEPARATOR)
        return report.getvalue()
    finally:
        if conn:
            conn.close()


def tenderGiftCardReport(posid, operatorid, period, *args):
    report = Report()
    report.write(_manager_report_header("Relatorio Gift Card", int(posid), 0, period))

    # Get gift card numbers for given period
    conn = None
    try:
        conn = dbd.open(mbcontext)
        cursor = conn.select("""
            SELECT OCP.Value, O.CreatedAt, O.SessionId, O.OrderId
            FROM orderdb.OrderCustomProperties OCP
            JOIN orderdb.Orders O
            ON O.OrderId = OCP.OrderId
            WHERE O.BusinessPeriod = %s AND OCP.Key='GIFT_CARD_JSON'
        """ % period)

        report.writeln("GIFT CARD N.   TIME  Check N R$       ")

        for order in cursor:
            cards = json.loads(order.get_entry("Value"))
            for card in cards:
                created_at = order.get_entry("CreatedAt").split('.')[0]
                created_at = datetime.datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S").strftime('%H:%M')
                order_id = str(order.get_entry("OrderId"))
                report.write("%14s %5s %7s %6.2f\n" % (card['card_number'], created_at, order_id, float(card['card_amount'])))

        return report.getvalue()
    finally:
        if conn:
            conn.close()


def itemAvailabilityReport(posid, operatorid, period, *args):
    def get_item(pcode):
        cursor2 = conn.select("""
            SELECT * FROM productdb.Product WHERE ProductCode = %s
        """ % pcode)
        for order in cursor2:
            return order.get_entry('ProductCode'), order.get_entry('ProductName')

    report = Report()
    report.write(_manager_report_header("Relatorio de Disponibilidade de Itens", int(posid), 0, period))

    # Get gift card numbers for given period
    conn = None
    try:
        conn = dbd.open(mbcontext)
        cursor = conn.select("""
            SELECT * FROM cache.GenericStorage WHERE DataKey LIKE 'ITEM_AVAILABILITY_%s%%'
        """ % period)

        report.writeln("P. Code  P. Name          Disponibilidade")

        for order in cursor:
            pcode = order.get_entry('DataKey').split('_')[-1]
            availability = order.get_entry('DataValue')
            pcode, pname = get_item(pcode)
            report.write("%-8s %-20s %8s\n" % (pcode, pname, availability))

        return report.getvalue()
    finally:
        if conn:
            conn.close()


def cashSalesReport(posid, posnumbers, operatorid, period, session_id):

    def add_header(title, title2="NetSales", title3="Tickt", title4="AvgTickt"):
        report.write("\n\n%-10s %8s %8s %8s" % (title[:10], title2[:8], title3[:8], title4[:8]))

    def order_hourly_info(conn, hourly_info, day_part):
        # get the data
        if int(operatorid):
            cursor = conn.select("""
                SELECT O.TotalGross,
                O.TotalTaxAmountAD,
                O.PriceListTotal,
                O.DiscountAmount,
                O.TotalNet,
                O.StateId,
                O.OrderType,
                SUM(
                    COALESCE(OI.OverwrittenUnitPrice,0)
                ) as Surcharge,
                GROUP_CONCAT(TT.TenderDescr || '|' || COALESCE(OT.TenderAmount,'0') || '|' || COALESCE(OT.TipAmount,'0')) as OrderTenders,
                GROUP_CONCAT(D.DiscountDescr || '|' || COALESCE(OD.DiscountAmount,'0')) as OrderDiscounts,
                datetime(O.CreatedAt, 'localtime') as CreatedAtLocal
                FROM orderdb.Orders O
                LEFT OUTER JOIN orderdb.OrderTender OT
                ON OT.OrderId = O.OrderId
                LEFT OUTER JOIN orderdb.OrderItem OI
                ON OI.OrderId = O.OrderId
                AND OI.PartCode >= 1000000
                LEFT OUTER JOIN productdb.TenderType TT
                ON OT.TenderId == TT.TenderId
                LEFT OUTER JOIN orderdb.OrderDiscount OD
                ON OD.OrderId == O.OrderId
                LEFT OUTER JOIN discountcalc.Discounts D
                ON OD.DiscountId == D.DiscountId
                WHERE O.BusinessPeriod='%s'
                AND O.StateId IN (4,5)
                AND O.OrderType IN (0,1)
                AND O.SessionId LIKE '%%user=%s,%%'
                GROUP BY O.OrderId""" % (period, str(operatorid)))
        else:
            cursor = conn.select("""
                SELECT O.TotalGross,
                O.TotalTaxAmountAD,
                O.PriceListTotal,
                O.DiscountAmount,
                O.TotalNet,
                O.StateId,
                O.OrderType,
                SUM(
                    COALESCE(OI.OverwrittenUnitPrice,0)
                ) as Surcharge,
                GROUP_CONCAT(TT.TenderDescr || '|' || COALESCE(OT.TenderAmount,'0') || '|' || COALESCE(OT.TipAmount,'0')) as OrderTenders,
                GROUP_CONCAT(D.DiscountDescr || '|' || COALESCE(OD.DiscountAmount,'0')) as OrderDiscounts,
                datetime(O.CreatedAt, 'localtime') as CreatedAtLocal
                FROM orderdb.Orders O
                LEFT OUTER JOIN orderdb.OrderTender OT
                ON OT.OrderId = O.OrderId
                LEFT OUTER JOIN orderdb.OrderItem OI
                ON OI.OrderId = O.OrderId
                AND OI.PartCode >= 1000000
                LEFT OUTER JOIN productdb.TenderType TT
                ON OT.TenderId == TT.TenderId
                LEFT OUTER JOIN orderdb.OrderDiscount OD
                ON OD.OrderId == O.OrderId
                LEFT OUTER JOIN discountcalc.Discounts D
                ON OD.DiscountId == D.DiscountId
                WHERE O.BusinessPeriod='%s'
                AND O.StateId IN (4,5)
                AND O.OrderType IN (0,1)
                GROUP BY O.OrderId""" % period)

        if not day_part:
            day_part['breakfast'] = {'interval': (datetime.time(0, 0), datetime.time(11, 0))}
            day_part['lunch'] = {'interval': (datetime.time(11, 0), datetime.time(17, 0))}
            day_part['dinner'] = {'interval': (datetime.time(17, 0), datetime.time(0, 0))}

        if not hourly_info:
            hourly_info['GrossSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['VoidSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['TaxSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['TipSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['CompSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['DiscountSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['SurchargeSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['NetSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['RefundSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['ReceivedSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['Tenders'] = {}
            hourly_info['Tips'] = {}
            hourly_info['Discounts'] = {}
            hourly_info['Comps'] = {}

        for row in cursor:
            created_at = row.get_entry('CreatedAtLocal')
            slot_day_time = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            slot_time = datetime.time(slot_day_time.hour, slot_day_time.minute)

            for dp in day_part:
                if slot_time > day_part[dp]['interval'][0] and slot_time <= day_part[dp]['interval'][1]:
                    hourly_info['GrossSales'][dp] += D(row.get_entry('TotalGross') or 0).quantize(D('.01'))

                    if int(row.get_entry('OrderType')) == 0:
                        if int(row.get_entry('StateId')) == 5:
                            hourly_info['TaxSales'][dp] += D(row.get_entry('TotalTaxAmountAD') or 0).quantize(D('.01'))
                            hourly_info['CompSales'][dp] += D(row.get_entry('DiscountAmount') if row.get_entry('PriceListTotal') == row.get_entry('DiscountAmount') else 0).quantize(D('.01'))
                            hourly_info['DiscountSales'][dp] += D(row.get_entry('DiscountAmount') if row.get_entry('PriceListTotal') != row.get_entry('DiscountAmount') else 0).quantize(D('.01'))
                            hourly_info['NetSales'][dp] += D(row.get_entry('TotalNet') or 0).quantize(D('.01'))
                            hourly_info['SurchargeSales'][dp] += D(row.get_entry('Surcharge') or 0).quantize(D('.01'))

                            if row.get_entry('OrderTenders'):
                                for tender in row.get_entry('OrderTenders').split(','):
                                    k, v, t = tender.split('|')
                                    if not hourly_info['Tenders'].get(k):
                                        hourly_info['Tenders'].update({k: {'breakfast': 0, 'lunch': 0, 'dinner': 0}})
                                    hourly_info['Tenders'][k][dp] += D(v).quantize(D('.01'))
                                    if D(t) != D(0):
                                        if not hourly_info['Tips'].get(k):
                                            hourly_info['Tips'].update({k: {'breakfast': 0, 'lunch': 0, 'dinner': 0}})
                                        hourly_info['Tips'][k][dp] += D(t).quantize(D('.01'))
                                        hourly_info['TipSales'][dp] += D(t).quantize(D('.01'))
                                    hourly_info['ReceivedSales'][dp] += D(v).quantize(D('.01'))

                            if row.get_entry('OrderDiscounts'):
                                for discount in row.get_entry('OrderDiscounts').split(','):
                                    k, v = discount.split('|')
                                    if not hourly_info['Discounts'].get(k) and row.get_entry('PriceListTotal') != row.get_entry('DiscountAmount'):
                                        hourly_info['Discounts'].update({k: {'breakfast': 0, 'lunch': 0, 'dinner': 0}})
                                    elif not hourly_info['Comps'].get(k) and row.get_entry('PriceListTotal') == row.get_entry('DiscountAmount'):
                                        hourly_info['Comps'].update({k: {'breakfast': 0, 'lunch': 0, 'dinner': 0}})

                                    if row.get_entry('PriceListTotal') != row.get_entry('DiscountAmount'):
                                        hourly_info['Discounts'][k][dp] += D(v).quantize(D('.01'))
                                    else:
                                        hourly_info['Comps'][k][dp] += D(v).quantize(D('.01'))

                        elif int(row.get_entry('StateId')) == 4 and int(row.get_entry('OrderType')) == 0:
                            hourly_info['VoidSales'][dp] += D(row.get_entry('TotalGross') or 0).quantize(D('.01'))

                    elif int(row.get_entry('OrderType')) == 1:
                        if int(row.get_entry('StateId')) == 5:
                            hourly_info['RefundSales'][dp] += D(row.get_entry('TotalGross') or 0).quantize(D('.01'))
    hourly_info = {}
    day_part = {}

    for posno in posnumbers:
        conn = None
        try:
            # create database connection
            conn = dbd.open(mbcontext, dbname=str(posno))

            # reserve a database connection
            conn.transaction_start()
            order_hourly_info(conn, hourly_info, day_part)
        finally:
            if conn:
                conn.close()

    gross_total = D(0)
    void_total = D(0)
    refund_total = D(0)
    tip_total = D(0)
    tax_total = D(0)
    comps_total = D(0)
    discounts_total = D(0)
    surcharge_total = D(0)
    net_total = D(0)
    received_total = D(0)

    for dp in day_part:
        hourly_info['GrossSales'][dp] += hourly_info['TipSales'][dp] + hourly_info['DiscountSales'][dp] + hourly_info['CompSales'][dp]
        gross_total += (hourly_info['GrossSales'].get(dp) or 0)
        void_total += hourly_info['VoidSales'].get(dp) or 0
        refund_total += hourly_info['RefundSales'].get(dp) or 0
        tip_total += hourly_info['TipSales'].get(dp) or 0
        tax_total += hourly_info['TaxSales'].get(dp) or 0
        comps_total += hourly_info['CompSales'].get(dp) or 0
        discounts_total += hourly_info['DiscountSales'].get(dp) or 0
        surcharge_total += hourly_info['SurchargeSales'].get(dp) or 0
        net_total += hourly_info['NetSales'].get(dp) or 0
        received_total += hourly_info['ReceivedSales'].get(dp) or 0

    report = StringIO()

    report.write(_manager_report_header('Resumo de Vendas', int(posid), operatorid, period))
    report.write("======================================")

    add_header('S.Day Part', 'BF', 'Almoco', 'Janta')
    report.write("\n%-10s %8s %8s %8s" % ('Vendas', hourly_info['GrossSales']['breakfast'], hourly_info['GrossSales']['lunch'], hourly_info['GrossSales']['dinner']))
    report.write("\n%-10s %8s %8s %8s" % ('Cancelados', hourly_info['VoidSales']['breakfast'], hourly_info['VoidSales']['lunch'], hourly_info['VoidSales']['dinner']))
    # report.write("\n%-10s %8s %8s %8s" % ('Reembolsos', hourly_info['RefundSales']['breakfast'], hourly_info['RefundSales']['lunch'], hourly_info['RefundSales']['dinner']))
    # report.write("\n%-10s %8s %8s %8s" % ('Impostos', hourly_info['TaxSales']['breakfast'], hourly_info['TaxSales']['lunch'], hourly_info['TaxSales']['dinner']))
    # report.write("\n%-10s %8s %8s %8s" % ('Surcharges', hourly_info['SurchargeSales']['breakfast'], hourly_info['SurchargeSales']['lunch'], hourly_info['SurchargeSales']['dinner']))
    # report.write("\n%-10s %8s %8s %8s" % ('Comps', hourly_info['CompSales']['breakfast'], hourly_info['CompSales']['lunch'], hourly_info['CompSales']['dinner']))

    for comp in hourly_info['Comps']:
        name = []
        map(name.append, [x[:4] for x in comp.split()])
        report.write("\n %-9s %8s %8s %8s" % (' '.join(name[:-1]), hourly_info['Comps'][comp]['breakfast'], hourly_info['Comps'][comp]['lunch'], hourly_info['Comps'][comp]['dinner']))

    '''
    report.write("\n%-10s %8s %8s %8s" % ('Descontos', hourly_info['DiscountSales']['breakfast'], hourly_info['DiscountSales']['lunch'], hourly_info['DiscountSales']['dinner']))
    for discount in hourly_info['Discounts']:
        name = []
        map(name.append, [x[:4] for x in discount.split()])
        report.write("\n %-9s %8s %8s %8s" % (' '.join(name[:-1]), hourly_info['Discounts'][discount]['breakfast'], hourly_info['Discounts'][discount]['lunch'], hourly_info['Discounts'][discount]['dinner']))
    report.write("\n%-10s %8s %8s %8s" % ('Tips', hourly_info['TipSales']['breakfast'], hourly_info['TipSales']['lunch'], hourly_info['TipSales']['dinner']))
    for tip in hourly_info['Tips']:
        report.write("\n %-9s %8s %8s %8s" % (tip, hourly_info['Tips'][tip]['breakfast'], hourly_info['Tips'][tip]['lunch'], hourly_info['Tips'][tip]['dinner']))
    '''

    report.write("\n%-10s %8s %8s %8s" % ('Received', hourly_info['ReceivedSales']['breakfast'], hourly_info['ReceivedSales']['lunch'], hourly_info['ReceivedSales']['dinner']))

    for tender in hourly_info['Tenders']:
        report.write("\n %-9s %8s %8s %8s" % (tender, hourly_info['Tenders'][tender]['breakfast'], hourly_info['Tenders'][tender]['lunch'], hourly_info['Tenders'][tender]['dinner']))

    add_header('S. Total', '', '', 'Total')

    report.write("\n%-10s %8s %8s %8s" % ('Vendas', '', '', gross_total))
    # report.write("\n%-10s %8s %8s %8s" % ('Liquido', '', '', net_total))
    report.write("\n%-10s %8s %8s %8s" % ('Cancelados', '', '', void_total))
    # report.write("\n%-10s %8s %8s %8s" % ('Reembolsos', '', '', refund_total))
    # report.write("\n%-10s %8s %8s %8s" % ('Impostos', '', '', tax_total))
    # report.write("\n%-10s %8s %8s %8s" % ('Surcharges', '', '', surcharge_total))
    # report.write("\n%-10s %8s %8s %8s" % ('Comps', '', '', comps_total))

    '''
    for comp in hourly_info['Comps']:
        name = []
        map(name.append, [x[:4] for x in comp.split()])
        report.write("\n %-9s %8s %8s %8s" % (' '.join(name[:-1]), '', '', hourly_info['Comps'][comp]['breakfast'] + hourly_info['Comps'][comp]['lunch'] + hourly_info['Comps'][comp]['dinner']))
    report.write("\n%-10s %8s %8s %8s" % ('Descontos', '', '', discounts_total))
    for discount in hourly_info['Discounts']:
        name = []
        map(name.append, [x[:4] for x in discount.split()])
        report.write("\n %-9s %8s %8s %8s" % (' '.join(name[:-1]), '', '', hourly_info['Discounts'][discount]['breakfast'] + hourly_info['Discounts'][discount]['lunch'] + hourly_info['Discounts'][discount]['dinner']))
    report.write("\n%-10s %8s %8s %8s" % ('Gorjetas', '', '', tip_total))
    for tip in hourly_info['Tips']:
        report.write("\n %-9s %8s %8s %8s" % (tip, '', '', hourly_info['Tips'][tip]['breakfast'] + hourly_info['Tips'][tip]['lunch'] + hourly_info['Tips'][tip]['dinner']))
    '''

    report.write("\n%-10s %8s %8s %8s" % ('Recebido', '', '', received_total))

    for tender in hourly_info['Tenders']:
        report.write("\n %-9s %8s %8s %8s" % (tender, '', '', hourly_info['Tenders'][tender]['breakfast'] + hourly_info['Tenders'][tender]['lunch'] + hourly_info['Tenders'][tender]['dinner']))

    return report.getvalue()


def pos_extended_report(posid, period, operatorid, store_wide, posnumbers, report_type="0", session_id="", *args):
    def order_hourly_info(conn, hourly_info, day_part):
        # get the data
        if int(operatorid):
            cursor = conn.select("""
                SELECT O.TotalGross,
                O.TotalTaxAmountAD,
                O.PriceListTotal,
                O.DiscountAmount,
                O.TotalNet,
                O.StateId,
                O.OrderType,
                SUM(
                    COALESCE(OI.OverwrittenUnitPrice,0)
                ) as Surcharge,
                GROUP_CONCAT(TT.TenderDescr || '|' || COALESCE(OT.TenderAmount,'0') || '|' || COALESCE(OT.TipAmount,'0')) as OrderTenders,
                GROUP_CONCAT(D.DiscountDescr || '|' || COALESCE(OD.DiscountAmount,'0')) as OrderDiscounts,
                datetime(O.CreatedAt, 'localtime') as CreatedAtLocal
                FROM orderdb.Orders O
                LEFT OUTER JOIN orderdb.OrderTender OT
                ON OT.OrderId = O.OrderId
                LEFT OUTER JOIN orderdb.OrderItem OI
                ON OI.OrderId = O.OrderId
                AND OI.PartCode >= 1000000
                LEFT OUTER JOIN productdb.TenderType TT
                ON OT.TenderId == TT.TenderId
                LEFT OUTER JOIN orderdb.OrderDiscount OD
                ON OD.OrderId == O.OrderId
                LEFT OUTER JOIN discountcalc.Discounts D
                ON OD.DiscountId == D.DiscountId
                WHERE O.BusinessPeriod='%s'
                AND O.StateId IN (4,5)
                AND O.OrderType IN (0,1)
                AND O.SessionId LIKE '%%user=%s,%%'
                GROUP BY O.OrderId""" % (period, str(operatorid)))
        else:
            cursor = conn.select("""
                SELECT O.TotalGross,
                O.TotalTaxAmountAD,
                O.PriceListTotal,
                O.DiscountAmount,
                O.TotalNet,
                O.StateId,
                O.OrderType,
                SUM(
                    COALESCE(OI.OverwrittenUnitPrice,0)
                ) as Surcharge,
                GROUP_CONCAT(TT.TenderDescr || '|' || COALESCE(OT.TenderAmount,'0') || '|' || COALESCE(OT.TipAmount,'0')) as OrderTenders,
                GROUP_CONCAT(D.DiscountDescr || '|' || COALESCE(OD.DiscountAmount,'0')) as OrderDiscounts,
                datetime(O.CreatedAt, 'localtime') as CreatedAtLocal
                FROM orderdb.Orders O
                LEFT OUTER JOIN orderdb.OrderTender OT
                ON OT.OrderId = O.OrderId
                LEFT OUTER JOIN orderdb.OrderItem OI
                ON OI.OrderId = O.OrderId
                AND OI.PartCode >= 1000000
                LEFT OUTER JOIN productdb.TenderType TT
                ON OT.TenderId == TT.TenderId
                LEFT OUTER JOIN orderdb.OrderDiscount OD
                ON OD.OrderId == O.OrderId
                LEFT OUTER JOIN discountcalc.Discounts D
                ON OD.DiscountId == D.DiscountId
                WHERE O.BusinessPeriod='%s'
                AND O.StateId IN (4,5)
                AND O.OrderType IN (0,1)
                GROUP BY O.OrderId""" % period)

        if not day_part:
            day_part['breakfast'] = {'interval': (datetime.time(0, 0), datetime.time(11, 0))}
            day_part['lunch'] = {'interval': (datetime.time(11, 0), datetime.time(17, 0))}
            day_part['dinner'] = {'interval': (datetime.time(17, 0), datetime.time(0, 0))}

        if not hourly_info:
            hourly_info['GrossSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['VoidSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['TaxSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['TipSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['CompSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['DiscountSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['SurchargeSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['NetSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['RefundSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['VoidRefundSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['ReceivedSales'] = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
            hourly_info['Tenders'] = {}
            hourly_info['Tips'] = {}
            hourly_info['Discounts'] = {}
            hourly_info['Comps'] = {}

        for row in cursor:
            created_at = row.get_entry('CreatedAtLocal')
            slot_day_time = datetime.datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            slot_time = datetime.time(slot_day_time.hour, slot_day_time.minute)

            for dp in day_part:
                if slot_time > day_part[dp]['interval'][0] and slot_time <= day_part[dp]['interval'][1]:
                    if int(row.get_entry('OrderType')) == 0:
                        hourly_info['GrossSales'][dp] += D(row.get_entry('TotalGross') or 0).quantize(D('.01'))
                        if int(row.get_entry('StateId')) == 5:
                            hourly_info['TaxSales'][dp] += D(row.get_entry('TotalTaxAmountAD') or 0).quantize(D('.01'))
                            hourly_info['CompSales'][dp] += D(row.get_entry('DiscountAmount') if row.get_entry('PriceListTotal') == row.get_entry('DiscountAmount') else 0).quantize(D('.01'))
                            hourly_info['DiscountSales'][dp] += D(row.get_entry('DiscountAmount') if row.get_entry('PriceListTotal') != row.get_entry('DiscountAmount') else 0).quantize(D('.01'))
                            hourly_info['NetSales'][dp] += D(row.get_entry('TotalNet') or 0).quantize(D('.01'))
                            hourly_info['SurchargeSales'][dp] += D(row.get_entry('Surcharge') or 0).quantize(D('.01'))

                            if row.get_entry('OrderTenders'):
                                for tender in row.get_entry('OrderTenders').split(','):
                                    k, v, t = tender.split('|')
                                    if not hourly_info['Tenders'].get(k):
                                        hourly_info['Tenders'].update({k: {'breakfast': 0, 'lunch': 0, 'dinner': 0}})

                                    hourly_info['Tenders'][k][dp] += D(v).quantize(D('.01'))

                                    if D(t) != D(0):
                                        if not hourly_info['Tips'].get(k):
                                            hourly_info['Tips'].update({k: {'breakfast': 0, 'lunch': 0, 'dinner': 0}})
                                        hourly_info['Tips'][k][dp] += D(t).quantize(D('.01'))
                                        hourly_info['TipSales'][dp] += D(t).quantize(D('.01'))

                                    hourly_info['ReceivedSales'][dp] += D(v).quantize(D('.01')) + D(t).quantize(D('.01'))

                            if row.get_entry('OrderDiscounts'):
                                for discount in row.get_entry('OrderDiscounts').split(','):
                                    k, v = discount.split('|')
                                    if not hourly_info['Discounts'].get(k) and row.get_entry('PriceListTotal') != row.get_entry('DiscountAmount'):
                                        hourly_info['Discounts'].update({k: {'breakfast': 0, 'lunch': 0, 'dinner': 0}})
                                    elif not hourly_info['Comps'].get(k) and row.get_entry('PriceListTotal') == row.get_entry('DiscountAmount'):
                                        hourly_info['Comps'].update({k: {'breakfast': 0, 'lunch': 0, 'dinner': 0}})

                                    if row.get_entry('PriceListTotal') != row.get_entry('DiscountAmount'):
                                        hourly_info['Discounts'][k][dp] += D(v).quantize(D('.01'))
                                    else:
                                        hourly_info['Comps'][k][dp] += D(v).quantize(D('.01'))

                        elif int(row.get_entry('StateId')) == 4 and int(row.get_entry('OrderType')) == 0:
                            hourly_info['VoidSales'][dp] += D(row.get_entry('TotalGross') or 0).quantize(D('.01'))

                    if int(row.get_entry('OrderType')) == 1:
                        hourly_info['RefundSales'][dp] += D(row.get_entry('TotalGross') or 0).quantize(D('.01'))
                        if int(row.get_entry('StateId')) == 4:
                            hourly_info['VoidRefundSales'][dp] += D(row.get_entry('TotalGross') or 0).quantize(D('.01'))

    posnumbers = posnumbers.split('|') if posnumbers else []
    store_wide = (store_wide.lower() == "true")

    if report_type == "sales_report":
        report_type = 'Sales Summary'

    if store_wide:
        report_type = '%s (Loja)' % report_type
    else:
        posnumbers = (posid, )

    hourly_info = {}
    day_part = {}

    for posno in posnumbers:
        conn = None
        try:
            # create database connection
            conn = dbd.open(mbcontext, dbname=str(posno))

            # reserve a database connection
            conn.transaction_start()
            order_hourly_info(conn, hourly_info, day_part)
        finally:
            if conn:
                conn.close()

    gross_total = D(0)
    void_total = D(0)
    refund_total = D(0)
    void_refund_total = D(0)
    tips_total = D(0)
    tax_total = D(0)
    comps_total = D(0)
    discounts_total = D(0)
    surcharge_total = D(0)
    net_total = D(0)
    received_total = D(0)

    for dp in day_part:
        hourly_info['GrossSales'][dp] += hourly_info['TipSales'][dp] + hourly_info['DiscountSales'][dp] + hourly_info['CompSales'][dp]
        gross_total += hourly_info['GrossSales'].get(dp) or 0
        void_total += hourly_info['VoidSales'].get(dp) or 0
        refund_total += hourly_info['RefundSales'].get(dp) or 0
        void_refund_total += hourly_info['VoidRefundSales'].get(dp) or 0
        tips_total += hourly_info['TipSales'].get(dp) or 0
        tax_total += hourly_info['TaxSales'].get(dp) or 0
        comps_total += hourly_info['CompSales'].get(dp) or 0
        discounts_total += hourly_info['DiscountSales'].get(dp) or 0
        surcharge_total += hourly_info['SurchargeSales'].get(dp) or 0
        net_total += hourly_info['NetSales'].get(dp) or 0
        received_total += hourly_info['ReceivedSales'].get(dp) or 0

    html = """
    <div style="overflow: auto; width: 900px; height: 480px;margin-bottom: 10px; font-family: 'monospace';">
        <span align='center'>%s</align>
        <table class="table table-hover" align="center">
            <thead>
                <tr>
                    <th style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</th>
                    <th style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</th>
                    <th style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</th>
                    <th style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</th>
                    <th style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</th>
                </tr>
            </thead>""" % (report_type, 'SUMMARY', 'BreakFast', 'Lunch', 'Dinner', 'TOTAL')
    html += """
            <tbody>
                <tr>
                    <td>%-32s</td>""" % ('Gross:')

    html += """<td>%12s</td>""" % (hourly_info['GrossSales'].get('breakfast') or 0)
    html += """<td>%12s</td>""" % (hourly_info['GrossSales'].get('lunch') or 0)
    html += """<td>%12s</td>""" % (hourly_info['GrossSales'].get('dinner') or 0)
    html += """
                    <td>%12s</td>
                </tr>
                <tr>
                    <td>%-32s</td>""" % (gross_total, '- Voids:')

    html += """<td>%12s</td>""" % (hourly_info['VoidSales'].get('breakfast') or 0)
    html += """<td>%12s</td>""" % (hourly_info['VoidSales'].get('lunch') or 0)
    html += """<td>%12s</td>""" % (hourly_info['VoidSales'].get('dinner') or 0)
    html += """
                    <td>%12s</td>
                </tr>
                <tr>
                    <td>%-32s</td>""" % (void_total, '- Tips:')

    html += """<td>%12s</td>""" % (hourly_info['TipSales'].get('breakfast') or 0)
    html += """<td>%12s</td>""" % (hourly_info['TipSales'].get('lunch') or 0)
    html += """<td>%12s</td>""" % (hourly_info['TipSales'].get('dinner') or 0)
    html += """
                    <td>%12s</td>
                </tr>
                <tr>
                    <td>%-32s</td>""" % (tips_total, '- Taxes:')

    html += """<td>%12s</td>""" % (hourly_info['TaxSales'].get('breakfast') or 0)
    html += """<td>%12s</td>""" % (hourly_info['TaxSales'].get('lunch') or 0)
    html += """<td>%12s</td>""" % (hourly_info['TaxSales'].get('dinner') or 0)
    html += """
                    <td>%12s</td>
                </tr>
                <tr>
                    <td>%-32s</td>""" % (tax_total, '- Comps:')

    html += """<td>%12s</td>""" % (hourly_info['CompSales'].get('breakfast') or 0)
    html += """<td>%12s</td>""" % (hourly_info['CompSales'].get('lunch') or 0)
    html += """<td>%12s</td>""" % (hourly_info['CompSales'].get('dinner') or 0)
    html += """
                    <td>%12s</td>
                </tr>
                <tr>
                    <td>%-32s</td>""" % (comps_total, '- Discounts:')

    html += """<td>%12s</td>""" % (hourly_info['DiscountSales'].get('breakfast') or 0)
    html += """<td>%12s</td>""" % (hourly_info['DiscountSales'].get('lunch') or 0)
    html += """<td>%12s</td>""" % (hourly_info['DiscountSales'].get('dinner') or 0)
    html += """
                    <td>%12s</td>
                </tr>
                <tr>
                    <td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % (discounts_total, '- Surcharges:')

    html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['SurchargeSales'].get('breakfast') or 0)
    html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['SurchargeSales'].get('lunch') or 0)
    html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['SurchargeSales'].get('dinner') or 0)
    html += """
                    <td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>
                </tr>
                <tr />
                <tr>
                    <td style="padding-bottom: 20px;">%-32s</td>""" % (surcharge_total, '= Net Sales:')

    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['NetSales'].get('breakfast') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['NetSales'].get('lunch') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['NetSales'].get('dinner') or 0)
    html += """
                    <td style="padding-bottom: 20px;">%12s</td>
                </tr>
                <tr />""" % (net_total)

    html += """ <tr>
                    <td>%-32s</td>""" % ('Refund Sales:')

    html += """<td>%12s</td>""" % (hourly_info['RefundSales'].get('breakfast') or 0)
    html += """<td>%12s</td>""" % (hourly_info['RefundSales'].get('lunch') or 0)
    html += """<td>%12s</td>""" % (hourly_info['RefundSales'].get('dinner') or 0)
    html += """
                    <td>%12s</td>
                </tr>
                <tr>
                    <td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % (refund_total, '- Void Refund Sales:')

    html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['VoidRefundSales'].get('breakfast') or 0)
    html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['VoidRefundSales'].get('lunch') or 0)
    html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['VoidRefundSales'].get('dinner') or 0)
    html += """
                    <td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>
                </tr>
                <tr />
                <tr>
                    <td style="padding-bottom: 20px;">%-32s</td>""" % (void_refund_total, '= Total Refund Sales:')

    html += """<td style="padding-bottom: 20px;">%12s</td>""" % ((hourly_info['RefundSales'].get('breakfast') or 0) - (hourly_info['VoidRefundSales'].get('breakfast') or 0))
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % ((hourly_info['RefundSales'].get('lunch') or 0) - (hourly_info['VoidRefundSales'].get('lunch') or 0))
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % ((hourly_info['RefundSales'].get('dinner') or 0) - (hourly_info['VoidRefundSales'].get('dinner') or 0))
    html += """
                    <td style="padding-bottom: 20px;">%12s</td>
                </tr>
                <tr />""" % (refund_total - void_refund_total)

    for i, tender in enumerate(hourly_info['Tenders'].keys()):
        if len(hourly_info['Tenders']) == i + 1:
            if i == 0:
                html += """<tr><td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % ('%s:' % tender)
            else:
                html += """<tr><td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % ('+ %s:' % tender)

            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Tenders'][tender]['breakfast'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Tenders'][tender]['lunch'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Tenders'][tender]['dinner'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td></tr>""" % (hourly_info['Tenders'][tender]['breakfast'] + hourly_info['Tenders'][tender]['lunch'] + hourly_info['Tenders'][tender]['dinner'])
        else:
            if i == 0:
                html += """<tr><td>%-32s</td>""" % ('%s:' % tender)
            else:
                html += """<tr><td>%-32s</td>""" % ('+ %s:' % tender)

            html += """<td>%12s</td>""" % (hourly_info['Tenders'][tender]['breakfast'] or 0)
            html += """<td>%12s</td>""" % (hourly_info['Tenders'][tender]['lunch'] or 0)
            html += """<td>%12s</td>""" % (hourly_info['Tenders'][tender]['dinner'] or 0)
            html += """<td>%12s</td></tr>""" % (hourly_info['Tenders'][tender]['breakfast'] + hourly_info['Tenders'][tender]['lunch'] + hourly_info['Tenders'][tender]['dinner'])

    html += """<tr />
                <tr>
                    <td style="padding-bottom: 20px;">%-32s</td>""" % ('= Total Received:')

    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['ReceivedSales'].get('breakfast') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['ReceivedSales'].get('lunch') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['ReceivedSales'].get('dinner') or 0)
    html += """
                    <td style="padding-bottom: 20px;">%12s</td>
                </tr>
                <tr />
                """ % (received_total)

    for i, tip in enumerate(hourly_info['Tips'].keys()):
        if len(hourly_info['Tips']) == i + 1:
            if i == 0:
                html += """<tr><td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % ('%s:' % tip)
            else:
                html += """<tr><td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % ('+ %s:' % tip)

            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Tips'][tip]['breakfast'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Tips'][tip]['lunch'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Tips'][tip]['dinner'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td></tr>""" % (hourly_info['Tips'][tip]['breakfast'] + hourly_info['Tips'][tip]['lunch'] + hourly_info['Tips'][tip]['dinner'])
        else:
            if i == 0:
                html += """<tr><td>%-32s</td>""" % ('%s:' % tip)
            else:
                html += """<tr><td>%-32s</td>""" % ('+ %s:' % tip)

            html += """<td>%12s</td>""" % (hourly_info['Tips'][tip]['breakfast'] or 0)
            html += """<td>%12s</td>""" % (hourly_info['Tips'][tip]['lunch'] or 0)
            html += """<td>%12s</td>""" % (hourly_info['Tips'][tip]['dinner'] or 0)
            html += """<td>%12s</td></tr>""" % (hourly_info['Tips'][tip]['breakfast'] + hourly_info['Tips'][tip]['lunch'] + hourly_info['Tips'][tip]['dinner'])

    html += """<tr />
                <tr>
                    <td style="padding-bottom: 20px;">%-32s</td>""" % ('= Total Tips:')

    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['TipSales'].get('breakfast') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['TipSales'].get('lunch') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['TipSales'].get('dinner') or 0)
    html += """
                    <td style="padding-bottom: 20px;">%12s</td>
                </tr>
                <tr />
                """ % (tips_total)

    for i, discount in enumerate(hourly_info['Discounts'].keys()):
        if len(hourly_info['Discounts']) == i + 1:
            if i == 0:
                html += """<tr><td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % ('%s:' % discount)
            else:
                html += """<tr><td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % ('+ %s:' % discount)

            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Discounts'][discount]['breakfast'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Discounts'][discount]['lunch'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Discounts'][discount]['dinner'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td></tr>""" % (hourly_info['Discounts'][discount]['breakfast'] + hourly_info['Discounts'][discount]['lunch'] + hourly_info['Discounts'][discount]['dinner'])
        else:
            if i == 0:
                html += """<tr><td>%-32s</td>""" % ('%s:' % discount)
            else:
                html += """<tr><td>%-32s</td>""" % ('+ %s:' % discount)

            html += """<td>%12s</td>""" % (hourly_info['Discounts'][discount]['breakfast'] or 0)
            html += """<td>%12s</td>""" % (hourly_info['Discounts'][discount]['lunch'] or 0)
            html += """<td>%12s</td>""" % (hourly_info['Discounts'][discount]['dinner'] or 0)
            html += """<td>%12s</td></tr>""" % (hourly_info['Discounts'][discount]['breakfast'] + hourly_info['Discounts'][discount]['lunch'] + hourly_info['Discounts'][discount]['dinner'])

    html += """<tr />
            <tr>
                <td style="padding-bottom: 20px;">%-32s</td>""" % ('= Total Discounts:')

    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['DiscountSales'].get('breakfast') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['DiscountSales'].get('lunch') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['DiscountSales'].get('dinner') or 0)
    html += """
                    <td style="padding-bottom: 20px;">%12s</td>
                </tr>
                <tr />
                """ % (discounts_total)

    for i, comps in enumerate(hourly_info['Comps'].keys()):
        if len(hourly_info['Comps']) == i + 1:
            if i == 0:
                html += """<tr><td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % ('%s:' % comps)
            else:
                html += """<tr><td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%-32s</td>""" % ('+ %s:' % comps)

            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Comps'][comps]['breakfast'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Comps'][comps]['lunch'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td>""" % (hourly_info['Comps'][comps]['dinner'] or 0)
            html += """<td style="border-bottom: 1px solid #000; padding-bottom: 10px;">%12s</td></tr>""" % (hourly_info['Comps'][comps]['breakfast'] + hourly_info['Comps'][comps]['lunch'] + hourly_info['Comps'][comps]['dinner'])
        else:
            if i == 0:
                html += """<tr><td>%-32s</td>""" % ('%s:' % comps)
            else:
                html += """<tr><td>%-32s</td>""" % ('+ %s:' % comps)

            html += """<td>%12s</td>""" % (hourly_info['Comps'][comps]['breakfast'] or 0)
            html += """<td>%12s</td>""" % (hourly_info['Comps'][comps]['lunch'] or 0)
            html += """<td>%12s</td>""" % (hourly_info['Comps'][comps]['dinner'] or 0)
            html += """<td>%12s</td></tr>""" % (hourly_info['Comps'][comps]['breakfast'] + hourly_info['Comps'][comps]['lunch'] + hourly_info['Comps'][comps]['dinner'])

    html += """<tr />
            <tr>
                <td style="padding-bottom: 20px;">%-32s</td>""" % ('= Total Comps:')

    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['CompSales'].get('breakfast') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['CompSales'].get('lunch') or 0)
    html += """<td style="padding-bottom: 20px;">%12s</td>""" % (hourly_info['CompSales'].get('dinner') or 0)
    html += """
                    <td style="padding-bottom: 20px;">%12s</td>
                </tr>
                <tr />
                """ % (comps_total)

    html += """
            </tbody>
        </table>
    </div>"""

    return html


def sats_report(posid, sat_status_list, *args):
    title = _center("SATs Status")
    current_datetime = time.strftime(DATE_TIME_FMT)

    # transform the string sat_status_list back into a dictionary
    d = ast.literal_eval(sat_status_list)

    # extract the POS id´s from the string sat_status_list
    pos_list = sorted(map(int, re.findall(r'[1-9]+', sat_status_list)))

    # create string I/O to append the report info
    report = StringIO()
    report.write(
        """%(SEPARATOR)s
%(title)s
  Data/hora.....: %(current_datetime)s
  POS...........: %(pos_list)s
""" % _join(globals(), locals()))
    width = 38
    report.write("%s\n" % SEPARATOR)
    report.write("  POS ID")
    report.write("SAT Status\n".rjust(width-len("  POS ID")))
    report.write("%s\n" % SINGLE_SEPARATOR)

    for pos in pos_list:
        report.write("  %s " % str(pos).zfill(2))
        status = str(d["SAT0%s" % str(pos)])
        report.write("%s\n" % status.rjust(width - len("   %s" % str(pos)), "."))

    report.write("%s\n" % SEPARATOR)
    report.write("\n")
    report.write("%s\n" % SEPARATOR)

    return report.getvalue()


def kds_report(posid, kds_status_list, *args):
    # create string I/O to append the report info
    report = StringIO()
    title = _center("KDSs Status")
    current_datetime = time.strftime(DATE_TIME_FMT)

    # transform the string kds_status_list back into a list of lists
    kds_list = ast.literal_eval(kds_status_list)
    sorted(kds_list, key=itemgetter(1))

    # deleting indexes
    for i in kds_list:
        del i[0]

    report.write(
        """%(SEPARATOR)s
%(title)s
  Data/hora.....: %(current_datetime)s
""" % _join(globals(), locals()))
    width = 38
    report.write("%s\n" % SEPARATOR)
    report.write("  KDS")
    report.write("Status\n".rjust(width-len("  KDS")))
    report.write("%s\n" % SINGLE_SEPARATOR)

    for kds_info in kds_list:
        kds = str(kds_info[0])
        report.write("  %s" % kds)
        report.write("%s\n" % kds_info[1].rjust(width-len("   %s" % kds), "."))

    report.write("%s\n" % SEPARATOR)
    report.write("\n")
    report.write("%s\n" % (SEPARATOR))

    return report.getvalue()


def printer_report(posid, printer_status_list, *args):
    # create string I/O to append the report info
    report = StringIO()
    title = _center("Printer Status")
    current_datetime = time.strftime(DATE_TIME_FMT)

    # transform the string kds_status_list back into a list of lists
    printer_list = ast.literal_eval(printer_status_list)

    report.write(
        """%(SEPARATOR)s
%(title)s
  Data/hora.....: %(current_datetime)s
""" % _join(globals(), locals()))
    width = 38
    report.write("%s\n" % SEPARATOR)
    report.write("  Impressora")
    report.write("Status\n".rjust(width-len("  Impressora")))
    report.write("%s\n" % SINGLE_SEPARATOR)

    for printer_info in printer_list:
        printer = str(printer_info[0])
        report.write("  %s" % printer)
        report.write("%s\n" % printer_info[1].rjust(width-len("   %s" % printer), "."))

    report.write("%s\n" % SEPARATOR)
    report.write("\n")
    report.write("%s\n" % (SEPARATOR))

    return report.getvalue()


def versions_report(posid, versions, *args):
    # create string I/O to append the report info
    report = StringIO()
    title = _center("Versoes Pigeon")
    current_datetime = time.strftime(DATE_TIME_FMT)

    data = versions.split(";")

    report.write(
        """%(SEPARATOR)s
%(title)s
  Data/hora.....: %(current_datetime)s
""" % _join(globals(), locals()))
    report.write("%s\n" % SEPARATOR)
    report.write("%s\n" % SINGLE_SEPARATOR)
    width = 37
    report.write("  Component version:")
    report.write("%s\n" % data[0].rjust(width-len("  Component version:"), "."))
    report.write("  Core version:")
    report.write("%s\n" % data[1].rjust(width-len("  Core version:"), "."))
    report.write("  Price version:")
    report.write("%s\n" % data[2].rjust(width-len("  Price version:"), "."))
    report.write("%s\n" % SEPARATOR)
    report.write("\n")
    report.write("%s\n" % (SEPARATOR))

    return report.getvalue()


def sats_op_report(posid, sats_op_list, *args):
    # create string I/O to append the report info
    report = StringIO()
    title = _center("SAT Status Operacional")
    current_datetime = time.strftime(DATE_TIME_FMT)

    splitter = sats_op_list.split("|")

    report.write(
        """%(SEPARATOR)s
%(title)s
  Data/hora.....: %(current_datetime)s
""" % _join(globals(), locals()))
    width = 38
    report.write("%s\n" % SEPARATOR)
    report.write("  SAT %s\n" % posid)
    report.write("%s\n" % SINGLE_SEPARATOR)

    if "ERROR -" in splitter[0]:
        report.write(splitter[0] + '\n')
    else:
        report.write("  Numero de série:")
        report.write("%s\n" % splitter[5].rjust(width - len("  Numero de série:"), "."))
        report.write("  Tipo de Lan:")
        report.write("%s\n" % splitter[6].rjust(width - len("   Tipo de Lan:"), "."))
        report.write("  IP da LAN:")
        report.write("%s\n" % splitter[7].rjust(width - len("   IP da LAN:"), "."))
        report.write("  MAC:")
        report.write("%s\n" % splitter[8].rjust(width - len("   MAC:"), "."))
        report.write("  Máscara:")
        report.write("%s\n" % splitter[9].rjust(width - len("  Máscara:"), "."))
        report.write("  Gateway:")
        report.write("%s\n" % splitter[10].rjust(width - len("   Gateway:"), "."))
        report.write("  DNS1:")
        report.write("%s\n" % splitter[11].rjust(width - len("   DNS1:"), "."))
        report.write("  DNS2:")
        report.write("%s\n" % splitter[12].rjust(width - len("   DNS2:"), "."))
        report.write("  Status da rede:")
        report.write("%s\n" % splitter[13].rjust(width - len("   Status da rede:"), "."))
        report.write("  Nível da Bateria:")
        report.write("%s\n" % splitter[14].rjust(width - len("  Nível da Bateria:"), "."))
        report.write("  Memória Total:")
        report.write("%s\n" % splitter[15].rjust(width - len("  Memória Total:"), "."))
        report.write("  Memória Usada:")
        report.write("%s\n" % splitter[16].rjust(width - len("  Memória Usada:"), "."))
        report.write("  Data e hora:")
        date_and_time = splitter[17][6:8] + "/" + splitter[17][4:6] + "/" + splitter[17][:4] + " " + splitter[17][8:10] + ":" + splitter[17][10:12] + ":" + splitter[17][12:14]
        report.write("%s\n" % date_and_time.rjust(width - len("   Data e hora:"), "."))
        report.write("  Versão do Software:")
        report.write("%s\n" % splitter[18].rjust(width - len("  Versão do Software:"), "."))
        # report.write("  Versão da tabela de informações::")
        # report.write("%s\n" % splitter[19].rjust(width - len("  Versão da tabela de informações::"), "."))
        # report.write("Último CF-e-SAT emitido:")
        # report.write("%s\n" % splitter[20].rjust(width - len("  Último CF-e-SAT emitido:"), "."))
        # report.write("Primeiro CF-e-SAT armazenado:")
        # report.write("%s\n" % splitter[21].rjust(width - len("  Primeiro CF-e-SAT armazenado:"), "."))
        # report.write("Último CF-e-SAT armazenado:")
        # report.write("%s\n" % splitter[22].rjust(width - len("  Último CF-e-SAT armazenado:"), "."))
        # report.write("  Última envio para SEFAZ:")
        # report.write("%s\n" % splitter[23].rjust(width - len("  Última envio para SEFAZ:"), "."))
        report.write("  Última comunicação com a SEFAZ:\n")
        report.write("      Data:")
        last_com_date = splitter[24][6:8] + "/" + splitter[24][4:6] + "/" + splitter[24][:4]
        report.write("%s\n" % last_com_date.rjust(width - len("       Data:"), "."))
        report.write("      Hora:")
        last_com_time = splitter[24][8:10] + ":" + splitter[24][10:12] + ":" + splitter[24][12:14]
        report.write("%s\n" % last_com_time.rjust(width - len("       Hora:"), "."))
        # report.write("  Emissão do certificado:")
        # report.write("%s\n" % splitter[25].rjust(width - len("  Emissão do certificado"), "."))
        report.write("  Data certificado:")
        date_and_time = splitter[26][6:8] + "/" + splitter[26][4:6] + "/" + splitter[26][:4]
        report.write("%s\n" % date_and_time.rjust(width - len("   Data certificado:"), "."))
        report.write("  Estado SAT:")
        report.write("%s\n" % splitter[27][:1].rjust(width - len("   Estado SAT:"), "."))

    report.write("%s\n" % SEPARATOR)
    report.write("\n")
    report.write("%s\n" % SEPARATOR)

    return report.getvalue()


def delivery_json_report(pos_id, order_number, json_order):
    # type: (str, str, unicode) -> unicode
    """
        nodes_dict:
        { ( tag, father ) : { text: '', level: '', sort_Key: '' }
    """
    json_order = json_order.encode('utf-8', errors='ignore')
    nodes_dict = json.loads(json_order)
    model = sysactions.get_model(pos_id)
    title = sysactions.translate_message(model, "DELIVERY_PED", str(order_number))

    #nodes_dict = sorted(nodes_dict.items(), key=lambda x: x[1]['sort_key'])

    report = StringIO()

    title = _center(title)
    current_datetime = _center(time.strftime(DATE_TIME_FMT))

    report.write("{}\n".format(SEPARATOR))
    report.write("{}\n".format(title))
    report.write("{}\n".format(current_datetime))
    report.write("{}\n".format(SEPARATOR))
    report.write("\n\n")
    level = 0

    def recursive_dict_print(dict_data, lvl):
        for tag in dict_data:
            tag_descr = _remove_accents(tag)
            value_descr = dict_data[tag]
            if isinstance(value_descr, dict):
                for count in range(lvl):
                    report.write('  ')
                report.write("{}\n".format(tag_descr))
                lvl += 1
                recursive_dict_print(value_descr, lvl)
            elif isinstance(value_descr, list):
                for x in value_descr:
                    recursive_dict_print(x, lvl)
                    report.write("\n")
            else:
                value_descr = _remove_accents(value_descr)
                for count in range(lvl):
                    report.write('  ')
                report.write("{}: {}\n".format(tag_descr, value_descr))

    recursive_dict_print(nodes_dict, level)

    return report.getvalue()


def delivery_ped_report(pos_id, order_number, ped_xml):
    # type: (str, str, str) -> unicode
    """
        nodes_dict:
        { ( tag, father ) : { text: '', level: '', sort_Key: '' }
    """
    nodes_dict = {}

    def _get_xml_node_values(xml, lvl=1, sort_key=0):
        father = xml.tag
        for node in xml:
            value = _remove_accents(node.text) if node.text else ''
            sort_key += 1
            nodes_dict[(node.tag, father)] = {'value': value, 'level': lvl, 'sort_key': sort_key}
            if len(node) > 0:
                sort_key += _get_xml_node_values(node, lvl + 1, sort_key)

        return sort_key

    _get_xml_node_values(etree.fromstring(ped_xml))

    model = sysactions.get_model(pos_id)
    title = sysactions.translate_message(model, "DELIVERY_PED", str(order_number))

    nodes_dict = sorted(nodes_dict.items(), key=lambda x: x[1]['sort_key'])

    report = StringIO()

    title = _center(title)
    current_datetime = _center(time.strftime(DATE_TIME_FMT))

    report.write("{}\n".format(SEPARATOR))
    report.write("{}\n".format(title))
    report.write("{}\n".format(current_datetime))
    report.write("{}\n".format(SEPARATOR))
    report.write("\n\n")

    fathers_list = list(dict.fromkeys([x[1] for x in [x[0] for x in nodes_dict]]))
    for tag, values in nodes_dict:
        tag_descr = tag[0].rjust(len(tag[0]) + values['level'])
        value_descr = values['value']
        if tag[0] in fathers_list:
            report.write("{}\n".format(tag_descr))
        else:
            report.write("{}: {}\n".format(tag_descr, value_descr))

    return report.getvalue()


def tip_report(date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, *args):
    global new_pos_list

    report = StringIO()
    title = _center("Relatorio de Gorjeta")
    current_datetime = time.strftime(DATE_TIME_FMT)
    formatted_store_id = get_store_id().zfill(5) + "\n"

    if operator_id != "0" and operator_id is not None:
        operator_name = etree.XML(sysactions.get_user_information(operator_id)).find(".//user").get("LongName")[:20]
    else:
        operator_name = "Todos"

    formatted_start_date = datetime.datetime.strptime(initial_date, "%Y%m%d").strftime("%d/%m/%y")
    formatted_end_date = datetime.datetime.strptime(end_date, "%Y%m%d").strftime("%d/%m/%y")

    report.write(
"""%(SEPARATOR)s
%(title)s
Loja.........: %(formatted_store_id)s
Data/hora....: %(current_datetime)s
Periodo......: %(formatted_start_date)s - %(formatted_end_date)s
Operador.....: %(operator_name)s
%(SEPARATOR)s
Operador               Venda   Gorjeta  
""" % _join(globals(), locals()))
    width = 38
    report.write("%s\n" % SEPARATOR)

    conn = None
    try:
        conn = dbd.open(mbcontext, dbname=str(pos_id))
        conn.transaction_start()

        query = """select UserId, SUM(TotalGross) as Sales, SUM(OrderTip) as Tip, Count(*) as Tables, SUM(NumberOfSeats) as Seats
FROM (
select sords.userid, stip.serviceid, sop.TotalGross * (SUM(sords.TotalGross) / soa.TotalGross) as TotalGross, stip.calculatedtip, (SUM(sords.TotalGross) / soa.TotalGross) * stip.calculatedtip AS OrderTip, tsvc.NumberOfSeats
from servicetip stip
join serviceorders sords on sords.serviceid = stip.serviceid
join tableservice tsvc on tsvc.serviceid = stip.serviceid
join (select serviceid, TotalGross from serviceorders where state = 'PAID') sop on sop.serviceid = stip.serviceid
join (select serviceid, SUM(TotalGross) as TotalGross from serviceorders where state = 'ABANDONED' Group by serviceid) soa on soa.serviceid = stip.serviceid
where strftime('%Y%m%d', tsvc.BusinessPeriod, 'utc') >= '{}' and strftime('%Y%m%d', tsvc.BusinessPeriod, 'utc') <= '{}'
and sords.state = 'ABANDONED' and sords.orderId in (select distinct Orderid from ServiceSplit where serviceid = stip.serviceid)
group by sords.userid, stip.serviceid, stip.calculatedtip, tsvc.NumberOfSeats
order by stip.ServiceId
) GROUP BY userId ORDER BY userId""".format(initial_date, end_date)

        cursor = conn.select(query)

        try:
            locale.setlocale(locale.LC_ALL, "portuguese_brazil")
        except:
            locale.setlocale(locale.LC_ALL, "pt_BR.UTF-8")

        report_lines_dict = {}
        for row in cursor:
            user = row.get_entry(0)
            operator_name = etree.XML(sysactions.get_user_information(user)).find(".//user").get("LongName")
            if operator_id != "0" and operator_id != user:
                continue
            report_lines_dict[operator_name] = TipInfo()
            report_lines_dict[operator_name].total_amount = float(row.get_entry(1))
            report_lines_dict[operator_name].tip_amount = float(row.get_entry(2))

        total_amount = 0.0
        total_tip = 0.0

        from collections import OrderedDict
        report_lines_dict = OrderedDict(sorted(report_lines_dict.items()))
        for operator_name, value in report_lines_dict.iteritems():
            _format_line(report, 19, operator_name.upper()[:17])
            _format_line(report, 10, '{0:>9}'.format(locale.format("%.2f", value.total_amount, True)))
            _format_line(report, 10, '{0:>9}'.format(locale.format("%.2f", value.tip_amount, True)))
            report.write("\n")

            total_amount = total_amount + value.total_amount
            total_tip = total_tip + value.tip_amount

        report.write("%s\n" % SEPARATOR)
        report.write("Total Vendas........: R$ {:>13}\n".format(locale.format("%.2f", total_amount, True)))
        report.write("Total Valor Gorjetas: R$ {:>13}\n".format(locale.format("%.2f", total_tip, True)))

    except Exception as _:
        pass
    finally:
        if conn:
            conn.close()

    return report.getvalue()


def generate_tickets_report(business_period):
    business_period = business_period[:10]
    pos_list = _get_quick_service_pos_list()
    average_ticket_report = AverageTicketReport(AverageTicketTableServiceRepository(mbcontext),
                                                AverageTicketOrderRepository(mbcontext, pos_list))
    report = average_ticket_report.generate_tickets_report(business_period)
    return report


def _get_quick_service_pos_list():
    msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
    if msg.token == TK_SYS_NAK:
        sys_log_error("Could not retrieve PosList")
        raise Exception("Could not retrieve PosList")

    pos_list = []
    for pos in msg.data.split("\0"):
        if sysactions.get_model(pos).find("WorkingMode").get("usrCtrlType") == "QSR":
            pos_list.append(pos)

    return sorted(map(int, pos_list))


def _format_line(report, field_qty, text):
    report_line = text[:field_qty]
    for _ in range(len(report_line), field_qty):
        report_line = report_line + " "

    report.write(report_line)


class TipInfo(object):
    def __init__(self):
        self.table_list = []
        self.number_of_seats = 0
        self.total_amount = 0.0
        self.tip_amount = 0.0


def _remove_accents(text):
    return normalize('NFKD', unicode(text)).encode('ASCII', 'ignore')
