# -*- coding: utf-8 -*-
# Module name: perfmon.py
# Module Description: Format manager reports
#
# Copyright © 2008-2009 MWneo Corporation
#
# $Id: perfmon.py 4292 2009-06-25 19:49:30Z drossi $
# $Revision: 4292 $
# $Date: 2009-06-25 16:49:30 -0300 (Thu, 25 Jun 2009) $
# $Author: drossi $

# Python standard modules

import time
import datetime
from cStringIO import StringIO

# Our modules

from msgbus import TK_POS_GETPOSLIST, TK_SYS_NAK, FM_XML
from systools import sys_log_error
from reports import dbd, mbcontext, config

# Return string with the hour in U.S.A. format. e.g. "2pm"
# Receive a string data ISO format e.g.: "2009-06-19T14:24:13.452342"


def extract12HourFromIso(dateIso):
    hour = int(dateIso[11:13])
    if (hour == 12):
        hour = "12pm"
    elif (hour > 11):
        hour = "%spm" % (hour - 12)
    else:
        hour = "%sam" % hour
    return hour

# return a xml for the performance monitor


def perfmon(*args):
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

        # get the business period, consulting the biggest businessPeriod was found in the table PosState
        sql = "SELECT MAX(BusinessPeriod) AS BusinessPeriod FROM PosCtrl.PosState;"
        cursor = conn.select(sql)
        period = cursor.get_row(0).get_entry("BusinessPeriod")
    finally:
        if conn:
            conn.close()
    # --------------------
    # get configuration bundles
    # --------------------
    dataRefresh = config.find_value("Reports.PerformaceMonitor.DataRefresh") or 1
    minCfg = config.find_value("Reports.PerformaceMonitor.MinimumServiceTime") or 100
    maxCfg = config.find_value("Reports.PerformaceMonitor.MaximumServiceTime") or 125
    # get all Periods defined on bundles
    periods = config.find_group("Reports.PerformaceMonitor.Periods")
    if not periods:
        return

    # --------------------
    # Starting XML content
    # --------------------
    # create string I/O to append the report info
    report = StringIO()
    report.write("<?xml version=\"1.0\"?>\n")
    report.write('<globaldata> \n')
    report.write('\t<data jsId="global" period="%s"  poslist="%s" \n' % (period, ','.join(map(str, poslist))))
    report.write('\t\tminServiceTime="%s" maxServiceTime="%s" \n' % (minCfg, maxCfg))
    report.write('\t\tdataRefresh="%s" />\n' % dataRefresh)

    # --------------------
    # standardization of data to query database
    # --------------------
    # loop in a periods to be found on configuration bundles
    for key in periods.keys:
        jsId, description, periodType, begin, end, lag, queryType, promoItem = [key.name] + key.values
        promoItemQty = 0     # to store quantity of items promotions
        productName = ""
        carQty = 0
        pseudoType = ""
        if period:
            lag = int(lag or 0)  # ensure a valid lag
            dtNow = datetime.datetime.now() + datetime.timedelta(0, 60 * lag)  # set dtNow to (now plus lag)
            dataMockup = {"FC": {'Qty': 0, 'ServiceTime': 0},
                          "DT": {'Qty': 0, 'ServiceTime': 0}}

            if periodType == "part-day":
                # part-day table
                partDay = [["0am-2am", "00:00am", "02:00am"],
                           ["2am-5am", "02:00am", "05:00am"],
                           ["5am-8am", "05:00am", "08:00am"],
                           ["Morning", "08:00am", "11:00am"],
                           ["Lunch", "11:00am", "02:00pm"],
                           ["Afternoon", "02:00pm", "5:00pm"],
                           ["Dinner", "5:00pm", "8:00pm"],
                           ["Night", "8:00pm", "11:00pm"],
                           ["11pm-12am", "11:00pm", "12:00am"]]
                part = partDay[(int(dtNow.strftime("%H")) + 1) / 3]
                pseudoType = "fixed"  # for facility
                descriptionPartDay = part[0]
                begin = part[1]
                end = part[2]

            if periodType == "dynamic":
                begin = int(begin or 0)
                end = int(end or 0)
                elapsed = (end - begin) * 60    # in Seconds. maximum one day
                perBegin = "%s%s" % ((dtNow + datetime.timedelta(0, 60 * begin)).isoformat()[:16], ":00.000")
                perEnd = "%s%s" % ((dtNow + datetime.timedelta(0, 60 * end)).isoformat()[:16], ":00.000")
            elif periodType == "complete-hour":
                begin = int(begin or 0)
                end = int(end or 0)
                elapsed = (end - begin) * 60    # in Seconds. maximum one day
                perBegin = "%s%s" % ((dtNow + datetime.timedelta(0, 60 * begin)).isoformat()[:14], "00:00.000")
                perEnd = "%s%s" % ((dtNow + datetime.timedelta(0, 60 * end)).isoformat()[:14], "00:00.000")
                descriptionCompleteHour = extract12HourFromIso(perBegin) + " - " + extract12HourFromIso(perEnd)
            elif periodType == "fixed" or pseudoType == "fixed":
                splt = begin.split(':')[0]
                if splt == "0" or splt == "00":
                    st = time.strptime(begin, "%H:%M%p")
                else:
                    st = time.strptime(begin, "%I:%M%p")
                begin = datetime.datetime.strptime("%s%02d:%02d" % (dtNow.isoformat()[:11], st.tm_hour, st.tm_min), "%Y-%m-%dT%H:%M")
                st = time.strptime(end, "%I:%M%p")
                end = datetime.datetime.strptime("%s%02d:%02d" % (dtNow.isoformat()[:11], st.tm_hour, st.tm_min), "%Y-%m-%dT%H:%M")
                elapsed = (end - begin).seconds   # in Seconds. maximum one day
                perBegin = begin.isoformat()
                perEnd = end.isoformat()
            elif periodType == "today":
                perBegin = "%s%s" % (dtNow.isoformat()[:11], "00:00:00.000")
                perEnd = "%s%s" % (dtNow.isoformat()[:11], "23:59:59.999")
                elapsed = 24 * 3600

            # --------------------
            # loop for all instances querying the current period
            # --------------------
            for posid in poslist:
                conn = None
                try:
                    conn = dbd.open(mbcontext, dbname=str(posid))
                    conn.transaction_start()
                    # set interval period in the temporary table report
                    conn.query("DELETE FROM temp.ReportsPeriod")
                    conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,endPeriod) VALUES(%s,%s)" % (period, period))
                    # SQL part with interval
                    sqlPeriod = "strftime('%%Y-%%m-%%dT%%H:%%M:%%S',CreatedAt,'localtime') BETWEEN '%s' AND '%s'" % (perBegin, perEnd)
                    lastCachedId = 0
                    # consulting Sales for FC and DT
                    if (queryType == "sales"):
                        for pod in dataMockup:
                            sql = """
                            CREATE TABLE IF NOT EXISTS cache.PerfMon (
                                PosId              INTEGER,
                                OrderId            INTEGER,
                                DistributionPoint  VARCHAR,
                                BusinessPeriod     INTEGER,
                                CreatedAt          DATETIME,
                                MultiOrderId       INTEGER,
                                totTime            INTEGER
                            );
                            """
                            conn.query(sql)
                            sql = """
                            INSERT INTO cache.PerfMon (PosId, OrderId, DistributionPoint, BusinessPeriod, CreatedAt, MultiOrderId, totTime)
                              SELECT
                                 %(posid)s AS PosId, OrderId, DistributionPoint, BusinessPeriod, CreatedAt, MultiOrderId,
                                 (
                                    strftime('%%s', PaidTime) || substr(strftime('%%f', PaidTime), 4)
                                    -
                                    strftime('%%s', StartTime) || substr(strftime('%%f', StartTime), 4)
                                 ) AS totTime
                              FROM
                                 (
                                 SELECT
                                      O.OrderId AS OrderId,
                                      O.DistributionPoint AS DistributionPoint,
                                      O.BusinessPeriod AS BusinessPeriod,
                                      O.CreatedAt AS CreatedAt,
                                      O.MultiOrderId AS MultiOrderId,
                                      (
                                           SELECT MIN(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=1 AND BusinessPeriod='%(period)s'
                                      ) AS StartTime,
                                      (
                                           SELECT MAX(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=5 AND BusinessPeriod='%(period)s'
                                      ) AS PaidTime
                                   FROM
                                      Orderdb.Orders O
                                   WHERE O.StateId=5 AND O.OrderType=0 AND BusinessPeriod='%(period)s'
                                 )
                              WHERE totTime<>0 AND (
                                  OrderId > (SELECT MAX(MaxID) FROM (SELECT MAX(OrderId) AS MaxID FROM cache.PerfMon WHERE PosId=%(posid)s UNION SELECT 0 AS MaxID))
                              )
                            """ % {"period": period, "lastCachedId": lastCachedId, "posid": posid}
                            conn.query(sql)
                            sql = """
                            SELECT
                               COUNT() AS Qty, SUM(totTime) AS TotServiceTime
                            FROM cache.PerfMon
                            WHERE PosId=%(posid)s AND DistributionPoint='%(pod)s' AND %(sqlPeriod)s;
                            """ % {"posid": posid, "period": period, "pod": pod, "sqlPeriod": sqlPeriod}
                            cursor = conn.select(sql)
                            for row in cursor:
                                dataMockup[pod]['Qty'] += int(row.get_entry("Qty") or 0)
                                dataMockup[pod]['ServiceTime'] += int(row.get_entry("TotServiceTime") or 0)
                    # Consult Promotion
                    elif (queryType == "promotion"):
                        sql = "SELECT sum(OrderedQty) AS qty FROM OrderItem WHERE PartCode = %s AND OrderId IN ( SELECT OrderId AS qty FROM cache.PerfMon WHERE BusinessPeriod=%s AND %s )" % (promoItem, period, sqlPeriod)
                        cursor = conn.select(sql)
                        for row in cursor:
                            promoItemQty += int(row.get_entry("qty") or 0)
                        # get Product Name
                        sql = "Select ProductName from product WHERE ProductCode='%s'" % promoItem
                        cursor = conn.select(sql)
                        for row in cursor:
                            productName = row.get_entry("ProductName")
                    # Consult cars
                    elif (queryType == "cars"):
                        sql = "SELECT count() AS qty FROM cache.PerfMon WHERE BusinessPeriod=%s AND DistributionPoint='DT' AND MultiOrderId is NULL AND %s" % (period, sqlPeriod)
                        cursor = conn.select(sql)
                        for row in cursor:
                            carQty += int(row.get_entry("qty") or 0)

                finally:
                    if conn:
                        conn.close()

        # --------------------
        # Write data of current period in the XML
        # --------------------
        report.write("\t<data ")
        report.write("jsId=\"%s\" " % jsId)
        report.write("Description=\"%s\" " % description)
        if periodType == "part-day":
            report.write("DescriptionPartDay=\"%s\" " % descriptionPartDay)
        elif periodType == "complete-hour":
            report.write("DescriptionCompleteHour=\"%s\" " % descriptionCompleteHour)

        report.write("\n\t\tPeriodType=\"%s\" \n" % periodType)
        report.write("\t\tPeriodBegin=\"%s\" " % perBegin)
        report.write("PeriodEnd=\"%s\" \n" % perEnd)
        report.write("\t\tQueryType=\"%s\" \n" % queryType)
        if (queryType == "sales"):
            fcQty = dataMockup["FC"]["Qty"]
            dtQty = dataMockup["DT"]["Qty"]
            fcServTime = dataMockup["FC"]["ServiceTime"] / 1000
            dtServTime = dataMockup["DT"]["ServiceTime"] / 1000
            fcServTimeAvg = int(fcServTime) / int(fcQty) if fcQty else ""
            dtServTimeAvg = int(dtServTime) / int(dtQty) if dtQty else ""
            report.write("\t\tFCQty=\"%s\" FCServTime=\"%s\" FCServTimeAvg=\"%s\" \n" % (fcQty, fcServTime, fcServTimeAvg))
            report.write("\t\tDTQty=\"%s\" DTServTime=\"%s\" DTServTimeAvg=\"%s\" \n" % (dtQty, dtServTime, dtServTimeAvg))
            report.write("\t\tTOTQty=\"%s\"" % (dtQty + fcQty))
        elif (queryType == "cars"):
            report.write("\t\tCarQty=\"%s\" CarHour=\"%s\" " % (carQty, carQty / (elapsed / 3600) if carQty else 0))
        elif (queryType == "promotion"):
            report.write("\t\tPromoItem=\"%s\" ProductName=\"%s\" PromoQty=\"%s\"" % (promoItem, productName, promoItemQty))

        # End xml tag
        report.write("/>\n")

    report.write("</globaldata>\n")
    # return the value as xml
    return (FM_XML, report.getvalue())
