# -*- coding: utf-8 -*-
# Python module responsible to listen to POS events and take actions based on those events
# Most actions are performed by an "order modification" event.

# Python standard modules
import datetime
import time
import base64
import re
import logging
import string
from xml.etree import cElementTree as etree

from posot import OrderTakerException
from systools import sys_log_info, sys_log_exception
# Our modules
import pyscripts
from pyscriptscache import cache as _cache
from sysactions import get_model, translate_message, write_ldisplay, get_poslist, has_current_order, is_operator_logged, get_custom_params, \
    get_cfg, get_business_period, show_messagebox, show_info_message, get_posot, get_current_order, format_date, get_podtype, get_posfunction, close_asynch_dialog
from msgbus import FM_PARAM
from bustoken import TK_SITEF_FINISH_PAYMENT
from msgbus import TK_SYS_ACK
from persistence import Driver as DBDriver
from helper import read_swconfig

# COMMENT HERE
import sys
import os
debugPath = '../python/pycharm-debug.egg'
if os.path.exists(debugPath):
    try:
        sys.path.index(debugPath)
    except:
        sys.path.append(debugPath)
    import pydevd

# Use the line below in the function you want to debug
# pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True)
# UNTIL HERE


# Message-bus context
mbcontext = pyscripts.mbcontext

# cache of MSR <-> POS mapping
msrposmap = {}
logger = logging.getLogger("PosActions")


