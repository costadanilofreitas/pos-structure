# -*- coding: utf-8 -*-

import base64
import datetime
import logging
import string
from xml.etree import cElementTree as eTree

import pyscripts
from actions.eft import finish_eft_transactions
from actions.events import event_publisher
from persistence import Driver as DBDriver
from pyscriptscache import cache as _cache
from sysactions import get_model, translate_message, write_ldisplay, get_poslist, has_current_order, get_podtype, \
    show_messagebox, show_info_message, get_posfunction, close_asynch_dialog, \
    is_operator_logged, get_custom

mbcontext = pyscripts.mbcontext
msrposmap = {}
finger_print_reader_dlg_id = -1

logger = logging.getLogger("PosActions")


def _device_data_event_received(params):
    data, subject, p_type, asynch, pos_id = params[:5]
    try:
        logger.info("Data {0} ".format(data))

        xml = eTree.XML(data)
        device = xml.find("Device")
        device_name = str(device.get("name"))

        if device_name.startswith("scanner"):
            publish_scanner_event_to_ui(device, device_name)
        elif device_name.startswith("scale"):
            _get_weight(device_name, xml)
    except Exception as _:
        logger.exception('Exception processing device thread')


def publish_scanner_event_to_ui(device, device_name):
    pos_id = int(device_name[7:])
    barcode = base64.b64decode(device.text).strip('\0')

    event_publisher.publish_event(pos_id, "SCANNER_DATA", "SCANNER", barcode)


def _get_weight(device_name, xml):
    from posactions import pos_scale_events

    encoded_weight = xml.find("Device").text
    decoded_weight = base64.b64decode(encoded_weight)
    weight = float(decoded_weight) / 1000
    pos_scale_events.add_weight(device_name, weight)


def event_order_modified_sitef(params):
    xml, subject, event_type = params[:3]

    order = eTree.XML(xml).find(".//Order")
    pos_id = order.get("posId") or order.get("originatorId")[3:]
    model = get_model(pos_id)

    if event_type == "PAID":
        pod_type = get_podtype(model)
        pos_function = get_posfunction(model)
        if pod_type not in ("OT", "DL") and pos_function not in ("OT", "DL"):
            from threading import Thread
            sitef_transactions_thread = Thread(target=finish_eft_transactions, args=(pos_id, order, "1"))
            sitef_transactions_thread.daemon = True
            sitef_transactions_thread.start()

    if event_type == "VOID_ORDER":
        pod_type = get_podtype(model)
        pos_function = get_posfunction(model)
        if pod_type not in ("OT", "DL") and pos_function not in ("OT", "DL"):
            from threading import Thread
            sitef_transactions_thread = Thread(target=finish_eft_transactions, args=(pos_id, order, "0"))
            sitef_transactions_thread.daemon = True
            sitef_transactions_thread.start()


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


def event_pos_state_changed(params):
    """Callback called by pyscripts module
    This will update the line display with necessary information about the POS state
    """
    xml, subject, event_type = params[:3]
    types = ("OPERATORLOGIN", "OPERATORPAUSE", "OPERATORLOGOUT")
    if event_type not in types:
        # Not interested on this event
        return None
    pos_id = str(eTree.XML(xml).find("POSState").get("posid"))
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
        try:
            if is_operator_logged(model):
                write_ldisplay(model, translate_message(model, "LDISPLAY_POS_ACTIVE"), True)
            else:
                write_ldisplay(model, translate_message(model, "LDISPLAY_POS_INACTIVE"), True)
        except:
            pass


