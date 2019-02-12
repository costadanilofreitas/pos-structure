# -*- coding: utf-8 -*-
import datetime
import json
from xml.etree import cElementTree as etree

from xml.etree import cElementTree as eTree
import pyscripts

from sysact_bk import validar_cpf
from msgbus import TK_POS_USERLOGOUT, FM_PARAM, TK_POS_BUSINESSEND, TK_SYS_ACK, TK_POS_BUSINESSBEGIN, TK_POS_USEROPEN, \
    TK_SYS_NAK, TK_POS_USERLOGIN, TK_CMP_MESSAGE, TK_EVT_EVENT
from sysactions import action, get_model, get_posot, has_operator_opened, send_message, \
    authenticate_user, mbcontext, \
    AuthenticationFailed, get_pricelist, has_current_order, get_current_order, show_info_message, \
    check_current_order, \
    show_messagebox, StopAction
from systools import sys_log_info, sys_log_exception, sys_log_error
from posot import OrderTakerException
from posactions import check_customer_name, doSale, doOption
from ui import get_product_nav
from persistence import Driver as DBDriver

# COMMENT HERE
# import sys
# import os
# debugPath = '../python/pycharm-debug.egg'
# if os.path.exists(debugPath):
#     try:
#         sys.path.index(debugPath)
#     except:
#         sys.path.append(debugPath)
#     import pydevd

# Use the line below in the function you want to debug
# UNTIL HERE

# usecs per second
USECS_PER_SEC = 1000000

# Kiosk product context
KIOSK_CONTEXT = '1'

@action
def doStartKioskOrder(posid):
    # TODO: user_id for Kiosk
    user_id = 2718
    user_password = 2818
    # void order in progress, if any
    doVoidKioskOrder(posid)
    model = get_model(posid)
    posot = get_posot(model)
    state = None
    pos_state = model.find("PosState")
    if pos_state is not None:
        state = pos_state.get("state")
    if state == "BLOCKED":
        try:
            # try to logout all users
            while has_operator_opened(model):
                user_ids = [int(op.get("id")) for op in model.findall("Operators/Operator") if op.get("state") in ("LOGGEDIN", "OPENED")]
                for userid in user_ids:
                    send_message("POS%d" % int(posid), TK_POS_USERLOGOUT, FM_PARAM, "%s\0%s" % (posid, userid))
                model = get_model(posid)

            # close day automatically
            msg = send_message("POS%d" % int(posid), TK_POS_BUSINESSEND, FM_PARAM, str(posid), timeout=90 * USECS_PER_SEC)
            if msg.token == TK_SYS_ACK:
                sys_log_info("Day closed successfully on Kiosk id: %s" % posid)
        except:
            sys_log_exception("Error closing business day on Kiosk id: %s" % posid)

    if state in ("CLOSED", "BLOCKED", "UNDEFINED"):
        try:
            # open day automatically
            bday = datetime.datetime.now().strftime("%Y%m%d")
            sys_log_info("Opening business day on Kiosk id: %s" % posid)
            msg = send_message("POS%d" % int(posid), TK_POS_BUSINESSBEGIN, FM_PARAM, "%s\0%s" % (posid, bday), timeout=90 * USECS_PER_SEC)
            if msg.token == TK_SYS_ACK:
                sys_log_info("Day opened successfully on Kiosk id: %s" % posid)
        except:
            sys_log_exception("Error opening business day on Kiosk id: %s" % posid)

    if not has_operator_opened(model):
        try:
            userinfo = authenticate_user(int(user_id), int(user_password))
            longusername = userinfo["LongName"]
            # open operator
            msg = mbcontext.MB_EasySendMessage("POS%d" % int(posid), token=TK_POS_USEROPEN, format=FM_PARAM, data='\0'.join([str(posid), str(user_id), '0', str(longusername)]))
            if msg.token == TK_SYS_NAK:
                sys_log_error("$OPERATION_FAILED")
                return
            # login the user
            msg = mbcontext.MB_EasySendMessage("POS%d" % int(posid), token=TK_POS_USERLOGIN, format=FM_PARAM, data='\0'.join([str(posid), str(user_id), str(longusername)]))
            if msg.token != TK_SYS_ACK:
                sys_log_error("$OPERATION_FAILED")
                return
        except AuthenticationFailed, ex:
            sys_log_error("$%s" % ex.message)

    posot.createOrder(posid, pricelist=get_pricelist(model))