def event_order_modifier(params):
    """Callback called by pyscripts module
    This will update the line display with necessary information about the order
    """
    # sale, void item, void order, total, tender, REOPENED, paid, charged modifyer
    xml, subject, event_type = params[:3]
    types = ("PAID", "DO_TENDER", "REOPENED", "TOTALED", "DO_SALE", "VOID_LINE", "VOID_ORDER", "STORED", "CHANGE_DIMENSION", "ORDER_PROPERTIES_CHANGED", "RECALLED")  # check - "DO_OPTION"
    if event_type not in types:
        # Not interested on this event
        return None

    order = etree.XML(xml).find(".//Order")
    pos_id = order.get("posId") or order.get("originatorId")[3:]
    model = get_model(pos_id)

    if event_type in ("DO_SALE", "CHANGE_DIMENSION", "VOID_LINE", "RECALLED", "ORDER_PROPERTIES_CHANGED"):
        last = order.get("lastModifiedLine")
        for line in order.findall("SaleLine"):
            if line.get("lineNumber") == last:
                qty, name, price = map(line.get, ("qty", "productName", "itemPrice"))
                subtotal = order.get("totalAmount")
                if event_type in ("DO_SALE", "CHANGE_DIMENSION"):
                    write_ldisplay(model, "%s %s\n$ SubTotal: %s" % (qty, name.encode("UTF-8"), subtotal), False)
                elif event_type in "ORDER_PROPERTIES_CHANGED":
                    write_ldisplay(model, translate_message(model, "LDISPLAY_MODIFY_ITEM", "\n$ SubTotal: %s" % subtotal), False)
                else:
                    write_ldisplay(model, translate_message(model, "LDISPLAY_VOIDED_ITEM", "$ SubTotal: %s" % subtotal), False)
                break

    if (event_type == "TOTALED") or (event_type == "ORDER_PROPERTIES_CHANGED" and order.get("state") == "TOTALED"):
        # Whopper Wi-Fi START
        if order.find(".//OrderProperty[@key='WHOPPER_WIFI_CODE']") is None and has_current_order(model):
            whopper_wifi_pod_types = (read_swconfig(mbcontext, "Store.WhopperWifiPodTypes") or '').split(';')
            store_id = read_swconfig(mbcontext, "Store.Id")

            order_id = order.get('orderId')
            podtype = get_podtype(model)
            if podtype in whopper_wifi_pod_types:
                try:
                    posot = get_posot(model)
                    wifi_code = get_whooper_wifi_code(store_id, order_id, datetime.datetime.now())
                    posot.setOrderCustomProperty("WHOPPER_WIFI_CODE", wifi_code)
                except OrderTakerException:
                    logger.exception("Error saving WHOPPER WIFI code - Order: {}".format(order_id))
        # Whopper Wi-Fi END

        order_due, order_total, order_id, order_tax = map(order.get, ("dueAmount", "totalAmount", "orderId", "taxTotal"))
        biggest = max(map(len, (order_total, order_tax, order_due)))
        order_due = "%*s" % (biggest, order_due)
        write_ldisplay(model, ("TOTAL: R$%r" % order_due), False)

    if event_type == "REOPENED":
        write_ldisplay(model, "")

    if event_type == "DO_TENDER":
        order_due = order.get("dueAmount")
        tender_paid = order.get("totalTender")
        biggest = max(map(len, (order_due, tender_paid)))
        order_due = "%*s" % (biggest, order_due)
        tender_paid = "%*s" % (biggest, tender_paid)
        tenders = order.findall("TenderHistory/Tender")
        if tenders:
            last_tender = tenders[len(tenders) - 1]
            tender_desc = last_tender.get("tenderDescr")
            write_ldisplay(model, translate_message(model, "LDISPLAY_ORDER_TENDER", tender_desc, tender_paid, order_due), False)

    if event_type == "STORED":
        write_ldisplay(model, translate_message(model, "LDISPLAY_POS_ACTIVE"), True)

    if event_type == "PAID":
        order_change = order.get("change")
        write_ldisplay(model, translate_message(model, "LDISPLAY_ORDER_PAID", order_change), False)
        time.sleep(3.0)
        write_ldisplay(model, translate_message(model, "LDISPLAY_POS_ACTIVE"), True)
        pod_type = get_podtype(model)
        pos_function = get_posfunction(model)
        if pod_type not in ("OT", "DL") and pos_function not in ("OT", "DL"):
            from threading import Thread
            sitef_transactions_thread = Thread(target=finish_sitef_transactions, args=(pos_id, order, "1"))
            sitef_transactions_thread.daemon = True
            sitef_transactions_thread.start()

    if event_type == "VOID_ORDER":
        order_id = order.get("orderId")
        write_ldisplay(model, translate_message(model, "LDISPLAY_VOIDED_ORDER", order_id), False)
        time.sleep(3.0)
        write_ldisplay(model, translate_message(model, "LDISPLAY_POS_ACTIVE"), True)
        pod_type = get_podtype(model)
        pos_function = get_posfunction(model)
        if pod_type not in ("OT", "DL") and pos_function not in ("OT", "DL"):
            from threading import Thread
            sitef_transactions_thread = Thread(target=finish_sitef_transactions, args=(pos_id, order, "0"))
            sitef_transactions_thread.daemon = True
            sitef_transactions_thread.start()

        delete_payments(order_id)


def delete_payments(order_id):
    conn = None
    try:
        conn = DBDriver().open(mbcontext, service_name="FiscalPersistence")
        conn.query("DELETE FROM PaymentData WHERE OrderId = %d" % int(order_id))
        logger.info("Pagamentos apagados para order %s" % order_id)
    except:
        logger.exception("Erro Apagando Pagamentos para order %s" % order_id)
    finally:
        if conn:
            conn.close()


def finish_sitef_transactions(pos_id, order, status):
    for i in xrange(0, 3, 1):
        try:
            order_id = order.get("orderId")
            created_at = order.get("createdAt").replace("-", "").replace(":", "")
            data_fiscal = created_at[:8]
            hora_fiscal = created_at[9:15]
            ret = mbcontext.MB_EasySendMessage("Sitef%02d" % int(pos_id), token=TK_SITEF_FINISH_PAYMENT, format=FM_PARAM, data="%s;%s;%s;%s;%s" % (str(pos_id), order_id, data_fiscal, hora_fiscal, status))
            if ret.token == TK_SYS_ACK:
                return
        except Exception as ex:
            show_info_message(pos_id, "Erro ao Encontrar SiTef", msgtype="info")
            sys_log_exception("Erro Enviando Finish Payment para a SiTef - Exception %s" % str(ex))


