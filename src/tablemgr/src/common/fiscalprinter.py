# -*- coding: utf-8 -*-
# Module name: fiscalprinter.py
# Module Description: Python module that contains APIs to access a fiscal printer
#
# Copyright (C) 2008-2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

import base64
from msgbus import TK_SYS_NAK, TK_FISCAL_CMD, FM_PARAM

__all__ = ("fpcmds", "fpreadout", "fpstatus", "fp",)


class fpcmds(object):

    """ class fpcmds
    This class export all commands to talk to fiscal printer
    """

    FPRN_GETSTATUS = 0x601              # gets fiscal printer status
    FPRN_INITIALIZE = 0x602             # initialize device
    FPRN_DATETIME = 0x605               # get/set date time
    FPRN_DAYLIGHTSAVINGS = 0x606        # get/set daylight savings
    FPRN_RESET = 0x607                  # reset device
    FPRN_LASTERROR = 0x608              # get last error
    FPRN_BEGINOFDAY = 0x609             # begin fiscal day
    FPRN_ENDOFDAY = 0x60a               # end fiscal day
    FPRN_XREPORT = 0x60b                # print current fiscal printer balance
    FPRN_MEMORYDUMP = 0x60c             # dump printer memory
    FPRN_NFBEGIN = 0x60d                # begin non-fiscal printing
    FPRN_NFEND = 0x60e                  # end non-fiscal printing
    FPRN_NFPRINT = 0x60f                # print non-fiscal line
    FPRN_READOUT = 0x610                # get fiscal readings (see fiscReadings enum)
    FPRN_OPERATOROPEN = 0x611           # operator open
    FPRN_OPERATORCLOSE = 0x612          # operator close
    FPRN_SALEBEGIN = 0x613              # begin fiscal sale printing
    FPRN_SALEEND = 0x614                # end fiscal sale printing
    FPRN_SALE = 0x615                   # print fiscal line item
    FPRN_SALETENDERBEGIN = 0x616        # sale tender begin
    FPRN_SALETENDER = 0x617             # sale tender
    FPRN_SALETENDEREND = 0x618          # sale tender end
    FPRN_SALECANCEL = 0x619             # cancel current sale
    FPRN_SALECANCELITEM = 0x61a         # cancel last printed line item
    FPRN_SALEITEMPRICE = 0x61b          # item price changed (discount or surcharge)
    FPRN_CANCELPREVORDER = 0x61c        # cancel previous order
    FPRN_SALETOTAL = 0x61d              # sale is totalled
    FPRN_PRINTBANKCHECK = 0x61e         # print a bank check in the fiscal printer (where it is supported)
    FPRN_AUTHENTICATE = 0x61f           # send an string for the printer authenticate a document
    FPRN_CASHIN = 0x620                 # insert cash into POS
    FPRN_CASHOUT = 0x621                # remove cash from POS (skim)
    FPRN_GETTAXLIST = 0x622             # get tax list
    FPRN_SETTAX = 0x623                 # add a tax in tax list
    FPRN_ZREPORT = 0x624                # print Z report
    FPRN_SAVEFILE = 0x625               # save file to the hard disk
    FPRN_READENCRYPTED = 0x626          # read one or more parameters from the encrypted fiscal files
    FPRN_WRITEENCRYPTED = 0x627         # overwrites a parameter in the read-write encrypted fiscal file
    FPRN_EFTSLIP = 0x628                # prints a EFT slip
    FPRN_REGISTERTENDERTYPE = 0x629     # registers a new tender type in the fiscal printer
    FPRN_READFILE = 0x62a               # read file from hard disk