@action
def doVoidKioskOrder(posid):
    model = get_model(posid)
    posot = get_posot(model)
    if has_current_order(model):
        order = get_current_order(model)
        try:
            if order and order.get("state") in ("IN_PROGRESS", "TOTALED"):
                posot.voidOrder(int(posid), lastpaidorder=0)
                setCardsPayment(posid, 0)
                setRemainingPayment(posid, 0)
                addValuePayment(posid, 0)
        except OrderTakerException, e:
            show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@action
def doResetModifiers(posid, line_number, level, item_id, part_code):
    model = get_model(posid)
    posot = get_posot(model)
    order = get_current_order(model)
    nextlevel = int(level) + 1
    item = "{0}.{1}".format(item_id, part_code)
    current_modifiers = [line for line in order.findall("SaleLine") if line.get("itemId") == item and line.get("lineNumber") == line_number]
    if not len(current_modifiers):
        # nothing was modified
        return
    modifiers_to_change = []
    for modifier in current_modifiers:
        def_qty = modifier.get("defaultQty")
        if modifier.get("qty") != def_qty:
            modifiers_to_change.append((modifier.get("partCode"), def_qty))

    posot.blkopnotify = True
    for pcode, qty in modifiers_to_change:
        posot.changeModifier(posid, line_number, item, nextlevel, pcode, qty)
    posot.blkopnotify = False
    posot.updateOrderProperties(posid, saletype=order.get("saleTypeDescr"))


@action
def doUpdateMedia(posid, *args):
    res = '{}'
    try:
        msg = mbcontext.MB_EasySendMessage('MediaManager', TK_EVT_EVENT, format=FM_PARAM, data='\0MediaManager\0UpdateMedia\0true\01\01\0', timeout=5000000)
        res = json.loads(msg.data)
        show_messagebox(posid, message="{0} arquivos enfileirados para download".format(res.get("queued", 0)), icon="info", timeout=180000)
    except:
        sys_log_exception("Exception retrieving media data")
    return res


@action
def getMediaData(posid, *args):
    res = '{}'
    try:
        msg = mbcontext.MB_EasySendMessage('MediaManager', TK_CMP_MESSAGE, data='GetMediaData', timeout=5000000)
        res = msg.data
    except:
        sys_log_exception("Exception retrieving media data")
    return res


@action
def doSaveCustomerInfo(posid, name, cpf=''):
    model = get_model(posid)

    check_current_order(posid, model=model, need_order=True)

    errors = []

    if not name:
        errors.append(['name', '$EMPTY_NAME_ERROR'])
    if not check_customer_name(posid, name, silent=True):
        errors.append(['name', '$BLACKLIST_NAME_ERROR'])

    posot = get_posot(model)

    if cpf:
        if not validar_cpf(cpf):
            errors.append(['doc', '$INVALID_CPF_ERROR'])

    if errors:
        return json.dumps(errors)

    posot.setOrderCustomProperty('CUSTOMER_NAME', name)
    if cpf:
        posot.setOrderCustomProperty('CUSTOMER_DOC', cpf)


@action
def doSavePaymentMethod(posid, method):
    model = get_model(posid)

    check_current_order(posid, model=model, need_order=True)

    errors = []

    if not method:
        errors.append(['method', '$EMPTY_PAYMENT_METHOD_ERROR'])

    posot = get_posot(model)
    if method == "RESET_PAYMENT_SCREEN":
        posot.setOrderCustomProperty('CUSTOMER_PAYMENT_METHOD', 'clear')
        return

    posot.setOrderCustomProperty('CUSTOMER_PAYMENT_METHOD', method)


@action
def doSaleMultiItems(posid, items, context):
    """
    Sale a group of items with quantity

    :param context: context which the product must be sold
    :param items: a json with the partcode as key and amount of items as value
    """
    PLU = 0
    QTY = 1

    def sale_items(item):
        if item[QTY] <= 0:
            return
        doSale(posid, '{}.{}'.format(context, item[PLU]), item[QTY], '', '')

    map(sale_items, json.loads(items).items())


