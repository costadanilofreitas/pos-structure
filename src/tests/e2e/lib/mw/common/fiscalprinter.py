# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\wrappers\python\fiscalprinter.py
import base64
from msgbus import TK_SYS_NAK, TK_FISCAL_CMD, FM_PARAM
__all__ = ('fpcmds', 'fpreadout', 'fpstatus', 'fp')

class fpcmds(object):
    """ class fpcmds
    This class export all commands to talk to fiscal printer
    """
    FPRN_GETSTATUS = 1537
    FPRN_INITIALIZE = 1538
    FPRN_DATETIME = 1541
    FPRN_DAYLIGHTSAVINGS = 1542
    FPRN_RESET = 1543
    FPRN_LASTERROR = 1544
    FPRN_BEGINOFDAY = 1545
    FPRN_ENDOFDAY = 1546
    FPRN_XREPORT = 1547
    FPRN_MEMORYDUMP = 1548
    FPRN_NFBEGIN = 1549
    FPRN_NFEND = 1550
    FPRN_NFPRINT = 1551
    FPRN_READOUT = 1552
    FPRN_OPERATOROPEN = 1553
    FPRN_OPERATORCLOSE = 1554
    FPRN_SALEBEGIN = 1555
    FPRN_SALEEND = 1556
    FPRN_SALE = 1557
    FPRN_SALETENDERBEGIN = 1558
    FPRN_SALETENDER = 1559
    FPRN_SALETENDEREND = 1560
    FPRN_SALECANCEL = 1561
    FPRN_SALECANCELITEM = 1562
    FPRN_SALEITEMPRICE = 1563
    FPRN_CANCELPREVORDER = 1564
    FPRN_SALETOTAL = 1565
    FPRN_PRINTBANKCHECK = 1566
    FPRN_AUTHENTICATE = 1567
    FPRN_CASHIN = 1568
    FPRN_CASHOUT = 1569
    FPRN_GETTAXLIST = 1570
    FPRN_SETTAX = 1571
    FPRN_ZREPORT = 1572
    FPRN_SAVEFILE = 1573
    FPRN_READENCRYPTED = 1574
    FPRN_WRITEENCRYPTED = 1575
    FPRN_EFTSLIP = 1576
    FPRN_REGISTERTENDERTYPE = 1577
    FPRN_READFILE = 1578


class fpreadout(object):
    """ class fpreadout
    This class export all fiscal readout options
    """
    FR_GT = 0
    FR_DAILYGT = 1
    FR_ZNUMBER = 2
    FR_ZLEFT = 3
    FR_RECPNUMBER = 4
    FR_COUPONAMT = 5
    FR_COUPONTAX = 6
    FR_RATEPERCENT = 7
    FR_RATEAMT = 8
    FR_RATEQTY = 9
    FR_VOIDAMT = 10
    FR_VOIDQTY = 11
    FR_DISCOUNTINFO = 12
    FR_SURCHARGEINFO = 13
    FR_FPSERIALNUMBER = 14
    FR_BUSINESSDAY = 15
    FR_PRINTERMODEL = 16
    FR_POSSTATION = 17
    FR_STORENUMBER = 18
    FR_NONFISCALQTY = 19
    FR_MFADDED = 20
    FR_PRINTERTYPE = 21
    FR_FIRMWAREVERSION = 22
    FR_USERNUMBER = 23
    FR_INFOLASTZ = 24
    FR_ZREPORTDATE = 25
    FR_CPTAXCNT = 26
    FR_DTLASTDOC = 27
    FR_NONFISCALREPQTY = 28
    FR_EFTSLIPQTY = 29
    FR_COOSLASTZ = 30


class fpstatus(object):
    """ class fpstatus
    This class exports all status for a fiscal-printer
    """
    FP_ERRSTATE = 1
    FP_ONSALE = 2
    FP_ONTENDER = 4
    FP_DAYLIGHTON = 8
    FP_REPORTZDONE = 16
    FP_VOIDALLOWED = 32
    FP_MEMFULL = 64
    FP_LOWPAPER = 128
    FP_OUTOFPAPER = 256
    FP_TIMEBLOCKED = 512
    FP_ISSQN = 1024
    FP_AUTOZ = 2048