class fpreadout(object):

    """ class fpreadout
    This class export all fiscal readout options
    """
    FR_GT = 0                   # current Grand Total value
    FR_DAILYGT = 1              # daily grand total
    FR_ZNUMBER = 2              # current Z report number
    FR_ZLEFT = 3                # number of Z reports still left
    FR_RECPNUMBER = 4           # current coupon number
    FR_COUPONAMT = 5            # current coupon sub-total
    FR_COUPONTAX = 6            # current coupon tax value
    FR_RATEPERCENT = 7          # percentage of the given rate
    FR_RATEAMT = 8              # daily amount for the given tax rate
    FR_RATEQTY = 9              # daily transac. qty for the given tax rate
    FR_VOIDAMT = 10             # cancel amount for the current business day
    FR_VOIDQTY = 11             # number of voided coupons in the current business day
    FR_DISCOUNTINFO = 12        # discount amount for the current business day
    FR_SURCHARGEINFO = 13       # surcharge amount for the current business day
    FR_FPSERIALNUMBER = 14      # fiscal printer serial number
    FR_BUSINESSDAY = 15         # retrieve current printer business day
    FR_PRINTERMODEL = 16        # fiscal printer model
    FR_POSSTATION = 17          # return the number of POS station configured in the fiscal printer
    FR_STORENUMBER = 18         # return the store number configured in the fiscal printer
    FR_NONFISCALQTY = 19        # return the number of non-fiscal operations done in the fiscal printer
    FR_MFADDED = 20             # Returns the date/time of recording the owner of the software and the symbol of the additional MF
    FR_PRINTERTYPE = 21         # Return the Manufacturer, Model and Type
    FR_FIRMWAREVERSION = 22     # Return the Firmware Version
    FR_USERNUMBER = 23          # Return the number of user
    FR_INFOLASTZ = 24           # Return the information about the last Z operation
    FR_ZREPORTDATE = 25         # Return the last date and time from Z report
    FR_CPTAXCNT = 26            # Return the coupon tax counter
    FR_DTLASTDOC = 27           # Return the date and time of the last printed document
    FR_NONFISCALREPQTY = 28     # Returns the non-fiscal reports counter
    FR_EFTSLIPQTY = 29          # Returns the EFT slips counter
    FR_COOSLASTZ = 30           # Returns the begin and end COOs for last z report