def add_or_update_default_options(query_template, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, ingredients=False, items=None, default_products=True, model=''):
    # Options - Pai tem default_qty = 1 e Filhos default_qty = 0
    # Ingredients - Pai tem default_qty = 0 e Filhos default_qty = 1
    all_options = [(_cache.get_tags_as_dict(part_code, "HasOptions"), 1, 0), (_cache.get_tags_as_dict(part_code, "Ingredients"), 0, 1)]
    forced_pricelist = get_custom(model, 'Special Catalog Enabled') if model else False

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
                if float(prod_qty) == 0:
                    default_qty = "0"
                else:
                    default_qty = qty_tags[temp_code][0] if qty_tags and temp_code in qty_tags else "1"
                price_key = _cache.get_best_price_key(item_id, temp_code, pod_type, forced_pricelist) or "NULL"
                queries.append(query_template % locals())

                if ingredients and options_line[2] == 1:
                    continue

                if default_products and len(opt.split(">")) > 1 and opt.split(">")[1]:
                    parent_item_id = item_id + '.' + temp_code
                    for product in opt.split(">")[1].split(";"):
                        # Default Product
                        item_id = parent_item_id
                        temp_code = product
                        temp_level = level + 2
                        inc_qty = prod_qty if float(prod_qty) == 0 else 1
                        ordered_qty = prod_qty if float(prod_qty) == 0 else 1
                        default_qty = options_line[2]
                        price_key = _cache.get_best_price_key(item_id, temp_code, pod_type, forced_pricelist) or "NULL"
                        queries.append(query_template % locals())

                        # Go to the NEXT LEVEL AND BEYOND
                        add_or_update_default_options(query_template, queries, order_id, line_number, item_id, temp_code, prod_qty, temp_level, pod_type, ingredients, items, model=model)

    parts = _cache.get_parts(part_code)
    if parts:
        for part in parts:
            if pod_type != "DT" and part in dt_only_dict:
                continue

            if part not in included_parts:
                item_id = context + '.' + part_code
                temp_code = part
                temp_level = level + 1
                inc_qty = prod_qty if float(prod_qty) == 0 else 1
                ordered_qty = prod_qty if float(prod_qty) == 0 else 1
                default_qty = float(parts[part][0] or prod_qty)
                price_key = _cache.get_best_price_key(item_id, temp_code, pod_type, forced_pricelist) or "NULL"

                # parts[part] -> Outros Elementos do Dicionário
                queries.append(query_template % locals())
                if items is not None:
                    price = _cache.get_best_price(item_id, temp_code, pod_type, forced_pricelist)
                    if price:
                        price = price[0]
                    items.append([item_id, temp_code, parts[part][3], price, line_number, prod_qty])

                # Go to the NEXT LEVEL
                add_or_update_default_options(query_template, queries, order_id, line_number, item_id, part, 1, temp_level, pod_type, ingredients, model=model)
# END of add_or_update_default_options


def update_options_and_defaults(queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, model=''):
    temp_update = """UPDATE orderdb.CurrentOrderItem SET DefaultQty = %(default_qty)s
    WHERE OrderId = %(order_id)s AND LineNumber = %(line_number)s AND ItemId = '%(item_id)s' AND Level = %(temp_level)s AND PartCode = '%(temp_code)s'"""

    add_or_update_default_options(temp_update, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, False, model=model)
# END update_options_and_defaults


def insert_options_and_defaults(queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, items=None, default_products=True, model=''):
    temp_insert = """INSERT OR REPLACE INTO orderdb.CurrentOrderItem (OrderId, LineNumber, ItemId, Level, PartCode, OrderedQty, IncQty, DefaultQty, PriceKey)
    VALUES (%(order_id)s, %(line_number)s, '%(item_id)s', %(temp_level)s, '%(temp_code)s', %(ordered_qty)s, %(inc_qty)s, %(default_qty)s, %(price_key)s)"""

    add_or_update_default_options(temp_insert, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, True, items, default_products, model=model)
# END of insert_options_and_defaults


def delete_options_and_defaults(queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, items=None, model=''):
    temp_delete = """DELETE FROM orderdb.CurrentOrderItem
    WHERE OrderId = %(order_id)s AND LineNumber = %(line_number)s AND ItemId LIKE '%(item_id)s%%' AND Level >= %(temp_level)s"""

    add_or_update_default_options(temp_delete, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, False, items, model=model)
# END of delete_options_and_defaults


def get_updated_sale_line_defaults(queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, model=''):
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
    add_or_update_default_options(temp_lines, queries, order_id, line_number, context, part_code, prod_qty, level, pod_type, False, model=model)
# END of get_updated_sale_line_defaults


def event_pre_new_order(params):
    queries = ["""DELETE FROM orderdb.CurrentOrderItem"""]

    if queries:
        return "\0".join(["0"] + [";".join(queries)])
    return None


def eft_status_update(params):
    message, pos_id = params[0].split(';')
    show_info_message(pos_id, "#SHOW|" + message, timeout=5000)


def finger_print_reader_callback(params):
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
    else:
        message = "Evento nao cadastrado"

    new_id = None
    if message is not None:
        logger.info("Fingerprint callback message: {}".format(message))
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
    pyscripts.subscribe_event_listener("ORDER_MODIFIED", event_order_modified_sitef)
    pyscripts.subscribe_event_listener("POS_STATECHANGED", event_pos_state_changed)
    pyscripts.subscribe_event_listener("PRE_NEW_ORDER", event_pre_new_order)
    pyscripts.subscribe_event_listener("SITEF_STATUS_UPDATE", eft_status_update)
    pyscripts.subscribe_event_listener("FPR_CALLBACK", finger_print_reader_callback)
    pyscripts.subscribe_event_listener("DEVICE_DATA", _device_data_event_received)
    check_current_state()
