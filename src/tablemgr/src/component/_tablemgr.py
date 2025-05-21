# -*- coding: utf-8 -*-
# Module name: _tablemgr.py
# Module Description: Component responsible for table service API implementation
#
# Copyright (C) 2018 MWneo Corporation
# Copyright (C) 2018 Omega Tech Enterprises Ltd.
# (All rights transferred from MWneo Corporation to Omega Tech Enterprises Ltd.)
#
# $Id: _tablemgr.py $
# $Revision: $
# $Date: $
# $Author: amerolli $

# standard modules
import os
import sys
import json
import time
from xml.etree import cElementTree as etree
from decimal import Decimal as D
from _threadpooltemplate import ThreadPool
import logging

from memorycache import CacheManager
from model import PeriodBasedExpiration
from repository import ProductRepository

# app modules
from msgbus import \
    TK_SLCTRL_OMGR_ORDERPICT, \
    TK_SLCTRL_OMGR_VOIDORDER, \
    TK_SLCTRL_OMGR_CREATEORDER, \
    TK_SLCTRL_OMGR_RECALLORDER, \
    TK_SLCTRL_OMGR_ORDERTOTAL, \
    TK_SLCTRL_OMGR_DOTENDER, \
    TK_SLCTRL_OMGR_CLEARTENDERS, \
    TK_SLCTRL_OMGR_STOREORDER, \
    TK_SLCTRL_OMGR_SETCUSTOMPROPERTIES, \
    TK_SLCTRL_OMGR_UPDPROPERTIES, \
    TK_CMP_TERM_NOW, \
    TK_SYS_NAK, \
    TK_EVT_EVENT, \
    TK_SYS_ACK, \
    TK_STORECFG_GET, \
    TK_CMP_MESSAGE, \
    MBException, \
    MBEasyContext, \
    FM_STRING, \
    FM_XML, \
    FM_PARAM, TK_SLCTRL_OMGR_RESETCURRORDER
from systools import sys_log_info, sys_log_exception
from syserrors import SE_USERCANCEL, SE_CFGLOAD, SE_MB_ERR, SE_SUCCESS, SE_DBINIT
import cfgtools
import persistence
import threading
from copy import deepcopy
from component._OrderException import OrderException

#
# constants
#
SERVICE_NAME = "TABLEMGR"
SERVICE_TYPE = "TABLEMGR"
EXPORTED_SERVICES = "%s:%s" % (SERVICE_NAME, SERVICE_TYPE)
REQUIRED_SERVICES = "Persistence|StoreWideConfig"
DEFAULT_SPLIT_KEY = "SingleOrder"

#
# globals
#
logger = logging.getLogger("TableManager")
mbcontext = None                     #: MBEasyContext instance
config = None                        #: configuration instance
store_id = None                      #: store id
store_layout = None                  #: store default layout loaded from components configuration
dbd = None                           #: Database driver
persistence_service = "Persistence"  #: Default persistence service
thread_pool_size = 10                #: Size of thread pool (default: 10 threads)
recall_lock = threading.Lock()
ORDER_MANAGER_TIMEOUT = 1000000 * 30
products_list_not_charge_tip = []

MANAGED_TOKENS = ["STORE_PICTURE", "LIST_TABLES", "TABLE_PICTURE", "START_SERVICE", "SLICE_SERVICE", "ABANDON_SERVICE",
                  "SET_CUSTOM_PROPERTY", "GET_CUSTOM_PROPERTY", "CREATE_ORDER", "SET_CURRENT_ORDER", "JOIN_TABLES",
                  "MOVE_TABLE", "UNLINK_TABLES", "TOTAL_SERVICE", "REOPEN_SERVICE", "CLOSE_SERVICE", "RECALL_SERVICE",
                  "STORE_SERVICE", "REGISTER_SERVICE_TENDER", "CLEAR_SERVICE_TENDERS", "TABLE_READY4SERVICE",
                  "CHANGE_TABLE_USER", "CHANGE_NUMBER_OF_SEATS", "CHANGE_SERVICE_TIP", "VOID_SERVICE_ORDER"]


def read_swconfig(key):
    """Get a store wide configuration."""
    rmsg = mbcontext.MB_EasySendMessage("StoreWideConfig", token=TK_STORECFG_GET, format=FM_PARAM, data=key)
    if rmsg.token != TK_SYS_ACK:
        raise Exception("Unable to get Store Wide Configuration {%s}" % (key))
    return str(rmsg.data)


def read_config():
    """Read the configuration file for this component"""
    global config, store_id, store_layout, persistence_service, thread_pool_size
    try:
        # parse the configuration
        config = cfgtools.read(os.environ["LOADERCFG"])
        thread_pool_size = int(config.find_value("TableManager/ThreadPoolSize") or "10")
        store_layout = config.find_group("TableManager/StoreLayout")
        store_layout = dict([(table.name, dict([(k.name, k.values[0]) for k in table.keys])) for table in store_layout.groups])
        persistence_service = (config.find_value("TableManager/PersistenceService") or "Persistence")
        # read global configurations
        store_id = read_swconfig("Store.Id")
    except:
        sys_log_exception("Error reading configuration file. Terminating")
        sys.exit(SE_CFGLOAD)


def start_cache_objects():
    global products_list_not_charge_tip
    product_cache_manager = CacheManager(PeriodBasedExpiration(60), new_object_func=_get_products_with_not_charge_tip)
    products_list_not_charge_tip = product_cache_manager.get_cached_object() or []


def _get_products_with_not_charge_tip():
    return ProductRepository(mbcontext).get_products_with_not_charge_tip()


def init_msgbus():
    """Initialize the message-bus context."""
    global mbcontext
    try:
        # Create a new context for us
        mbcontext = MBEasyContext(SERVICE_NAME)
        # Wait for the Hypervisor to allow us to start-up
        if SE_SUCCESS != mbcontext.MB_EasyWaitStart(EXPORTED_SERVICES, REQUIRED_SERVICES):
            # We must terminate for some reason
            sys_log_info("Terminating Table Service component after 'MB_EasyWaitStart'")
            sys.exit(SE_SUCCESS)
    except MBException:
        sys_log_exception("Message-bus error while initializing the Table Service component. Terminating")
        sys.exit(SE_MB_ERR)


def init_persistence():
    """Initializes the persistence layer"""
    global dbd
    try:
        dbd = persistence.Driver()
    except:
        sys_log_exception("Error initializing Table service component persistence. Terminating")
        logger.exception("Error initializing Table service component persistence. Terminating")
        sys.exit(SE_DBINIT)


def get_db_connection(pos_id):
    """Retrieves a database connection in the appropriate instance"""
    dbconn = dbd.open(mbcontext, dbname=str(pos_id), service_name=persistence_service.encode('utf-8'), logger=logger)
    dbconn.query("PRAGMA busy_timeout = 30000;")
    # dbconn.query("PRAGMA journal_mode = WAL;")
    return dbconn


def reset_store_layout_setup():
    """Resets the tblserviceTable table based on the store layout configured"""
    dbconn = get_db_connection(1)
    params = []
    for k, v in store_layout.items():
        t = deepcopy(v)
        t["id"] = k
        params.append(t)
    dbconn.pquery("resetStoreLayout", PreparedStringTable="json:{0}".format(json.dumps(params)))


def get_user_sessionid(pos_id, user_id):
    """Retrieves the user's POS session ID"""
    sql = """
        SELECT SessionId
        FROM posctrl.UserSession
        WHERE CloseTime IS NULL AND OperatorId={0}
        ORDER BY OpenTime DESC
        LIMIT 1
    """.format(user_id)
    dbconn = get_db_connection(pos_id)
    cursor = dbconn.select(sql)
    for row in cursor:
        return row.get_entry(0)
    return None


def get_service_tenders(pos_id, service_id):
    dbconn = get_db_connection(pos_id)
    cursor = dbconn.pselect("getServiceTenders", serviceId=service_id)
    return [dict([(cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols())]) for row in cursor]


def get_service_tips(pos_id, service_id):
    dbconn = get_db_connection(pos_id)
    cursor = dbconn.pselect("getServiceTips", serviceId=service_id)
    return [dict([(cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols())]) for row in cursor]


def get_split_service(pos_id, service_id):
    dbconn = get_db_connection(pos_id)
    cursor = dbconn.pselect("getSplitServiceOrders", serviceId=service_id)
    return [dict([(cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols())]) for row in cursor]


def get_service_tenders_consolidated(pos_id, service_id):
    dbconn = get_db_connection(pos_id)
    cursor = dbconn.pselect("getServiceTendersConsolidated", serviceId=service_id)
    return [dict([(cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols())]) for row in cursor]


def send_order_message(params, pos_id, token):
    params = "\0".join(str(p) for p in params)
    msg = mbcontext.MB_EasySendMessage(
        "ORDERMGR%d" % pos_id,
        token,
        FM_PARAM,
        params,
        timeout=ORDER_MANAGER_TIMEOUT)

    if msg.token != TK_SYS_ACK:
        params = msg.data.split('\0')
        raise OrderException(params[0], "%s: %s" % (params[0], params[1]))

    return msg.data


def create_order(pos_id, table, storeorder=False, blk_notify=False, pricelist="EI", sessionid="", additionalinfo="", multiorderid="", ordertype="SALE", saletype="EAT_IN", ordersubtype="", custom_properties={}):
    params = ("1", pos_id, pricelist, "POS%02d" % int(pos_id), "", table["businessPeriod"].replace('-', ''), "TS", sessionid, additionalinfo, multiorderid, ordertype, saletype, ordersubtype)

    order_id = None
    try:
        response = send_order_message(params, pos_id, TK_SLCTRL_OMGR_CREATEORDER)
        data = response.split('\0')
        order = etree.XML(data[2])
        order_id = order.get("orderId")
    except OrderException as ex:
        if ex.get_code() == "8":  # There is an Open Order in POS
            store_order(pos_id, blk_notify=True)

            return create_order(pos_id, table, storeorder, blk_notify, pricelist, sessionid, additionalinfo, multiorderid, ordertype, saletype, ordersubtype, custom_properties)
        logger.exception("Error when retrieving order id")
        raise

    if order_id is None:
        raise Exception("$ORDERMGR_COULD_NOT_CREATE_ORDER")

    logger.debug("Created order with id: {}".format(order_id))
    _link_order_with_table(blk_notify, custom_properties, order_id, pos_id, table)

    if storeorder:
        store_order(pos_id, blk_notify=blk_notify)

    return order_id


