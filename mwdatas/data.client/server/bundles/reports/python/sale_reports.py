# -*- coding: utf-8 -*-

# --- DO NOT CHANGE THE IMPORT ORDER --- #
import time
import json
import qrcode
import printer_wrapper
import sysactions
import xml.sax
import xml.sax.handler
import helper
import re
import os
import sys

from constants import *
from xml.etree import ElementTree as eTree
from cStringIO import StringIO
from reports import dbd, mbcontext, config
from systools import sys_log_exception
from unicodedata import normalize
from production import SystemOrderParser
from prodpersist import OrderXml
from persistence import Driver as DBDriver

debug_path = '../python/pycharm-debug.egg'
if os.path.exists(debug_path):
    try:
        sys.path.index(debug_path)
    except ValueError:
        sys.path.append(debug_path)
    # noinspection PyUnresolvedReferences
    import pydevd

# Copy the line bellow and paste inside your function to debug
# pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True, suspend=True)

sysactions.mbcontext = mbcontext
COLS = 42
SMALL_COLS = 42
SEPARATOR = ("=" * COLS)
SMALL_SEPARATOR = ("=" * SMALL_COLS)
DATE_TIME_FMT = "%d/%m/%Y %H:%M:%S"
DATE_FMT = "%d/%m/%Y"
TIME_FMT = "%H:%M:%S"
RECEIPTS_HEADER = config.find_value("Receipts.Header", "BEM-VINDO AO BURGER KING\\#00007971\\\\").split("\\")
pick_up_type = None
list_coupons = None
products_ordination = None
standalone_products_exception = None
store_id = None


def main():
    pass


def _join(dic1, dic2):
    d = dict(dic1)
    d.update(dic2)
    return d


def _cut(s):
    if len(s) > COLS:
        # If there is a line-feed at the end, keep it
        return s[:COLS] if (s[-1] != "\n") else (s[:(COLS - 1)] + "\n")
    return s


def _center(s, cols=COLS):
    if not s:
        return s
    s = _cut(s)
    miss = cols - len(s)
    if miss == 0:
        return s
    left = miss / 2
    return (" " * left) + s


