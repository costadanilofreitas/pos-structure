# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\reports\reports.py
import os
import sys
import json
import time
import threading
from cStringIO import StringIO
import cfgtools
import persistence
from msgbus import TK_CMP_TERM_NOW, TK_REPORT_GENERATE, TK_SYS_NAK, TK_SYS_ACK, FM_PARAM, FM_STRING, MBException, MBEasyContext
from systools import sys_log_info, sys_log_debug, sys_log_exception, sys_log_warning
from syserrors import SE_SUCCESS, SE_USERCANCEL, SE_DBINIT, SE_CFGLOAD, SE_MB_ERR
__all__ = ('mbcontext', 'dbd', 'config', 'repinst', 'Report', 'set_language', 'gettext', 'ngettext')
_SERVICE_NAME = 'ReportsGenerator'
_SERVICE_TYPE = 'Reports'
_EXPORTED_SERVICES = '%s:%s' % (_SERVICE_NAME, _SERVICE_TYPE)
_REQUIRED_SERVICES = 'Persistence'
mbcontext = None
dbd = None
config = None
repinst = None
translations = {}
basedir = None

def set_language(language):
    global translations
    global basedir
    global config
    translations_dir = config.find_value('Reports.TranslationsDir', default=os.path.join(basedir, 'python', 'translations'))
    i18n_file = os.path.join(translations_dir, '{0}.json'.format(language))
    if not os.path.isfile(i18n_file):
        sys_log_warning('Translation file {0} not found'.format(i18n_file))
        return
    with open(i18n_file) as f:
        translations = json.loads(f.read())


def gettext(message):
    return translations.get(message, message)


def ngettext(singular, plural, n):
    if n != 1:
        return translations.get(plural, plural)
    return translations.get(singular, singular)


class Report(object):
    """
    Helper class to create reports. This simulates the StringIO API, with some additions
    """
    io = None
    TO_ASCII_TABLE = {192: 'A',
     193: 'A',
     194: 'A',
     195: 'A',
     196: 'A',
     197: 'A',
     198: 'Ae',
     199: 'C',
     200: 'E',
     201: 'E',
     202: 'E',
     203: 'E',
     204: 'I',
     205: 'I',
     206: 'I',
     207: 'I',
     208: 'Th',
     209: 'N',
     210: 'O',
     211: 'O',
     212: 'O',
     213: 'O',
     214: 'O',
     216: 'O',
     217: 'U',
     218: 'U',
     219: 'U',
     220: 'U',
     221: 'Y',
     222: 'th',
     223: 'ss',
     224: 'a',
     225: 'a',
     226: 'a',
     227: 'a',
     228: 'a',
     229: 'a',
     230: 'ae',
     231: 'c',
     232: 'e',
     233: 'e',
     234: 'e',
     235: 'e',
     236: 'i',
     237: 'i',
     238: 'i',
     239: 'i',
     240: 'th',
     241: 'n',
     242: 'o',
     243: 'o',
     244: 'o',
     245: 'o',
     246: 'o',
     248: 'o',
     249: 'u',
     250: 'u',
     251: 'u',
     252: 'u',
     253: 'y',
     254: 'th',
     255: 'y',
     161: '!',
     162: '{cent}',
     163: '{pound}',
     164: '{currency}',
     165: '{yen}',
     166: '|',
     167: '{section}',
     168: '{umlaut}',
     169: '{C}',
     170: '{^a}',
     171: '<<',
     172: '{not}',
     173: '-',
     174: '{R}',
     175: '_',
     176: '{degrees}',
     177: '{+/-}',
     178: '{^2}',
     179: '{^3}',
     180: "'",
     181: '{micro}',
     182: '{paragraph}',
     183: '*',
     184: '{cedilla}',
     185: '{^1}',
     186: '{^o}',
     187: '>>',
     188: '{1/4}',
     189: '{1/2}',
     190: '{3/4}',
     191: '?',
     215: '*',
     247: '/',
     8218: "'",
     8219: "'",
     8220: '"',
     8221: '"',
     8222: '"',
     8223: '"'}

    def __init__(self, cols = 38):
        """Create a new report helper with the given number of columns"""
        self.io = StringIO()
        self.COLS = cols

    def cut(self, s):
        """Cut 's' to the max number of cols """
        if not isinstance(s, unicode):
            s = unicode(s, 'UTF-8')
        if len(s) > self.COLS:
            return s[:self.COLS]
        return s

    def center(self, s):
        """Center 's'"""
        s = self.cut(s)
        miss = self.COLS - len(s)
        if miss == 0:
            return s
        left = miss / 2
        return ' ' * left + s

    def fmt_number(number, decimalPlaces = 2, decimalSep = '.', thousandsSep = ','):
        """Format a number"""
        sign = '-' if number < 0 else ''
        number = abs(number)
        number, dec = ('%.*f' % (decimalPlaces, number)).split('.')
        if thousandsSep:
            sepPos = len(number) - 3
            while sepPos >= 1:
                number = number[:sepPos] + thousandsSep + number[sepPos:]
                sepPos -= 3

        if decimalSep:
            number += decimalSep + dec
        return sign + number

    def ascii(self, unicrap):
        """Replace UNICODE Latin-1 characters with
        something equivalent in 7-bit ASCII. All characters in the standard
        7-bit ASCII range are preserved.
        """
        tb = self.TO_ASCII_TABLE
        if not isinstance(unicrap, unicode):
            unicrap = unicrap.decode('utf-8')
        r = [ tb.get(ord(i), i) for i in unicrap ]
        return str(''.join(r))

    def write(self, data):
        """Write data to the report"""
        if isinstance(data, unicode):
            data = data.encode('UTF-8')
        self.io.write(data)

    def writeln(self, data):
        """Write data to the report, followed by a line-feed"""
        if isinstance(data, unicode):
            data = data.encode('UTF-8')
        self.io.write(data)
        self.io.write('\n')

    def getvalue(self):
        """Get the report value as a string"""
        return self.io.getvalue()