def _link_order_with_table(blk_notify, custom_properties, order_id, pos_id, table):
    try:
        # Set TableId Custom Order Property
        properties = etree.Element("Properties")
        etree.SubElement(properties, "Property", {"key": "TABLE_ID", "value": table["id"]})
        etree.SubElement(properties, "Property", {"key": "SERVICE_ID", "value": table["serviceId"]})
        if "sector" in table and table["sector"] is not None:
            etree.SubElement(properties, "Property", {"key": "SECTOR", "value": table["sector"]})
        for k, v in custom_properties.items():
            etree.SubElement(properties, "Property", {"key": k, "value": str(v)})

        set_order_properties(pos_id, blk_notify, order_id, properties)
        update_order_properties(pos_id, blk_notify=blk_notify, orderid=order_id)
    except OrderException as _:
        logger.exception("Error setting Custom Properties. The order {} will be voided".format(order_id))
        void_order(pos_id, order_id, blk_notify=blk_notify)
        raise


def void_order(pos_id, order_id, abandon="1", blk_notify=True):
    params = ("1" if blk_notify else "0", pos_id, "0", order_id, abandon)
    send_order_message(params, pos_id, TK_SLCTRL_OMGR_VOIDORDER)


def tender_order(pos_id, blk_notify=False, tenderid="", amount="", donotclose=False, ordertenderid="", tipamount="", tenderdetail=""):
    params = ("1" if blk_notify else "0", pos_id, tenderid, amount, 1 if donotclose else 0, ordertenderid, tipamount, tenderdetail)
    response = send_order_message(params, pos_id, TK_SLCTRL_OMGR_DOTENDER)
    data = response.split('\0')

    if data[2]:
        order = etree.XML(data[2])
        return dict(order.items())


def clear_tender(pos_id, blk_notify=False, tender_id=""):
    params = ("1" if blk_notify else "0", pos_id, tender_id)
    send_order_message(params, pos_id, TK_SLCTRL_OMGR_CLEARTENDERS)


def recall_order(pos_id, order_id, session_id="", srcposid="", blk_notify=False, service_id=None):
    dbconn = get_db_connection(pos_id)
    if service_id is not None:
        dbconn.pquery("registerServiceOrder", serviceId=service_id, orderId=order_id, posId=pos_id)

    logger.debug("Sending recall to POS: {} / Order Id: {} / Source POS ID: {}".format(pos_id, order_id, srcposid))
    try:
        # TRY TO RECALL ORDER IN KNOW POS
        params = ("1" if blk_notify else "0", pos_id, order_id, session_id, srcposid)
        with recall_lock:
            send_order_message(params, pos_id, TK_SLCTRL_OMGR_RECALLORDER)
    except OrderException as _:
        # WHEN IT FAILS SEARCH ORDER IN ALL POS
        params = ("1" if blk_notify else "0", pos_id, order_id, session_id, "")
        with recall_lock:
            send_order_message(params, pos_id, TK_SLCTRL_OMGR_RECALLORDER)

    logger.debug("Sent recall to ORDERMGR")


def total_order(pos_id, blk_notify=False):
    params = ("1" if blk_notify else "0", pos_id, 0)
    response = send_order_message(params, pos_id, TK_SLCTRL_OMGR_ORDERTOTAL)

    data = response.split('\0')
    if data[2]:
        order = etree.XML(data[2])
        return D(order.get("totalAmount") or "0.00")
    return D("0.00")


def reset_current_order(pos_id, blk_notify=False):
    params = ("1" if blk_notify else "0", pos_id)
    send_order_message(params, pos_id, TK_SLCTRL_OMGR_RESETCURRORDER)


def store_order(pos_id, blk_notify=False):
    params = ("1" if blk_notify else "0", pos_id)
    try:
        send_order_message(params, pos_id, TK_SLCTRL_OMGR_STOREORDER)
    except OrderException as ex:
        if ex.get_code() == "6":  # Order already Exists
            return True
        raise

    return True


def set_order_properties(pos_id, blk_notify=False, order_id="", properties=""):
    params = ("1" if blk_notify else "0", pos_id, order_id, etree.tostring(properties, encoding="utf-8", method="xml"))
    send_order_message(params, pos_id, TK_SLCTRL_OMGR_SETCUSTOMPROPERTIES)
    return True


def update_order_properties(pos_id, blk_notify=False, ordertype="", saletype="", exemptioncode="", podtype="", additionalinfo="", pricelist="", orderSubType="", orderid="", tip=""):
    params = (("1" if blk_notify else "0"), pos_id, ordertype, saletype, exemptioncode, podtype, additionalinfo, pricelist, orderSubType, orderid, tip)
    send_order_message(params, pos_id, TK_SLCTRL_OMGR_UPDPROPERTIES)
    return True


def order_picture(pos_id, order_id=None):
    params = ("" if order_id is not None else pos_id, order_id or "", "true")
    response = send_order_message(params, pos_id, TK_SLCTRL_OMGR_ORDERPICT)

    data = response.split('\0')
    if data[2]:
        return data[2]

    logger.exception("Order picture error: POS ID: {} / ORDER ID: {} / RESPONSE {}".format(pos_id, order_id, response))


def get_parameters(argv, msg):
    pos_id = int(argv[0])
    user_id = int(argv[1]) if len(argv) > 1 and argv[1] else None
    table_id = argv[2] if len(argv) > 2 and argv[2] else None

    if not all([pos_id, user_id, table_id, msg]):
        raise Exception("$INVALID_PARAMETERS")

    store_tables = handle_list_tables([pos_id, None, None])
    pos_table = filter(lambda t: int(t.get("currentPOSId") or "-1") == pos_id, store_tables)
    if len(pos_table) > 1:
        logger.warning("There are more than one table for this POS")

    if pos_table and pos_table[0]['id'] != table_id:
        logger.warning("SERVING_ANOTHER_TABLE : POS TABLE: {} / TABLE_ID: {}".format(pos_table[0]['id'], table_id))
        raise Exception("$TABLE_CURRENTLY_SERVING_ANOTHER_TABLE")

    tables = filter(lambda t: t["id"] == table_id, store_tables)
    if not tables:
        raise Exception("$NO_TABLE_FOUND")

    table = tables[0]
    return pos_id, table, table_id, user_id