@action
def doSetCustomerAsOfAge(posid, is_of_age):
    """
    Set if customer is either underage or of age

    :param is_of_age: "true" if user is of age, "false" otherwise
    """

    model = get_model(posid)
    posot = get_posot(model)
    posot.setOrderCustomProperty("CUSTOMER_IS_OF_AGE", is_of_age)


@action
def getKioskConfig(posid):
    """
    Get kiosk configuration parameters

    :return: json with all kiosk-related configurations
    """
    # TODO: get kiosk configuration correctly
    params = {
        'descr_id': 1
    }
    conn = None
    try:
        conn = DBDriver().open(pyscripts.mbcontext, service_name="Persistence")
        cursor = conn.pselect("getDescriptions", **params)
        descriptions = {row.get_entry(0): row.get_entry(1) for row in cursor}
    finally:
        if conn:
            conn.close()

    config = {
        'supportedLangs': ['en', 'es', 'pt', 'ja'],
        'screenTimeout': 40,
        'cancelTimeoutWindow': 6,
        'topBannerTimeout': 5,
        'alcoholics': ['160001'],
        'baseContext': KIOSK_CONTEXT,
        'ignoredItems': ['150007'],
        'descriptions': descriptions
    }
    return json.dumps(config)


@action
def getNavigationData(posid, max_levels=10, default_descr_id=1):
    return json.dumps(get_product_nav(int(max_levels), default_descr_id))


@action
def doOptionMultiItems(posid, items, context, line_number):
    """
    Resolve an option with a list of items

    :param items: a json with the partcode as key and amount of items as value
    :param context: context which the option should be resolved
    :param line_number: the line number to resolve the option
    """
    PLU = 0
    QTY = 1

    def sale_items(item):
        if item[QTY] <= 0:
            return
        doOption(posid, context, item[PLU], item[QTY], line_number)

    map(sale_items, json.loads(items).items())


@action
def getPrices(_):
    """
    Get a dict with all prices grouped by item ID and context
    """
    conn = None
    params = {
        'pricelist': 'EI'
    }
    try:
        conn = DBDriver().open(pyscripts.mbcontext, service_name="Persistence")
        cursor = conn.pselect("getProductPrices", **params)
        products = {row.get_entry(0): {
            'default': float(row.get_entry(1) or 0),
            'added': float(row.get_entry(2) or 0)
        } for row in cursor}

        combos = {}
        cursor = conn.pselect("getCompositions")
        for row in cursor:
            combo_code = row.get_entry(0)
            part_code = row.get_entry(1)
            default_qty = int(row.get_entry(2))
            part_is_option = int(row.get_entry(3)) == 1
            item_code = row.get_entry(4)
            item_to_find = item_code if part_is_option else part_code

            value = (products.get('{}.{}.{}.{}'.format(KIOSK_CONTEXT, combo_code, part_code, item_to_find)) or
                     products.get('{}.{}.{}'.format(combo_code, part_code, item_to_find)) or
                     products.get('{}.{}'.format(part_code, item_to_find)) or
                     products.get('{}.{}'.format(combo_code, item_to_find)) or
                     products.get(item_to_find) or {}).get('default', 0) * default_qty

            if not combos.get(combo_code):
                combos[combo_code] = {'default': 0}
            combos[combo_code]['default'] += value

        products.update(combos)
        return json.dumps(products)
    finally:
        if conn:
            conn.close()

@action
def doVoidOrderWithConfirmation(posid):
    model = get_model(posid)
    btn_id = show_messagebox(posid, "$BACK_CANCEL_ORDER_BODY", title="$BACK_CANCEL_ORDER_TITLE", icon="warning", buttons="$CANCEL|$OK")
    sys_log_info("Selected id {0}".format(btn_id))
    if btn_id == 1:
        doVoidKioskOrder(posid)

@action
def addValuePayment(posid, value):
    """
    Add value Paid

    :param payment_method: value
    """

    model = get_model(posid)
    posot = get_posot(model)

    valueTotal = float(value) + float(posot.setOrderCustomProperty("CUSTOMER_PAYMENT_VALUE"))
    posot.setOrderCustomProperty("CUSTOMER_PAYMENT_VALUE", valueTotal)