class _ReportsImpl(object):
    """private - class used just to keep private functions on a single namespace"""

    def __init__(self):
        """private - initializes this production system"""
        self.terminating = False
        self.report_functions = {}
        self.read_config()
        service = config.find_value('Reports.ServiceName') or _SERVICE_NAME
        self.init_msgbus(service)
        self.init_persistence()
        self.import_modules()

    def main_loop(self):
        """private - main loop that handles all production commands"""
        global mbcontext
        ctx = mbcontext
        while not self.terminating:
            msg = None
            msg = ctx.MB_EasyGetMessage()
            try:
                if msg is None:
                    sys_log_info('Reports message-bus context has been finalized! Exiting')
                    return
                if msg.token == TK_CMP_TERM_NOW:
                    ctx.MB_EasyReplyMessage(msg)
                    sys_log_info('Reports received TK_CMP_TERM_NOW! Exiting')
                    return
                if msg.token == TK_REPORT_GENERATE:
                    threading.Thread(target=self.run_report, args=[msg]).start()
                else:
                    msg.token = TK_SYS_NAK
                    ctx.MB_EasyReplyMessage(msg)
            except:
                sys_log_exception('Exception trapped (and ignored) on message-bus thread!')
                if msg and not self.terminating:
                    msg.token = TK_SYS_NAK
                    ctx.MB_EasyReplyMessage(msg)

        return

    def run_report(self, msg):
        """private - handles a TK_REPORT_GENERATE message"""
        ctx = mbcontext
        try:
            if msg.format != FM_PARAM:
                raise Exception('Received report request with unknown format: %d' % msg.format)
            params = msg.data.split('\x00')
            if not params:
                raise Exception('Received report request without a report name')
            report_name = params[0]
            report_func = self.report_functions.get(report_name)
            if not report_func:
                raise Exception('Received report request for an unknown report: %s' % report_name)
            if report_func:
                start = time.time()
                params = params[1:]
                report_format = FM_STRING
                reply_token = TK_SYS_ACK
                report_data = report_func(*params)
                if isinstance(report_data, tuple):
                    report_format, report_data = report_data
                elif isinstance(report_data, dict):
                    report_format = report_data.get('format', report_format)
                    reply_token = report_data.get('token', report_format)
                    report_data = report_data.get('data', '')
                report_data = report_data.encode('UTF-8') if isinstance(report_data, unicode) else str(report_data)
                sys_log_info('TK_REPORT_GENERATE - Report [%s] generated in [%.03f secs]' % (report_name, time.time() - start))
                msg.token = reply_token
                ctx.MB_ReplyMessage(msg, report_format, data=report_data)
        except:
            sys_log_exception('Exception trapped (and ignored) on report thread!')
            if msg and not self.terminating:
                msg.token = TK_SYS_NAK
                ctx.MB_EasyReplyMessage(msg)

    def init_persistence(self):
        """private - initializes the persistence layer"""
        global dbd
        try:
            dbd = persistence.Driver()
        except:
            sys_log_exception('Error initializing reports component persistence. Terminating')
            sys.exit(SE_DBINIT)

    def read_config(self):
        """private - reads the configuration file"""
        global config
        try:
            config = cfgtools.read(os.environ['LOADERCFG'])
        except:
            sys_log_exception('Error reading configuration file. Terminating')
            sys.exit(SE_CFGLOAD)

    def init_msgbus(self, service = _SERVICE_NAME):
        """private - initializes the message-bus context"""
        global mbcontext
        try:
            mbcontext = MBEasyContext('reports')
            if SE_SUCCESS != mbcontext.MB_EasyWaitStart('%s:%s' % (service, _SERVICE_TYPE), _REQUIRED_SERVICES):
                sys_log_info("Terminating reports component after 'MB_EasyWaitStart'")
                sys.exit(SE_SUCCESS)
        except MBException:
            sys_log_exception('Message-bus error while initializing the reports component. Terminating')
            sys.exit(SE_MB_ERR)

    def import_modules(self):
        import types
        modules = ['kernel_reports'] + config.find_values('Reports.Modules')
        for name in modules:
            sys_log_debug('Loading report module: %s' % name)
            try:
                module = __import__(name)
                for symbol in (s for s in dir(module) if not s.startswith('_')):
                    obj = getattr(module, symbol)
                    if isinstance(obj, types.FunctionType) and getattr(obj, '__module__', None) == name:
                        sys_log_debug('Loading symbol: %s from %s' % (symbol, name))
                        self.report_functions[symbol] = obj

            except:
                sys_log_exception('Exception trapped while importing module %s' % name)

        return


def main():
    """ main()
    Main entry point of the component
    """
    global repinst
    global basedir
    try:
        sys_log_info('Starting reports component')
        basedir = os.path.dirname(os.path.abspath(os.environ['LOADERCFG']))
        impl = _ReportsImpl()
        repinst = impl
        language = config.find_value('Reports.Language', default='en')
        set_language(language)
        sys_log_info('Reports component has been started with success')
        impl.main_loop()
    except KeyboardInterrupt:
        sys.exit(SE_USERCANCEL)