def handle_list_tables(argv, msg=None, dbconn=None):
    """Retrieves the list of available seats and the current related service, if any.
       @param posId  (argv[0])    Current POS source
       @param userId (argv[1])    (optional) Retrieves only tables from provided userId
       @param tableId (argv[2])   (optional) Retrieves information only from provided tableId
       @param withProps (argv[3]) (optional) Retrieves properties information
       @param msg MBMessage       (optional) If provided this will reply the MB message with the
                                             list of table in JSON format
       @param dbconn Object       (optional) Object that holds the a DB connection already
                                             instantiated. If not provided, this will create a
                                             new connection for its usage.
       @return list of dict objects or reply msgbus message if <msg> is provided.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    withprops = int(argv[3]) if len(argv) > 3 and argv[3] else 0
    if dbconn is None:
        dbconn = get_db_connection(posid)
    cursor = dbconn.pselect("listTables", posId=posid, userId=userid, tableId=tableid, withProps=withprops)
    json_cols = ['orders', 'linkedTables', 'properties', 'splitOrders', 'slicedServices']
    result_obj = [dict([(cursor.get_name(i), row.get_entry(i) if cursor.get_name(i) not in json_cols else json.loads(row.get_entry(i))) for i in range(cursor.cols())]) for row in cursor]
    if msg:
        msg.token = TK_SYS_ACK
        mbcontext.MB_ReplyMessage(msg, FM_STRING, json.dumps(result_obj))
        return None
    return result_obj


def get_store_picture_xml(pos_id, subject=None, type=None):
    """Retrieves the XML document used for STORE_MODIFIED event
       @param posId   Current POS source
       @param subject (optional) Produces an Event XML document
       @param type    (optional) Default to subject
       @return XML document.
    """
    tblist = handle_list_tables([pos_id, None, None, 1])
    # filter out Tabs closed or Linked
    closedtabs = [t["id"] for t in filter(lambda tb: (int(tb["type"]) == 2 and int(tb["status"]) in (5, 7)), tblist)]
    tblist = filter(lambda tb: (int(tb["type"]) == 1 or int(tb["status"]) not in (5, 7)), tblist)
    # builds response XML
    root = etree.Element("Event", {"subject": subject, "type": (type or subject)})
    tables = etree.SubElement(root, "Tables")
    for t in tblist:
        orders = t.pop("orders", None)
        linkedtables = t.pop("linkedTables", None)
        t.pop("splitOrders", None)
        slicedservices = t.pop("slicedServices", None)
        properties = t.pop("properties", None)
        if orders is not None:
            t["orders"] = ",".join([str(order["orderId"]) for order in orders])
        if linkedtables is not None:
            linkedtables = filter(lambda x: (x not in closedtabs), linkedtables)
            t["linkedTables"] = ",".join(linkedtables)
        if slicedservices is not None:
            t["slicedTabs"] = ",".join([ss["tableId"] for ss in slicedservices])
        table = etree.SubElement(tables, "Table", dict(filter(lambda i: i[1] is not None, t.items())))
        if properties is not None:
            etree.SubElement(table, "Properties", dict(filter(lambda i: i[1] is not None, properties.items())))
    if subject is not None:
        return etree.tostring(root, encoding="utf-8", method="xml")
    return etree.tostring(tables, encoding="utf-8", method="xml")


def handle_set_custom_property(argv, msg=None):
    """Sets a custom properties associated with a table or a service.
       @param posId          (argv[0])  Current POS source
       @param propKey        (argv[1])  Property key
       @param propValue      (argv[2])  (optional) Property value. If omitted, removes the key.
       @param tableId        (argv[3])  (optional) Table identification. If not provided, <serviceId> must be provided.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param serviceId      (argv[4])  (optional) Service identification. If not provided, <tableId> must be provided.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
    """
    posid = int(argv[0])
    propKey = argv[1] if len(argv) > 1 and argv[1] else None
    propValue = argv[2] if len(argv) > 2 and argv[2] else None
    tableid = argv[3] if len(argv) > 3 and argv[3] else None
    serviceid = int(argv[4]) if len(argv) > 4 and argv[4] else None
    if not all([posid, propKey, any([tableid, serviceid]), msg]):
        raise Exception("$INVALID_PARAMETERS")
    if serviceid is None:
        table = handle_list_tables([posid, None, tableid])
        if not table:
            raise Exception("$NO_TABLE_FOUND")
        table = table[0]
    dbconn = get_db_connection(posid)
    dbconn.pquery("setServiceCustomProperty",
                  serviceId=(serviceid or table["serviceId"]),
                  propertyKey=propKey,
                  propertyValue=propValue,
                  PreparedStringTable="json:[]")
    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)


def handle_get_custom_property(argv, msg=None):
    """Retrieves the list of custom properties associated with the given table or service.
       @param posId          (argv[0])  Current POS source
       @param propKey        (argv[1])  (optinal) Property key
       @param tableId        (argv[2])  (optional) Table identification. If not provided, <serviceId> must be provided.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param serviceId      (argv[3])  (optional) Service identification. If not provided, <tableId> must be provided.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return A dict or reply msgbus message <msg>, if provided.
    """
    posid = int(argv[0])
    propKey = argv[1] if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    serviceid = int(argv[3]) if len(argv) > 3 and argv[3] else None
    if not all([posid, any([tableid, serviceid])]):
        raise Exception("$INVALID_PARAMETERS")
    if serviceid is None:
        table = handle_list_tables([posid, None, tableid])
        if not table:
            raise Exception("$NO_TABLE_FOUND")
        table = table[0]
    dbconn = get_db_connection(posid)
    cursor = dbconn.pselect("getServiceCustomProperty",
                            serviceId=(serviceid or table["serviceId"]),
                            propertyKey=propKey)
    result_obj = dict([(row.get_entry(0), row.get_entry(1)) for row in cursor])
    if msg is not None:
        msg.token = TK_SYS_ACK
        mbcontext.MB_ReplyMessage(msg, FM_STRING, json.dumps(result_obj))
        return None
    return result_obj


def handle_table_picture(argv, msg=None, subject=None, type=None):
    """Retrieves the ordering information of a <tableId>.
       @param posId  (argv[0])  Current POS source
       @param tableId (argv[1]) Table identification
       @return XML document or reply message if <msg> is provided.
    """
    pos_id = int(argv[0])
    table_id = argv[1] if len(argv) > 1 and argv[1] else None
    if not all([pos_id, table_id]):
        raise Exception("$INVALID_PARAMETERS")
    table_list = handle_list_tables([pos_id, None, None, 1])
    # filter out Tabs closed or Linked
    closed_tabs = [t["id"] for t in filter(lambda tb: (int(tb["type"]) == 2 and int(tb["status"]) in (5, 7)), table_list)]
    table = filter(lambda tb: (tb["id"] == table_id), table_list)
    if not table:
        raise Exception("$NO_TABLE_FOUND")
    table = table[0]
    linked_tables = table.pop("linkedTables", None)

    if linked_tables is not None:
        linked_tables = filter(lambda x: (x not in closed_tabs), linked_tables)
        table["linkedTables"] = ",".join(linked_tables)
    sliced_services = table.pop("slicedServices", None)

    if sliced_services is not None:
        table["slicedTabs"] = ",".join([ss["tableId"] for ss in sliced_services])
    orders = None

    db_connection = None
    table_orders = table.pop("splitOrders", None)
    if _table_is_totaled(table):
        orders = etree.Element("Orders")
        dueamount = D(0)
        changeamount = D(0)
        tenderamount = D(0)
        totaltax = D(0)
        totaldiscount = D(0)
        totaltip = D(0)

        current_pos_id = table.get("currentPOSId")
        if current_pos_id is not None and int(current_pos_id) == pos_id:
            for split_order in table_orders:
                if split_order['state'] != "TOTALED" and split_order['state'] != "PAID":
                    recalled = False
                    try:
                        recall_order(pos_id, split_order['orderId'], blk_notify=True)
                        recalled = True
                    except Exception as _:
                        order = etree.XML(order_picture(pos_id))
                        if int(order.get('orderId')) != split_order['orderId'] or \
                                order.get('state') not in ('TOTALED', 'PAID'):
                            raise

                    if recalled:
                        total_order(pos_id, blk_notify=False)
                        order = etree.XML(order_picture(pos_id))
                        store_order(pos_id, blk_notify=False)
                else:
                    order = etree.XML(order_picture(pos_id))
                    if int(order.get('orderId')) != split_order['orderId']:
                        break
                    current_pos_order_id = table.get("currentPOSOrderID")
                    if current_pos_order_id != str(split_order['orderId']):
                        if db_connection is None:
                            db_connection = get_db_connection(pos_id)
                        db_connection.pquery("updateCurrentServiceOrder", posId=pos_id, orderId=split_order['orderId'])
                        update_order_properties(pos_id=pos_id, orderid=split_order['orderId'])

                totaldiscount += D(order.get("discountAmount") or "0.00")
                totaltax += D(order.get("taxTotal") or "0.00")
                totaltip += D(order.get("tip") or "0.00")
                damount = D(order.get("dueAmount") or "0.00")
                if damount < D(0):
                    order.set("dueAmount", "0.00")
                    order.set("change", str((damount * D(-1)).quantize(D("0.01"))))
                else:
                    dueamount += damount
                orders.append(order)
                for tender in order.findall("TenderHistory/Tender"):
                    changeamount += D(tender.get("change") or "0.00")
                    tenderamount += D(tender.get("tenderAmount") or "0.00")

        table["discountAmount"] = str(totaldiscount.quantize(D("0.01")))
        table["taxTotal"] = str(totaltax.quantize(D("0.01")))
        table["dueAmount"] = str(dueamount.quantize(D("0.01")))
        table["change"] = str(changeamount.quantize(D("0.01")))
        table["totalTender"] = str(tenderamount.quantize(D("0.01")))
        table["tip"] = str(totaltip.quantize(D("0.01")))
    else:
        table_orders = (table.pop("orders", None) or [])

    table_orders_ids = [str(o.get("orderId")) for o in table_orders if "orderId" in o]
    table["orders"] = ",".join(table_orders_ids)

    if table_orders_ids:
        orders = '<Orders>'
        for order_id in table_orders_ids:
            order = etree.XML(order_picture(pos_id, order_id)).find('.//Order')
            state = order.get("state")
            table_order_state = [str(o.get("state")) for o in table_orders if o.get("orderId") == int(order_id)][0]
            if state != table_order_state:
                if db_connection is None:
                    db_connection = get_db_connection(pos_id)
                db_connection.pquery("updateCurrentOrderState", posId=pos_id, orderId=order_id, state=state)

            if state not in ('VOIDED', 'ABANDONED'):
                orders += etree.tostring(order)
        orders += '</Orders>'
        orders = etree.XML(orders)

    properties = table.pop("properties", None)
    tenders = get_service_tenders(pos_id, table["serviceId"])
    xtable = etree.Element("Table", dict(filter(lambda i: i[1] is not None, table.items())))
    if properties:
        etree.SubElement(xtable, "Properties", dict(filter(lambda i: i[1] is not None, properties.items())))
    if tenders:
        xservicetenders = etree.SubElement(xtable, "ServiceTenders")
        for tender in tenders:
            etree.SubElement(xservicetenders, "ServiceTender", dict(filter(lambda i: i[1] is not None, tender.items())))
    if orders:
        xtable.append(orders)
    event_xml = None
    if subject is not None:
        event = etree.Element("Table", {"subject": subject, "type": (type or subject)})
        event.append(xtable)
        event_xml = etree.tostring(event, encoding="utf-8", method="xml")
    result_xml = etree.tostring(xtable, encoding="utf-8", method="xml")
    if msg:
        msg.token = TK_SYS_ACK
        mbcontext.MB_ReplyMessage(msg, FM_XML, result_xml)
        return None
    return (result_xml, event_xml)


def _table_is_totaled(table):
    return int(table["status"]) == 6


def handle_start_service(argv, msg=None):
    """Starts a new service in a existent Table or creates a new Tab.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param businessPeriod (argv[2])  Current business period YYYY-MM-DD
       @param tableId        (argv[3])  (optional) Table identification. If omitted, it will create a 'Tab' service.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param numberOfSeats  (argv[4])  (optional) The number of seats requested for this service.
       @param customProps    (argv[5])  (optional) JSON object containing custom properties to be associated to the
                                         new service.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: StartService => containing the current Store Picture.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    bperiod = argv[2] if len(argv) > 2 and argv[2] else None
    tableid = argv[3] if len(argv) > 3 and argv[3] else None
    noseats = int(argv[4]) if len(argv) > 4 and argv[4] else None
    customprops = json.loads(argv[5]) if len(argv) > 5 and argv[5] else {}
    if not isinstance(customprops, dict):
        raise Exception("$INVALID_PARAMETERS")
    customprops = [{'propKey': k, 'propValue': v} for k, v in customprops.items()]
    typeid = 2 if tableid is None else 1
    if not all([posid, userid, bperiod, msg]):
        raise Exception("$INVALID_PARAMETERS")
    table = None
    if tableid:
        table = handle_list_tables([posid, None, tableid])
        table = table[0] if table else None
    if table is not None and int(table["status"]) != 1:
        raise Exception("$INVALID_TABLE_STATUS")
    dbconn = get_db_connection(posid)
    cursor = dbconn.pselect("startService",
                            posId=posid, userId=userid,
                            businessPeriod=bperiod, typeId=typeid,
                            tableId=tableid, numberOfSeats=noseats)
    result_obj = None
    for row in cursor:
        result_obj = dict([(cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols())])
        break

    if result_obj and customprops:
        dbconn.pquery("setServiceCustomProperty",
                      serviceId=(result_obj["serviceId"]),
                      PreparedStringTable="json:{0}".format(json.dumps(customprops)))

    msg.token = TK_SYS_ACK if result_obj else TK_SYS_NAK
    mbcontext.MB_ReplyMessage(msg, FM_STRING, json.dumps(result_obj))
    store_modified_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="StartService")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "StartService", store_modified_xml)