@action
def addItemToPay(posid, saleLines):

    model = get_model(posid)
    posot = get_posot(model)

    sale_lines_list = json.loads(saleLines)
    list = []

    if has_current_order(model):
        order = get_current_order(model)
        list_items = posot.getOrderCustomProperties(key="ITEMS_TO_PAY", orderid=order.get("orderId"))

        if list_items is not None:
            list_items = eTree.XML(list_items)

            if list_items.find("OrderProperty") is not None:
                if list_items.find("OrderProperty").attrib['key'] == 'ITEMS_TO_PAY':
                    list = json.loads(list_items.find("OrderProperty").get('value'))

        list.extend(sale_lines_list)
        posot.setOrderCustomProperty(key="ITEMS_TO_PAY", value=json.dumps(list))


@action
def setCardsPayment(posid, cards):
    """
    Set cards total to paid

    :param payment_method:  int value
    """

    model = get_model(posid)
    posot = get_posot(model)
    posot.setOrderCustomProperty("CUSTOMER_PAYMENT_CARDS", cards)

@action
def setRemainingPayment(posid, remaining_cards):
    """
    Set remaining cards to paid

    :param remaining_cards:  int value
    """

    model = get_model(posid)
    posot = get_posot(model)
    posot.setOrderCustomProperty("CUSTOMER_PAYMENT_REMAINING_CARDS", remaining_cards)

@action
def addValueTryToPay(posid, amount, tenderType):
    """
    Set remaining cards to paid

    :param amount:  int value to pay
    :param tenderType:  int C�digo do cart�o
    """

    model = get_model(posid)
    posot = get_posot(model)
    posot.setOrderCustomProperty("VALUE_TRY_TO_PAY", amount)
    posot.setOrderCustomProperty("TENDER_TYPE", tenderType)

def clear_options(posid, line_number, option=None):
    model = get_model(posid)
    posot = get_posot(model)

    order_pict = etree.XML(posot.orderPicture(posid))
    sale_lines = order_pict.findall(".//SaleLine[@lineNumber='{}']".format(line_number))

    if option:
        options_list = {option}
    else:
        options_list = set(map(lambda x: x.get('partCode'), order_pict.findall(
            ".//SaleLine[@lineNumber='{}'][@itemType='OPTION']".format(line_number))))

    def is_in_option(item_id):
        return not options_list.isdisjoint(item_id.split('.'))

    for line in filter(lambda x: is_in_option(x.get('itemId')) and int(x.get('qty')) > 0, sale_lines):
        posot.clearOption(posid, line_number, "", "{}.{}".format(line.get('itemId'), line.get('partCode')))
    pass


@action
def doSaleKiosk(posid, part_code, qty="", size="", sale_type="EAT_IN", *args):
    model = get_model(posid)
    posot = get_posot(model)
    if not has_current_order(model):
        raise StopAction()

    posot.blkopnotify = True
    try:
        sale_line = doSale(posid, part_code, qty, size, sale_type, *args)
        # if sale_line:
        #     sale_line_xml = etree.XML(sale_line)
        #     clear_options(posid, sale_line_xml.get('lineNumber'))
    finally:
        posot.blkopnotify = False
        order = get_current_order(model)
        posot.updateOrderProperties(posid, saletype=order.get("saleTypeDescr"))


@action
def doSubstituteOptionItems(posid, linenumber='', option='', new_items_list='{}'):
    model = get_model(posid)
    posot = get_posot(model)
    if not has_current_order(model):
        raise StopAction()
    posot.blkopnotify = True
    try:
        clear_options(posid, linenumber, option)
        for new_option, qty in json.loads(new_items_list).items():
            if int(qty) == 0:
                continue
            posot.doOption(posid, new_option, qty, linenumber, '@')
    finally:
        posot.blkopnotify = False
        order = get_current_order(model)
        posot.updateOrderProperties(posid, saletype=order.get("saleTypeDescr"))


# def main():
   # pydevd.settrace('localhost', port=9125, stdoutToServer=True, stderrToServer=True, suspend=False)
