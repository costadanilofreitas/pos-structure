# Embedded file name: C:\Program Files\OpenSSH\gitlabci\mwapp\src\kernel\pyscripts\posot.py
from systools import sys_log_info, sys_log_debug
from msgbus import TK_SYS_NAK, TK_SYS_ACK, TK_SLCTRL_OMGR_DOSALE, TK_SLCTRL_OMGR_DOOPTION, TK_SLCTRL_OMGR_CLEAROPTION, TK_SLCTRL_OMGR_VOIDLINE, TK_SLCTRL_OMGR_VOIDORDER, TK_SLCTRL_OMGR_SPLITORDER, TK_SLCTRL_OMGR_SPLITORDERLINE, TK_SLCTRL_OMGR_LISTOPTIONS, TK_SLCTRL_OMGR_LISTOPTSOLUTIONS, TK_SLCTRL_OMGR_CHANGEMODIFIER, TK_SLCTRL_OMGR_DOMULTIOPTIONS, TK_SLCTRL_OMGR_LISTMODIFIERS, TK_SLCTRL_OMGR_CHANGEMODIFIERS, TK_SLCTRL_OMGR_CHANGEDIMENSION, TK_SLCTRL_OMGR_ORDERPICT, TK_SLCTRL_OMGR_LISTORDERS, TK_SLCTRL_OMGR_RECALLORDER, TK_SLCTRL_OMGR_CHANGEQTY, TK_SLCTRL_OMGR_STOREORDER, TK_SLCTRL_OMGR_ORDERTOTAL, TK_SLCTRL_OMGR_ORDERREOPEN, TK_SLCTRL_OMGR_DOTENDER, TK_SLCTRL_OMGR_CLEARTENDERS, TK_SLCTRL_OMGR_RESETCURRORDER, TK_SLCTRL_OMGR_SETLSTSALELINE, TK_SLCTRL_OMGR_UPDPROPERTIES, TK_SLCTRL_OMGR_CREATEORDER, TK_SLCTRL_OMGR_VOIDHISTORY, TK_SLCTRL_OMGR_PRICEOVERWRITE, TK_SLCTRL_PMGR_CUSTOMPARAM, TK_SLCTRL_PMGR_PRODUCTSBYTAGS, TK_SLCTRL_PMGR_PRODUCTDIM, TK_SLCTRL_OMGR_SETCUSTOMPROPERTY, TK_SLCTRL_OMGR_GETCUSTOMPROPERTY, TK_SLCTRL_OMGR_LIST_DISCOUNTS, TK_SLCTRL_OMGR_APPLY_DISCOUNT, TK_SLCTRL_OMGR_CLEAR_DISCOUNT, TK_SLCTRL_OMGR_MERGE_ORDERS, TK_SLCTRL_OMGR_ADDCOMMENT, TK_SLCTRL_OMGR_DELCOMMENT, TK_SLCTRL_OMGR_UPDCOMMENT, TK_SLCTRL_OMGR_SETCUSTOMPROPERTIES, TK_SLCTRL_OMGR_FRACTIONATELINE, TK_SLCTRL_OMGR_REVERTLINEFRACTION, TK_SLCTRL_OMGR_RESETORDERTENDER, FM_PARAM, MBEasyContext
from persistence import Driver as DBDriver
from xml.etree import cElementTree as etree
import json
import xml.sax.saxutils as saxutils
__all__ = ('OrderItem',
 'Order',
 'OrderTakerException',
 'ClearOptionException',
 'OrderTaker')

class OrderItem(object):

    def __init__(self, xmlline):
        """ OrderItem(xmlline) -> instance of OrderItem
        
            This class represents an order picture item. It has the attributes like 'itemId', 'partCode', 'qty', etc.
        
            @param xmlline: {xml.etree} - the xml sale line retrieved by TK_SLCTRL_OMGR_ORDERPICT token of ORDERMGR service
            @return: an OrderItem instance
        """
        self._saleLine = xmlline
        for attr, value in xmlline.items():
            setattr(self, attr, value)


class Order(object):

    def __init__(self, xmlorder):
        """ Order(xmlorder) -> instance of Order
        
            This class represents an order picture wiall its attributes retrieved by a call to OrderTaker.getOrderPicture
        
            @param xmlorder: {xml.etree} - the xml retrieved by TK_SLCTRL_OMGR_ORDERPICT token of ORDERMGR service
            @return: an Order instance
        """
        xml = etree.XML(xmlorder)
        for attr, value in xml.items():
            setattr(self, attr, value)

        self._saleLines = xml.findall('SaleLine')

    def getNumberOfItems(self):
        """ order.getNumberOfItems() -> int
        
            Gets the number of sale line elements in the order.
            @return: number of sale line elements.
        """
        return len(self._saleLines)

    def getItem(self, index):
        """ order.getItem(index) -> instance of OrderItem
        
            Returns an instance of OrderItem class from the index element of this Order instance
        
            @param index: {int} the i-th element of this Order instance to be retrieved
            @return: an OrderItem instance
        """
        return OrderItem(self._saleLines[index])


class OrderTakerException(Exception):

    def __init__(self, code, descr = ''):
        """ OrderTakerException(code, descr="") -> instance of OrderTakerException
        
            Base exception class for all OrderTaker class methods.
            @param code: {int} - the error code
            @param descr: {str} - an error description
            @return: an OrderTakerException instance
        """
        super(OrderTakerException, self).__init__('Error code: {0}; Error description: {1}'.format(code, descr))
        self._code = int(code)
        self._descr = descr

    def getErrorCode(self):
        """ e.getErrorCode() -> int
        
            Gets the code related to an error in a call to a method from the OrderTaker class instance.
            @return: the error code
        """
        return self._code

    def getErrorDescr(self):
        """ e.getErrorCode() -> str
        
            Gets any description available for the related error code.
            @return: the error code description
        """
        return self._descr


class ClearOptionException(Exception):

    def __init__(self, xmloption):
        """ ClearOptionException(xmloption) -> instance of ClearOptionException
        
            Exception class used by the OrderTaker.clearOption method when the user should decide which option to be cleared.
            @param options: {xml.etree} the xml document returned by the TK_SLCTRL_OMGR_CLEAROPTION token from ORDERMGR service.
            @return: the ClearOptionException instance
        """
        super(ClearOptionException, self).__init__('User must choose which option should be cleared')
        self._options = [ dict(option.items()) for option in xmloption.findall('Option') ]

    def getNumberOfOptions(self):
        """ e.getNumberOfOptions() -> int
        
            Returns the number of options available to be chosen.
            @return: number of options available to be chosen.
        """
        return len(self._options)

    def getOptions(self):
        """ e.getOption(index) -> [dict]
        
            Retrieves the options informations in a list of dictionaries.
            @return:  list of dictionaries.
        """
        return self._options