class fpstatus(object):

    """ class fpstatus
    This class exports all status for a fiscal-printer
    """
    FP_ERRSTATE = 0x00000001        # printer in error state (set this whenever POS cannot continue without fixing it)
    FP_ONSALE = 0x00000002          # fiscal coupon opened
    FP_ONTENDER = 0x00000004        # tender mode
    FP_DAYLIGHTON = 0x00000008      # daylight savings active
    FP_REPORTZDONE = 0x00000010     # report Z is already done for the business period
    FP_VOIDALLOWED = 0x00000020     # fiscal printer allows to cancel fiscal coupon
    FP_MEMFULL = 0x00000040         # fiscal printer memory is full - call support
    FP_LOWPAPER = 0x00000080        # low paper in fiscal printer
    FP_OUTOFPAPER = 0x00000100      # out of paper
    FP_TIMEBLOCKED = 0x00000200     # fiscal printer blocked by time (Z report is needed)
    FP_ISSQN = 0x00000400           # extra - fiscal printer ISSQN parameter has been programmed (Imposto Sobre Servico de Qualquer Natureza)
    FP_AUTOZ = 0x00000800           # extra - fiscal printer "Automatic Z" parameter has been programmed


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
        self.fpservice = "FiscalPrinter%s" % int(posid)

    def _checkErr(self, msg):
        """(private) check for TK_SYS_NAK and raise exception"""
        if msg.token == TK_SYS_NAK:
            params = msg.data.split('\0')
            if len(params) > 1:
                raise FPException(params[0], params[1])
            if len(params) == 1:
                raise FPException(params[0], "Fiscal-printer error")
            raise FPException(-1, "Fiscal-printer error")

    def printerRead(self, extra=False):
        """ fp.printerRead() -> int64
        Gets the fiscal printer current bitmap status
        @param extra: If True, extra printer status will be returned (flags related to the printer configuration)
        @return: status bit-map
        @raise FPException on fiscal-printer error
        """
        data = "%s\0%s" % (fpcmds.FPRN_GETSTATUS, "true" if extra else "false")
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return int(msg.data, 0)

    def getBusinessDay(self):
        """ fp.getBusinessDay() -> Get the Business Day opened in the Fiscal Printer
        Retrieves information from the fiscal printer
        @return: return the Business Day opened on a format "YYYYMMDD":
        If the Business Day is not opened in the Fiscal Printer, the Business Day will return as "2000-00-00"
        @raise FPException on fiscal-printer error
        """
        data = "%s\0%s" % (fpcmds.FPRN_READOUT, fpreadout.FR_BUSINESSDAY)
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data

    def printXReport(self):
        """ fp.printXReport() -> depends on cmd
        Prints an "X" report
        @return: an integer 64 bits in hexadecimal representation
        @raise FPException on fiscal-printer error
        """
        data = "%s" % (fpcmds.FPRN_XREPORT)
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
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
        data = "\0".join(
            map(str, [fpcmds.FPRN_CASHOUT, tenderId, tenderName, amount]))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)

    def cashIn(self, tenderId, tenderName, amount):
        """ fp.cashIn(tenderId, tenderName, amount)
        Performs a cash-in (initial/additional float) operation
        @param tenderId: tender id
        @param tenderName: tender name
        @param amount: cash-in amount
        @raise FPException on fiscal-printer error
        """
        data = "\0".join(
            map(str, [fpcmds.FPRN_CASHIN, tenderId, tenderName, amount]))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)

    def readOut(self, readout_option, params=[]):
        """ fp.readOut(readout_option, params=[]) -> readout value
        Performs a fiscal printer readout
        @return: the readout data
        @raise FPException on fiscal-printer error
        """
        data = "\0".join(
            map(str, [fpcmds.FPRN_READOUT, readout_option] + params))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
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
        data = "\0".join(
            map(str, [fpcmds.FPRN_SAVEFILE, file_name, file_data]))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data

    def readFile(self, file_name):
        """ fp.readFile(file_name) -> data
        Reads a file from the fiscal printer machine
        @param file_name: file name
        @raise FPException on fiscal-printer error
        @return: File data
        """
        data = "\0".join(map(str, [fpcmds.FPRN_READFILE, file_name]))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
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
        data = "\0".join(map(str, [fpcmds.FPRN_READENCRYPTED] + list(keys)))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        res = msg.data.split('\0')
        return (res if len(keys) != 1 else res[0])

    def writeEncrypted(self, key, value):
        """ fp.writeEncrypted(key, value)
        Writes a key,value to the read-write encrypted fiscal file
        @param key: key
        @param value: value
        @raise FPException on fiscal-printer error
        """
        data = "\0".join(map(str, [fpcmds.FPRN_WRITEENCRYPTED, key, value]))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)

    def printNonFiscal(self, report):
        """ printNonFiscal(report)
        Prints a non-fiscal report
        @param report: report to print
        """
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, str(fpcmds.FPRN_NFBEGIN))
        self._checkErr(msg)
        data = "%d\0%s" % (fpcmds.FPRN_NFPRINT, report)
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, str(fpcmds.FPRN_NFEND))
        self._checkErr(msg)

    def printEftSlip(self, tendername, text, twocopies=False, orderid="", tenderid="", amount=""):
        """ printEftSlip(self, tenderName, text, orderid="", tenderid="", amount="")
        Prints a EFT slip
        @param tendername: tender name
        @param text: text to print
        @param twocopies: indicates if it should print two copies
        @param orderid: order id
        @param tenderid: tender id
        @param amount: amount
        """
        data = "\0".join(map(str, [fpcmds.FPRN_EFTSLIP, orderid, tenderid,
                                   tendername, amount, text, ("true" if twocopies else "false")]))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)

    def printMFD(self, begin, end):
        """ fp.printMFD() -> depends on cmd
        Prints an "MFD" report on fiscal printer
        @raise FPException on fiscal-printer error
        """
        data = "%d\0%s\0%s\0%s\0%s\0\0\0" % (
            fpcmds.FPRN_MEMORYDUMP, "D", begin, end, "0")
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
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
        res = self.genericFiscalCMD(fpcmds.FPRN_DAYLIGHTSAVINGS, "-1")
        return (res == "1")

    def setDST(self, enabled):
        """ fp.setDST()
        Enables or disables the printer "Daylight Savings Time" (DST)
        @param enabled: If True, DST will be enabled, otherwise it will be disabled
        @raise FPException on fiscal-printer error
        """
        op = "1" if enabled else "0"
        self.genericFiscalCMD(fpcmds.FPRN_DAYLIGHTSAVINGS, op)

    def genericFiscalCMD(self, cmd, *params):
        """ genericFiscalCMD(cmd, *params)
        Executes any fiscal command
        @param cmd: Fiscal command (fpcmds.*)
        @param params: Fiscal command parameters
        @raise FPException on fiscal-printer error
        @return: the response data (depends on the command)
        """
        data = "\0".join(map(str, [cmd] + list(params)))
        msg = self._mbctxt.MB_EasySendMessage(
            self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
        self._checkErr(msg)
        return msg.data
