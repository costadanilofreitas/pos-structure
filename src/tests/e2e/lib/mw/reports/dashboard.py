# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\reports\dashboard.py
from cStringIO import StringIO
from xml.sax.saxutils import quoteattr
from collections import defaultdict
from msgbus import TK_SYS_NAK, TK_POS_GETPOSLIST, TK_HV_QUERY_BY_TYPE, TK_PRN_GETSTATUS, FM_STRING, FM_XML
from systools import sys_log_debug, sys_log_error
from reports import dbd, mbcontext, config

def cursor2list(cursor):
    names = cursor.get_names()
    indexes = range(cursor.cols())
    return [ dict(zip(names, [ row.get_entry(i) for i in indexes ])) for row in cursor ]


def dashboardsales():
    itemlist = []
    sales = []
    warnings = []
    podsales = []
    sos = []
    period = None
    msg = mbcontext.MB_EasySendMessage('PosController', TK_POS_GETPOSLIST)
    if msg.token == TK_SYS_NAK:
        sys_log_error('Could not retrieve PosList')
        raise Exception('Could not retrieve PosList')
    poslist = sorted(map(int, msg.data.split('\x00')))
    conn = dbd.open(mbcontext)
    sql = 'SELECT MAX(BusinessPeriod) AS BusinessPeriod FROM PosCtrl.PosState;'
    cursor = conn.select(sql)
    try:
        period = cursor.get_row(0).get_entry('BusinessPeriod')
    except:
        pass

    if period:
        for posid in poslist:
            conn.set_dbname(str(posid))
            sql = "\n                SELECT ProductName, QtySold AS Qty\n                FROM temp.PMIXView\n                WHERE BusinessPeriod = '%s' AND PartType = 0 AND Qty >0\n                ORDER BY Qty DESC LIMIT 8;" % period
            itemlist.append(cursor2list(conn.select(sql)))
            sql = "SELECT PaidCount,PaidGrossAmt FROM temp.CASHView WHERE BusinessPeriod='%s' AND PosId='%s';" % (period, posid)
            sales.append(cursor2list(conn.select(sql)))
            sql = "SELECT DistributionPoint as Pod,tdsum(TotalGross) AS TotalGross,tdsum(TotalNet) AS TotalNet FROM orderdb.Orders WHERE BusinessPeriod='%s' AND StateId=5 GROUP BY DistributionPoint;" % period
            podsales.append(cursor2list(conn.select(sql)))
            sql = "\n                 SELECT\n                  sum(otTime) as TotOTTime\n                  ,sum(csTime) as TotCSTime\n                  ,sum(dtTime) as TotDTTime\n                  ,sum(totTime) as TotTime\n                 FROM\n                  (\n                  SELECT\n                     OrderId\n                     , (\n                        strftime('%%s', TotaledTime) || substr(strftime('%%f', TotaledTime), 4)\n                        -\n                         strftime('%%s', StartTime) || substr(strftime('%%f', StartTime), 4)\n                     ) AS otTime\n                     , (\n                        strftime('%%s', PaidTime) || substr(strftime('%%f', PaidTime), 4)\n                        -\n                        strftime('%%s', TotaledTime) || substr(strftime('%%f', TotaledTime), 4)\n                     ) AS csTime\n                     , (\n                        strftime('%%s', PaidTime) || substr(strftime('%%f', PaidTime), 4)\n                        -\n                        strftime('%%s', RecalledTime) || substr(strftime('%%f', RecalledTime), 4)\n                     ) AS dtTime\n                     , (\n                        strftime('%%s', PaidTime) || substr(strftime('%%f', PaidTime), 4)\n                        -\n                        strftime('%%s', StartTime) || substr(strftime('%%f', StartTime), 4)\n                     ) AS totTime\n                  FROM\n                     (\n                     SELECT\n                          O.OrderId AS OrderId\n                          , (\n                               SELECT MIN(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=1 AND BusinessPeriod='%(period)s'\n                          ) AS StartTime\n                          , (\n                               SELECT MAX(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=3 AND BusinessPeriod='%(period)s'\n                          ) AS TotaledTime\n                          , (\n                               SELECT MAX(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=5 AND BusinessPeriod='%(period)s'\n                          ) AS PaidTime\n                          , (\n                               SELECT MIN(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=2 AND BusinessPeriod='%(period)s'\n                          ) AS StoredTime\n                          , (\n                               SELECT MAX(Timestamp) FROM Orderdb.OrderStateHistory WHERE OrderId=O.OrderId AND StateId=6 AND BusinessPeriod='%(period)s'\n                          ) AS RecalledTime\n                       FROM\n                          Orderdb.Orders O\n                       WHERE O.StateId=5\n                    )\n                 )\n                 ;\n            " % {'period': period}
            sos.append(cursor2list(conn.select(sql)))

    warnings.append({'DrawerOpenTimeout': '0',
     'EFTTimeout': '0',
     'PrinterError': '0'})
    msg = mbcontext.MB_SendMessage(mbcontext.hv_service, TK_HV_QUERY_BY_TYPE, FM_STRING, 'printer')
    if msg.token == TK_SYS_NAK:
        sys_log_error('Could not retrieve PosList')
        raise Exception('Could not retrieve PosList')
    for periph in msg.data.split('\x00') if msg.data else []:
        msg = mbcontext.MB_EasySendMessage(periph, TK_PRN_GETSTATUS)
        if msg.token == TK_SYS_NAK:
            sys_log_error('Could not retrieve Status of' % periph)
        elif msg.data != '0':
            sys_log_debug('Printer Status: %r' % msg.data)
            warnings[0]['PrinterError'] = '1'

    totItemSold = defaultdict(int)
    for posItemList in itemlist:
        for item in posItemList:
            totItemSold[item['ProductName']] += int(item['Qty'] or 0)

    topItems = sorted(totItemSold.items(), key=lambda x: x[1], reverse=True)[:8]
    itemListFinal = []
    for x in range(len(topItems)):
        itemListFinal.append({'name%d' % (x + 1): topItems[x][0],
         'qty%d' % (x + 1): topItems[x][1]})

    totSales = defaultdict(float)
    for posidsales in sales:
        for sale in posidsales:
            for key, value in sale.iteritems():
                totSales[key] += float(sale[key] or 0)

    totsales = {'amount': '$ %.2f' % float(totSales['PaidGrossAmt']),
     'transactions': '%d' % totSales['PaidCount'],
     'avgTicket': '$ %.2f' % float(totSales['PaidGrossAmt'] / totSales['PaidCount'] if totSales['PaidCount'] else 0)}
    totSales = [totsales]
    totpodsales = defaultdict(lambda : {'Pod': '',
     'TotalGross': 0.0,
     'TotalNet': 0.0})
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
        podListFinal.append({'name%d' % (x + 1): totpodsales[x]['Pod'],
         'value%d' % (x + 1): totpodsales[x]['TotalGross']})
        podAllNames.append(totpodsales[x]['Pod'])
        podAllValues.append('%.2f' % totpodsales[x]['TotalGross'])

    podListFinal.append({'allNames': ','.join(podAllNames),
     'allValues': ','.join(podAllValues)})
    totpodsales = podListFinal
    totsos = defaultdict(int)
    for posItemList in sos:
        for item in posItemList:
            totsos['TotOTTime'] += int(item['TotOTTime'] or 0)
            totsos['TotCSTime'] += int(item['TotCSTime'] or 0)
            totsos['TotDTTime'] += int(item['TotDTTime'] or 0)
            totsos['TotTime'] += int(item['TotTime'] or 0)

    totsos['TotOTTime'] = int(float(totsos['TotOTTime']) / 1000)
    totsos['TotCSTime'] = int(float(totsos['TotCSTime']) / 1000)
    totsos['TotDTTime'] = int(float(totsos['TotDTTime']) / 1000)
    totsos['TotTime'] = int(float(totsos['TotTime']) / 1000)
    totsos['allValues'] = '%s,%s,%s' % (totsos['TotOTTime'], totsos['TotCSTime'], totsos['TotDTTime'])
    totsos = [totsos]
    report = StringIO()
    report.write('<?xml version="1.0"?>\n')
    report.write('<globaldata> \n')
    report.write('\t<data jsId="global" period="Business Period: %s" poslist="POS List: %s" ' % (period, ','.join(map(str, poslist))))
    report.write('dataRefresh="%s" ' % (config.find_value('Reports.DashboardSales.DataRefresh') or 1))
    report.write(' />\n')
    for mylist, tagname in ((itemListFinal, 'topitems'),
     (totSales, 'sales'),
     (warnings, 'warnings'),
     (totpodsales, 'podsales'),
     (totsos, 'sos')):
        report.write('\t<data ')
        report.write('jsId="%s"' % tagname)
        for item in mylist:
            for key, value in item.iteritems():
                report.write(' %s=%s ' % (key, quoteattr(str(value) if value is not None else '')))

        report.write(' />\n')

    report.write('</globaldata>\n')
    conn.close()
    return (FM_XML, report.getvalue())