class OrderTaker(object):
    ONLY_OPENOPTIONS = 1
    ONLY_CLOSEDOPTIONS = 2
    ALL_OPTIONS = ONLY_CLOSEDOPTIONS | ONLY_OPENOPTIONS
    originatorId = ''
    originatorNumber = ''
    businessPeriod = ''
    podType = ''
    sessionId = ''
    additionalInfo = ''
    ordermgr = None
    productmgr = None
    blkopnotify = False

    def __init__(self, posid, mbeasycontext = None, ordermgr = None, productmgr = None):
        """ OrderTaker(posid, mbeasycontext = None) -> instance of OrderTaker
        
            This class implements the basic operations of a POS order taker. It should be used as an order taker API.
            The implementation uses the ORDERMGR service currently implemented in the SALECTRLCOMP component.
            The user must provide its own Message Bus context. If not, an internal MB context is defined for tests purposes only.
        
            @param posid: {int} The POS identification used to determine which OrderManager service instance should be used.
            @param mbeasycontext: {msgbus.MBEasyContext} The Message Bus context (easy interface) to be used for communication with the ORDERMGR service.
            @param ordermgr: {str} Optional service name to be used for order manager
            @param productmgr: {str} Optional service name to be used for product manager
            @return: an OrderTaker class instance
        """
        self._posid = posid
        self.ordermgr = ordermgr
        self.productmgr = productmgr
        self._mbctxt = mbeasycontext or MBEasyContext('posot')
        self._conn = DBDriver().open(self._mbctxt) if not self.ordermgr else None
        self.blkopnotify = False
        return

    def _getOrderMgrService(self):
        if self.ordermgr:
            return self.ordermgr
        return 'ORDERMGR%s' % self._posid

    def _getProductMgrService(self):
        if self.productmgr:
            return self.productmgr
        return 'PRODUCTMGR%s' % self._posid

    def doSale(self, posid, itemid, pricelist, qtty = 1, verifyOption = True, dimension = '', saletype = '', aftertotal = '0', applydefopts = False):
        """ ot.doSale(posid, itemid, pricelist, qtty=1, verifyOption=True, dimension="", saletype="", aftertotal="0", applydefopts=False) -> str
        
            Sell an item in the current POS order. If no order is currently open for the specified POS, a new order is created for this POS.
            It can be also used as an alternative to OrderTaker.doOption method; e.g. if the item being sold can solve an open option, it will be used for it respecting the quantity parameter.
            In this case, if all options are solved, the remaning items will be sold separatly.
        
            @param posid: {int} an POS system identification
            @param itemid: {str} the item identification to be sold
            @param pricelist: {str} the price list identification to be used for this order
            @param qtty: {int} the quantity parameter; number of items to be sold. Default is one item.
            @param verifyOption: {bool} (optional) flag indicating if if should first check for open options before adding a new sale line for the requested item.
            @param dimension: {str} (optional) a character which defines the dimension of the product to be sold
            @param saletype: {str} (optional} if set, it should be the ID of the Sale Type to be used if a new order should be created. e.g. EAT_IN, TAKE_OUT, etc...
            @param aftertotal: {str} (optional) if set, forces the sell operation even if the order was already totaled.
            @param applydefopts: {bool} (optional) if set, applies any configured default option
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         itemid,
         pricelist,
         qtty,
         '1' if verifyOption else '0',
         dimension,
         self.originatorId,
         self.originatorNumber,
         self.businessPeriod,
         self.podType,
         self.sessionId,
         self.additionalInfo,
         saletype,
         aftertotal,
         '1' if applydefopts else '0')
        sys_log_info('POSOT doSale: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_DOSALE, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        if msg.token == TK_SYS_ACK and len(params) > 2:
            return params[2]
        return ''

    def doOption(self, posid, itemid, qtty, lineNumber = '', dimension = '', applydefopts = False):
        """ ot.doOption(posid, itemid, qtty, lineNumber="", dimension="") -> dict
        
            Sell an item as an option solution. It first checks if any item in the sale has an open option that can be solved with the provided product.
            If so, that option is solved and the list of solved options is retuned.
        
            @param posid: {int} the POS identification
            @param itemid: {str} the item identification to be used to solve the option
            @param qtty: {int} the quantity of items that can be used to solve open options. The remaning items won't be added to the order.
            @param lineNumber: (str) optional parameter used to indicate a prefered line number in which the option should be used.
            @param dimension: {str} (optional) a character which defines the dimension of the product to be sold. Also, if the dimension set is a '@' character, it tells the system to look up for the nearest product in terms of dimension for a option.
            @param applydefopts: {bool} (optional) if set, applies any configured default option
            @return: a list of dictionaries with informations about the solved options.
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         itemid,
         qtty,
         lineNumber,
         dimension,
         '1' if applydefopts else '0')
        sys_log_info('POSOT doOption: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_DOOPTION, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        if len(params) > 2 and params[2]:
            xml = etree.XML(params[2])
            return [ dict(option.items()) for option in xml.findall('SaleLine') ]
        return []

    def clearOption(self, posid, salelines, qty = '', itemid = ''):
        """ ot.clearOption(posid, salelines, qty="", itemid="")
        
            Clear a previously made option.
            If more than one option is available in the requested sale line, the user must choose which item identification should be cleared.
        
            @param posid: {int} - the POS identification
            @param salelines: {str} - pipe separated list of lines to search for the item to be cleared
            @param qty: {int} - quantity of items to be cleared. If ommited, it will clear all option items.
            @param itemid: {str} - if more than one option product is presented in the requested line, the user must use this parameter to specify which option item should be cleared.
            @raise ClearOptionException: when the user should choose which option item should be cleared.
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         salelines,
         itemid,
         qty)
        sys_log_info('POSOT clearOption: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_CLEAROPTION, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        if len(params) > 2 and params[2]:
            xml = etree.XML(params[2])
            raise ClearOptionException(xml)

    def doMultipleOptions(self, posid, itemid, qty, salelines, partcodes, quantities = ''):
        """ ot.doMultipleOptions(self, posid, itemid, qty, salelines, partcodes, quantities="")
        
            Sell an item as an option solution. It first checks if any item in the sale has an open option that can be solved with the provided product.
            If so, that option is solved and the list of solved options is retuned.
        
            @param posid: {int} the POS identification
            @param itemid: {str} the item identification to be used to solve the options
            @param qty: {int} number of items to be customized with the provided set of options
            @param salelines: {str} it is pipe (|) separated list of desired line numbers to be used for look up for the qty items to be worked
            @param partcodes: {str} it is pipe (|) separated list of the desired selected options
            @param quantities: {str} (optional) if set, it is pipe (|) separated list of the desired quantities for the selected options. If not set, 1 is used as default quantity for each provided option.
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         itemid,
         qty,
         salelines,
         partcodes,
         quantities)
        sys_log_info('POSOT doMultipleOptions: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_DOMULTIOPTIONS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        if len(params) > 2 and params[2]:
            xml = etree.XML(params[2])
            return [ dict(option.items()) for option in xml.findall('SaleLine') ]
        return []

    def voidLine(self, posid, salelines):
        """ ot.voidLine(posid, salelines)
        
            Voids a list of sale lines separated by pipe '|'.
            It also can be used to void just one sale line.
        
            @param posid: {int} - the POS identification
            @param salelines: {str} - pipe-separated list of sale lines to be voided
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0', posid, salelines)
        sys_log_info('POSOT voidLine: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_VOIDLINE, FM_PARAM, reqbuf)
        if msg.token == TK_SYS_NAK:
            params = msg.data.split('\x00')
            raise OrderTakerException(params[0], params[1])

    def voidOrder(self, posid, lastpaidorder = 0, orderid = '', abandon = 0):
        """ ot.voidOrder(posid, lastpaidorder=0, orderid=0)
        
            Voids the current in-progress POS order.
        
            @param posid: {int} the POS identification
            @param lastpaidorder: {int} flag indicating if the operation should be applied to the last paid order
            @param orderid: {int} overrides previous parameters and voids that specific order
            @param abandon: {int} flag indicating if the order status must be set to ABANDONED instead of VOIDED
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         '1' if lastpaidorder else '0',
         orderid,
         '1' if abandon else '0')
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_VOIDORDER, FM_PARAM, reqbuf)
        if msg.token == TK_SYS_NAK:
            params = msg.data.split('\x00')
            raise OrderTakerException(params[0], params[1])

    def splitOrderLine(self, posid, saleline, newqty):
        """ ot.splitOrderLine(posid, saleline, newqty)
        
            Splits a sale line into two lines where the selected line will have the requested quantity of items.
        
            @param posid: {int} the POS identification
            @param saleline: {int} the order line that should be split
            @param newqty: {int} the quantity to be set to the selected order line
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         saleline,
         newqty)
        sys_log_info('POSOT splitOrderLine: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_SPLITORDERLINE, FM_PARAM, reqbuf)
        if msg.token == TK_SYS_NAK:
            params = msg.data.split('\x00')
            raise OrderTakerException(params[0], params[1])

    def splitOrder(self, posid, salelines):
        """ ot.splitOrder(posid, salelines) -> int
        
            Splits the current in-progress POS order.
            A new order is created with the selected sale lines from the original order.
            The new order is created an its state is set to stored.
        
            @param posid: {int} the POS identification
            @param saleline: {int} the order line that should be split
            @return: a dictionary with the new order attributes
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0', posid, salelines)
        sys_log_info('POSOT splitOrder: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_SPLITORDER, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        xml = etree.XML(params[2])
        order = xml.find('Order')
        return dict(order.items())

    def fractionateOrderLine(self, posid, saleline, fractionqty):
        """ ot.fractionateOrderLine(posid, saleline, fractionqty)
        
            Fractionate a sale line into two or more lines. This differs from the splitOrderLine API because it is floating point friendly.
        
            @param posid: {int} the POS identification
            @param saleline: {int} the order line that should be fractionated
            @param fractionqty: {int} the quantity to fractionate the referred line number quantity
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         saleline,
         fractionqty)
        sys_log_info('POSOT fractionateOrderLine: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_FRACTIONATELINE, FM_PARAM, reqbuf)
        if msg.token == TK_SYS_NAK:
            params = msg.data.split('\x00')
            raise OrderTakerException(params[0], params[1])

    def revertsFractionatedOrderLine(self, posid, saleline):
        """ ot.revertsFractionatedOrderLine(posid, saleline)
        
            Reverts a previously fractionated a sale line to its original ordered qty.
        
            @param posid: {int} the POS identification
            @param saleline: {int} the order line that should get reverted
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0', posid, saleline)
        sys_log_info('POSOT revertsFractionatedOrderLine: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_REVERTLINEFRACTION, FM_PARAM, reqbuf)
        if msg.token == TK_SYS_NAK:
            params = msg.data.split('\x00')
            raise OrderTakerException(params[0], params[1])

    def listOpenOptions(self, posid):
        """ ot.listOpenOptions(posid) -> list
        
            Lists the current in-progress POS order open options.
        
            @param posid: {int} the POS identification
            @return: a list of dictionaries with informations about the open options
            @raise OrderTakerException: in case of any errors.
        """
        params = (posid, self.ONLY_OPENOPTIONS, '')
        sys_log_info('POSOT listOpenOptions: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_LISTOPTIONS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        xml = etree.XML(params[2])
        return [ dict(option.items()) for option in xml.findall('SaleLine') ]

    def listOptions(self, posid, flags, salelines):
        """ ot.listOptions(posid, flags, salelines) -> list
        
            Lists the current in-progress POS order options with additional parameters.
        
            @param posid: {int} the POS identification
            @param flags: {int} one of the predefined: ONLY_OPENOPTIONS, ONLY_CLOSEDOPTIONS or ALL_OPTIONS.
            @param salelines: {str} list of sale lines to search for options
            @return: a list of dictionaries with informations about the open options
            @raise OrderTakerException: in case of any errors.
        """
        params = (posid, flags, salelines)
        sys_log_info('POSOT listOptions: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_LISTOPTIONS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        xml = etree.XML(params[2])
        return [ dict(option.items()) for option in xml.findall('SaleLine') ]

    def listOptionSolutions(self, posid, linenumber, itemid):
        """ ot.listOptionSolutions(posid, linenumber, itemid) -> list
        
            Lists the current in-progress POS order option's possible solutions with additional parameters.
        
            @param posid: {int} the POS identification
            @param linenumber: {int} the line number to query information from.
            @param itemid: {str} the options itemid (context + partcode)
            @return: a list of dictionaries with informations about the open options
            @raise OrderTakerException: in case of any errors.
        """
        params = (posid, linenumber, itemid)
        sys_log_info('POSOT listOptionSolutions: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_LISTOPTSOLUTIONS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        xml = etree.XML(params[2])
        return [ dict(option.items()) for option in xml.findall('SaleLine') ]

    def listModifiers(self, posid, saleline = '', itemid = ''):
        """ ot.listModifiers(posid, saleline="", itemid="") -> dict
        
            Lists the current in-progress POS order possible modifiers (ingredients and can-adds).
        
            @param posid: {int} the POS identification
            @param saleline: {str} (optional) if set it will query for the specific line number
            @param itemid: {str} (optional) if set it will query for the specific item id
            @return: a list of dictionaries with informations about the available modifiers
            @raise OrderTakerException: in case of any errors.
        """
        params = (posid, saleline, itemid)
        sys_log_info('POSOT listModifiers: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_LISTMODIFIERS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        if params[2]:
            xml = etree.XML(params[2])
        else:
            return None
        return [ dict(option.items()) for option in xml.findall('SaleLine') ]

    def listExtraModifiers(self, posid, saleline = '', itemid = ''):
        """ ot.listExtraModifiers(posid, saleline="", itemid="") -> dict
        
            Lists the current in-progress POS order possible modifiers (ingredients and can-adds)
            using a specific database model.
        
            @param posid: {int} the POS identification
            @param saleline: {str} (optional) if set it will query for the specific line number
            @param itemid: {str} (optional) if set it will query for the specific item id
            @return: a list of dictionaries with informations about the available modifiers
            @raise OrderTakerException: in case of any errors.
        """
        return self.get_modifiers_xml(posid, itemid)

    def changeModifier(self, posid, saleline, itemid, level, partcode, newqty):
        """ ot.changeModifier(posid, saleline, itemid, level, partcode, newqty)
        
            Apply changes to the ingrdients or can-adds of an item in the current in-progress POS order.
        
            @param posid: {int} the POS identification
            @param saleline: {str} the order sale line
            @param itemid: {str} the item identification
            @param level: {str} the modifier level in the sale line
            @param partcode: {str} the modifier product code
            @param newqty: {str} the modifier new quantity field
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         saleline,
         itemid,
         level,
         partcode,
         newqty)
        sys_log_info('POSOT changeModifier: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_CHANGEMODIFIER, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def changeModifiers(self, posid, xml):
        """ ot.changeModifiers(posid, xml)
        
            Applies many modifier changes at one time in a list of sale lines.
        
            @param posid: {int} the POS identification
            @param xml: {str} an XML describing the changes to be made in the following format:
                <Modifiers posId="1" orderId="12" lineNumbers="1,2,3" qty="2">
                    <Modifier itemId="50000.211.11"  level="2" partCode="1003" newQty="4"/>
                    <Modifier itemId="50000.211.11"  level="2" partCode="1010" newQty="2"/>
                    <Modifier itemId="50000.211.511" level="2" partCode="2501" newQty="2"/>
                </Modifiers>
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0', posid, xml)
        sys_log_info('POSOT changeModifiers: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_CHANGEMODIFIERS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def changeDimension(self, posid, salelines, operation, dimension = '', qty = '', level = '', itemid = '', partcode = ''):
        """ ot.changeDimension(posid, salelines, operation, dimension="", qty="", level="", itemId="", partCode="")
        
            Changes the dimension of an item in the current in-progress POS order.
        
            @param posid: {int} the POS identification
            @param salelines: {str} a list of sale lines to be used in the operation
            @param operation: {str} the item identification. Possible values: 0 - for down size; 1 - for up size; and, 2 - to set an specific dimension
            @param dimension: {str} (optional) if the operation is 2 and this parameter is set, the required item dimension will be changed to the one defined by this parameter
            @param qty: {str} (optional) number of lines to be (up/down)sized
            @param level: {str} (optional) indicates which level to operate
            @param itemid: {str} (optional) indicates which itemid to operate
            @param partcode: {str} (optional) indicates which product to change the dimension
            @raise OrderTakerException: in case of any errors.
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         salelines,
         operation,
         dimension,
         qty,
         level,
         itemid,
         partcode)
        sys_log_info('POSOT changeDimension: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_CHANGEDIMENSION, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def orderPicture(self, posid = '', orderid = '', nocache = False):
        """ ot.orderPicture(posid) -> instance of Order
        
            Gets a picture of the current POS order.
        
            @param posid: {int} optional - the POS identification
            @param orderid: {int} optional - the order identification
            @param nocache: {bool} optional - set to True if you want to force order manager to create a new order picture
            @return: the Order picture xml
            @raise OrderTakerException: in case of any errors.
            @note: At least one of "posid" or "orderid" must be specified
        """
        if orderid not in ('', None, 0):
            posid = ''
        params = (posid, orderid, 'true' if nocache else 'false')
        sys_log_info('POSOT orderPicture: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_ORDERPICT, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        return params[2]

    def listOrders(self, state = '', originatorid = '', podtype = '', since = '', until = '', sessionid = '', period = '', limit = '', decrescent = '', instnbr = '', inclppty = '', exclppty = '', pptyval = '', orderby = '', showTenders = False):
        """ ot.listOrders(state, originatorid="", podtype="", since="", until="", sessionid="", period="", limit="", decrescent="", instnbr="", inclppty="", exclppty="", pptyval="", orderby="")
        
            List the orders in a specified state.
            Additional parameters can be used to filter the orders list.
            The 'since'and 'until' parameters are timestamp parameters in the following format: 'YYYY-MM-DD HH:MM:SS'
        
            @param state: {str} (optional) state description as defined in the OrderState table
            @param originatorid: {str} (optional) an originator identification (e.g "POS0001")
            @param podtype: {str} (optional) distribution point
            @param since: {str} (optional) get orders created since a date/time
            @param until: {str} (optional) get orders created until a date/time
            @param sessionid: {str} (optional) get orders from the given POS session id
            @param period: {str} (optional) get orders from the given business period
            @param limit: {int} (optional) limits the number of returned orders
            @param decrescent: {bool} (optional) sort results in decrescent order
            @param instnbr: {str} (optional) instance number
            @param inclppty: {str} (optional) included order custom property
            @param exclppty: {str} (optional) excluded order custom property
            @param pptyval: {str} (optional) order custom property value
            @param orderby: {str} (optional) order results by a specific column
            @return: a list of dictionaries with the order properties
            @raise OrderTakerException: in case of errors.
        """
        decrescent = '1' if decrescent and decrescent != '0' else ''
        tender_history = '1' if showTenders is True else '0'
        params = (state,
         originatorid,
         podtype,
         since,
         until,
         sessionid,
         period,
         limit,
         inclppty,
         exclppty,
         pptyval,
         orderby,
         decrescent,
         instnbr,
         tender_history)
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_LISTORDERS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        xml = etree.XML(params[2])
        result = []
        for order in xml.findall('Order'):
            order_dict = dict(order.items())
            order_dict['custom_properties'] = {}
            for order_property in order.findall('CustomOrderProperties/OrderProperty'):
                order_dict['custom_properties'][order_property.get('key')] = order_property.get('value')

            order_dict['tender_history'] = []
            for tender in order.findall('TenderHistory/Tender'):
                order_dict['tender_history'].append(dict(tender.items()))

            result.append(order_dict)

        return result

    def storeOrder(self, posid):
        """ ot.storeOrder(posid)
        
            Put the current in-progress POS order in stored state.
        
            @param posid: {int} the POS identification
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0', posid)
        sys_log_info('POSOT storeOrder: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_STOREORDER, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def recallOrder(self, posid, orderid, sessionid = '', sourceposid = ''):
        """ ot.recallOrder(posid, orderid, sessionid="", sourceposid="")
        
            Recalls an order associating it as a in-progress order to a POS
        
            @param posid: {int} the POS identification
            @param orderid: {int} the desired order identification
            @param sessionid: {str} (optional) the session id to associate the order with
            @param sourceposid: {str} (optional) the POS that should be used as source for recall
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         orderid,
         sessionid,
         sourceposid)
        sys_log_info('POSOT recallOrder: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_RECALLORDER, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def changeLineItemQty(self, posid, linenumbers, newqty, itemid = '', consolidate = '0'):
        """ ot.changeLineItemQty(posid, linenumbers, newqty, itemid="")
        
            Changes an item quantity.
            If the quantity is set to 0 (zero) in a main item (item on level 0), the line is voided.
        
            @param posid: {int} the POS identification
            @param linenumbers: {str} list of line numbers to have its quantity field changed
            @param newqty: {int} the new quantity to be set
            @param itemid: {str} (optional) if set, the item with the specified id is searched inside the line to be modified, otherwise, the main item of the line is used.
            @param consolidate: {str} (optional) if set, do the operation consolidate the total qty of all line numbers
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         linenumbers,
         newqty,
         itemid,
         consolidate)
        sys_log_info('POSOT changeLineItemQty: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_CHANGEQTY, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def doTotal(self, posid, backup = False):
        """ ot.doTotal(posid, backup=False) -> {str}
        
            Checks if the order is completed (no open options), compute the total amount and updates the order state to TOTALED.
        
            @param posid: {int} the POS identification
            @param backup: {str} (optional) backup flag: 1-saves a backup copy of the current POS order before any order modification; 0-no backup is done.
            @return: the current total amount of the current POS order
            @raise OrderTakerException: in case of any errors
        """
        backup = 1 if backup else 0
        params = ('1' if self.blkopnotify else '0', posid, backup)
        sys_log_info('POSOT doTotal: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_ORDERTOTAL, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        if params[2]:
            order = etree.XML(params[2])
            return order.get('totalAmount')
        return ''

    def reopenOrder(self, posid, restore = False):
        """ ot.reopenOrder(posid, restore=False)
        
            Reopens a totaled order. This operations rolls back a previous call to doTotal method.
            This will let the user change the order again.
        
            @param posid: {int} the POS identification
            @param restore: {str} (optional) restore flag to indicating that the kernel should restore the previous pos order after re-open it.
            @raise OrderTakerException: in case of any errors
        """
        restore = 1 if restore else 0
        params = ('1' if self.blkopnotify else '0', posid, restore)
        sys_log_info('POSOT reopenOrder: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_ORDERREOPEN, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def resetOrderTenders(self, orderid, ordertenders = []):
        """ ot.resetOrderTenders(orderid, ordertenders) -> {dict}
        
            Performs a tender operation in the current POS order.
            If the total amount of the order is reached, the order is considered paid and its state is changed.
            If the optional parameter 'amount' is not set, it will tender the exact total amount of the order and close it.
        
            @param orderid: {int} a known tender type identification
            @param ordertenders: {list} (optional) the amount tendered. it must be a string with cents after a period character (e.g. 5.99)
            @return: a dictionary with the tender operation informations (TotalAmount, TotalTender and Change) after reset.
            @raise OrderTakerException: in case of any errors
        """
        if not ordertenders:
            return None
        else:
            REQATTR = ('tenderid', 'amount', 'tip', 'tenderdetail')
            for t in ordertenders:
                if not isinstance(t, dict):
                    raise OrderTakerException(-1, "Invalid 'ordertenders' parameter. Expects a list of dictionaries.")
                if not all([ k in REQATTR for k in t.keys() ]):
                    raise OrderTakerException(-1, "Invalid 'ordertenders' parameter. Missing required attributes.")

            ordertenders = json.dumps(ordertenders)
            params = (self._posid, orderid, ordertenders)
            sys_log_info('POSOT resetOrderTenders: {0}'.format(params))
            reqbuf = '\x00'.join((str(p) for p in params))
            msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_RESETORDERTENDER, FM_PARAM, reqbuf)
            params = msg.data.split('\x00')
            if msg.token == TK_SYS_NAK:
                raise OrderTakerException(params[0], params[1])
            order = etree.XML(params[2])
            return dict(order.items())

    def doTender(self, posid, tenderid, amount = '', donotclose = False, ordertenderid = None, tipamount = '', tenderdetail = ''):
        """ ot.doTender(posid, tenderid, amount="", donotclose=False, ordertenderid=None, tipamount="", tenderdetail="") -> {dict}
        
            Performs a tender operation in the current POS order.
            If the total amount of the order is reached, the order is considered paid and its state is changed.
            If the optional parameter 'amount' is not set, it will tender the exact total amount of the order and close it.
        
            @param posid: {int} the POS identification
            @param tenderid: {int} a known tender type identification
            @param amount: {str} (optional) the amount tendered. it must be a string with cents after a period character (e.g. 5.99)
            @param donotclose: {int} (optional) flag the indicates if the tender should close (PAID state) the order if it reacjes the total due (default is 0 - close it)
            @param ordertenderid: {int} (optional) if provided, it will try to update a previous tendered amount with the new one.
            @param tipamount: {str} (optional) the tip amount within this tender. it must be a string with cents after a period character (e.g. 5.99)
            @param tenderdetail: {str} (optional) additional tender information
            @return: a dictionary with the tender operation informations (TotalAmount, TotalTender and Change)
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         tenderid,
         amount,
         1 if donotclose else 0,
         str(ordertenderid) if ordertenderid else '',
         tipamount,
         tenderdetail)
        sys_log_info('POSOT doTender: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_DOTENDER, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        order = etree.XML(params[2])
        return dict(order.items())

    def clearTenders(self, posid, tenderid = '', ordertenderid = ''):
        """ ot.clearTenders(posid, tenderid) -> {dict}
        
            Clears all tender information in the current POS order.
        
            @param posid: {int} the POS identification
            @param tenderid: {int} Optional. If set clears only that tender id.
            @param ordertenderid: {int} Optional. If set clears only that tender operation.
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         tenderid,
         ordertenderid)
        sys_log_info('POSOT clearTenders: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_CLEARTENDERS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def resetCurrentOrder(self, posid):
        """ ot.resetCurrentOrder(posid)
        
            Reset the order id field associated with the current posid.
        
            @param posid: {int} the POS identification
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0', posid)
        sys_log_info('POSOT resetCurrentOrder: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_RESETCURRORDER, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def updateLastModifiedSaleLine(self, posid, linenumber):
        """ ot.updateLastModifiedSaleLine(posid, linenumber)
        
            Reset the current POS order last modified sale line.
        
            @param posid: {int} the POS identification
            @param linenumber: {int} the new line number to be applied
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0', posid, linenumber)
        sys_log_info('POSOT updateLastModifiedSaleLine: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_SETLSTSALELINE, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def updateOrderProperties(self, posid = '', ordertype = '', saletype = '', exemptioncode = '', podtype = '', additionalinfo = '', pricelist = '', orderSubType = '', orderid = '', tip = ''):
        """ ot.updateOrderProperties(posid="", ordertype="", saletype="", exemptioncode="", podtype="", additionalinfo="", pricelist="", orderSubType="", orderid="") -> {str}
        
            Update current POS in-progress order properties.
        
            @param posid: {str} the POS identification
            @param ordertype: {str} (optional) update the order type as defined in the OrderType table.
                   Currently acceptable values are: - SALE (the default value)
                                                    - REFUND
                                                    - WASTE
                                                    - SKIPCAR
            @param saletype: {str} (optional) update the sale type as defined in the SaleType table.
                   Currently acceptable values are: - EAT_IN (the default value)
                                                    - TAKE_OUT
            @param exemptioncode: {str} (optional) set a exemption code for the order. If a 'clear' string is provided, any code previously set will be removed.
            @param podtype: {str}  (optional) update the current distribution point of the order
            @param additionalinfo: {str} (optional) update addtional information associated with the order
            @param pricelist: {str} (optional) the new price list to  be used in the order
            @param orderSubType: {str} (optional) the order sub-type (a string that scripts may use to classify orders)
            @param orderid: {str} (optional) if provided, it will search for the order in all instances and update its properties
            @param tip: {str} (optional) if provided, it will set the tip amount for the order and will increase the Gross Amount
            @return: a XML with the order summary
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         ordertype,
         saletype,
         exemptioncode,
         podtype,
         additionalinfo,
         pricelist,
         orderSubType,
         orderid,
         tip)
        sys_log_info('POSOT updateOrderProperties: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_UPDPROPERTIES, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        return params[2]

    def createOrder(self, posid, pricelist, multiorderid = '', orderType = 'SALE', saletype = '', orderSubType = ''):
        """ ot.createOrder(posid, pricelist, multiorderid="") -> order id
        
            Creates a new (empty) order, optionally associated to
            another order, if the parameter "multiorderid" is passed.
        
            The following attributes can be set directly on this instance to control attributes of the order:
            (originatorNumber, businessPeriod, podType, sessionId, additionalInfo)
        
            Other properties may be set/modified by further calling #updateOrderProperties.
        
            @param posid: {int} the POS identification
            @param pricelist: {str} the price list identification to be used for this order
            @param multiorderid: {int} (optional) - if given an existing order id, the newly
                                 created order will be a "multi-order".
            @param ordertype: {str} (optional) update the order type as defined in the OrderType table.
                   Currently acceptable values are: - SALE (the default value)
                                                    - REFUND
                                                    - WASTE
                                                    - SKIPCAR
            @param saletype: {str} (optional) the sale type. Acceptable values are: 'EAT_IN', 'TAKE_OUT', 'DRIVE_THRU' ...
            @param orderSubType: {str} (optional) the order sub-type (a string that scripts may use to classify orders)
            @return: a dictionary with the new order attributes
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         pricelist,
         self.originatorId,
         self.originatorNumber,
         self.businessPeriod,
         self.podType,
         self.sessionId,
         self.additionalInfo,
         multiorderid,
         orderType,
         saletype,
         orderSubType)
        sys_log_info('POSOT createOrder: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_CREATEORDER, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        order = etree.XML(params[2])
        return dict(order.items())

    def voidHistory(self, posid, orderid = ''):
        """ ot.voidHistory(posid, orderid="") -> str
        
            Retrieves the POS current order void line operations history.
            This method is intended to retrieve enough information for reduction reports or business logics.
        
            @param posid: {int} the POS identification
            @param orderid: {str} (optional) the Order identification number
            @return a XML document with the void operations history.
            @raise OrderTakerException: in case of any errors
        """
        params = (posid, orderid)
        sys_log_info('POSOT voidHistory: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_VOIDHISTORY, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        return params[2]

    def priceOverwrite(self, posid, linenumber = '', unitprice = ''):
        """ ot.priceOverwrite(posid, linenumber="", unitprice="")
        
            Sets/Resets the price of an item in the current POS order.
        
            @param posid: {int} the POS identification
            @param linenumber: {str} (optional) the item's line number, if not provided, it will try to use the latest modified line of the current POS order.
            @param unitprice: {str} (optional) the item's new unit price or, if not provided, it will reset the item's price to its original.
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         posid,
         linenumber,
         unitprice)
        sys_log_info('POSOT priceOverwrite: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_PRICEOVERWRITE, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def productCustomParameters(self, pcodelist, paramid = ''):
        """ ot.productCustomParameters(self, pcodelist, paramid="") -> str
        
            Queries the product database for its custom parameters.
        
            @param pcodelist: {str} a list of products identification separated by | (pipe)
            @param paramid: {str} optional parameter id
            @return: a XML document with the product's custom parameters and tags description.
            @raise OrderTakerException: in case of any errors
        """
        params = (self._posid, pcodelist, paramid)
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getProductMgrService(), TK_SLCTRL_PMGR_CUSTOMPARAM, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        return params[2]

    def productsByTags(self, tags):
        """ ot.productsByTags(self, tags) -> str
        
            Queries the product database for products containing the given tags.
        
            @param tags: {str} pipe separated list of desired tags to match
            @return: a XML document with the product's custom parameters and tags description.
            @raise OrderTakerException: in case of any errors
        """
        params = (self._posid, tags)
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getProductMgrService(), TK_SLCTRL_PMGR_PRODUCTSBYTAGS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        return params[2]

    def productDimension(self, pcodelist):
        """ ot.productCustomParameters(self, pcodelist) -> str
        
            Queries the product database for the dimension of one or more products.
        
            @param pcodelist: {str} a list of products identification separated by | (pipe)
            @param paramid: {str} optional parameter id
            @return: a XML document with the products' dimensions
            @raise OrderTakerException: in case of any errors
        """
        params = (self._posid, pcodelist)
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getProductMgrService(), TK_SLCTRL_PMGR_PRODUCTDIM, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        return params[2]

    def setOrderCustomProperty(self, key, value = 'clear', orderid = '', linenumber = '', itemid = '', level = '', partcode = ''):
        """ ot.setOrderCustomProperty(self, key, value="clear", orderid="", linenumber="", itemid="", level="", partcode="")
        
            Sets or resets the an order (order level) or an order item (sale line level) custom property.
            If the value parameter is not set (None) the corresponding custom property will be removed.
            If the orderid parameter is defined, the custom parameter will be set for that order.
        
            @param key: {str} the custom property key
            @param value: {str} the custom property value
            @param orderid: {str} optional. if set, this order will be modified.
            @param linenumber: {str} - optional. item linenumber
            @param itemid: {str} optional. item context
            @param level: {int} optional. item level
            @param partcode: {int} optional. item product code
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         self._posid,
         orderid,
         key,
         value,
         linenumber,
         itemid,
         level,
         partcode)
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_SETCUSTOMPROPERTY, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            if value == 'clear' and params[0] == '7':
                return
            raise OrderTakerException(params[0], params[1])

    def setOrderCustomProperties(self, properties, orderid = '', linenumber = '', itemid = '', level = '', partcode = ''):
        """ ot.setOrderCustomProperties(self, properties, orderid="", linenumber="", itemid="", level="", partcode="")
        
            Sets or resets the an order (order level) or an order item (sale line level) custom properties.
            If the value parameter is not set (None) the corresponding custom property will be removed.
            If the orderid parameter is defined, the custom parameter will be set for that order.
        
            @param properties: {dict} the custom properties to set
            @param orderid: {str} optional. if set, this order will be modified.
            @param linenumber: {str} - optional. item linenumber
            @param itemid: {str} optional. item context
            @param level: {int} optional. item level
            @param partcode: {int} optional. item product code
            @raise OrderTakerException: in case of any errors
        """
        if not properties:
            return
        xml = '<Properties>'
        for key, value in properties.items():
            try:
                value = str(value)
            except:
                value = value.encode('utf-8')

            xml += '<Property key={0} value={1}/>'.format(saxutils.quoteattr(str(key)).encode('utf-8'), saxutils.quoteattr(value))

        xml += '</Properties>'
        params = ('1' if self.blkopnotify else '0',
         self._posid,
         orderid,
         xml,
         linenumber,
         itemid,
         level,
         partcode)
        sys_log_info('POSOT setOrderCustomProperties: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_SETCUSTOMPROPERTIES, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def getOrderCustomProperties(self, key = '', orderid = '', linenumber = ''):
        """ ot.getOrderCustomProperties(self, key="", orderid="", linenumber="") -> str
        
            Retrieves the available order's custom properties.
        
            @param key: {str} optional. the custom property key. if not set all the available properties will be retrieved.
            @param orderid: {str} optional. if set, this order will be searched
            @param linenumber: {str} - optional. item linenumber
            @return: a XML document with the orders' custom properties
            @raise OrderTakerException: in case of any errors
        """
        params = (self._posid,
         orderid,
         key,
         linenumber)
        sys_log_info('POSOT getOrderCustomProperties: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_GETCUSTOMPROPERTY, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        return params[2]

    def getOrderDiscounts(self, applied = True):
        """ ot.getOrderDiscounts(applied=True) -> str
        
            Retrieves the order's discounts details.
        
            @param applied: {bool} Optional flag indicating if you want to list the discounts applied on the order, if false, lists the discounts that can be applied.
            @return: a XML document with the orders' discount details
            @raise OrderTakerException: in case of any errors
        """
        applied = 1 if applied else 0
        params = (self._posid, applied)
        sys_log_info('POSOT getOrderDiscounts: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_LIST_DISCOUNTS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])
        return params[2]

    def applyDiscount(self, discountid, discountamt, linenumber = '', itemid = '', level = '', partcode = '', forcebyitem = 0):
        """ applyDiscount(discountid, discountamt, linenumber="", itemid="", level="", partcode="")
        
            Apply a discount on the order or on a sale line.
        
            @param discountid: {int} - discount id (pre-defined on discountcalc.Discounts table)
            @param discountamt: {str} - discount amount
            @param linenumber: {int} - optional - if defined, applies the discount on the given line number, otherwise on the whole sale. note that the next parameter become mandatory on this case
            @param itemid: {str} - optional - item context (only pass this parameter if linenumber is defined)
            @param level: {int} - optional - item level (only pass this parameter if linenumber is defined)
            @param partcode: {int} - optional - item product code (only pass this parameter if linenumber is defined)
            @param forcebyitem: {int} - optional - forces order discount by item (distribute total amount among all sale items) (default=0)
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         self._posid,
         discountid,
         discountamt,
         linenumber,
         itemid,
         level,
         partcode,
         forcebyitem)
        sys_log_info('POSOT applyDiscount: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_APPLY_DISCOUNT, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def clearDiscount(self, discountid = '', linenumber = '', itemid = '', level = '', partcode = ''):
        """ applyDiscount(discountid="", linenumber="", itemid="", level="", partcode="")
        
            Clear (remove) a discount on the order or on a sale line.
        
            @param discountid: {int} - optional - if defined, clears only the given discount id
            @param linenumber: {int} - optional - if defined, clears the discount on the given line number, otherwise on the whole sale. note that the next parameter become mandatory on this case
            @param itemid: {str} - optional - item context (only pass this parameter if linenumber is defined)
            @param level: {int} - optional - item level (only pass this parameter if linenumber is defined)
            @param partcode: {int} - optional - item product code (only pass this parameter if linenumber is defined)
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         self._posid,
         discountid,
         linenumber,
         itemid,
         level,
         partcode)
        sys_log_info('POSOT clearDiscount: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_CLEAR_DISCOUNT, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def mergeOrders(self, orderids):
        """ mergeOrders(orderids="")
        
            Merge the order items of a list of orders into the current POS order.
        
            @param orderids: {str} - list of order ids separated by one of the characters ";,| -".
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0', self._posid, orderids)
        sys_log_info('POSOT mergeOrders: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_MERGE_ORDERS, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def addComment(self, linenumber, itemid, level, partcode, comment):
        """ addComment(linenumber, itemid, level, partcode, comment)
        
            Adds a comment in the desired item line.
        
            @param linenumber: {str} - item linenumber (accept multiple lines separated by comma)
            @param itemid: {str} item context
            @param level: {int} item level
            @param partcode: {int} item product code
            @param comment: {str} - comment text
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         self._posid,
         linenumber,
         itemid,
         level,
         partcode,
         comment)
        sys_log_info('POSOT addComment: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_ADDCOMMENT, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def delComment(self, commentid):
        """ delComment(commentid)
        
            Deletes a comment in all lines that has that id.
        
            @param commentid: {int} - comment identification
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0', self._posid, commentid)
        sys_log_info('POSOT delComment: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_DELCOMMENT, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def updComment(self, commentid, comment):
        """ updComment(commentid)
        
            Updates a comment in all lines that has that id.
        
            @param commentid: {int} - comment identification
            @param comment: {str} - comment's new text
            @raise OrderTakerException: in case of any errors
        """
        params = ('1' if self.blkopnotify else '0',
         self._posid,
         commentid,
         comment)
        sys_log_info('POSOT updComment: {0}'.format(params))
        reqbuf = '\x00'.join((str(p) for p in params))
        msg = self._mbctxt.MB_EasySendMessage(self._getOrderMgrService(), TK_SLCTRL_OMGR_UPDCOMMENT, FM_PARAM, reqbuf)
        params = msg.data.split('\x00')
        if msg.token == TK_SYS_NAK:
            raise OrderTakerException(params[0], params[1])

    def get_is_combo(self, prod_code):
        query = "\n            SELECT CustomParamValue\n            FROM ProductCustomParams\n            WHERE ProductCode = {0} AND CustomParamId = 'COMBO';\n        ".format(prod_code)
        cursor = self._conn.select(query)
        for row in cursor:
            return str(row.get_entry(0))

        return '0'

    def get_product_customization_xml(self, pos_id, product_code):
        default_build_query = "\n            SELECT customParamValue\n            FROM ProductCustomParams\n            WHERE CustomParamId = 'defaultBuild'\n                AND (ProductCode = 900000000 + {0} or ProductCode = {0});\n        ".format(product_code)
        default_build = None
        for row in self._conn.select(default_build_query):
            default_build = row.get_entry(0).split('|')

        if default_build:
            default_build = dict(((i, default_build.count(i)) for i in default_build))
        xml_query = "\n            SELECT CustomParamValue\n            FROM ProductCustomParams\n            WHERE CustomParamId = 'MODIFIER_SET_XML'\n                AND ProductCode = (\n                    SELECT replace(Tag, 'ModifierSetID=', '')\n                    FROM ProductTags\n                    WHERE ProductCode = {0}\n                        AND Tag LIKE 'ModifierSetID=%'\n                    LIMIT 1\n                );\n        ".format(product_code)
        cursor = self._conn.select(xml_query)
        ret = None
        for row in cursor:
            ret = row.get_entry(0)

        if not ret:
            return ''
        else:
            ret = etree.fromstring(ret)
            ret.tag = 'Order'
            ret.attrib = {'posId': str(pos_id),
             'productCode': str(product_code),
             'isCombo': self.get_is_combo(product_code)}
            for elem in ret.findall('minQty'):
                elem.tag = 'minQtySet'

            for elem in ret.findall('maxQty'):
                elem.tag = 'maxQtySet'

            for elem in ret.findall('groups/modifierGroup'):
                for el in elem.findall('items/item/itemNumber'):
                    el.tag = 'productCode'

                for el in elem.findall('items/item/itemName'):
                    el.tag = 'description'

                elem.find('modifierType').tag = 'type'
                elem.find('minQty').tag = 'minQtyGroup'
                elem.find('maxQty').tag = 'maxQtyGroup'
                elem.tag = 'group'

            for elem in ret.findall('groups/group/items/item'):
                prod_code = elem.find('productCode').text
                if default_build:
                    if prod_code in default_build.keys():
                        elem.find('buildQty').text = str(default_build[prod_code])

            return etree.tostring(ret, encoding='utf-8')

    def get_modifiers_xml(self, pos_id, product_code):
        return self.get_product_customization_xml(pos_id, product_code)

    def sale_using_dict(self, pos_id, pricelist, sale_dict):
        """
        Sale products using a specific dictionary.
        Example:
        
        sale = [
            {
                "id": <prod_code>,
                "qty": <prod_qty>,
                "modifiers": [
                    (<modifier_id>, <modifier_qty>),
                    ...
                ],
                "options": [
                    {
                        "id": <option_id>,
                        "qty": <option_qty>,
                        "modifiers": [
                            (<modifier_id>, <modifier_qty>),
                            ...
                        ]
                    },
                    ...
                ]
            },
            {
                ...
            }
        ]
        """
        pos_id = pos_id or self._posid
        order_id = None
        for item in sale_dict:
            sale = self.doSale(pos_id, itemid='1.%d' % item['id'], pricelist=pricelist, qtty=item['qty'], verifyOption=False)
            sale = etree.XML(sale)
            sale_lines = sale.attrib['lineNumber']
            if not order_id:
                order_id = etree.XML(self.orderPicture(pos_id)).get('orderId')
            if item['options']:
                options_dict = {}
                for opt in item['options']:
                    if options_dict.get(opt['id']):
                        options_dict[opt['id']] += int(opt['qty'])
                    else:
                        options_dict[opt['id']] = int(opt['qty'])

                options_codes = []
                options_qty = []
                for k, v in options_dict.items():
                    options_codes.append(str(k))
                    options_qty.append(str(v))

                sys_log_debug('will register these options: %r || %r || %r || %r || %r || %r' % (pos_id,
                 item['id'],
                 item['qty'],
                 sale_lines,
                 options_codes,
                 options_qty))
                self.doMultipleOptions(pos_id, '1.%d' % item['id'], item['qty'], sale_lines, '|'.join(options_codes), '|'.join(options_qty))
            if item['modifiers']:
                modifiers_xml = '<Modifiers posId="{0}" orderId="{1}" lineNumbers="{2}" qty="{3}" itemType="{4}" level="0">\n'.format(pos_id, order_id, sale_lines, item['qty'], 'PRODUCT')
                for modifier in item['modifiers']:
                    modifiers_xml += '   <Modifier itemId="1.{0}" partCode="{1}" newQty="{2}" level="1" />\n'.format(item['id'], modifier[0], modifier[1])

                modifiers_xml += '</Modifiers>'
                self.changeModifiers(pos_id, modifiers_xml)

        return