def handle_slice_service(argv, msg=None):
    """Slices an existent service initiating a new service with an existent Table or
       creating a new Tab, with parts of the current service.
       The new service business period will the same equal to the original service.
       @param posId           (argv[0])  Current POS source
       @param userId          (argv[1])  User identification
       @param newServiceSetup (argv[2])  JSON: List of objects corresponding to the ordered lines in the actual
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
       @param srcTableId      (argv[3])  Source Table identification.
                                         If not provided, <serviceId> must be provided.
                                         This parameter may be obtained by a call to LIST_TABLES.
       @param destTableId     (argv[4])  (optional) Destination Table identification.
                                         If omitted, it will create a 'Tab' service.
                                         This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: SliceService => containing the current Store Picture.
    """
    # validate all input parameters
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    newsetup = json.loads(argv[2]) if len(argv) > 2 and argv[2] else None
    tempsetup = []
    for s in newsetup:
        order_id, lines = map(s.get, ("originalOrderId", "lineNumbers"))
        tempsetup.extend([dict(zip(("originalOrderId", "lineNumber"), t)) for t in [(order_id, l) for l in lines]])
    if not tempsetup:
        raise Exception("$INVALID_PARAMETERS")
    for i, s in enumerate(tempsetup):
        s["sliceLineNumber"] = (i+1)
    srctableid = argv[3] if len(argv) > 3 and argv[3] else None
    if not all([posid, userid, srctableid, msg]):
        raise Exception("$INVALID_PARAMETERS")
    sessionid = get_user_sessionid(posid, userid)
    if sessionid is None:
        raise Exception("$NO_SESSION_ID_FOUND")
    dsttableid = argv[4] if len(argv) > 4 and argv[4] else None
    dsttable = None
    typeid = 2
    if dsttableid is not None:
        dsttable = handle_list_tables([posid, None, dsttableid])
        dsttable = dsttable[0] if dsttable else None
        typeid = 1
    if dsttable is not None and int(dsttable["status"]) != 1:
        raise Exception("$INVALID_TABLE_STATUS")
    srctable = handle_list_tables([posid, None, srctableid])
    if not srctable:
        raise Exception("$NO_TABLE_FOUND")
    srctable = srctable[0]
    if int(srctable["status"]) != 4:
        raise Exception("$INVALID_TABLE_STATUS")
    # recall orders from other POS ids ...
    for order in (srctable.get("orders") or []):
        if int(order["posId"]) != posid:
            recall_order(posid, order["orderId"], sessionid, order["posId"], blk_notify=True, service_id=srctable["serviceId"])
            store_order(posid, blk_notify=False)
    # create a new service ...
    new_order_id = None
    new_service = None
    intrans = False
    hasconn = False
    success = False
    dbconn = get_db_connection(posid)
    try:
        dbconn.transaction_start()
        hasconn = True
        cursor = dbconn.pselect("startService",
                                posId=posid, userId=userid,
                                businessPeriod=srctable["businessPeriod"],
                                srcServiceId=srctable["serviceId"],
                                typeId=typeid, tableId=dsttableid, numberOfSeats="1")
        for row in cursor:
            new_service = dict([(cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols())])
            break
        if not new_service:
            raise Exception("$UNABLE_TO_SLICE_SERVICE")
        if dsttable is None:
            dsttable = handle_list_tables([posid, None, new_service["tableId"]], dbconn=dbconn)
            if not dsttable:
                raise Exception("$UNABLE_TO_SLICE_SERVICE")
            dsttable = dsttable[0]
        # create a new order
        new_order_id = create_order(
            posid, dsttable, blk_notify=True, storeorder=True,
            sessionid=sessionid, ordersubtype="SLICED_SERVICE",
            custom_properties={"SOURCE_SERVICE_ID": srctable["serviceId"]}
        )
        dbconn.query("BEGIN TRANSACTION;")
        intrans = True
        dbconn.pquery("registerServiceOrder", serviceId=dsttable["serviceId"], orderId=new_order_id, posId=posid)
        dbconn.pquery("updateTableServiceStatus", serviceId=dsttable["serviceId"], status="InProgress")
        dbconn.pquery(
            "sliceServiceOrders",
            serviceId=dsttable["serviceId"],
            orderId=new_order_id,
            PreparedStringTable="json:{0}".format(json.dumps(tempsetup))
        )
        dbconn.pquery("storeService", serviceId=dsttable["serviceId"], posId=posid)
        success = True
    finally:
        if intrans:
            dbconn.query("COMMIT TRANSACTION;" if success else "ROLLBACK TRANSACTION;")
        if hasconn:
            dbconn.transaction_end()
        if new_order_id and not success:
            void_order(posid, new_order_id)
        if new_service is not None and not success:
            dbconn.pquery("updateTableServiceStatus", serviceId=new_service["serviceId"], status="Closed")
    msg.token = TK_SYS_ACK if success else TK_SYS_NAK
    mbcontext.MB_ReplyMessage(msg, FM_STRING, json.dumps(new_service))
    store_modified_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="SliceService")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "SliceService", store_modified_xml)


def handle_abandon_service(argv, msg=None):
    """Abandon a service closing all related orders.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: AbandonService => containing the current Store Picture.
    """
    pos_id, table, table_id, user_id = get_parameters(argv, msg)

    for order in (table.get("orders") or []):
        void_order(pos_id, order["orderId"])

    dbconn = get_db_connection(pos_id)
    dbconn.pquery("updateTableServiceStatus", serviceId=table["serviceId"], status="Closed")
    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)
    store_modified_xml = get_store_picture_xml(pos_id, subject="STORE_MODIFIED", type="AbandonService")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "AbandonService", store_modified_xml)


def handle_create_order(argv, msg=None):
    """Creates a new POS order within the provided table.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: CreateOrder => containing the current Store Picture.
    """
    pos_id, table, table_id, user_id = get_parameters(argv, msg)

    session_id = get_user_sessionid(pos_id, user_id)
    if session_id is None:
        raise Exception("$NO_SESSION_ID_FOUND")

    price_list = argv[3] if len(argv) > 3 and argv[3] else None
    orderid = create_order(pos_id, table, pricelist=price_list, sessionid=session_id)

    intrans = False
    success = False
    hasconn = False
    try:
        dbconn = get_db_connection(pos_id)
        hasconn = True

        dbconn.transaction_start()
        intrans = True

        dbconn.query("BEGIN TRANSACTION;")

        dbconn.pquery("registerServiceOrder", serviceId=table["serviceId"], orderId=orderid, posId=pos_id)
        dbconn.pquery("updateCurrentOrderId", posId=pos_id, orderId=orderid)
        dbconn.pquery("updateTableServiceStatus", serviceId=table["serviceId"], status="InProgress")
        success = True
    except Exception as _:
        sys_log_exception("Unexpected exception")
    finally:
        if intrans:
            dbconn.query("COMMIT TRANSACTION;" if success else "ROLLBACK TRANSACTION;")
        if hasconn:
            dbconn.transaction_end()

    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, '<Order orderId="{0}"/>'.format(orderid))
    store_modified_xml = get_store_picture_xml(pos_id, subject="STORE_MODIFIED", type="CreateOrder")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "CreateOrder", store_modified_xml)