class FPException(BaseException):
    """Exception raised on fiscal-printer errors"""

    def __init__(self, errcode, errmsg):
        BaseException.__init__(self, errmsg)
        self.errcode = errcode
        self.errmsg = errmsg


class fp(object):
    """ class fp
    Contains APIs to access the fiscal-printer of a POS.
    """

    def __init__(self, posid, mb_easycontext):
        """ fp(posid) -> instance of Fiscal Printer Class
        This class export methods to direct exchange information with the fiscal printer attached with the given posid
        @param posid: {int} - pos id number
        @param mb_easycontext: {MBEasyContext} - Easy message-bus context
        @return: fp instance
        """
        self._posid = posid
        self._mbctxt = mb_easycontext
        self.fpservice = 'FiscalPrinter%s' % int(posid)

    def _checkErr(self, msg):
        """(private) check for TK_SYS_NAK and raise exception"""
        if msg.token == TK_SYS_NAK:
            params = msg.data.split('\x00')
            if len(params) > 1:
                raise FPException(params[0], params[1])
            if len(params) == 1:
                raise FPException(params[0], 'Fiscal-printer error')
            raise FPException(-1, 'Fiscal-printer error')

    def printerRead(self, extra = False):
        """ fp.printerRead() -> int64
        Gets the fiscal printer current bitmap status
        @param extra: If True, extra printer status will be returned (flags related to the printer configuration)
        @return: status bit-map
        @raise FPException on fiscal-printer error
        """
        data = '%s\x00%s' % (fpcmds.FPRN_GETSTATUS, 'true' if extra else 'false')
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return int(msg.data, 0)

    def getBusinessDay(self):
        """ fp.getBusinessDay() -> Get the Business Day opened in the Fiscal Printer
        Retrieves information from the fiscal printer
        @return: return the Business Day opened on a format "YYYYMMDD":
        If the Business Day is not opened in the Fiscal Printer, the Business Day will return as "2000-00-00"
        @raise FPException on fiscal-printer error
        """
        data = '%s\x00%s' % (fpcmds.FPRN_READOUT, fpreadout.FR_BUSINESSDAY)
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data

    def printXReport(self):
        """ fp.printXReport() -> depends on cmd
        Prints an "X" report
        @return: an integer 64 bits in hexadecimal representation
        @raise FPException on fiscal-printer error
        """
        data = '%s' % fpcmds.FPRN_XREPORT
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data

    def cashOut(self, tenderId, tenderName, amount):
        """ fp.cashOut(tenderId, tenderName, amount)
        Performs a cash-out (SKIM) operation
        @param tenderId: tender id
        @param tenderName: tender name
        @param amount: cash-out amount
        @raise FPException on fiscal-printer error
        """
        data = '\x00'.join(map(str, [fpcmds.FPRN_CASHOUT,
         tenderId,
         tenderName,
         amount]))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)

    def cashIn(self, tenderId, tenderName, amount):
        """ fp.cashIn(tenderId, tenderName, amount)
        Performs a cash-in (initial/additional float) operation
        @param tenderId: tender id
        @param tenderName: tender name
        @param amount: cash-in amount
        @raise FPException on fiscal-printer error
        """
        data = '\x00'.join(map(str, [fpcmds.FPRN_CASHIN,
         tenderId,
         tenderName,
         amount]))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)

    def readOut(self, readout_option, params = []):
        """ fp.readOut(readout_option, params=[]) -> readout value
        Performs a fiscal printer readout
        @return: the readout data
        @raise FPException on fiscal-printer error
        """
        data = '\x00'.join(map(str, [fpcmds.FPRN_READOUT, readout_option] + params))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data

    def saveFile(self, file_name, file_data):
        """ fp.saveFile(file_name, file_data)
        Saves a file in the fiscal printer machine
        @param file_name: file name
        @param file_data: file data
        @raise FPException on fiscal-printer error
        @return: Full and absolute path of the saved file
        """
        file_data = base64.b64encode(file_data)
        data = '\x00'.join(map(str, [fpcmds.FPRN_SAVEFILE, file_name, file_data]))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data

    def readFile(self, file_name):
        """ fp.readFile(file_name) -> data
        Reads a file from the fiscal printer machine
        @param file_name: file name
        @raise FPException on fiscal-printer error
        @return: File data
        """
        data = '\x00'.join(map(str, [fpcmds.FPRN_READFILE, file_name]))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data

    def readEncrypted(self, *keys):
        """ fp.readEncrypted(*keys) -> list or str
        Reads a list of keys from the encrypted fiscal files
        @param keys: keys to read
        @return: The requested value (empty if the key was not found). A list will be returned if more than
                 one value is requested.
        @raise FPException on fiscal-printer error
        """
        data = '\x00'.join(map(str, [fpcmds.FPRN_READENCRYPTED] + list(keys)))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        res = msg.data.split('\x00')
        if len(keys) != 1:
            return res
        return res[0]

    def writeEncrypted(self, key, value):
        """ fp.writeEncrypted(key, value)
        Writes a key,value to the read-write encrypted fiscal file
        @param key: key
        @param value: value
        @raise FPException on fiscal-printer error
        """
        data = '\x00'.join(map(str, [fpcmds.FPRN_WRITEENCRYPTED, key, value]))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)

    def printNonFiscal(self, report):
        """ printNonFiscal(report)
        Prints a non-fiscal report
        @param report: report to print
        """
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, str(fpcmds.FPRN_NFBEGIN))
        self._checkErr(msg)
        data = '%d\x00%s' % (fpcmds.FPRN_NFPRINT, report)
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, str(fpcmds.FPRN_NFEND))
        self._checkErr(msg)

    def printEftSlip(self, tendername, text, twocopies = False, orderid = '', tenderid = '', amount = ''):
        """ printEftSlip(self, tenderName, text, orderid="", tenderid="", amount="")
        Prints a EFT slip
        @param tendername: tender name
        @param text: text to print
        @param twocopies: indicates if it should print two copies
        @param orderid: order id
        @param tenderid: tender id
        @param amount: amount
        """
        data = '\x00'.join(map(str, [fpcmds.FPRN_EFTSLIP,
         orderid,
         tenderid,
         tendername,
         amount,
         text,
         'true' if twocopies else 'false']))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)

    def printMFD(self, begin, end):
        """ fp.printMFD() -> depends on cmd
        Prints an "MFD" report on fiscal printer
        @raise FPException on fiscal-printer error
        """
        data = '%d\x00%s\x00%s\x00%s\x00%s\x00\x00\x00' % (fpcmds.FPRN_MEMORYDUMP,
         'D',
         begin,
         end,
         '0')
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data

    def getPrinterTimestamp(self):
        """ fp.getPrinterTimestamp()
        Retrieves the fiscal printer date and time
        @return: The printer date and time in the ISO8601 format (YYYY-MM-ddThh:mm:ss)
        @raise FPException on fiscal-printer error
        """
        return self.genericFiscalCMD(fpcmds.FPRN_DATETIME)

    def isDSTenabled(self):
        """ fp.isDSTenabled() -> bool
        Checks if the "Daylight Savings Time" (DST) is currently enabled in the fiscal printer.
        @return: True if DST is enabled, False otherwise
        @raise FPException on fiscal-printer error
        """
        res = self.genericFiscalCMD(fpcmds.FPRN_DAYLIGHTSAVINGS, '-1')
        return res == '1'

    def setDST(self, enabled):
        """ fp.setDST()
        Enables or disables the printer "Daylight Savings Time" (DST)
        @param enabled: If True, DST will be enabled, otherwise it will be disabled
        @raise FPException on fiscal-printer error
        """
        op = '1' if enabled else '0'
        self.genericFiscalCMD(fpcmds.FPRN_DAYLIGHTSAVINGS, op)

    def genericFiscalCMD(self, cmd, *params):
        """ genericFiscalCMD(cmd, *params)
        Executes any fiscal command
        @param cmd: Fiscal command (fpcmds.*)
        @param params: Fiscal command parameters
        @raise FPException on fiscal-printer error
        @return: the response data (depends on the command)
        """
        data = '\x00'.join(map(str, [cmd] + list(params)))
        msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data