def event_pos_state_changed(params):
    """Callback called by pyscripts module
    This will update the line display with necessary information about the POS state
    """
    xml, subject, event_type = params[:3]
    types = ("OPERATORLOGIN", "OPERATORPAUSE", "OPERATORLOGOUT")
    if event_type not in types:
        # Not interested on this event
        return None
    pos_id = str(etree.XML(xml).find("POSState").get("posid"))
    model = get_model(pos_id)
    if event_type in ("OPERATORPAUSE", "OPERATORLOGOUT"):
        write_ldisplay(model, translate_message(model, "LDISPLAY_POS_INACTIVE"), True)
    else:
        write_ldisplay(model, translate_message(model, "LDISPLAY_POS_ACTIVE"), True)
    return None


def check_current_state():
    """
    Called during initialization to check current POS state and set the correct message in the customer display
    """
    for posid in get_poslist():
        posid = str(posid)
        model = get_model(posid)
        if has_current_order(model):
            continue
        if is_operator_logged(model):
            write_ldisplay(model, translate_message(model, "LDISPLAY_POS_ACTIVE"), True)
        else:
            write_ldisplay(model, translate_message(model, "LDISPLAY_POS_INACTIVE"), True)


def add_or_update_default_options(query_template, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, ingredients=False, items=None, default_products=True):
    # Options - Pai tem default_qty = 1 e Filhos default_qty = 0
    # Ingredients - Pai tem default_qty = 0 e Filhos default_qty = 1
    all_options = [(_cache.get_tags_as_dict(part_code, "HasOptions"), 1, 0), (_cache.get_tags_as_dict(part_code, "Ingredients"), 0, 1)]

    # Busca quais options devem estar apenas no OrderTaker
    dt_only_list = _cache.get_tags_as_dict(part_code, "DTOnly").split("|")
    dt_only_dict = {}
    for dt_only in dt_only_list:
        dt_only_dict[dt_only] = dt_only

    included_parts = {}
    if all_options:

        for options_line in all_options:
            if not options_line[0]:
                continue

            qty_tags = None
            temp_tags = _cache.get_tags_as_dict(part_code, "QtyOptions")
            if temp_tags:
                qty_tags = {tag.split(">")[0]: (tag.split(">")[1].split(";")[0], tag.split(">")[1].split(";")[1], tag.split(">")[1].split(";")[2]) for tag in temp_tags.split("|")}

            options = options_line[0].split("|")
            for opt in options:
                # OPTION - Code
                item_id = context + '.' + part_code
                temp_code = opt.split(">")[0]
                if pod_type != "DT" and temp_code in dt_only_dict:
                    continue

                included_parts[temp_code] = temp_code

                temp_level = level + 1
                inc_qty = qty_tags[temp_code][1] if qty_tags and temp_code in qty_tags else "1"
                ordered_qty = "NULL"
                if int(prod_qty) == 0:
                    default_qty = "0"
                else:
                    default_qty = qty_tags[temp_code][0] if qty_tags and temp_code in qty_tags else "1"
                price_key = _cache.get_best_price_key(item_id, temp_code, pod_type) or "NULL"
                queries.append(query_template % locals())

                if ingredients and options_line[2] == 1:
                    temp_update = """UPDATE orderdb.CurrentOrderItem SET DefaultQty = %(default_qty)s
                    WHERE OrderId = %(order_id)s and LineNumber = %(line_number)s and ItemId = '%(item_id)s' and PartCode = '%(temp_code)s'"""
                    default_qty = 0
                    queries.append(temp_update % locals())

                    continue

                if default_products and len(opt.split(">")) > 1 and opt.split(">")[1]:
                    parent_item_id = item_id + '.' + temp_code
                    for product in opt.split(">")[1].split(";"):
                        # Default Product
                        item_id = parent_item_id
                        temp_code = product
                        temp_level = level + 2
                        inc_qty = prod_qty if int(prod_qty) == 0 else 1
                        ordered_qty = prod_qty if int(prod_qty) == 0 else 1
                        default_qty = options_line[2]
                        price_key = _cache.get_best_price_key(item_id, temp_code, pod_type) or "NULL"
                        queries.append(query_template % locals())

                        # Go to the NEXT LEVEL AND BEYOND
                        add_or_update_default_options(query_template, queries, order_id, line_number, item_id, temp_code, prod_qty, temp_level, pod_type, ingredients, items)

    parts = _cache.get_parts(part_code)
    if parts:
        for part in parts:
            if pod_type != "DT" and part in dt_only_dict:
                continue

            if part not in included_parts:
                item_id = context + '.' + part_code
                temp_code = part
                temp_level = level + 1
                inc_qty = prod_qty if int(prod_qty) == 0 else 1
                ordered_qty = prod_qty if int(prod_qty) == 0 else 1
                default_qty = int(parts[part][0] or prod_qty)
                price_key = _cache.get_best_price_key(item_id, temp_code, pod_type) or "NULL"

                # parts[part] -> Outros Elementos do Dicionário
                queries.append(query_template % locals())
                if items is not None:
                    price = _cache.get_best_price(item_id, temp_code, pod_type)[0]
                    items.append([item_id, temp_code, parts[part][3], price, line_number, prod_qty])

                # Go to the NEXT LEVEL
                add_or_update_default_options(query_template, queries, order_id, line_number, item_id, part, 1, temp_level, pod_type, ingredients)
