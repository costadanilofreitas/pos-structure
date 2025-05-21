import json
import inspect


# standard modules
from pyscripts import mbcontext
from posot import OrderTaker, OrderTakerException
from sysactions import send_message, get_podtype, get_operator_session, get_business_period
from systools import sys_log_info
from msgbus import TK_SYS_NAK, TK_CMP_MESSAGE, FM_STRING, FM_PARAM


# exports
__all__ = ("TableService", "TableServiceException", "get_posts")

default_timeout = 90*1000*1000


class TableServiceException(OrderTakerException):
    def __init__(self, errmsg=""):
        """Base exception class for all TableService class methods.
           @param errmsg: {str} - an error description
           @return: an TableServiceException instance
        """
        super(TableServiceException, self).__init__("-1", "Table service error: {0}".format(errmsg))


class TableService(OrderTaker):
    def __init__(self, posid, mbeasycontext=None, ordermgr=None, productmgr=None, tablemgr=None):
        """Table Service API class.
           @param errmsg: {str} - an error description
           @return: an TableServiceException instance
        """
        super(TableService, self).__init__(posid, mbeasycontext, ordermgr, productmgr)
        self.tablemgr = tablemgr or "TABLEMGR"

    def listTables(self, userid=None, tableid=None, withprops=None):
        """Retrieves the list of available seats and the current related service, if any.
           @param userId    (optional) Retrieves only tables from provided userId
           @param tableId   (optional) Retrieves information only from provided tableId
           @param withProps (optional) Retrieves properties information
           @return list of dict objects.
        """
        params = ("LIST_TABLES", self._posid, userid or "", tableid or "", withprops or "")
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return json.loads(msg.data)

    def storePicture(self, forceupdate=False):
        """Retrieves the XML document wich current tables layout and availability.
           @param forceupdate  (optional) Forces a STORE_MODIFIED event to publish the current store status
           @return Store picture XML document.
        """
        params = ("STORE_PICTURE", self._posid, (1 if forceupdate else 0))
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def setCustomProperty(self, propkey, propvalue=None, tableid=None, serviceid=None):
        """Sets a custom properties associated with a table or a service.
           @param propKey        Property key
           @param propValue      (optional) Property value. If ommited, removes the key.
           @param tableId        (optional) Table identification. If not provided, <serviceId> must be provided.
                                            This parameter may be obtained by a call to LIST_TABLES.
           @param serviceId      (optional) Service identification. If not provided, <tableId> must be provided.
                                            This parameter may be obtained by a call to LIST_TABLES.
           @return None
        """
        params = ("SET_CUSTOM_PROPERTY", self._posid, propkey, (propvalue or ""), (tableid or ""), (serviceid or ""))
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))

    def getCustomProperty(self, propkey, propvalue=None, tableid=None, serviceid=None):
        """Retrieves the list of custom properties associated with the given table or service.
           @param propKey        (argv[1])  (optinal) Property key
           @param tableId        (argv[2])  (optional) Table identification. If not provided, <serviceId> must be provided.
                                            This parameter may be obtained by a call to LIST_TABLES.
           @param serviceId      (argv[3])  (optional) Service identification. If not provided, <tableId> must be provided.
                                            This parameter may be obtained by a call to LIST_TABLES.
           @return dict
        """
        params = ("GET_CUSTOM_PROPERTY", self._posid, (propkey or ""), (propvalue or ""), (tableid or ""), (serviceid or ""))
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return json.loads(msg.data)

    def getTablePicture(self, tableid):
        """Retrieves the ordering information of a <tableId>.
           @param tableId   Table identification
           @return Table picture XML document.
        """
        params = ("TABLE_PICTURE", self._posid, tableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def recallService(self, userid, tableid):
        """Recover the service for a Table.
           This API associates the caller (session or POS) to Table to cotinue its service.
           @param userId        User identification
           @param tableId       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @return Table picture XML.
                   Produces the following event:
                   - subject: STORE_MODIFIED type: RecallService => containing the current Store Picture.
        """
        params = ("RECALL_SERVICE", self._posid, userid, tableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def storeService(self, userid, tableid):
        """Releases the Table saving the current service.
           This API removes the session association done by the recallService.
           @param userId        User identification
           @param tableId       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @return None
                   Produces the following event:
                   - subject: TABLE_STORED type: TableService => containing the current Table Picture.
                   - subject: STORE_MODIFIED type: ServiceStored => containing the current Store Picture.
        """
        params = ("STORE_SERVICE", self._posid, userid, tableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        else:
            return True

    def startService(self, userid, bperiod, tableid="", noseats="", customprops={}):
        """Starts a new service in a existent Table or opening a new Tab.
           @param userId      User identification
           @param bperiod     Current business period YYYY-MM-DD
           @param tableId     (optional) Table identification. If ommited, it will create a 'Tab' service.
                              This parameter may be obtained by a call to LIST_TABLES.
           @param noseats     (optional) The number of seats requested for this service.
           @param customProps (optional) Dictionary containing custom properties to be associated to the
                              new service.
           @return dict
                   Produces the following event:
                   - subject: STORE_MODIFIED type: StartService => containing the current Store Picture.
        """
        params = ("START_SERVICE", self._posid, userid, bperiod, tableid, noseats, json.dumps(customprops))
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return json.loads(msg.data)

    def sliceService(self, userid, newsetup, srctableid, dsttableid=""):
        """Slices an existent service initiating a new service with an existent Table or
           creating a new Tab, with parts of the current service.
           The new service business period will the same equal to the original service.
           @param posId             Current POS source
           @param userId            User identification
           @param newSetup          JSON: List of objects corresponding to the ordered lines in the actual
                                    service, describing how the new service will be create with the those
                                    items. All selected items will be hosted in a single order on the
                                    destination table.
                                    JSON expected format:
                                        [
                                            {"originalOrderId": <int>,
                                            "lineNumbers": [<int>, <int>, ...]},
                                            {"originalOrderId": <int>,
                                            "lineNumbers": [<int>, <int>, ...]},
                                            ...
                                        ]
                                    Sample JSON:
                                        [
                                            {"originalOrderId":123,"lineNumbers":[1,3]},
                                            {"originalOrderId":124,"lineNumbers":[5]}
                                        ]
           @param srcTableId        Source Table identification.
                                    If not provided, <serviceId> must be provided.
                                    This parameter may be obtained by a call to LIST_TABLES.
           @param destTableId       (optional) Destination Table identification.
                                    If omitted, it will create a 'Tab' service.
                                    This parameter may be obtained by a call to LIST_TABLES.
           @return dict
                   Sample response JSON:
                        {
                            "serviceId": "14",
                            "tableId": "TAB-403"
                        }
                   Produces the following event:
                   - subject: STORE_MODIFIED type: SliceService => containing the current Store Picture.
        """
        params = ("SLICE_SERVICE", self._posid, userid, newsetup, srctableid, dsttableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return json.loads(msg.data)

    def abandonService(self, userid, tableid):
        """Abandon a service closing all related orders.
           @param userId        User identification
           @param tableId       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @return None
                   Produces the following event:
                   - subject: STORE_MODIFIED type: AbandonService => containing the current Store Picture.
        """
        params = ("ABANDON_SERVICE", self._posid, userid, tableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))

    def createOrder(self, userid, tableid, price_list=''):
        """Creates a new POS order within the provided table.
           @param userId        User identification
           @param tableId       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param price_list    price_list ID to use as primary source of prices on created order as: EI.DT - first uses
                                DT price list, if not found context, look up price on EI
           @return Order XML.
                   Produces the following event:
                   - subject: STORE_MODIFIED type: CreateOrder => containing the current Store Picture.
        """
        params = ("CREATE_ORDER", self._posid, userid, tableid, price_list)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def setCurrentOrder(self, userid, tableid, orderid):
        """Creates a new POS order within the provided table.
           @param userId        User identification
           @param tableId       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param orderId       Order identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @return None
        """
        params = ("SET_CURRENT_ORDER", self._posid, userid, tableid, orderid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))

    def voidServiceOrder(self, userid, tableid, orderid):
        params = ("VOID_SERVICE_ORDER", self._posid, userid, tableid, orderid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))


    def registerServiceTender(self, userid, tableid, tenderid, amount="", tenderdetail="", orders=[]):
        """Register a tender (payment) for the current service in the provided Table identification.
           If the optional parameter 'amount' is not set, it will tender the exact total amount for all orders in the table.
           @param userid        User identification
           @param tableid       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param tenderid      A known tender type identification
           @param amount        (optional) the amount tendered. it must be a string with cents after a period character (e.g. 5.99)
           @param tenderdetail  (optional) additional tender information
           @param orders        (deprecated)
           @return Table picture XML.
        """
        orders = ",".join([str(x) for x in orders])
        params = ("REGISTER_SERVICE_TENDER", self._posid, userid, tableid, tenderid, amount, tenderdetail)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def clearServiceTenders(self, userid, tableid, servicetenderid=""):
        """Removes all registered service tenders (payments) in the provided Table.
           @param userid           User identification
           @param tableid          Table identification.
                                   This parameter may be obtained by a call to LIST_TABLES.
           @param serviceTenderId  (optional) If set clears only that service tender id.
           @return Table picture XML.
        """
        params = ("CLEAR_SERVICE_TENDERS", self._posid, userid, tableid, servicetenderid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def totalService(self, userid, tableid, tiprate="", tipamt="", splitsetup="", saletype="EAT_IN"):
        """Total the orders of a service and produces a table picture.
           @param userId        User identification
           @param tableId       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param tipRate       (optional)
                                Tip rate to be applied to the totaled orders or the whole service.
           @param tipAmt        (optional)
                                Tip amount to be applied to the totaled orders or the whole service.
           @param splitsetup    (deprecated)
           @param saletype      (optional. Default: EAT_IN.)
                                EAT_IN, TAKE_OUT, DRIVE_THRU, DELIVERY, etc.
           @return Table picture XML.
                   Produces the following events:
                   - subject: TABLE_TOTALED type: TableService => containing the current Table Picture;
                   - subject: STORE_MODIFIED type: TableTotaled => containing the current Store Picture.
        """
        params = ("TOTAL_SERVICE", self._posid, userid, tableid, tiprate or "", tipamt or "", splitsetup or "", saletype or "EAT_IN")
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def changeServiceTip(self, userid, tableid, tiprate="", tipamt="", orders=""):
        """Total the orders of a service and produces a table picture.
           @param posId          Current POS source
           @param userId         User identification
           @param tableId        Table identification.
                                 This parameter may be obtained by a call to LIST_TABLES.
           @param tipRate        (optional)
                                 Tip rate to be applied to the totaled orders or the whole service.
           @param tipAmt         (optional)
                                 Tip amount to be applied to the totaled orders or the whole service.
           @param orders         (deprecated)
           @return Table picture XML.
        """
        params = ("CHANGE_SERVICE_TIP", self._posid, userid, tableid, tiprate or "", tipamt or "", orders or "")
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def closeService(self, userid, tableid):
        """Finalizes the service, closing all related orders.
           @param userId        User identification
           @param tableId       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @return Table picture XML.
                   Produces the following events:
                   - subject: TABLE_CLOSED type: TableService => containing the current Table Picture;
                   - subject: STORE_MODIFIED type: TableClosed => containing the current Store Picture.
        """
        params = ("CLOSE_SERVICE", self._posid, userid, tableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def reopenService(self, userid, tableid):
        """Reopen previous totaled orders of a service and produces a table picture.
           @param userId        User identification
           @param tableId       Table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @return Table picture XML.
                   Produces the following events:
                   - subject: TABLE_REOPENED type: TableService => containing the current Table Picture;
                   - subject: STORE_MODIFIED type: TableReopened => containing the current Store Picture.
        """
        params = ("REOPEN_SERVICE", self._posid, userid, tableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))
        return msg.data

    def joinTables(self, userid, fromtableid, desttableid, numberofseats=""):
        """Join 2 tables as a single service, moving all orders to the destination table.
           @param userId        User identification
           @param fromTableId   Source table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param destTableId   Destination table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param numberOfSeats (optional) The number of seats if the destination table is available.
           @return None
                   Produces the following event:
                   - subject: STORE_MODIFIED type: JoinTable => containing the current Store Picture.
        """
        params = ("JOIN_TABLES", self._posid, userid, fromtableid, desttableid, numberofseats)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))

    def moveTable(self, userid, fromtableid, desttableid, numberofseats=""):
        """Move orders from one table to another and close the source table.
           @param userId        User identification
           @param fromTableId   Source table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param destTableId   Destination table identification.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param numberOfSeats (optional) The number of seats if the destination table is available.
           @return None
                   Produces the following event:
                   - subject: STORE_MODIFIED type: MoveTable => containing the current Store Picture.
        """
        params = ("MOVE_TABLE", self._posid, userid, fromtableid, desttableid, numberofseats)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))

    def unlinkTables(self, userid, tableid, unlinktableid=""):
        """Move orders from one table to another and close the source table.
           @param userId        User identification
           @param tableId       Major table identification. Table which other tables are linked to.
                                This parameter may be obtained by a call to LIST_TABLES.
           @param unlinkTableId (optional) Specific table to unlink. If none is provided, all tables linked to the major one will be release.
                                This parameter may be obtained by a call to LIST_TABLES.
           @return None
                   Produces the following event:
                   - subject: STORE_MODIFIED type: UnlinkTables => containing the current Store Picture.
        """
        params = ("UNLINK_TABLES", self._posid, userid, tableid, unlinktableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))

    def tableReady4Service(self, userid, tableid):
        """Set table as Available status once again. This is tipically done after the Table service is Closed.
           @param userId        User identification
           @param tableId       Major table identification. Table which other tables are linked to.
                                This parameter may be obtained by a call to LIST_TABLES.
           @return None
                   Produces the following event:
                   - subject: STORE_MODIFIED type: TableReady => containing the current Store Picture.
        """
        params = ("TABLE_READY4SERVICE", self._posid, userid, tableid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))

    def changeTableUser(self, userid, tableid="", serviceid=""):
        """Changes the service operator
           @param posId          Current POS Id
           @param userId         User Id to transfer service to
           @param tableId        (optional) Table identification. If not provided, <serviceId> must be provided.
                                 This parameter may be obtained by a call to LIST_TABLES.
           @param serviceId      (optional) Service identification. If not provided, <tableId> must be provided.
                                 This parameter may be obtained by a call to LIST_TABLES.
           @return None
                   Produces the following event:
                   - subject: STORE_MODIFIED type: TableUserChanged => containing the current Store Picture.
        """
        params = ("CHANGE_TABLE_USER", self._posid, userid, tableid, serviceid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))

    def changeNumberOfSeats(self, userid, numberofseats, tableid="", serviceid=""):
        """Changes the service number of seats
           @param posId          Current POS Id
           @param userId         User Id to transfer service to
           @param numberOfSeats  The new number of seats
           @param tableId        (optional) Table identification. If not provided, <serviceId> must be provided.
                                 This parameter may be obtained by a call to LIST_TABLES.
           @param serviceId      (optional) Service identification. If not provided, <tableId> must be provided.
                                 This parameter may be obtained by a call to LIST_TABLES.
           @return Reply msgbus message <msg>.
                   Produces the following event:
                   - subject: STORE_MODIFIED type: NOSeatsChanged => containing the current Store Picture.
        """
        params = ("CHANGE_NUMBER_OF_SEATS", self._posid, userid, numberofseats, tableid, serviceid)
        sys_log_info("TableService.{0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params))
        reqbuf = "\0".join([str(p) for p in params])
        msg = send_message(self.tablemgr, TK_CMP_MESSAGE, format=FM_PARAM, data=reqbuf, timeout=default_timeout)
        if msg.token == TK_SYS_NAK:
            raise TableServiceException(errmsg=(msg.data if msg.format == FM_STRING and msg.data else "API exception: {0}({1})".format(inspect.getframeinfo(inspect.currentframe()).function, params)))


def get_posts(model, ordermgr=None, productmgr=None, tablemgr=None):
    """Retrieves an TableService API instance for the given POS model.
       This API can be used to perform order operations (create service, create order, sale, void, etc)
    @return {TableService} - instance
    """
    posot = TableService(model.get("posId", "1") if model is not None else "1", mbcontext, ordermgr, productmgr, tablemgr)
    if model is not None:
        posot.podType = get_podtype(model)
        posot.businessPeriod = get_business_period(model)
        posot.sessionId = get_operator_session(model)
        operator = model.find("Operator")
        if operator is not None:
            posot.operatorId = operator.get("id")
    return posot