def production_pick_list(production_xml, grouped_items=False, *args):
    global pick_up_type
    try:
        if pick_up_type is None:
            pick_up_type = sysactions.get_storewide_config("Store.pickUpDisplayType", defval="Manager")
    except Exception as _:
        pick_up_type = 'Manager'

    """ Generates a pick list from production XML """
    def _report_header(title, order_t, reprint=False, receipt=False):
        header_pod_type = order_t.get("pod_type")
        totem_print = header_pod_type == "TT"
        street_name_element, street_number_element, neighborhood_element, postal_code_element, city_element, state_element, complement_element, reference_element = "", "", "", "", "", "", "", ""

        sale_type_node = ""
        if totem_print:
            sale_type = "(TOTEM)"
        else:
            if header_pod_type == "DT":
                sale_type = "(DRIVE-THRU)"
            elif header_pod_type == "DL":
                sale_type = "(DELIVERY)"

                try:
                    street_name_element = get_xml_node_value(order_t, "STREET_NAME")
                    street_number_element = get_xml_node_value(order_t, "STREET_NUMBER")
                    neighborhood_element = get_xml_node_value(order_t, "NEIGHBORHOOD")
                    postal_code_element = get_xml_node_value(order_t, "POSTAL_CODE")
                    city_element = get_xml_node_value(order_t, "CITY")
                    state_element = get_xml_node_value(order_t, "STATE")
                    complement_element = get_xml_node_value(order_t, "COMPLEMENT")
                    reference_element = get_xml_node_value(order_t, "REFERENCE")

                except Exception:
                    sys_log_exception("Error in get address on Delivery picklist")

                sale_type_node = get_xml_node_value(order_t, "PICKUP_TYPE")
                if sale_type_node is not None:
                    sale_type_node = sale_type_node.get("value", "") if hasattr(sale_type_node, 'get') else sale_type_node
                    if sale_type_node.upper() == "TAKE_OUT":
                        sale_type = " (BK EXPRESS - VIAGEM)"
                    elif sale_type_node.upper() == "EAT_IN":
                        sale_type = " (BK EXPRESS - LOJA)"
            else:
                sale_type_node = get_xml_node_value(order_t, "SALE_TYPE")
                sale_type_node = sale_type_node.get("value", "") if hasattr(sale_type_node, 'get') else sale_type_node
                if sale_type_node is not None:
                    if sale_type_node == "TAKE_OUT":
                        sale_type = " (VIAGEM)"
                    else:
                        sale_type = " (LOJA)"
                else:
                    sale_type = " (LOJA)"
                    sale_type_node = ""

        title = _center(title + sale_type, SMALL_COLS)

        # Retrieve the last "StateHistory/State" entry
        timestamp = get_xml_node_value(order_t, "PAID", "state", "timestamp")
        if len(timestamp) > 0:
            # Convert it to a time object
            timestamp = time.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
            order_datetime = time.strftime(DATE_TIME_FMT, timestamp)
        else:
            order_datetime = ""

        current_datetime = time.strftime(DATE_TIME_FMT, time.localtime())

        if reprint:
            reprinted_at = "\nReimpresso..: %s" % current_datetime
        else:
            order_datetime = current_datetime
            reprinted_at = ""

        guest_name = get_xml_node_value(order_t, 'CUSTOMER_NAME')
        posid = int(order_t.get("originator")[-3:])
        order_id = int(order_t.get("order_id"))
        preheader = ""
        store_id = get_store_id(posid)

        if receipt:
            preheader = "\n".join(_center(line) for line in RECEIPTS_HEADER)

        header = """%(TXT_NORMAL)s%(TXT_BOLD_OFF)s%(TXT_FONT_A)s%(preheader)s%(SMALL_SEPARATOR)s\n%(title)s %(reprinted_at)s
Data/hora...: %(order_datetime)s
Numero Ped..: %(order_id)s (Reg #%(posid)02d) / %(store_id)s
""" % _join(globals(), locals())

        if sale_type_node is not None and sale_type_node.upper() == "DELIVERY":
            header += "Nome Cliente: %(TXT_BOLD_ON)s%(guest_name)s%(TXT_NORMAL)s%(TXT_BOLD_OFF)s\n" % _join(globals(), locals())
        else:
            header += "Nome Cliente: %(TXT_BOLD_ON)s%(TXT_4SQUARE)s%(guest_name)s%(TXT_NORMAL)s%(TXT_BOLD_OFF)s\n" % _join(globals(), locals())

        if header_pod_type == "DL":
            if street_name_element is not "" and sale_type_node is not None and sale_type_node.upper() not in ["TAKE_OUT", "EAT_IN"]:
                header += """Endereco....: {0}, {1}\n""".format(street_name_element, street_number_element)
                if complement_element is not None and len(complement_element) > 0:
                    header += """Complemento.: {0}\n""".format(complement_element)
                if reference_element is not None and len(reference_element) > 0:
                    header += """Referencia..: {0}\n""".format(reference_element)
                if neighborhood_element is not None and len(neighborhood_element) > 0:
                    header += """Bairro......: {0}\n""".format(neighborhood_element)
                if postal_code_element is not None and len(postal_code_element) > 0:
                    header += """CEP.........: {0}\n""".format(postal_code_element)
                if city_element is not None and len(city_element) > 0:
                    header += """Cidade......: {0}\n""".format(city_element)
                if state_element is not None and len(state_element) > 0:
                    header += """Estado......: {0}\n""".format(state_element)

            parceiro = ""
            parceiro_node = get_xml_node_value(order_t, "PARTNER")
            if parceiro_node is not None:
                parceiro = parceiro_node.get("value", "") if hasattr(parceiro_node, 'get') else parceiro_node

            parceiro_id = ""
            parceiro_id_node = get_xml_node_value(order_t, "SHORT_REFERENCE")
            if parceiro_id_node is not None:
                parceiro_id = parceiro_id_node.get("value") if hasattr(parceiro_id_node, 'get') else parceiro_id_node

            header += """Parceiro....: {0}
N Parceiro..: {1}
""".format(parceiro.upper(), parceiro_id)

        header += SMALL_SEPARATOR
        return header

    def get_xml_node_value(order_temp, prop_value, prop_name="key", value_name="value"):
        node = order_temp.findall(".//*[@{0}='{1}']".format(prop_name, prop_value))
        if node is not None and len(node) > 0:
            return remove_accents(node[0].get(value_name, "").encode("utf-8"))
        else:
            return ""

    def add_item(item, level=0, only_level=0, actual_level=0, is_sub_item=False, father_def_qty="0", father_type=""):
        tags = None
        try:
            if item.get('json_tags') is not None:
                tags = json.loads(item.get('json_tags')) or []
                for tag in tags:
                    if 'NOPICKLIST=TRUE' in tag.upper():
                        return  # Ignore this item
        except ValueError:
            pass
        except Exception as ex_tag:
            sys_log_exception("Error reading Tags in PickList print - Exception %s" % str(ex_tag))
            pass
        try:
            items_keys = ("qty", "default_qty", "item_type", "description", "modifier_label", "only", "min_qty", "level", "line_number", "part_code")
            qty, default_qty, item_type, name, label, only_flag, min_qty, item_level, line_number, part_code = map(item.get, items_keys)

            only = (only_flag == "true")

            item_level = int(float(item_level)) if item_level else 0
        except Exception as e:
            sys_log_exception("Error item_level %s" % str(e))

        if item_level == 0 and qty == "0":
            return  # Ignore Removed Items

        #if item_type in ("INGREDIENT", "CANADD") and (((qty == default_qty) and (only_level == 0)) or ((qty == min_qty) and (only_level > 0)) or item_level != level):
        #    return  # Ignore this item

        if item_type in "COMBO" and qty == default_qty and int(qty) == 0:
            return  # Ignore Empty COMBOS

        qty_str = str(qty) + " "

        if father_type == "OPTION":
            qty_str = qty_str if qty != "0" else "  Sem   "
            qty_str = "  Extra " if int(qty) >= int(default_qty) and father_def_qty == "0" and level != 0 else qty_str

        if label is not None:
            qty_str = ""
            label = "%s" % label
        else:
            label = ""

        if item_level != 0 and qty_str.strip() == "1":
            qty_str = "  "

        if qty >= default_qty and only_level > 0 and item_type == "INGREDIENT":
            only_str = "Only "
            if qty == default_qty:
                label = ""
        else:
            only_str = ""

        if item_type not in "OPTION":
            actual_level += 1
            line = _cut("%s %s%s%s%s" % (("  " * int(actual_level)), qty_str, only_str, label, name))

            if is_sub_item:
                if tags and 'CFH=true' in tags:
                    actual_level -= 1
                else:
                    if qty >= default_qty and father_def_qty == "0" and father_type == "OPTION":
                        for i in range(0, int(qty) - int(default_qty)):
                            report.write("%s\n" % line.encode("utf-8"))
                    else:
                        report.write("%s\n" % line.encode("utf-8"))
            else:
                data = "%(TXT_BOLD_ON)s%(line)s%(TXT_BOLD_OFF)s\n" % _join(globals(), locals())
                report.write(data.encode("utf-8"))

            for comment in item.findall('Comment'):
                report.write("%s (%s)\n" % ("  " * int(actual_level), remove_accents(comment.get('comment').encode('utf-8'))))

        level += 1
        sorted_items = sorted(item.findall("Item"), cmp=custom_compare) if level > 0 else item.findall("Item")
        for sub_item in sorted_items:
            is_sub_item = True
            add_item(sub_item, level, only_level + (1 if only else 0), actual_level, is_sub_item, default_qty, item_type)

    def custom_compare(a, b):
        a_item_type = a.get("item_type")
        b_item_type = b.get("item_type")
        if a_item_type != b_item_type and not ((a_item_type == "INGREDIENT" and b_item_type == "CANADD") or (a_item_type == "CANADD" and b_item_type == "INGREDIENT")):
            return 1 if a_item_type < b_item_type else -1
        if a.get("priority") != b.get("priority"):
            return 1 if a.get("priority") < b.get("priority") else -1
        return 1 if a.get("description") > b.get("description") else -1

    def center_text(text, sep=" "):
        line_size = COLS
        text = " %s " % text
        inicio = sep * int((line_size - len(text)) / 2)
        meio = inicio + text
        fim = sep * (line_size - len(meio))
        return meio + fim

    def add_sale_type(order_t):
        sale_pod_type = order_t.get("pod_type")

        sale_type = ""
        if sale_pod_type == "DT":
            sale_type = "DRIVE-THRU"
        else:
            if order_t.get("sale_type") != 'EAT_IN':
                sale_type = (order_t.get("sale_type")).replace('_', ' ').title()
                if sale_type.upper() == "APP":
                    pickup_type_element = get_xml_node_value(order_t, "PICKUP_TYPE").upper()

                    if pickup_type_element is not None:
                        pickup_type_element = pickup_type_element.get("value", "") if hasattr(pickup_type_element, 'get') else pickup_type_element
                        if pickup_type_element.upper() == "TAKE_OUT":
                            sale_type = "VIAGEM"

                        if pickup_type_element.upper() == "EAT_IN":
                            sale_type = ""

                if "TAKE" in sale_type.upper():
                    sale_type = "VIAGEM"

        if sale_type != "":
            sale_type = center_text(sale_type, '*')
            report.write("\n%s\n\n" % sale_type)
        else:
            report.write("\n\n")

    def create_qrcode(data):
        qr = qrcode.QRCode(
            version=2,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=5,
            border=4,
        )

        qr.add_data(data)
        qr.make(fit=True)

        img = qr.make_image()
        img = img.convert("RGB")
        img = printer_wrapper.image(img)

        return img.strip()

    report = StringIO()
    order_xml = eTree.XML(production_xml)
    is_reprint = False

    if order_xml.tag == "Orders":
        is_reprint = True
        order = order_xml.find('Order')
        handler = SystemOrderParser()
        xml.sax.parseString(eTree.tostring(order), handler)
        order_xml = handler.order
        convert_xml = OrderXml()
        order_xml = eTree.XML(convert_xml.to_xml(order_xml))

    order = order_xml if order_xml.tag == "ProductionOrder" else order_xml.find("ProductionOrder")

    pod_type = order.get("pod_type")
    if pod_type == "KK":
        return Exception()

    report.write("%(TXT_ALIGN_LT)s" % _join(globals(), locals()))
    report.write("%(TXT_BOLD_ON)s" % _join(globals(), locals()))
    report.write(_report_header("", order, reprint=is_reprint))
    report.write("%(TXT_BOLD_OFF)s" % _join(globals(), locals()))
    add_sale_type(order)

    report.write("%(TXT_BOLD_ON)s" % _join(globals(), locals()))
    sz = report.tell()

    def get_order_sum_up(active_sale_lines):
        global list_coupons
        if not list_coupons:
            conn = None
            try:
                conn = DBDriver().open(sysactions.mbcontext)
                list_coupons = [row.get_entry(0) for row in conn.select("select productcode from productdb.producttags where tag like 'color%';")]
            except Exception as ex:
                sys_log_exception("Exception getting list of coupons -> Ex: {}".format(ex))
            finally:
                if conn:
                    conn.close()

        global products_ordination
        if not products_ordination:
            products_ordination = (helper.read_swconfig(sysactions.mbcontext, "Products.ProductsOrdination") or "").split("\0")

        global standalone_products_exception
        if not standalone_products_exception:
            standalone_products_exception = (helper.read_swconfig(sysactions.mbcontext, "Products.StandaloneProductsException") or "").split("\0")

        order_sum = ''
        parsed_sale_lines = get_parsed_sale_lines(active_sale_lines)

        products_in_exception = []
        products_not_in_exception = []
        for sale_line in active_sale_lines:
            item_type = sale_line.get('item_type')
            if item_type not in ('COMBO', 'OPTION', 'CANADD'):
                search_results = re.search(r'Category=(.*?)"', sale_line.get("json_tags") or "")
                category = search_results.group(1) if search_results else ""
                if category in standalone_products_exception:
                    products_in_exception.append(sale_line)
                else:
                    products_not_in_exception.append(sale_line)
        if len(products_in_exception) > 0 and len(products_not_in_exception) == 0:
            return None

        for cat in parsed_sale_lines:
            consolidated = {}
            for item in parsed_sale_lines[cat]:
                main_sale_line = item[0]
                part_code = main_sale_line.get('part_code')
                if part_code in consolidated:
                    if len(item) == 1:
                        found = False
                        for item_list in consolidated[part_code]:
                            if len(item_list) == 1:
                                item_list[0].set('real_qty', str(int(float(consolidated[part_code][0][0].get('real_qty')) + float(item[0].get('real_qty')))))
                                found = True
                                break
                        if not found:
                            consolidated[part_code].insert(0, item)
                    else:
                        item_len = len(item)
                        found = False
                        for item_list in consolidated[part_code]:
                            if len(item_list) == item_len:
                                for i in range(1, item_len):
                                    if item_list[i].get('qty') == item[i].get('qty') and \
                                            item_list[i].get('part_code') == item[i].get('part_code'):
                                        item_list[0].set('real_qty', str(int(float(item_list[0].get('real_qty')) + float(item[0].get('real_qty')))))
                                        found = True
                                        break
                        if not found:
                            consolidated[part_code].append(item)
                else:
                    consolidated[part_code] = [item]
            parsed_sale_lines[cat] = []
            for part_code in sorted(consolidated.keys()):
                product_sale_lines = []
                for sale_line_group in consolidated[part_code]:
                    product_sale_lines.extend(sale_line_group)
                parsed_sale_lines[cat].extend(product_sale_lines)

        sorted_sale_lines = []

        for category in products_ordination:
            sorted_sale_lines.extend(parsed_sale_lines.get(category) or [])
        for sale_line in sorted_sale_lines:
            order_sum = item_to_add(sale_line, order_sum, list_coupons)
        return order_sum

    def item_to_add(sale_line, order_sum, list_coupons):
        if sale_line.get('partCode') not in list_coupons:
            product_name = sale_line.get('description')
            qty = float(sale_line.get('real_qty'))
            product_type = sale_line.get('item_type')
            modification = (sale_line.get('modification') or 'false') == 'true'
            is_option = (sale_line.get('is_option') or 'false') == 'true'
            if product_type == 'CANADD':
                qty = max(qty - int(sale_line.get("default_qty")), 0)

            formated_qty = str(int(qty)) if qty > 0 else "Sem"
            if qty > 0:

                if product_type in ('PRODUCT', 'CANADD') and not modification:
                    order_sum += '   {0} {1}\n'.format(formated_qty, product_name)
                else:
                    if is_option:
                        order_sum += '      {0} {1}\n'.format(formated_qty, product_name)
                    else:
                        order_sum += '      {0} Extra {1}\n'.format(formated_qty, product_name)
            else:
                if product_type in ('PRODUCT', 'CANADD'):
                    order_sum += '      {0} {1}\n'.format(formated_qty, product_name)

        return order_sum

    def get_parsed_sale_lines(active_sale_lines):
        sale_line_dict = {}
        categories = []
        last_item_type = ''
        last_level = ''
        base_category = ''
        options = {}
        base_level = int(active_sale_lines[0].get('level'))
        ignore_combo = False

        for sale_line in active_sale_lines:
            level = int(sale_line.get('level'))
            item_type = sale_line.get('item_type')

            if level == 0 and float(sale_line.get('qty')) == 0 and item_type == "COMBO":
                ignore_combo = True
                continue
            elif level == 0 and float(sale_line.get('qty')) != 0:
                ignore_combo = False

            if ignore_combo and level > 0:
                continue

            if float(sale_line.get('default_qty')) == 0 \
                    and float(sale_line.get('qty')) == 0 \
                    and float(sale_line.get('qty_added')) == 0:
                continue

            if item_type not in ('COMBO', 'OPTION'):
                if float(sale_line.get('real_qty')) <= 0 and int(sale_line.get('default_qty') or 0) == 0:
                    continue
                search_result = re.search(r'Category=(.*?)"', sale_line.get("json_tags") or "")
                category = search_result.group(1) if search_result else ""

                search_results = re.search(r'"QtyOptions=(.*?)"', sale_line.get("json_tags") or "")
                if search_results:
                    for qty in search_results.group(1).split('|'):
                        option, qts = qty.split('>')
                        _, min_qty, _ = qts.split(';')
                        options[option] = float(min_qty)

            # Removing COMBO type
            if item_type == 'COMBO':
                base_level = level + 1
                last_item_type = item_type
                last_level = level
                continue
            # Products with level 0 are fathers
            elif item_type != 'OPTION' and level <= base_level:
                if category not in categories:
                    categories.append(category)
                    sale_line_dict.setdefault(category, [])
                sale_line_dict[category].append([sale_line])
                base_category = category
                base_level = level

            # If last type are OPTION or COMBO and is a father, he add the current product as father too
            elif item_type != 'OPTION' and last_item_type in ('OPTION', 'COMBO') and (last_level == base_level or last_level == 0):
                if category not in categories:
                    categories.append(category)
                    sale_line_dict.setdefault(category, [])
                sale_line_dict[category].append([sale_line])
                base_category = category
                if last_item_type != 'COMBO':
                    base_level = level

            # Modifications are added in same category of your father
            elif item_type != 'OPTION' and level > base_level:
                sale_line.set('modification', 'true')
                last_context_id = sale_line.get('item_id').split('.')[-1]
                if last_context_id in options and options[last_context_id] > 0:
                    sale_line.set('is_option', 'true')
                    options[last_context_id] -= float(sale_line.get('real_qty'))
                sale_line_dict[base_category][-1].append(sale_line)

            last_item_type = item_type
            last_level = level

        return sale_line_dict

    if grouped_items:
        def fix_production_xml_qty(item, parent_qty=None):
            is_combo = item.get('item_type') == "OPTION"
            is_ingredient = False
            for tag in json.loads(item.get('json_tags')):
                if "Category=EXTRA" == tag:
                    is_ingredient = True
                    break
                elif "CFH=true" == tag:
                    break

            if parent_qty is not None and not is_combo:
                item.set('real_qty', str(parent_qty) if ((not is_ingredient) and parent_qty) else item.get('qty'))
            for item_child in item:
                fix_production_xml_qty(item_child, int(item.get('qty')) * (parent_qty or 1) if not is_combo else parent_qty)

        map(fix_production_xml_qty, order.find('Items'))
        sale_lines = [x for x in order.findall(".//Item")]
        for sale_line in sale_lines:
            for child in sale_line:

                sale_line.remove(child)

        order_sum = get_order_sum_up(sale_lines)
        if order_sum:
            report.write(order_sum)
        else:
            return Exception()
    else:
        map(add_item, order.findall("Items/Item"))

    if sz == report.tell():
        return Exception()

    report.write("%(TXT_BOLD_OFF)s\n" % _join(globals(), locals()))
    add_sale_type(order)

    # Prints QRCode only when it will be used for PickupDisplay on PickList
    if "PickList" in pick_up_type:
        report.write("%(TXT_ALIGN_CT)s" % _join(globals(), locals()))
        report.write("%s" % create_qrcode('QR' + (order.get("order_id")).zfill(8) + 'BK'))

    return report.getvalue()


def remove_accents(txt, codif='utf-8'):
    return normalize('NFKD', txt.decode(codif)).encode('ASCII', 'ignore')


def production_grouped_pick_list(production_xml, *args):
    return production_pick_list(production_xml, True, *args)


def get_store_id(pos_id):
    global store_id

    if not store_id:
        conn = None
        try:
            conn = dbd.open(mbcontext, dbname=str(pos_id))
            cursor = conn.select("SELECT KeyValue FROM storecfg.Configuration WHERE KeyPath = 'Store.Id'")
            for row in cursor:
                store_id = row.get_entry(0)
                break
        finally:
            if conn:
                conn.close()
    return store_id