# END of add_or_update_default_options


def update_options_and_defaults(queries, order_id, line_number, context, part_code, prod_qty, level, pod_type):
    temp_update = """UPDATE orderdb.CurrentOrderItem SET DefaultQty = %(default_qty)s
    WHERE OrderId = %(order_id)s AND LineNumber = %(line_number)s AND ItemId = '%(item_id)s' AND Level = %(temp_level)s AND PartCode = '%(temp_code)s'"""

    add_or_update_default_options(temp_update, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, False)
# END update_options_and_defaults


def insert_options_and_defaults(queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, items=None, ingredients=True, default_produtcts=True):
    temp_insert = """INSERT OR REPLACE INTO orderdb.CurrentOrderItem (OrderId, LineNumber, ItemId, Level, PartCode, OrderedQty, IncQty, DefaultQty, PriceKey)
    VALUES (%(order_id)s, %(line_number)s, '%(item_id)s', %(temp_level)s, '%(temp_code)s', %(ordered_qty)s, %(inc_qty)s, %(default_qty)s, %(price_key)s)"""

    add_or_update_default_options(temp_insert, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, ingredients, items, default_produtcts)
# END of insert_options_and_defaults


def delete_options_and_defaults(queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, items=None):
    temp_delete = """DELETE FROM orderdb.CurrentOrderItem
    WHERE OrderId = %(order_id)s AND LineNumber = %(line_number)s AND ItemId LIKE '%(item_id)s%%' AND Level >= %(temp_level)s"""

    add_or_update_default_options(temp_delete, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, False, items)
# END of delete_options_and_defaults


def get_updated_sale_line_defaults(queries, order_id, line_number, context, part_code, prod_qty, level, pod_type):
    temp_lines = """
        {
            "order_id": "%(order_id)s",
            "line_number": "%(line_number)s",
            "item_id": "%(item_id)s",
            "level": "%(temp_level)s",
            "part_code": "%(temp_code)s",
            "ordered_qty": "%(ordered_qty)s",
            "inc_qty": "%(inc_qty)s",
            "default_qty": "%(default_qty)s",
            "price_key": "%(price_key)s"
        }
    """
    add_or_update_default_options(temp_lines, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, False)
# END of get_updated_sale_line_defaults