def handle_set_current_order(argv, msg=None):
    """Creates a new POS order within the provided table.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param orderId        (argv[3])  Order identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    orderid = int(argv[3]) if len(argv) > 3 and argv[3] else None
    if not all([posid, userid, tableid, orderid, msg]):
        raise Exception("$INVALID_PARAMETERS")
    table = handle_list_tables([posid, None, tableid])
    if not table:
        raise Exception("$NO_TABLE_FOUND")
    table = table[0]
    orders = filter(lambda o: o["orderId"] == orderid, table.pop('orders', []))
    if not orders:
        raise Exception("$TABLE_ORDER_NOT_FOUND")
    sessionid = get_user_sessionid(posid, userid)
    recall_order(posid, orderid, sessionid, orders[0]["posId"], service_id=table["serviceId"])
    dbconn = get_db_connection(posid)
    dbconn.pquery("updateCurrentOrderId", posId=posid, orderId=orderid)
    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)


def handle_void_service_order(argv, msg=None):
    pos_id, table, table_id, user_id = get_parameters(argv, msg)
    order_id = int(argv[3]) if len(argv) > 3 and argv[3] else None

    orders = []
    for order in table["orders"]:
        if order["orderId"] == order_id:
            orders.append(order)

    if not orders:
        raise Exception("$TABLE_ORDER_NOT_FOUND")

    session_id = get_user_sessionid(pos_id, user_id)
    recall_order(pos_id, order_id, session_id, blk_notify=True, service_id=table["serviceId"])

    try:
        db_conn = get_db_connection(pos_id)
        db_conn.pquery("updateCurrentOrderState", state="VOIDED", orderId=order_id)
        void_order(pos_id, order_id, "0", True)
    except Exception as _:
        store_order(pos_id, blk_notify=True)

    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg)


def handle_total_service(argv, msg=None):
    """Total the orders of a service and produces a table picture.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param tipRate        (argv[3])  (optional)
                                        Tip rate to be applied to the totaled orders or the whole service.
       @param tipAmt         (argv[4])  (optional)
                                        Tip amount to be applied to the totaled orders or the whole service.
       @param saleType       (argv[5])  (optional)
                                        EAT_IN, TAKE_OUT, DRIVE_THRU, DELIVERY, etc.
       @return Reply msgbus message <msg>.
               Produces the following events:
               - subject: TABLE_TOTALED type: TableService => containing the current Table Picture;
               - subject: STORE_MODIFIED type: TableTotaled => containing the current Store Picture.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    tiprate = argv[3] if len(argv) > 3 and argv[3] else None
    tipamt = argv[4] if len(argv) > 4 and argv[4] else None
    saletype = argv[5] if len(argv) > 5 and argv[5] else "EAT_IN"

    if not all([posid, userid, tableid, msg]):
        raise Exception("$INVALID_PARAMETERS")
    table = handle_list_tables([posid, None, tableid])
    if not table:
        raise Exception("$NO_TABLE_FOUND")
    table = table[0]

    if int(table["status"]) != 4:
        raise Exception("$INVALID_TABLE_STATUS")

    if int(table.get("currentPOSId") or "-1") != int(posid):
        raise Exception("$INVALID_CURRENT_TABLE_POS")

    sessionid = get_user_sessionid(posid, userid)
    if sessionid is None:
        raise Exception("$NO_SESSION_ID_FOUND")
    # recall orders from other POS ids ...
    for order in (table.get("orders") or []):
        logger.debug("Recalling order")
        recall_order(posid, order["orderId"], sessionid, order["posId"], blk_notify=True, service_id=table["serviceId"])
        logger.debug("Recalled order")
        logger.debug("Storing order")
        store_order(posid, blk_notify=False)
        logger.debug("Stored order")
    # retrieves a list of all orders and its line numbers
    dbconn = get_db_connection(posid)
    cursor = dbconn.pselect("getServiceOrderItem", serviceId=table["serviceId"])
    service_order_items = [dict([(cursor.get_name(i), json.loads(row.get_entry(i)) if cursor.get_name(i) == "lineNumbers" else row.get_entry(i)) for i in range(cursor.cols())]) for row in cursor]
    if len(service_order_items) == 0:
        raise Exception("service_order_items cannot be empty when an order is being totaled")
    # create split orders based on the setup
    splitlist = []
    has_tip = any([tiprate, tipamt])
    splitobj = {
        "splitKey": DEFAULT_SPLIT_KEY,
        "splitOrderId": create_order(
            posid, table, storeorder=False, blk_notify=True, saletype=saletype,
            sessionid=sessionid, ordersubtype="SPLIT_SERVICE",
            custom_properties={"SPLIT_KEY": DEFAULT_SPLIT_KEY}
        )
    }
    new_order_id = splitobj["splitOrderId"]
    for item in service_order_items:
        for line in item["lineNumbers"]:
            splitobj.update({
                "originalOrderId": item["originalOrderId"],
                "lineNumber": line}
            )
            splitlist.append(deepcopy(splitobj))
    success = False
    intrans = False
    hasconn = False
    try:
        # initiate DB transaction
        dbconn.transaction_start()
        hasconn = True

        dbconn.query("BEGIN TRANSACTION;")
        intrans = True
        dbconn.pquery("registerServiceOrder", serviceId=table["serviceId"], orderId=new_order_id, posId=posid)
        dbconn.pquery("updateCurrentOrderId", posId=posid, orderId=new_order_id)
        # split original table orders in new orders for payment
        dbconn.pquery(
            "registerSplitService",
            serviceId=table["serviceId"],
            PreparedStringTable="json:{0}".format(json.dumps(splitlist))
        )
        dbconn.pselect(
            "splitServiceOrders",
            serviceId=table["serviceId"]
        )
        dbconn.query("COMMIT TRANSACTION;")
        intrans = False

        # totalize orders and apply previous tenders if available
        logger.debug("Totaling order")
        table_total = total_order(posid, blk_notify=(not has_tip))
        logger.debug("Totaled order")

        # determine tip amount and update totaled order and table service status
        dbconn.query("BEGIN TRANSACTION;")
        intrans = True
        tip_amount = "0.00"
        if has_tip:
            tipobj = {
                "splitKey": DEFAULT_SPLIT_KEY,
                "splitOrderId": new_order_id
            }

            total_items_tip = _get_total_amount_removing_products_without_tip(posid)
            if tiprate is not None:
                tip_amount = str((total_items_tip * (D(tiprate) / D("100"))).quantize(D("0.01")))
                tipobj["rate"] = tiprate
            elif tipamt is not None:
                tip_amount = str(D(tipamt).quantize(D("0.01")))
                tipobj["amount"] = tipamt
            tipobj["tip"] = tip_amount
            update_order_properties(posid, blk_notify=False, tip=tip_amount)
            dbconn.pquery(
                "registerServiceTip",
                serviceId=table["serviceId"],
                sessionId=sessionid,
                PreparedStringTable="json:{0}".format(
                    json.dumps([tipobj])
                )
            )
        table_total = str(D(table_total) + D(tip_amount))

        # update table service status, reply and send event
        dbconn.pquery("updateTableServiceStatus", serviceId=table["serviceId"], status="Totaled", totalAmount=str(table_total))
        success = True
    except Exception as _:
        logger.exception("Error totaling table")
    finally:
        if intrans:
            dbconn.query("COMMIT TRANSACTION;" if success else "ROLLBACK TRANSACTION;")
        if not success and new_order_id:
            try:
                dbconn.query("BEGIN TRANSACTION;")
                dbconn.pquery("resetSplitService", serviceId=table["serviceId"])
                dbconn.query("COMMIT TRANSACTION;")

                reset_current_order(posid)
            except Exception as _:
                logger.exception("Error on resetSplitService")
                dbconn.query("ROLLBACK TRANSACTION;")
        if hasconn:
            dbconn.transaction_end()
        if not success:
            raise Exception("$FAILED_TOTAL_SERVICE")

    table_picture_xml, event_xml = handle_table_picture([posid, tableid, True], subject="TABLE_TOTALED", type="TableService")
    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, table_picture_xml)
    mbcontext.MB_EasyEvtSend("TABLE_TOTALED", "TableService", event_xml, sourceid=int(posid))
    store_modified_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="TableTotaled")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "TableTotaled", store_modified_xml)


def _get_total_amount_removing_products_without_tip(pos_id):
    total_items_tip = 0
    order = etree.XML(order_picture(pos_id))
    for sale_line in order.findall("SaleLine"):
        if _product_generates_tip(sale_line):
            total_items_tip += D(sale_line.get("itemPrice") or 0)
    return total_items_tip


def _product_generates_tip(sale_line):
    return int(sale_line.get("partCode")) not in products_list_not_charge_tip


