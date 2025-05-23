# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\reports\perfmon.py
import time
import datetime
from cStringIO import StringIO
from msgbus import TK_SYS_NAK, TK_POS_GETPOSLIST, FM_XML
from systools import sys_log_error
from reports import dbd, mbcontext, config

def extract12HourFromIso(dateIso):
    hour = int(dateIso[11:13])
    if hour == 12:
        hour = '12pm'
    elif hour > 11:
        hour = '%spm' % (hour - 12)
    else:
        hour = '%sam' % hour
    return hour


def perfmon(*args):
    msg = mbcontext.MB_EasySendMessage('PosController', TK_POS_GETPOSLIST)
    if msg.token == TK_SYS_NAK:
        sys_log_error('Could not retrieve PosList')
        raise Exception('Could not retrieve PosList')
    poslist = sorted(map(int, msg.data.split('\x00')))
    conn = dbd.open(mbcontext)
    sql = 'SELECT MAX(BusinessPeriod) AS BusinessPeriod FROM PosCtrl.PosState;'
    cursor = conn.select(sql)
    period = cursor.get_row(0).get_entry('BusinessPeriod')
    conn.close()
    dataRefresh = config.find_value('Reports.PerformaceMonitor.DataRefresh') or 1
    minCfg = config.find_value('Reports.PerformaceMonitor.MinimumServiceTime') or 100
    maxCfg = config.find_value('Reports.PerformaceMonitor.MaximumServiceTime') or 125
    periods = config.find_group('Reports.PerformaceMonitor.Periods')
    if not periods:
        return
    report = StringIO()
    report.write('<?xml version="1.0"?>\n')
    report.write('<globaldata> \n')
    report.write('\t<data jsId="global" period="%s"  poslist="%s" \n' % (period, ','.join(map(str, poslist))))
    report.write('\t\tminServiceTime="%s" maxServiceTime="%s" \n' % (minCfg, maxCfg))
    report.write('\t\tdataRefresh="%s" />\n' % dataRefresh)
    for key in periods.keys:
        jsId, description, periodType, begin, end, lag, queryType, promoItem = [key.name] + key.values
        promoItemQty = 0
        productName = ''
        carQty = 0
        pseudoType = ''
        if period:
            lag = int(lag or 0)
            dtNow = datetime.datetime.now() + datetime.timedelta(0, 60 * lag)
            dataMockup = {'FC': {'Qty': 0,
                    'ServiceTime': 0},
             'DT': {'Qty': 0,
                    'ServiceTime': 0}}
            if periodType == 'part-day':
                partDay = [['0am-2am', '00:00am', '02:00am'],
                 ['2am-5am', '02:00am', '05:00am'],
                 ['5am-8am', '05:00am', '08:00am'],
                 ['Morning', '08:00am', '11:00am'],
                 ['Lunch', '11:00am', '02:00pm'],
                 ['Afternoon', '02:00pm', '5:00pm'],
                 ['Dinner', '5:00pm', '8:00pm'],
                 ['Night', '8:00pm', '11:00pm'],
                 ['11pm-12am', '11:00pm', '12:00am']]
                part = partDay[(int(dtNow.strftime('%H')) + 1) / 3]
                pseudoType = 'fixed'
                descriptionPartDay = part[0]
                begin = part[1]
                end = part[2]
            if periodType == 'dynamic':
                begin = int(begin or 0)
                end = int(end or 0)
                elapsed = (end - begin) * 60
                perBegin = '%s%s' % ((dtNow + datetime.timedelta(0, 60 * begin)).isoformat()[:16], ':00.000')
                perEnd = '%s%s' % ((dtNow + datetime.timedelta(0, 60 * end)).isoformat()[:16], ':00.000')
            elif periodType == 'complete-hour':
                begin = int(begin or 0)
                end = int(end or 0)
                elapsed = (end - begin) * 60
                perBegin = '%s%s' % ((dtNow + datetime.timedelta(0, 60 * begin)).isoformat()[:14], '00:00.000')
                perEnd = '%s%s' % ((dtNow + datetime.timedelta(0, 60 * end)).isoformat()[:14], '00:00.000')
                descriptionCompleteHour = extract12HourFromIso(perBegin) + ' - ' + extract12HourFromIso(perEnd)
            elif periodType == 'fixed' or pseudoType == 'fixed':
                splt = begin.split(':')[0]
                if splt == '0' or splt == '00':
                    st = time.strptime(begin, '%H:%M%p')
                else:
                    st = time.strptime(begin, '%I:%M%p')
                begin = datetime.datetime.strptime('%s%02d:%02d' % (dtNow.isoformat()[:11], st.tm_hour, st.tm_min), '%Y-%m-%dT%H:%M')
                st = time.strptime(end, '%I:%M%p')
                end = datetime.datetime.strptime('%s%02d:%02d' % (dtNow.isoformat()[:11], st.tm_hour, st.tm_min), '%Y-%m-%dT%H:%M')
                elapsed = (end - begin).seconds
                perBegin = begin.isoformat()
                perEnd = end.isoformat()
            elif periodType == 'today':
                perBegin = '%s%s' % (dtNow.isoformat()[:11], '00:00:00.000')
                perEnd = '%s%s' % (dtNow.isoformat()[:11], '23:59:59.999')
                elapsed = 86400
            for posid in poslist:
                conn = dbd.open(mbcontext)
                conn.set_dbname(str(posid))
                conn.transaction_start()
                conn.query('DELETE FROM temp.ReportsPeriod')
                conn.query('INSERT INTO temp.ReportsPeriod(StartPeriod,endPeriod) VALUES(%s,%s)' % (period, period))
                sqlPeriod = "strftime('%%Y-%%m-%%dT%%H:%%M:%%S',CreatedAt,'localtime') BETWEEN '%s' AND '%s'" % (perBegin, perEnd)
                lastCachedId = 0
                if queryType == 'sales':
                    for pod in dataMockup:
                        sql = '\n                        CREATE TABLE IF NOT EXISTS cache.PerfMon (\n                            PosId              INTEGER,\n                            OrderId            INTEGER,\n                            DistributionPoint  VARCHAR,\n                            BusinessPeriod     INTEGER,\n                            CreatedAt          DATETIME,\n                            MultiOrderId       INTEGER,\n                            totTime            INTEGER\n                        );\n                        '
                        conn.query(sql)
                        sql = "\n                        INSERT INTO cache.PerfMon (PosId, OrderId, DistributionPoint, BusinessPeriod, CreatedAt, MultiOrderId, totTime)\n                          SELECT\n                             %(posid)s AS PosId, OrderId, DistributionPoint, BusinessPeriod, CreatedAt, MultiOrderId,\n                             (\n                                strftime('%%s', PaidTime) || substr(strftime('%%f', PaidTime), 4)\n                                -\n                                strftime('%%s', StartTime) || substr(strftime('%%f', StartTime), 4)\n                             ) AS totTime\n                          FROM\n                             (\n                             SELECT\n                                  O.OrderId AS OrderId,\n                                  O.DistributionPoint AS DistributionPoint,\n                                  O.BusinessPeriod AS BusinessPeriod,\n                                  O.CreatedAt AS CreatedAt,\n                                  O.MultiOrderId AS MultiOrderId,\n                                  (\n                                       SELECT MIN(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=1 AND BusinessPeriod='%(period)s'\n                                  ) AS StartTime,\n                                  (\n                                       SELECT MAX(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=5 AND BusinessPeriod='%(period)s'\n                                  ) AS PaidTime\n                               FROM\n                                  Orderdb.Orders O\n                               WHERE O.StateId=5 AND O.OrderType=0 AND BusinessPeriod='%(period)s'\n                             )\n                          WHERE totTime<>0 AND (\n                              OrderId > (SELECT MAX(MaxID) FROM (SELECT MAX(OrderId) AS MaxID FROM cache.PerfMon WHERE PosId=%(posid)s UNION SELECT 0 AS MaxID))\n                          )\n                        " % {'period': period,
                         'lastCachedId': lastCachedId,
                         'posid': posid}
                        conn.query(sql)
                        sql = "\n                        SELECT\n                           COUNT() AS Qty, SUM(totTime) AS TotServiceTime\n                        FROM cache.PerfMon\n                        WHERE PosId=%(posid)s AND DistributionPoint='%(pod)s' AND %(sqlPeriod)s;\n                        " % {'posid': posid,
                         'period': period,
                         'pod': pod,
                         'sqlPeriod': sqlPeriod}
                        cursor = conn.select(sql)
                        for row in cursor:
                            dataMockup[pod]['Qty'] += int(row.get_entry('Qty') or 0)
                            dataMockup[pod]['ServiceTime'] += int(row.get_entry('TotServiceTime') or 0)

                elif queryType == 'promotion':
                    sql = 'SELECT sum(OrderedQty) AS qty FROM OrderItem WHERE PartCode = %s AND OrderId IN ( SELECT OrderId AS qty FROM cache.PerfMon WHERE BusinessPeriod=%s AND %s )' % (promoItem, period, sqlPeriod)
                    cursor = conn.select(sql)
                    for row in cursor:
                        promoItemQty += int(row.get_entry('qty') or 0)

                    sql = "Select ProductName from product WHERE ProductCode='%s'" % promoItem
                    cursor = conn.select(sql)
                    for row in cursor:
                        productName = row.get_entry('ProductName')

                elif queryType == 'cars':
                    sql = "SELECT count() AS qty FROM cache.PerfMon WHERE BusinessPeriod=%s AND DistributionPoint='DT' AND MultiOrderId is NULL AND %s" % (period, sqlPeriod)
                    cursor = conn.select(sql)
                    for row in cursor:
                        carQty += int(row.get_entry('qty') or 0)

                conn.transaction_end()
                conn.close()

        report.write('\t<data ')
        report.write('jsId="%s" ' % jsId)
        report.write('Description="%s" ' % description)
        if periodType == 'part-day':
            report.write('DescriptionPartDay="%s" ' % descriptionPartDay)
        elif periodType == 'complete-hour':
            report.write('DescriptionCompleteHour="%s" ' % descriptionCompleteHour)
        report.write('\n\t\tPeriodType="%s" \n' % periodType)
        report.write('\t\tPeriodBegin="%s" ' % perBegin)
        report.write('PeriodEnd="%s" \n' % perEnd)
        report.write('\t\tQueryType="%s" \n' % queryType)
        if queryType == 'sales':
            fcQty = dataMockup['FC']['Qty']
            dtQty = dataMockup['DT']['Qty']
            fcServTime = dataMockup['FC']['ServiceTime'] / 1000
            dtServTime = dataMockup['DT']['ServiceTime'] / 1000
            fcServTimeAvg = int(fcServTime) / int(fcQty) if fcQty else ''
            dtServTimeAvg = int(dtServTime) / int(dtQty) if dtQty else ''
            report.write('\t\tFCQty="%s" FCServTime="%s" FCServTimeAvg="%s" \n' % (fcQty, fcServTime, fcServTimeAvg))
            report.write('\t\tDTQty="%s" DTServTime="%s" DTServTimeAvg="%s" \n' % (dtQty, dtServTime, dtServTimeAvg))
            report.write('\t\tTOTQty="%s"' % (dtQty + fcQty))
        elif queryType == 'cars':
            report.write('\t\tCarQty="%s" CarHour="%s" ' % (carQty, carQty / (elapsed / 3600) if carQty else 0))
        elif queryType == 'promotion':
            report.write('\t\tPromoItem="%s" ProductName="%s" PromoQty="%s"' % (promoItem, productName, promoItemQty))
        report.write('/>\n')

    report.write('</globaldata>\n')
    return (FM_XML, report.getvalue())