def event_post_new_line(params):
    logger.debug("--- event_post_new_line START ---")
    queries = []

    # Get Line 0 of the Sale - Normally a COMBO
    xml = etree.XML(params[0])
    line = xml.find("SaleLine")
    pos_id, order_id, item_id_line, part_code_line, prod_qty, line_number = map(line.get, ("posId", "orderId", "itemId", "partCode", "qty", "lineNumber"))

    model = get_model(pos_id)
    pod_type = get_podtype(model)

    not_kiosk = pod_type != 'TT'
    # RUN BABY RUN
    insert_options_and_defaults(queries, order_id, line_number, item_id_line, part_code_line, prod_qty, 0, pod_type, default_produtcts=not_kiosk)

    logger.debug("--- event_post_new_line END ---")
    if queries:
        return "\0".join(["0"] + [";".join(queries)])
    return None
# END event_post_new_line


def event_pre_new_order(params):
    queries = ["""DELETE FROM orderdb.CurrentOrderItem"""]

    if queries:
        return "\0".join(["0"] + [";".join(queries)])
    return None
# END event_post_new_line


def event_options_solved(params):
    xml = etree.XML(params[0])
    queries = []
    order = xml.find("Order")
    posid, orderid = map(order.get, ("posId", "orderId"))
    for line in order.findall("SaleLine"):
        itemid, partCode, optionCode, qty, lineNumber = map(line.get, ("itemId", "partCode", "optionItemId", "multipliedQty", "lineNumber"))
        # Retrieve the list of custom parameters
        xml = get_custom_params(posid, pcodelist=str(optionCode))
        for param in xml.findall("Product/CustomParameter"):
            if (param.get("id") or "").lower() == "defaultoption" and param.get("value"):
                # Found the "DefaultOption" parameter, lets perform a "doOption"
                for defOptCode in param.get("value").split('|'):
                    queries.append(
                        """
                     UPDATE orderdb.CurrentOrderItem
                     SET LastOrderedQty=OrderedQty, OrderedQty=1, IncQty=IncQty+%(qty)s
                     WHERE OrderId=%(orderid)s AND LineNumber=%(lineNumber)s AND Level>1 AND PartCode=%(defOptCode)s AND ItemId LIKE '%(itemid)s.%(partCode)s.%(optionCode)s.%%'
                     """ % locals())
    if queries:
        return "\0".join(["0"] + queries)
    return None
# END event_options_solved