def handle_change_service_tip(argv, msg=None):
    """Total the orders of a service and produces a table picture.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param tipRate        (argv[3])  (optional)
                                        Tip rate to be applied to the totaled orders or the whole service.
       @param tipAmt         (argv[4])  (optional)
                                        Tip amount to be applied to the totaled orders or the whole service.
       @return Reply msgbus message <msg>.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    tiprate = argv[3] if len(argv) > 3 and argv[3] else None
    tipamt = argv[4] if len(argv) > 4 and argv[4] else None

    if not all([posid, userid, tableid, any([tipamt, tiprate]), msg]):
        raise Exception("$INVALID_PARAMETERS")
    table = handle_list_tables([posid, None, tableid])

    if not table:
        raise Exception("$NO_TABLE_FOUND")
    table = table[0]

    if not _table_is_totaled(table):
        raise Exception("$INVALID_TABLE_STATUS")

    sessionid = get_user_sessionid(posid, userid)
    if sessionid is None:
        raise Exception("$NO_SESSION_ID_FOUND")

    current_pos_order_state = table.get("currentOrderState")
    current_pos_order_id = table.get("currentPOSOrderID")
    if not current_pos_order_id or current_pos_order_state != "TOTALED":
        raise Exception("$INVALID_CURRENT_ORDER_STATUS")

    service_tips = []
    table_total = (table.get("totalAmount") or "0.00")
    current_tip_amount = (table.get("tipAmount") or "0.00")
    tip = {
        "splitKey": DEFAULT_SPLIT_KEY,
        "splitOrderId": current_pos_order_id,
        "totalAmount": str(D(table_total)-D(current_tip_amount))
    }
    if tiprate is not None:
       tip["rate"] = tiprate
    elif tipamt is not None:
        tip["amount"] = tipamt
    if "rate" in tip:
        tip["tip"] = str((D(tip["totalAmount"]) * (D(tip["rate"]) / D("100"))).quantize(D("0.01")))
    elif "amount" in tip:
        tip["tip"] = str(D(tip["amount"]).quantize(D("0.01")))
    service_tips.append(tip)
    dbconn = get_db_connection(posid)
    intrans = False
    hasconn = False
    success = False
    try:
        dbconn.transaction_start()
        hasconn = True
        dbconn.query("BEGIN TRANSACTION;")
        intrans = True
        update_order_properties(posid, blk_notify=False, orderid=str(current_pos_order_id), tip=tip["tip"])
        dbconn.pquery("updateTableServiceStatus", serviceId=table["serviceId"], status="Totaled", totalAmount=str(D(tip["totalAmount"])+D(tip["tip"])))
        dbconn.pquery("clearServiceTips", serviceId=table["serviceId"], orderId=current_pos_order_id, sessionId=sessionid)
        dbconn.pquery("clearServiceTenders", serviceId=table["serviceId"], orderId=current_pos_order_id, sessionId=sessionid)
        dbconn.pquery("registerServiceTip", serviceId=table["serviceId"], sessionId=sessionid, PreparedStringTable="json:{0}".format(json.dumps(service_tips)))
        success = True
    finally:
        if intrans:
            dbconn.query("COMMIT TRANSACTION;" if success else "ROLLBACK TRANSACTION;")
        if hasconn:
            dbconn.transaction_end()
    table_picture_xml, _ = handle_table_picture([posid, tableid])
    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, table_picture_xml)


def handle_close_service(argv, msg=None):
    """Finalizes the service, closing all related orders.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following events:
               - subject: TABLE_CLOSED type: TableService => containing the current Table Picture;
               - subject: STORE_MODIFIED type: TableClosed => containing the current Store Picture.
    """
    pos_id, table, table_id, user_id = get_parameters(argv, msg)

    if not _table_is_totaled(table):
        raise Exception("$INVALID_TABLE_STATUS")

    session_id = get_user_sessionid(pos_id, user_id)
    order = etree.XML(order_picture(pos_id))
    if D(order.get("dueAmount") or "0") > D("0"):
        raise Exception("$NOT_ALL_ORDERS_ARE_PAID")

    total_order_ids = [o['orderId'] for o in table.get('splitOrders') or []]
    try:
        tenders = order.findall("TenderHistory/Tender")
        last_tender = tenders[-1]
        tender_order(pos_id,
                     blk_notify=False,
                     tenderid=last_tender.get("tenderType"),
                     amount=last_tender.get("tenderAmount"),
                     donotclose=False,
                     ordertenderid=last_tender.get("tenderId"),
                     tipamount=last_tender.get("tip"))
    except Exception as _:
        for order in total_order_ids:
            order_xml = etree.XML(order_picture(pos_id, order))
            if order_xml.find(".//Order").get('state') != 'PAID':
                raise

    dbconn = get_db_connection(pos_id)
    service_id = table["serviceId"]
    # raise Exception("$NOT_ALL_ORDERS_ARE_PAID") - OK
    for order in (table.get("orders") or []):
        order_id = order['orderId']
        if order_id in total_order_ids:
            continue

        if order['state'] not in ('VOIDED', 'ABANDONED'):
            try:
                order_pos = order["posId"]
                recall_order(pos_id, order_id, session_id, srcposid=order_pos, blk_notify=True, service_id=service_id)
            except Exception as _:
                current_order = etree.XML(order_picture(pos_id))
                current_order_id = int(current_order.get('orderId'))
                current_order_state = current_order.get('state')

                if current_order_id != order_id and current_order_state not in ('IN_PROGRESS', 'TOTALED'):
                    temp_order = etree.XML(order_picture(pos_id, order_id))
                    temp_order = temp_order.find(".//Order")
                    temp_order_state = temp_order.get('state')

                    if temp_order_state not in ('VOIDED', 'ABANDONED'):
                        raise

                    dbconn.pquery("updateCurrentOrderState", posId=pos_id, orderId=order_id, state=temp_order_state)
                    order['state'] = temp_order_state

        # raise Exception("$NOT_ALL_ORDERS_ARE_PAID") - OK
        if order['state'] not in ('VOIDED', 'ABANDONED', 'PAID'):
            for retries in range(1, 3):
                try:
                    void_order(pos_id, order_id, blk_notify=True)
                    break
                except Exception as _:
                    sys_log_exception("Error voiding Order {} on POS {}".format(order_id, pos_id))
                    if retries == 3:
                        raise

    # raise Exception("$NOT_ALL_ORDERS_ARE_PAID") - OK
    table_picture_xml, event_xml = handle_table_picture([pos_id, table_id], subject="TABLE_CLOSED", type="TableService")
    dbconn.pquery("updateTableServiceStatus", serviceId=service_id, status="Closed")

    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, table_picture_xml)
    mbcontext.MB_EasyEvtSend("TABLE_CLOSED", "TableService", event_xml, sourceid=int(pos_id))
    store_modified_xml = get_store_picture_xml(pos_id, subject="STORE_MODIFIED", type="TableTotaled")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "TableClosed", store_modified_xml)


def handle_reopen_service(argv, msg=None):
    """Reopen previous totaled orders of a service and produces a table picture.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following events:
               - subject: TABLE_REOPENED type: TableService => containing the current Table Picture;
               - subject: STORE_MODIFIED type: TableReopened => containing the current Store Picture.
    """
    pos_id, table, table_id, user_id = get_parameters(argv, msg)

    if not _table_is_totaled(table):
        raise Exception("$INVALID_TABLE_STATUS")

    current_pos_order_state = table.get("currentOrderState")
    current_pos_order_id = table.get("currentPOSOrderID")
    dbconn = get_db_connection(pos_id)
    intrans = False
    hasconn = False
    success = False
    try:
        dbconn.transaction_start()
        hasconn = True
        dbconn.query("BEGIN TRANSACTION;")
        intrans = True

        if current_pos_order_id and current_pos_order_state in ("IN_PROGRESS", "TOTALED"):
            store_order(pos_id, blk_notify=False)

        dbconn.pquery("resetSplitService", serviceId=table["serviceId"])
        dbconn.pquery("updateTableServiceStatus", serviceId=table["serviceId"], status="InProgress")

        success = True
    finally:
        if intrans:
            dbconn.query("COMMIT TRANSACTION;" if success else "ROLLBACK TRANSACTION;")
        if hasconn:
            dbconn.transaction_end()

    table_picture_xml, event_xml = handle_table_picture([pos_id, table_id], subject="TABLE_REOPENED", type="TableService")
    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, table_picture_xml)
    mbcontext.MB_EasyEvtSend("TABLE_REOPENED", "TableService", event_xml, sourceid=int(pos_id))
    store_modified_xml = get_store_picture_xml(pos_id, subject="STORE_MODIFIED", type="TableTotaled")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "TableReopened", store_modified_xml)


def handle_recall_service(argv, msg=None):
    """Recover the service for a Table.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: RecallService => containing the current Store Picture.
    """
    pos_id, table, table_id, user_id = get_parameters(argv, msg)

    current_pos_id = table.get("currentPOSId")
    if current_pos_id is not None and int(current_pos_id) != pos_id:
        raise Exception("$TABLE_RECALLED_IN_ANOTHER_STATION")

    if int(table["status"]) in (1, 5, 7):
        raise Exception("$INVALID_TABLE_STATUS")

    sessionid = get_user_sessionid(pos_id, user_id)
    dbconn = get_db_connection(pos_id)
    dbconn.pquery("recallService", serviceId=table["serviceId"], posId=pos_id, sessionId=sessionid)

    if _table_is_totaled(table):
        totaled_orders = table.pop("splitOrders", None)
        if totaled_orders is not None:
            for split_order in totaled_orders:
                __last_order = (split_order == totaled_orders[-1])
                if not __last_order:
                    store_order(pos_id, blk_notify=False)
                    continue

                current_pos_order_id = table.get("currentPOSOrderID")
                current_pos_order_state = table.get("currentOrderState")
                if current_pos_order_id is not None and current_pos_order_id != str(split_order['orderId']):
                    if current_pos_order_state != 'STORED':
                        store_order(pos_id, blk_notify=False)

                try:
                    recall_order(pos_id, split_order['orderId'], sessionid, blk_notify=__last_order, service_id=table["serviceId"])
                    dbconn.pquery("updateCurrentOrderId", posId=pos_id, orderId=split_order['orderId'])
                except Exception as _:
                    order = etree.XML(order_picture(pos_id, split_order['orderId']))
                    order = order.find(".//Order")
                    split_order['state'] = order.get('state')
                    if order.get('state') in ('PAID', 'TOTALED'):
                        dbconn.pquery("updateCurrentOrderId", posId=pos_id, orderId=order.get('orderId'))
                    elif order.get('state') in ('VOIDED', 'SYSTEM_VOIDED'):
                        dbconn.pquery("resetSplitService", serviceId=table["serviceId"])
                        dbconn.pquery("updateTableServiceStatus", serviceId=table["serviceId"], status="InProgress")
                        break
                    else:
                        dbconn.pquery("storeService", serviceId=table["serviceId"], posId=pos_id)
                        raise

                if split_order['state'] not in ('PAID', 'TOTALED'):
                    total_order(pos_id, blk_notify=False)

    table_picture_xml, _ = handle_table_picture([pos_id, table_id])
    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, table_picture_xml)
    store_modified_xml = get_store_picture_xml(pos_id, subject="STORE_MODIFIED", type="RecallService")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "RecallService", store_modified_xml)


def handle_store_service(argv, msg=None):
    """Releases the Table saving the current service.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following events:
               - subject: TABLE_STORED type: TableService => containing the current Table Picture.
               - subject: STORE_MODIFIED type: ServiceStored => containing the current Store Picture.
    """
    pos_id, table, table_id, user_id = get_parameters(argv, msg)

    current_pos_id = table.get("currentPOSId")
    if not current_pos_id or int(current_pos_id) != pos_id:
        raise Exception("$TABLE_NOT_RECALLED_IN_THIS_STATION")

    if _table_is_totaled(table):
        totaled_orders = table.pop("splitOrders", None)
        if totaled_orders is not None:
            for split_order in totaled_orders:
                if split_order["state"] == "PAID":
                    sys_log_exception("Table is already PAID")
                    raise Exception("$COULD_NOT_DESELECT_TABLE")

    dbconn = get_db_connection(pos_id)
    current_order_id = table.get("currentOrderId")
    if current_order_id is not None:
        try:
            dbconn.pquery("registerServiceOrder", serviceId=table["serviceId"], orderId=current_order_id, posId=pos_id)
        except Exception as _:
            sys_log_exception("Unexpected exception")
            raise Exception("$COULD_NOT_DESELECT_TABLE")
        store_order(pos_id)

    try:
        dbconn.pquery("storeService", serviceId=table["serviceId"], posId=pos_id)
    except Exception as _:
        sys_log_exception("Unexpected exception")
        raise Exception("$COULD_NOT_DESELECT_TABLE")

    table_picture_xml, event_xml = handle_table_picture([pos_id, table_id], subject="TABLE_STORED", type="TableService")
    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, table_picture_xml)
    mbcontext.MB_EasyEvtSend("TABLE_STORED", "TableService", event_xml, sourceid=int(pos_id))
    store_modified_xml = get_store_picture_xml(pos_id, subject="STORE_MODIFIED", type="ServiceStored")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "ServiceStored", store_modified_xml)


def handle_register_service_tender(argv, msg=None):
    """Register a tender (payment) for the current service in the provided Table identification.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param tenderid       (argv[3])  A known tender type identification
       @param amount         (argv[4])  (optional) the amount tendered. it must be a string with cents after a period character (e.g. 5.99)
       @param tenderdetail   (argv[5])  (optional) additional tender information
       @return Reply msgbus message <msg>.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    tenderid = argv[3] if len(argv) > 3 and argv[3] else None
    amount = argv[4] if len(argv) > 4 and argv[4] else None
    tenderdetail = argv[5] if len(argv) > 5 and argv[5] else None
    if not all([posid, userid, tableid, tenderid, msg]):
        raise Exception("$INVALID_PARAMETERS")
    table = handle_list_tables([posid, None, tableid])
    if not table:
        raise Exception("$NO_TABLE_FOUND")
    table = table[0]
    if not _table_is_totaled(table):
        raise Exception("$INVALID_TABLE_STATUS")
    sessionid = get_user_sessionid(posid, userid)
    current_pos_order_state = table.get("currentOrderState")
    current_pos_order_id = table.get("currentPOSOrderID")
    if not current_pos_order_id or current_pos_order_state != "TOTALED":
        raise Exception("$INVALID_CURRENT_ORDER_STATUS")
    totaltendered = D(0)
    amount = D(amount) if amount is not None else None
    totaltenderamount = amount if amount is not None else D(0)
    order = etree.XML(order_picture(posid))
    due_amount = D(order.get("dueAmount") or "0.00")
    tip_amount = D(order.get("tip") or "0.00")
    if due_amount <= D(0):
        msg.token = TK_SYS_NAK
        mbcontext.MB_EasyReplyMessage(msg)
        return
    if amount is None:
        amount = due_amount

    tender_tip = calculate_tender_tip(amount, due_amount, tip_amount)

    tender_order(
        posid,
        blk_notify=False,
        donotclose=True,
        tenderid=tenderid,
        amount=str(amount),
        tipamount=str(tender_tip),
        tenderdetail=(tenderdetail or "")
    )
    totaltendered += amount
    if totaltendered > D(0):
        dbconn = get_db_connection(posid)
        dbconn.pquery("registerServiceTenders",
                      serviceId=table["serviceId"],
                      tenderId=tenderid,
                      totalTenderAmount=str(totaltenderamount),
                      PreparedIntegerTable=(','.join([current_pos_order_id])),
                      sessionId=sessionid)
    table_picture_xml, _ = handle_table_picture([posid, tableid])
    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, table_picture_xml)


