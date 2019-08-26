# -*- coding: utf-8 -*-
# Module name: manager_reports.py
# Module Description: Format manager reports
#
# Copyright © 2008-2009 MWneo Corporation
#
# $Id: manager_reports.py 2488 2008-10-29 13:40:08Z rrosauro $
# $Revision: 2488 $
# $Date: 2008-10-29 11:40:08 -0200 (qua, 29 out 2008) $
# $Author: rrosauro $

# Python standard modules

from cStringIO import StringIO
from xml.sax.saxutils import quoteattr
from collections import defaultdict

# Our modules

from msgbus import TK_POS_GETPOSLIST, TK_SYS_NAK, TK_HV_QUERY_BY_TYPE, TK_PRN_GETSTATUS, \
    FM_STRING, FM_XML
from systools import sys_log_error, sys_log_debug
from reports import dbd, mbcontext, config


def cursor2list(cursor):
    names = cursor.get_names()
    indexes = range(cursor.cols())
    return [dict(zip(names, [row.get_entry(i) for i in indexes])) for row in cursor]


def dashboardsales():
    itemlist = []
    sales = []
    warnings = []
    podsales = []
    sos = []
    period = None

    # get a pos list
    msg = mbcontext.MB_EasySendMessage("PosController", TK_POS_GETPOSLIST)
    if msg.token == TK_SYS_NAK:
        sys_log_error("Could not retrieve PosList")
        raise Exception("Could not retrieve PosList")
    poslist = sorted(map(int, msg.data.split("\0")))
    # create database connection
    conn = None
    try:
        conn = dbd.open(mbcontext)

        # get business period
        sql = "SELECT MAX(BusinessPeriod) AS BusinessPeriod FROM PosCtrl.PosState;"
        cursor = conn.select(sql)

        try:
            period = cursor.get_row(0).get_entry("BusinessPeriod")
        except:
            pass

        if period:
            for posid in poslist:
                conn.set_dbname(str(posid))

                # top sold items
                sql = """
                    SELECT ProductName, QtySold AS Qty
                    FROM temp.PMIXView
                    WHERE BusinessPeriod = '%s' AND PartType = 0 AND Qty >0
                    ORDER BY Qty DESC LIMIT 8;""" % period

                itemlist.append(cursor2list(conn.select(sql)))

                # total sales
                sql = "SELECT PaidCount,PaidGrossAmt FROM temp.CASHView WHERE BusinessPeriod='%s' AND PosId='%s';" % (period, posid)
                sales.append(cursor2list(conn.select(sql)))

                # sales by location
                sql = "SELECT DistributionPoint as Pod,tdsum(TotalGross) AS TotalGross,tdsum(TotalNet) AS TotalNet FROM orderdb.Orders WHERE BusinessPeriod='%s' AND StateId=5 GROUP BY DistributionPoint;" % period
                podsales.append(cursor2list(conn.select(sql)))

                # speedy of service
                sql = """
                     SELECT
                      sum(otTime) as TotOTTime
                      ,sum(csTime) as TotCSTime
                      ,sum(dtTime) as TotDTTime
                      ,sum(totTime) as TotTime
                     FROM
                      (
                      SELECT
                         OrderId
                         , (
                            strftime('%%s', TotaledTime) || substr(strftime('%%f', TotaledTime), 4)
                            -
                             strftime('%%s', StartTime) || substr(strftime('%%f', StartTime), 4)
                         ) AS otTime
                         , (
                            strftime('%%s', PaidTime) || substr(strftime('%%f', PaidTime), 4)
                            -
                            strftime('%%s', TotaledTime) || substr(strftime('%%f', TotaledTime), 4)
                         ) AS csTime
                         , (
                            strftime('%%s', PaidTime) || substr(strftime('%%f', PaidTime), 4)
                            -
                            strftime('%%s', RecalledTime) || substr(strftime('%%f', RecalledTime), 4)
                         ) AS dtTime
                         , (
                            strftime('%%s', PaidTime) || substr(strftime('%%f', PaidTime), 4)
                            -
                            strftime('%%s', StartTime) || substr(strftime('%%f', StartTime), 4)
                         ) AS totTime
                      FROM
                         (
                         SELECT
                              O.OrderId AS OrderId
                              , (
                                   SELECT MIN(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=1 AND BusinessPeriod='%(period)s'
                              ) AS StartTime
                              , (
                                   SELECT MAX(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=3 AND BusinessPeriod='%(period)s'
                              ) AS TotaledTime
                              , (
                                   SELECT MAX(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=5 AND BusinessPeriod='%(period)s'
                              ) AS PaidTime
                              , (
                                   SELECT MIN(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=2 AND BusinessPeriod='%(period)s'
                              ) AS StoredTime
                              , (
                                   SELECT MAX(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=6 AND BusinessPeriod='%(period)s'
                              ) AS RecalledTime
                           FROM
                              Orderdb.Orders O
                           WHERE O.StateId=5
                        )
                     )
                     ;
                """ % {"period": period}
                sos.append(cursor2list(conn.select(sql)))

        # Initialize with no error "0"
        warnings.append({"DrawerOpenTimeout": "0", "EFTTimeout": "0", "PrinterError": "0"})
        # get a printer list
        msg = mbcontext.MB_SendMessage(mbcontext.hv_service, TK_HV_QUERY_BY_TYPE, FM_STRING, "printer")
        if msg.token == TK_SYS_NAK:
            sys_log_error("Could not retrieve PosList")
            raise Exception("Could not retrieve PosList")

        for periph in msg.data.split('\0') if msg.data else []:
            # get a status for each printer
            msg = mbcontext.MB_EasySendMessage(periph, TK_PRN_GETSTATUS)
            if msg.token == TK_SYS_NAK:
                sys_log_error("Could not retrieve Status of" % periph)
            else:
                if msg.data != '0':
                    sys_log_debug("Printer Status: %r" % msg.data)
                    warnings[0]['PrinterError'] = "1"  # Set warning on

        # consolidation top sold items
        totItemSold = defaultdict(int)
        for posItemList in itemlist:
            for item in posItemList:
                totItemSold[item['ProductName']] += int(item['Qty'] or 0)
        topItems = sorted(totItemSold.items(), key=lambda x: x[1], reverse=True)[:8]
        itemListFinal = []
        for x in range(len(topItems)):
            itemListFinal.append({"name%d" % (x + 1): topItems[x][0], "qty%d" % (x + 1): topItems[x][1]})

        # consolidation  total sales
        totSales = defaultdict(float)
        for posidsales in sales:
            for sale in posidsales:
                for key, value in sale.iteritems():
                    totSales[key] += float(sale[key] or 0)
        totsales = {'amount': "$ %.2f" % float(totSales['PaidGrossAmt']),
                    'transactions': "%d" % totSales['PaidCount'],
                    'avgTicket': "$ %.2f" % float(totSales['PaidGrossAmt'] / totSales['PaidCount'] if totSales['PaidCount'] else 0)}
        totSales = [totsales]

        # consolidation   sales by location
        totpodsales = defaultdict(lambda: {'Pod': '', 'TotalGross': 0.0, 'TotalNet': 0.0})
        for posidsales in podsales:
            for itpodsales in posidsales:
                pod = itpodsales['Pod']
                totpodsales[pod]['Pod'] = pod
                totpodsales[pod]['TotalGross'] += float(itpodsales['TotalGross'] or 0)
                totpodsales[pod]['TotalNet'] += float(itpodsales['TotalNet'] or 0)
        totpodsales = totpodsales.values()

        podListFinal = []
        podAllNames = []
        podAllValues = []
        for x in range(len(totpodsales)):
            podListFinal.append({"name%d" % (x + 1): totpodsales[x]['Pod'], "value%d" % (x + 1): totpodsales[x]['TotalGross']})
            podAllNames.append(totpodsales[x]['Pod'])
            podAllValues.append("%.2f" % totpodsales[x]['TotalGross'])
        podListFinal.append({"allNames": ','.join(podAllNames), "allValues": ','.join(podAllValues)})
        totpodsales = podListFinal

        # consolidation   speed of service (sos)
        totsos = defaultdict(int)
        for posItemList in sos:
            for item in posItemList:
                totsos['TotOTTime'] += int(item['TotOTTime'] or 0)
                totsos['TotCSTime'] += int(item['TotCSTime'] or 0)
                totsos['TotDTTime'] += int(item['TotDTTime'] or 0)
                totsos['TotTime'] += int(item['TotTime'] or 0)
        # remove the hundreadth
        totsos['TotOTTime'] = int(float(totsos['TotOTTime']) / 1000)
        totsos['TotCSTime'] = int(float(totsos['TotCSTime']) / 1000)
        totsos['TotDTTime'] = int(float(totsos['TotDTTime']) / 1000)
        totsos['TotTime'] = int(float(totsos['TotTime']) / 1000)
        totsos['allValues'] = "%s,%s,%s" % (totsos['TotOTTime'], totsos['TotCSTime'], totsos['TotDTTime'])
        totsos = [totsos]

        # create string I/O to append the report info
        report = StringIO()
        report.write("<?xml version=\"1.0\"?>\n")
        report.write('<globaldata> \n')
        report.write('\t<data jsId="global" period="Business Period: %s" poslist="POS List: %s" ' % (period, ','.join(map(str, poslist))))
        report.write('dataRefresh="%s" ' % (config.find_value("Reports.DashboardSales.DataRefresh") or 1))
        report.write(' />\n')
        for mylist, tagname in ((itemListFinal, "topitems"), (totSales, "sales"), (warnings, "warnings"), (totpodsales, "podsales"), (totsos, "sos")):
            report.write("\t<data ")
            report.write("jsId=\"%s\"" % tagname)
            for item in mylist:
                for key, value in item.iteritems():
                    report.write(" %s=%s " % (key, (quoteattr(str(value) if value is not None else ""))))
            report.write(" />\n")
        report.write("</globaldata>\n")
    finally:
        if conn:
            conn.close()

    # return the value as xml
    return (FM_XML, report.getvalue())