def event_msr_data(params):
    if not msrposmap:
        # Build the MSR <-> POS mapping - note that this is done only once!
        for posid in get_poslist():
            config = get_cfg(posid)
            for msr in (config.find_values("UsedServices.msr") or tuple()):
                msrposmap[str(msr)] = str(posid)
    xml = etree.XML(params[0])
    msr = str(xml.find("MSR").get("name"))
    if msr not in msrposmap:
        # No POS is associated to this MSR name
        return
    # Get the POS ID associated to this MSR name
    posid = msrposmap[msr]
    model = get_model(posid)
    bperiod = get_business_period(model)
    # Get all MSR tracks
    tracks = [el.findtext("./") for el in xml.findall("MSR/Track")]
    if not tracks:
        return
    # Decode track #1
    data = base64.b64decode(tracks[0])
    # Check for the "ECC" prefix - quick check to avoid the regular expression
    if not data.startswith("ECC"):
        return  # Not a eLanes Community Card
    # Create a regular expression to validate and extract all ECC fields
    regex = re.compile(r"^ECC(\w{2})(\d{5})(\d{8})(\d{8})(\d{5})(.{5,40})$")
    match = regex.match(data)
    if not match:
        show_messagebox(posid, "$CARD_NOT_VALID_UNREADABLE", icon="error")
        return
    # Extract all ECC fields
    region, programcode, startdate, enddate, cardid, programname = match.groups()
    # Remove unnecessary spaces from the program name
    programname = programname.strip()
    try:
        # Check if the start and end dates are well-formed
        today = datetime.date(int(bperiod[:4]), int(bperiod[4:6]), int(bperiod[6:8]))
        start = datetime.date(int(startdate[:4]), int(startdate[4:6]), int(startdate[6:8]))
        end = datetime.date(int(enddate[:4]), int(enddate[4:6]), int(enddate[6:8]))
    except:
        show_messagebox(posid, "$CARD_NOT_VALID_UNREADABLE", icon="error")
        sys_log_info("Community Card program [%s] - invalid dates - start=[%s] end=[%s] - posid [%s]" % (programname, startdate, enddate, posid))
        return
    # Check if the program start and end dates are valid
    if start <= today <= end:
        # We must have an order in-progress to register this ECC
        if not has_current_order(model):
            sys_log_info("Community Card program [%s] - ORDER NOT IN PROGRESS - posid [%s]" % (programname, posid))
            show_info_message(posid, "$NEED_TO_HAVE_ORDER", msgtype="warning")
            return
        posot = get_posot(model)
        order = get_current_order(model)
        orderid = order.get("orderId")
        # All good! lets register this ECC on the current order
        try:
            posot.setOrderCustomProperty("ECC_TRACK_1", data, orderid)
            if len(tracks) > 1:
                posot.setOrderCustomProperty("ECC_TRACK_2", tracks[1], orderid)
            if len(tracks) > 2:
                posot.setOrderCustomProperty("ECC_TRACK_3", tracks[2], orderid)
            info = eval(order.findtext("AdditionalInfo") or "{}")
            info["ECC_PROGRAMNAME"] = programname
            posot.updateOrderProperties(posid, additionalinfo=repr(info))
            sys_log_info("Community Card program [%s] registered for order id [%s], posid [%s]" % (programname, orderid, posid))
            show_info_message(posid, "Community card program: %s" % programname, msgtype="success")
        except:
            sys_log_exception("Error writing eLanes Community Card data. program [%s] - order id [%s] - posid [%s]" % (programname, orderid, posid))
            show_messagebox(posid, "$ERROR_REGISTERING_COMMUNITY_CARD|%s" % programname, icon="error")
    else:
        if today > end:
            sys_log_info("Community Card program [%s] ENDED at [%s] - posid [%s]" % (programname, enddate, posid))
            show_messagebox(posid, "$COMMUNITY_CARD_PROGRAM_ENDED_AT|%s" % (format_date(enddate)), icon="warning")
        else:
            sys_log_info("Community Card program [%s] STARTS at [%s] - posid [%s]" % (programname, startdate, posid))
            show_messagebox(posid, "$COMMUNITY_CARD_PROGRAM_STARTS_AT|%s" % (format_date(startdate)), icon="warning")
# END event_msr_data


def sitef_status_update(params):
    message, pos_id = params[0].split(';')
    show_info_message(pos_id, message, timeout=180000)
# END def sitef_status_update


