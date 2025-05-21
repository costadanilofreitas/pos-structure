# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\reports\kernel_reports.py
from xml.etree import cElementTree as etree
from xml.sax import saxutils
from msgbus import TK_SYS_NAK, FM_STRING
from systools import sys_log_warning, sys_log_exception
from reports import dbd, mbcontext, Report

def procedure_xml(request_xml, *args):
    try:
        xml = etree.XML(request_xml)
        procedure = str(xml.get('procedure') or '')
        if not procedure:
            sys_log_warning('Received an invalid XML request: %s' % request_xml)
            return {'format': FM_STRING,
             'token': TK_SYS_NAK,
             'data': 'Invalid request'}
        instance = str(xml.get('instance') or '')
        params = {}
        if instance:
            params['instance'] = instance
        for param in xml.findall('Param'):
            name, value = param.get('name'), param.get('value')
            params[name.encode('UTF-8')] = value.encode('UTF-8')

        conn = dbd.open(mbcontext)
        if instance:
            conn.set_dbname(instance)
        cursor = conn.pselect(procedure, **params)
        quoteattr = saxutils.quoteattr
        escape = saxutils.escape
        report = Report()
        report.writeln('<?xml version="1.0" encoding="UTF-8"?>')
        report.writeln('<ReportResponse procedure=%s instance=%s>' % (quoteattr(procedure), quoteattr(instance)))
        colnames = cursor.get_names()
        indexes = range(len(colnames))
        for row in cursor:
            report.write('\t<Row')
            for i in indexes:
                val = row.get_entry(i)
                if val:
                    report.write(' %s=%s' % (escape(colnames[i]), quoteattr(val)))

            report.writeln('/>')

        report.writeln('</ReportResponse>')
        conn.close()
        return report.getvalue()
    except Exception as ex:
        sys_log_exception('Error executing procedure report')
        return {'format': FM_STRING,
         'token': TK_SYS_NAK,
         'data': unicode(ex).encode('UTF-8')}