def calculate_tender_tip(amount, due_amount, tip_amount):
    due_amount_without_tip = due_amount - tip_amount
    if not tender_has_tip(amount, due_amount_without_tip):
        return 0

    if tender_pays_products(due_amount_without_tip):
        if tender_has_change(amount, due_amount):
            return due_amount - due_amount_without_tip
        else:
            return amount - due_amount_without_tip

    if tender_has_change(amount, due_amount):
        return due_amount

    return amount


def tender_has_tip(amount, due_amount_without_tip):
    return amount > due_amount_without_tip


def tender_pays_products(due_amount_without_tip):
    return due_amount_without_tip > 0


def tender_has_change(amount, due_amount):
    return amount > due_amount


def handle_clear_service_tenders(argv, msg=None):
    """Removes all registered service tenders (payments) in the provided Table.
       @param posId           (argv[0])  Current POS source
       @param userId          (argv[1])  User identification
       @param tableId         (argv[2])  Table identification.
                                         This parameter may be obtained by a call to LIST_TABLES.
       @param serviceTenderId (argv[3])  (optional) If set clears only that service tender id.
       @return Reply msgbus message <msg>.
    """
    pos_id, table, table_id, user_id = get_parameters(argv, msg)

    if not _table_is_totaled(table):
        raise Exception("$INVALID_TABLE_STATUS")

    service_tender_id = argv[3] if len(argv) > 3 and argv[3] else None
    current_pos_order_state = table.get("currentOrderState")
    current_pos_order_id = table.get("currentPOSOrderID")
    if not current_pos_order_id or current_pos_order_state != "TOTALED":
        raise Exception("$INVALID_CURRENT_ORDER_STATUS")
    sessionid = get_user_sessionid(pos_id, user_id)
    dbconn = get_db_connection(pos_id)
    clear_tender(pos_id, blk_notify=False)
    dbconn.pquery("clearServiceTenders", serviceId=table["serviceId"], serviceTenderId=service_tender_id, sessionId=sessionid)
    table_picture_xml, _ = handle_table_picture([pos_id, table_id])
    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, table_picture_xml)


def handle_table_ready4service(argv, msg=None):
    """Makes the table available again.
       @param posId          (argv[0])  Current POS source
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: TableReady => containing the current Store Picture.
    """
    posid = int(argv[0])
    userid = argv[1] if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    if not all([posid, userid, tableid, msg]):
        raise Exception("$INVALID_PARAMETERS")
    table = handle_list_tables([posid, None, tableid])
    if not table:
        raise Exception("$NO_TABLE_FOUND")
    table = table[0]
    if int(table["type"]) != 1:
        raise Exception("$ONLY_SEAT_TABLES_CAN_BE_MADE_AVAILABLE")
    if int(table["status"]) != 7:
        raise Exception("$INVALID_TABLE_STATUS")
    dbconn = get_db_connection(posid)
    if "serviceId" in table and table["serviceId"]:
        dbconn.pquery("updateTableServiceStatus", serviceId=table["serviceId"], status="Available")
    else:
        dbconn.pquery("updateTableServiceStatus", tableId=table["id"], status="Available")
    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)
    store_modified_xml = get_store_picture_xml(posid, subject="TABLE_READY", type="TableService")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "TableReady", store_modified_xml)


def handle_move_table(argv, msg=None):
    """Move orders from one table to another and close the source table.
       @param posId          (argv[0])  Current POS Id
       @param userId         (argv[1])  User identification
       @param fromTableId    (argv[2])  Source table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param destTableId    (argv[3])  Destination table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param numberOfSeats  (argv[4])  (optional) The number of seats if the destination table is available.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: MoveTable => containing the current Store Picture.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    fromtableid = argv[2] if len(argv) > 2 and argv[2] else None
    desttableid = argv[3] if len(argv) > 3 and argv[3] else None
    noseats = int(argv[4]) if len(argv) > 4 and argv[4] else None
    if not all([posid, userid, fromtableid, desttableid, msg]):
        raise Exception("$INVALID_PARAMETERS")
    tables = filter(lambda t: (t["id"] in (fromtableid, desttableid)), handle_list_tables([posid]))
    if len(tables) != 2:
        raise Exception("$NO_TABLE_FOUND")
    fromTable = tables[0] if tables[0]["id"] == fromtableid else tables[1]
    destTable = tables[0] if tables[0]["id"] == desttableid else tables[1]

    if int(destTable["type"]) != 1:  # Seat
        raise Exception("$INVALID_DEST_TABLE")

    if int(fromTable["status"]) != 4:            # In-Progress
        raise Exception("$INVALID_TABLE_STATUS")

    if int(destTable["status"]) not in [1, 3, 4]:     # Available, Seated, In-Progress
        raise Exception("$INVALID_TABLE_STATUS")

    dbconn = get_db_connection(posid)
    newService = None
    if int(destTable["status"]) == 1:
        cursor = dbconn.pselect("startService",
                                posId=posid, userId=userid,
                                businessPeriod=fromTable["businessPeriod"], typeId=1,
                                tableId=destTable["id"], numberOfSeats=noseats, statusDescr="InProgress")
        for row in cursor:
            newService = dict([(cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols())])
            break
    dbconn.pquery("moveTable", fromServiceId=fromTable["serviceId"], destServiceId=(newService["serviceId"] if newService is not None else destTable["serviceId"]), numberOfSeats=noseats)

    destTablePicture = etree.XML(handle_table_picture([posid, desttableid])[0])
    destOrders = destTablePicture.findall(".//Order")
    for destOrder in destOrders:
        orderid = destOrder.get("orderId")
        sessionid = get_user_sessionid(posid, userid)
        srcposid = str(int(destOrder.get("originatorId")[3:]))
        recall_order(posid, orderid, sessionid, srcposid, True, destTablePicture.get("serviceId"))
        properties = etree.Element("Properties")
        etree.SubElement(properties, "Property", {"key": "TABLE_ID", "value": destTablePicture.get("id")})

        set_order_properties(posid, False, orderid, properties)
        store_order(posid)

    if int(destTable["status"]) in [2, 3]:
        dbconn.pquery("updateTableServiceStatus", serviceId=destTable["serviceId"], status="InProgress")

    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)
    store_modified_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="MoveTable")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "MoveTable", store_modified_xml)


def handle_join_tables(argv, msg=None):
    """Join 2 tables as a single service, moving all orders to the destination table.
       @param posId          (argv[0])  Current POS Id
       @param userId         (argv[1])  User identification
       @param fromTableId    (argv[2])  Source table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param destTableId    (argv[3])  Destination table identification.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param numberOfSeats  (argv[4])  (optional) The number of seats if the destination table is available.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: JoinTable => containing the current Store Picture.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    fromtableid = argv[2] if len(argv) > 2 and argv[2] else None
    desttableid = argv[3] if len(argv) > 3 and argv[3] else None
    noseats = int(argv[4]) if len(argv) > 4 and argv[4] else None

    if not all([posid, userid, fromtableid, desttableid, msg]):
        raise Exception("$INVALID_PARAMETERS")

    tables = filter(lambda t: (t["id"] in (fromtableid, desttableid)), handle_list_tables([posid]))

    if len(tables) != 2:
        raise Exception("$NO_TABLE_FOUND")

    fromTable = tables[0] if tables[0]["id"] == fromtableid else tables[1]
    destTable = tables[0] if tables[0]["id"] == desttableid else tables[1]

    fromTableLinks = fromTable["linkedTables"]

    dbconn = get_db_connection(posid)

    if fromTableLinks:
        dbconn.pquery("unlinkTables", serviceId=fromTable["serviceId"])

        for linkedTable in fromTableLinks:
            dbconn.pquery("linkTable", fromTableId=linkedTable,
                          destServiceId=destTable["serviceId"],
                          numberOfSeats=noseats)

    if int(fromTable["status"]) not in (1, 2, 3, 4):  # Available, Waiting2BSeated, Seated or InProgress
        raise Exception("$INVALID_TABLE_STATUS")

    if int(destTable["status"]) not in (1, 2, 3, 4):  # Available, Waiting2BSeated, Seated or InProgress
        raise Exception("$INVALID_TABLE_STATUS")

    newService = None

    if int(destTable["status"]) == 1:
        cursor = dbconn.pselect("startService",
                                posId=posid, userId=userid,
                                businessPeriod=fromTable["businessPeriod"], typeId=1,
                                tableId=destTable["id"], numberOfSeats=noseats, statusDescr="InProgress")
        for row in cursor:
            newService = dict([(cursor.get_name(i), row.get_entry(i)) for i in range(cursor.cols())])
            break

    if int(fromTable["status"]) == 1:
        dbconn.pquery("linkTable", fromTableId=fromTable["id"], destServiceId=(newService["serviceId"] if newService is not None else destTable["serviceId"]), numberOfSeats=noseats)
    else:
        dbconn.pquery("joinTables", fromServiceId=fromTable["serviceId"], destServiceId=(newService["serviceId"] if newService is not None else destTable["serviceId"]), numberOfSeats=noseats)

    if int(destTable["status"]) in [2, 3] and int(fromTable["status"]) == 4:
        dbconn.pquery("updateTableServiceStatus", serviceId=destTable["serviceId"], status="InProgress")

    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)
    store_modified_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="JoinTables")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "JoinTables", store_modified_xml)