finger_print_reader_dlg_id = -1
def finger_print_reader_callbacl(params):
    global finger_print_reader_dlg_id

    params_list = params[0].split(";")
    pos_id = params_list[0]
    extra_data = None
    if len(params_list) > 1:
        extra_data = params_list[1]

    event_type = params[2]

    message = None
    title = "Impressao Digital"
    timeout = 300000

    if event_type == "EVT_CLOSE_ALL_DIALOGS":
        pass
    elif event_type == "EVT_FINGER_ALREADY_REGISTERED":
        title = "Erro"
        message = "Impressão digital já cadastrada para outro usuário"
        timeout = 3000
    elif event_type == "EVT_BAD_FINGERPRINT_READ":
        title = "Erro"
        message = "Leitura da impressão digital inválida. Tente novamente"
    elif event_type == "EVT_PLACE_RIGHT_INDEX_FINGER":
        message = "Posicione o indicador direito no leitor"
    elif event_type == "EVT_PLACE_FINGER_LOGIN":
        title = "Login de usuario"
        message = "Posicione o dedo no leitor"
    elif event_type == "EVT_PLACE_FINGER_AUTHORIZATION":
        title = "Autorizacao requerida"
        message = "Posicione o dedo no leitor"
    elif event_type == "EVT_FINGER_READ_SUCCESSFULLY":
        message = "Leitura efetuada com sucesso"
    elif event_type == "EVT_FINGER_READ_SUCCESSFULLY_READ_AGAIN":
        if extra_data == '1':
            message = "Primeira"
        elif extra_data == '2':
            message = "Segunda"
        elif extra_data == '3':
            message = "Terceira"
        elif extra_data == '4':
            message = "Quarta"
        elif extra_data == '5':
            message = "Quinta"
        elif extra_data == '6':
            message = "Sexta"
        elif extra_data == '7':
            message = "Sétima"
        elif extra_data == '8':
            message = "Oitava"
        elif extra_data == '9':
            message = "Nona"
        elif extra_data == '10':
            message = "Décima"
        elif extra_data == '11':
            message = "Décima Primeira"
        else:
            message = ""

        message += " leitura efetuada com sucesso. Posicione o dedo novamente no leitor"
    elif event_type == "EVT_ENROLLMENT_SUCCESS":
        message = "Cadastro realizado com sucesso"
        timeout = 3000
    elif event_type == "EVT_FINGER_ALREADY_REGISTERED":
        message = "Impressão digital já cadastrada para outro usuário"
        timeout = 3000
    else:
        message = "Evento nao cadastrado"

    new_id = None
    if message is not None:
        new_id = show_messagebox(pos_id, message, title, "info", buttons="", timeout=timeout, asynch=True)

    if finger_print_reader_dlg_id != -1:
        close_asynch_dialog(pos_id, finger_print_reader_dlg_id)

    if new_id is not None:
        finger_print_reader_dlg_id = new_id
# END def finger_print_reader_callbacl


def get_whooper_wifi_code(bk_number, order_id, date):
    alphabet = string.digits + string.ascii_uppercase

    cc = str(bk_number).zfill(5)[-5:] + str(order_id).zfill(4)[-4:] + datetime.datetime.strftime(date, "%d%m%y")

    scrambled_concat = cc[9] + cc[8] + cc[1] + cc[7] + cc[11] + cc[14] + cc[2] + cc[3] + cc[5] + cc[6] + cc[4] + cc[10] + cc[12] + cc[13] + cc[0]
    simplified_scrambled_concat = cc[9] + cc[10] + cc[8] + cc[1] + cc[7] + cc[2] + cc[3] + cc[5] + cc[6] + cc[4] + cc[0]

    bases10 = []
    for i in range(0, 11):
        bases10.append(int(simplified_scrambled_concat[i]) * pow(10, 10 - i))

    the_number = sum(bases10)

    code_number = []
    for i in range(6, -1, -1):
        code_number.append((the_number / pow(36, i)) % 36)

    multiple = 15
    divisor_number_sum = 0
    while multiple > 0:
        for number in scrambled_concat:
            divisor_number_sum += int(number) * multiple
            multiple -= 1
    code_number.append(divisor_number_sum % 36)

    code_alphanumeric = []
    for i in code_number:
        code_alphanumeric.append(alphabet[i])

    final_code = ''.join(code_alphanumeric)
    return final_code


#
# Main function (called by pyscripts)
#
def main():
    # pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True, suspend=False)
    pyscripts.subscribe_event_listener("ORDER_MODIFIED", event_order_modifier)
    pyscripts.subscribe_event_listener("POS_STATECHANGED", event_pos_state_changed)
    pyscripts.subscribe_event_listener("PRE_NEW_ORDER", event_pre_new_order)
    pyscripts.subscribe_event_listener("POST_NEW_LINE", event_post_new_line)
    pyscripts.subscribe_event_listener("OPTIONS_SOLVED", event_options_solved)
    pyscripts.subscribe_event_listener("MSR_DATA", event_msr_data)
    pyscripts.subscribe_event_listener("SITEF_STATUS_UPDATE", sitef_status_update)
    pyscripts.subscribe_event_listener("FPR_CALLBACK", finger_print_reader_callbacl)
    check_current_state()