def handle_unlink_tables(argv, msg=None):
    """Releases 2 previously joined tables. Their status will get closed.
       @param posId          (argv[0])  Current POS Id
       @param userId         (argv[1])  User identification
       @param tableId        (argv[2])  Major table identification. Table which other tables are linked to.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param unlinkTableId  (argv[3])  (optional) Specific table to unlink. If none is provided, all tables linked to the major one will be release.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: UnlinkTables => containing the current Store Picture.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    ulnktableid = argv[3] if len(argv) > 3 and argv[3] else None
    if not all([posid, userid, tableid, msg]):
        raise Exception("$INVALID_PARAMETERS")
    tables = filter(lambda t: (t["id"] in (tableid, ulnktableid)), handle_list_tables([posid]))
    if not tables:
        raise Exception("$NO_TABLE_FOUND")
    majorTable = None
    tableUnlink = None
    while tables:
        table = tables.pop()
        if table["id"] == tableid:
            majorTable = table
            continue
        if table["id"] == ulnktableid:
            tableUnlink = table
    if ulnktableid is not None and tableUnlink is None:
        raise Exception("$UNLINK_TABLE_NOT_FOUND")
    if tableUnlink is not None and int(tableUnlink["status"]) != 5:
        raise Exception("$INVALID_TABLE_STATUS")
    dbconn = get_db_connection(posid)
    if tableUnlink:
        dbconn.pquery("unlinkTables", serviceId=majorTable["serviceId"], tableId=tableUnlink["id"])
    else:
        dbconn.pquery("unlinkTables", serviceId=majorTable["serviceId"])
    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)
    store_modified_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="UnlinkTables")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "UnlinkTables", store_modified_xml)


def handle_store_picture(argv, msg=None):
    """Gets current Store picture.
       @param posId          (argv[0])  Current POS Id
       @param forceUpdate    (argv[1])  (optional) Force a <STORE_MODIFIED> event to propagate the current state
       @return Reply msgbus message <msg> and produces an event (subject: STORE_MODIFIED type: StorePicture)
               containing the current Store Picture.
    """
    posid = int(argv[0])
    force = (int(argv[1]) > 0) if len(argv) > 1 and argv[1] else False
    store_picture_xml = get_store_picture_xml(posid)
    msg.token = TK_SYS_ACK
    mbcontext.MB_ReplyMessage(msg, FM_XML, store_picture_xml)
    if force:
        event_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="StorePicture")
        mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "StorePicture", event_xml)


def handle_change_table_user(argv, msg=None):
    """Changes the service operator
       @param posId          (argv[0])  Current POS Id
       @param userId         (argv[1])  User Id to transfer service to
       @param tableId        (argv[2])  (optional) Table identification. If not provided, <serviceId> must be provided.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param serviceId      (argv[3])  (optional) Service identification. If not provided, <tableId> must be provided.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: TableUserChanged => containing the current Store Picture.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    tableid = argv[2] if len(argv) > 2 and argv[2] else None
    serviceid = int(argv[3]) if len(argv) > 3 and argv[3] else None
    if not all([posid, userid, any([tableid, serviceid]), msg]):
        raise Exception("$INVALID_PARAMETERS")
    if serviceid is None:
        table = handle_list_tables([posid, None, tableid])
        if not table:
            raise Exception("$NO_TABLE_FOUND")
        table = table[0]
        serviceid = int(table["serviceId"])
    dbconn = get_db_connection(posid)
    dbconn.pquery("updateServiceUser", serviceId=serviceid, userId=userid)
    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)
    event_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="TableUserChanged")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "TableUserChanged", event_xml)


def handle_change_number_of_seats(argv, msg=None):
    """Changes the service number of seats
       @param posId          (argv[0])  Current POS Id
       @param userId         (argv[1])  User Id to transfer service to
       @param numberOfSeats  (argv[2])  The new number of seats
       @param tableId        (argv[3])  (optional) Table identification. If not provided, <serviceId> must be provided.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @param serviceId      (argv[4])  (optional) Service identification. If not provided, <tableId> must be provided.
                                        This parameter may be obtained by a call to LIST_TABLES.
       @return Reply msgbus message <msg>.
               Produces the following event:
               - subject: STORE_MODIFIED type: NOSeatsChanged => containing the current Store Picture.
    """
    posid = int(argv[0])
    userid = int(argv[1]) if len(argv) > 1 and argv[1] else None
    noseats = int(argv[2]) if len(argv) > 2 and argv[2] else None
    tableid = argv[3] if len(argv) > 3 and argv[3] else None
    serviceid = int(argv[4]) if len(argv) > 4 and argv[4] else None
    if not all([posid, userid, noseats, any([tableid, serviceid]), msg]):
        raise Exception("$INVALID_PARAMETERS")
    if serviceid is None:
        table = handle_list_tables([posid, None, tableid])
        if not table:
            raise Exception("$NO_TABLE_FOUND")
        table = table[0]
        serviceid = int(table["serviceId"])
    dbconn = get_db_connection(posid)
    dbconn.pquery("updateServiceNumberOfSeats", serviceId=serviceid, numberOfSeats=noseats)
    msg.token = TK_SYS_ACK
    mbcontext.MB_EasyReplyMessage(msg)
    event_xml = get_store_picture_xml(posid, subject="STORE_MODIFIED", type="NOSeatsChanged")
    mbcontext.MB_EasyEvtSend("STORE_MODIFIED", "NOSeatsChanged", event_xml)


def handle_event(msg):
    """Handle an incoming event"""
    msg.token = TK_SYS_NAK
    mbcontext.MB_EasyReplyMessage(msg)
    try:
        params = []
        if msg.data:
            params = msg.data.split('\0')
        if params and len(params) > 4:
            if params[1] == "ORDER_MODIFIED" and params[2] != "ORDER_PROPERTIES_CHANGED":
                logger.debug("Handling: %s %s", params[1], params[2:])
                pos_id = params[4]
                order = etree.XML(params[0])
                order = order.find(".//Order")
                order_id = order.get("orderId")
                state = order.get("state")

                dbconn = get_db_connection(pos_id)
                dbconn.pquery("updateCurrentOrderState", posId=pos_id, orderId=order_id, state=state)
                logger.debug("Successfully processed: %s", params[1])
    except Exception as _:
        sys_log_exception("Unexpected exception")
        logger.exception("Unexpected exception")


lock_message = threading.Lock()
handling_message = {}


def handle_message(msg):
    global handling_message
    pos_id = None
    error_message = None
    handling = False

    try:
        msg.token = TK_SYS_NAK
        msg_params = msg.data.split('\0')
        check_message_parameters(msg, msg_params)

        logger.debug("Handling: %s %s", msg_params[0], msg_params[1:])
        func = globals().get("handle_{0}".format(msg_params[0].lower()))
        pos_id = msg_params[1]
        with lock_message:
            if int(pos_id) not in handling_message:
                handling_message[int(pos_id)] = False

        time_limit = (time.time() + 5.0)
        while time.time() < time_limit:
            with lock_message:
                if handling_message[int(pos_id)] is False:
                    handling = True
                    handling_message[int(pos_id)] = True
                    break
            time.sleep(0.100)
        else:
            logger.error("ERROR - Nested Operations POS {0} / {1}".format(pos_id, msg_params[0]))
            raise Exception("$NESTED_TABLE_OPERATIONS")

        if func and callable(func):
            func(msg_params[1:], msg)
            msg = None  # at this point, the message was already replied

        logger.debug("Successfully processed: %s", msg_params[0])
    except Exception as e:
        sys_log_exception("Error handling message on Table Service")
        logger.exception("Error handling message on Table Service")
        error_message = str(e)
    finally:
        with lock_message:
            if pos_id is not None and handling:
                handling_message[int(pos_id)] = False

    if msg is not None:
        if error_message is not None:
            mbcontext.MB_ReplyMessage(msg, FM_STRING, error_message)
        else:
            mbcontext.MB_EasyReplyMessage(msg)


def check_message_parameters(msg, msg_params):
    if msg.format != FM_PARAM or msg.data is None:
        raise Exception("$INVALID_PARAMETERS")
    if len(msg_params) < 2:
        raise Exception("$INVALID_PARAMETERS")
    if msg_params[0] not in MANAGED_TOKENS:
        raise Exception("$INVALID_PARAMETERS")


def main_loop():
    global thread_pool_size
    mbcontext.MB_EasyEvtSubscribe("ORDER_MODIFIED")
    pool = ThreadPool(thread_pool_size)

    while True:
        msg = mbcontext.MB_EasyGetMessage()

        if (not msg) or (msg.token == TK_CMP_TERM_NOW):
            mbcontext.MB_EasyReplyMessage(msg)
            break
        elif msg.token == TK_EVT_EVENT:
            pool.add_task(handle_event, msg)
        elif msg.token == TK_CMP_MESSAGE:
            pool.add_task(handle_message, msg)
        else:
            msg.token = TK_SYS_NAK
            mbcontext.MB_EasyReplyMessage(msg)
    pool.wait_complete()


def main():
    """Main entry point of the component."""
    try:
        init_msgbus()
        init_persistence()
        read_config()
        start_cache_objects()
        reset_store_layout_setup()
        main_loop()
    except KeyboardInterrupt:
        sys.exit(SE_USERCANCEL)
