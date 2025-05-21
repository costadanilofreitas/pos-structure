# -*- coding: utf-8 -*-

import collections
import time
import xml.sax
import xml.sax.handler
from cStringIO import StringIO
from unicodedata import normalize
from xml.etree import ElementTree as eTree

# START - DO NOT CHANGE THIS IMPORT ORDINATION
import sysactions
from helper import MwOrderStatus
from production.processor import SystemOrderParser, OrderXml
from reports import mbcontext
import printer_wrapper
from constants import *
from systools import sys_log_exception, sys_log_warning
# END - DO NOT CHANGE THIS IMPORT ORDINATION

sysactions.mbcontext = mbcontext

COLS = 42
SMALL_COLS = 42
SIMPLE_SEPARATOR = ("-" * SMALL_COLS)
SEPARATOR = ("=" * COLS)
SMALL_SEPARATOR = ("=" * SMALL_COLS)
DATE_TIME_FMT = "%d/%m/%Y %H:%M:%S"
DATE_FMT = "%d/%m/%Y"
TIME_FMT = "%H:%M:%S"
PICKUP_TYPE = None


def production_pick_list(order_xml, *args):
    try:
        production_order, is_reprint = _parse_order_xml_to_production_order(order_xml)
        if _order_is_voided(production_order):
            sys_log_warning("ignoring voided order")
            return Exception()

        pod_type = production_order.get("pod_type")
        if pod_type == "KK":
            return Exception()

        report = StringIO()

        report.write("%(TXT_ALIGN_LT)s" % _join(globals(), locals()))
        report.write("%(TXT_BOLD_ON)s" % _join(globals(), locals()))

        report_header = _get_report_header(production_order, is_reprint)
        report.write(report_header)

        report.write("%(TXT_BOLD_OFF)s" % _join(globals(), locals()))

        pre_sale_lines_report = report.tell()

        grouped_sale_lines = _get_grouped_sale_lines_by_seat(production_order)
        formatted_sale_lines = _get_formatted_sale_lines_by_seats(grouped_sale_lines, production_order)

        report.write(formatted_sale_lines)

        if pre_sale_lines_report == report.tell():
            sys_log_warning("Order has no sale lines to print")
            return Exception()

        report = _add_additional_comments(report, production_order)
        report = _add_sale_type(report, production_order)

        qr_code = _get_qr_code(production_order)
        if qr_code:
            report.write(qr_code)

        return report.getvalue()
    except Exception as _:
        sys_log_exception("Error building production PickList")


def _order_is_voided(production_order):
    return MwOrderStatus.VOIDED.name == production_order.get("state", "")


def _get_qr_code(production_order):
    global PICKUP_TYPE
    try:
        if PICKUP_TYPE is None:
            PICKUP_TYPE = sysactions.get_storewide_config("Store.pickUpDisplayType", defval="Manager")
    except Exception as _:
        PICKUP_TYPE = 'Manager'

    # Prints QRCode only when it will be used for PickupDisplay on PickList
    if "PickList" in PICKUP_TYPE:
        return _create_qrcode('QR' + (production_order.get("order_id")).zfill(8) + 'BK')
    else:
        return ""


def _parse_order_xml_to_production_order(order_xml):
    order_xml = eTree.XML(order_xml)
    if order_xml.tag == "Orders":
        order = order_xml.find('Order')
        handler = SystemOrderParser()
        xml.sax.parseString(eTree.tostring(order), handler)
        order_xml = handler.order
        convert_xml = OrderXml()
        order_xml = eTree.XML(convert_xml.to_xml(order_xml))
    production_order = order_xml if order_xml.tag == "ProductionOrder" else order_xml.find("ProductionOrder")

    is_reprint = False
    production_items = production_order.findall(".//Items") or []
    for item in production_items:
        is_reprint = len(item.findall(".//TagHistory/TagEvent[@tag='printed']")) > 0

    return production_order, is_reprint


def _get_report_header(production_order, is_reprint):
    header_pod_type = production_order.get("pod_type")
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
                street_name_element = _get_xml_node_value(production_order, "STREET_NAME")
                street_number_element = _get_xml_node_value(production_order, "STREET_NUMBER")
                neighborhood_element = _get_xml_node_value(production_order, "NEIGHBORHOOD")
                postal_code_element = _get_xml_node_value(production_order, "POSTAL_CODE")
                city_element = _get_xml_node_value(production_order, "CITY")
                state_element = _get_xml_node_value(production_order, "STATE")
                complement_element = _get_xml_node_value(production_order, "COMPLEMENT")
                reference_element = _get_xml_node_value(production_order, "REFERENCE")

            except Exception:
                sys_log_exception("Error in get address on Delivery picklist")

            sale_type_node = _get_xml_node_value(production_order, "PICKUP_TYPE")
            if sale_type_node is not None:
                sale_type_node = sale_type_node.get("value", "") if hasattr(sale_type_node, 'get') else sale_type_node
                if sale_type_node.upper() == "TAKE_OUT":
                    sale_type = " (BK EXPRESS - VIAGEM)"
                elif sale_type_node.upper() == "EAT_IN":
                    sale_type = " (BK EXPRESS - LOJA)"
        else:
            sale_type_node = _get_xml_node_value(production_order, "SALE_TYPE")
            sale_type_node = sale_type_node.get("value", "") if hasattr(sale_type_node, 'get') else sale_type_node
            if sale_type_node is not None:
                if sale_type_node == "TAKE_OUT":
                    sale_type = " (VIAGEM)"
                else:
                    sale_type = " (LOJA)"
            else:
                sale_type = " (LOJA)"
                sale_type_node = ""

    title = _center(sale_type, SMALL_COLS)

    produced_datetime = ""
    timestamp = _get_first_printed_time(production_order)
    if timestamp is not None:
        timestamp = time.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
        produced_datetime = time.strftime(DATE_TIME_FMT, timestamp)

    if is_reprint:
        current_datetime = time.strftime(DATE_TIME_FMT, time.localtime())
        reprinted_at = "Reimpresso....: %s" % current_datetime
    else:
        reprinted_at = ""

    posid = int(production_order.get("originator")[-2:])
    order_id = int(production_order.get("order_id"))
    user_id = production_order.get("session_id").split("user=")[1].split(",")[0]
    user_name = eTree.XML(sysactions.get_user_information(user_id)).find(".//user").get("LongName")[:15]
    user_info = "{} / {}".format(user_id, user_name)

    table_id = None
    if production_order.find(".//Property[@key='TAB_ID']") is not None:
        order_descr = "Comanda/Pedido"
        table_id = production_order.find(".//Property[@key='TAB_ID']").get('value')
        order_descr_id = "{} / {}".format(table_id, order_id)
    elif production_order.find(".//Property[@key='TABLE_ID']") is not None:
        order_descr = "Mesa/Pedido..."
        table_id = production_order.find(".//Property[@key='TABLE_ID']").get('value')
        order_descr_id = "{} / {}".format(table_id, order_id)
    else:
        order_descr = "Numero Pedido."
        order_descr_id = order_id

    created_at = time.strptime(production_order.get("created_at"), "%Y-%m-%dT%H:%M:%S.%f")
    created_at = time.strftime(DATE_TIME_FMT, created_at)

    preheader = ""
    if is_reprint:
        preheader = "*** REIMPRESAO ***"
    preheader = _center(preheader, SMALL_COLS)

    header = "%(TXT_NORMAL)s%(TXT_BOLD_OFF)s%(TXT_FONT_A)s%(preheader)s\n%(SMALL_SEPARATOR)s\n%(title)s" % _join(globals(), locals())
    header += "\n%(order_descr)s: %(order_descr_id)s (POS #%(posid)02d)" % _join(globals(), locals())
    header += "\nHora Pedido...: {}".format(created_at)
    header += "\nHora Produzido: {}".format(produced_datetime)

    if is_reprint:
        header +="\n{}".format(reprinted_at)

    header +="\nOperador......: {}".format(user_info)
    header +="\n{}".format(SMALL_SEPARATOR)

    if header_pod_type == "DL":
        if street_name_element is not "" and sale_type_node is not None and sale_type_node.upper() not in ["TAKE_OUT",
                                                                                                           "EAT_IN"]:
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
        parceiro_node = _get_xml_node_value(production_order, "PARTNER")
        if parceiro_node is not None:
            parceiro = parceiro_node.get("value", "") if hasattr(parceiro_node, 'get') else parceiro_node

            parceiro_id = ""
            parceiro_id_node = _get_xml_node_value(production_order, "SHORT_REFERENCE")
            if parceiro_id_node is not None:
                parceiro_id = parceiro_id_node.get("value") if hasattr(parceiro_id_node, 'get') else parceiro_id_node

            header += """Parceiro....: {0}
N Parceiro..: {1}
""".format(parceiro.upper(), parceiro_id)

        header += SMALL_SEPARATOR
    return header


def _get_grouped_sale_lines_by_seat(production_order):
    pos_id = int(production_order.get("originator")[-2:])
    model = sysactions.get_model(pos_id)

    grouped_sale_lines = {}
    pre_option_level = None
    seats_by_line_number = {}
    preceding_removed_combo = False

    for item in production_order.findall(".//Item"):
        line_number = item.get("line_number")
        if line_number in seats_by_line_number:
            item_seat = seats_by_line_number[line_number]
        else:
            item_seat = 0
            for prop in item.findall("Properties/Property"):
                if prop.attrib["key"] == "seat":
                    seat_quantity = prop.attrib["value"]
                    item_seat = seat_quantity
                    break

        if line_number not in seats_by_line_number:
            seats_by_line_number[line_number] = item_seat

        sale_line, pre_option_level, preceding_removed_combo = _get_formatted_sale_line(model,
                                                                                        item,
                                                                                        pre_option_level,
                                                                                        preceding_removed_combo)
        if sale_line:
            if item_seat in grouped_sale_lines:
                grouped_sale_lines[item_seat].append(sale_line)
            else:
                grouped_sale_lines[item_seat] = [sale_line]

    return grouped_sale_lines.items() if len(grouped_sale_lines) > 0 else grouped_sale_lines


def _get_formatted_sale_lines_by_seats(grouped_sale_lines, production_order):
    formatted_sale_lines = "\n"
    seat_title = " Assento {}"
    table_title = " Mesa"

    for seat, sale_lines_by_seat in collections.OrderedDict(sorted(grouped_sale_lines)).items():
        if production_order.find("./Properties/Property[@key='TABLE_ID']") is not None:
            title = seat_title.format(seat) if int(seat) != 0 else table_title
            formatted_sale_lines += "{}\n{}\n".format(title, SIMPLE_SEPARATOR)

        for sale_line in sale_lines_by_seat:
            if sale_line is not None:
                formatted_sale_lines += sale_line

        formatted_sale_lines += "\n"

    return formatted_sale_lines


def _get_formatted_sale_line(model, sale_line, pre_option_level=None, preceding_removed_combo=False):
    item_type = None if "item_type" not in sale_line.attrib else sale_line.get("item_type")

    level = int(sale_line.get("level"))

    if item_type == "COMBO":
        preceding_removed_combo = False

    if level == 0:
        pre_option_level = None

    if item_type in [None, "OPTION", "COUPON"]:
        pre_option_level = level if item_type == "OPTION" else None
        return None, pre_option_level, preceding_removed_combo

    qty = float(sale_line.get("qty") or 0)
    default_qty = float(sale_line.get("default_qty") or 0)

    if (qty == 0 and default_qty == 0) or preceding_removed_combo:
        if item_type == "COMBO":
            preceding_removed_combo = True
        return None, None, preceding_removed_combo

    if qty < default_qty and qty == 0:
        qty_description = sysactions.translate_message(model, "WITHOUT")
    else:
        qty_description = str(qty)

    indentation = " " * ((pre_option_level or level) + 1)
    product_name = sale_line.get("description")

    item_comment = sale_line.find("./Comment")
    if item_comment is not None:
        comment = item_comment.get("comment")

        comment_description = ""
        jumped_comment = ""
        if comment:
            if comment.startswith("["):
                comment_description = comment.replace("[", "").replace("]", "").upper()
                comment_description = sysactions.translate_message(model, comment_description)
            else:
                description = "[" + comment + "]"
                line_rjust = int(len(description) + len(indentation) + round(qty, 1))
                jumped_comment = _remove_accents(description.rjust(line_rjust))

        product_description = str(comment_description or qty_description) + " " + product_name
        line_rjust = len(product_description) + len(indentation)
        description = _remove_accents(product_description.rjust(line_rjust))

        formatted_sale_line = description + "\n"
        if jumped_comment:
            formatted_sale_line += jumped_comment + "\n"
    else:
        formatted_sale_line = indentation + qty_description + " " + _remove_accents(product_name) + "\n"

    if level <= pre_option_level:
        pre_option_level = None

    return formatted_sale_line, pre_option_level, preceding_removed_combo


def _get_xml_node_value(order_temp, prop_value, prop_name="key", value_name="value"):
    node = order_temp.findall(".//*[@{0}='{1}']".format(prop_name, prop_value))
    if node is not None and len(node) > 0:
        return _remove_accents(node[0].get(value_name, "").encode("utf-8"))
    else:
        return ""


def _add_sale_type(report, order_t):
    sale_pod_type = order_t.get("pod_type")

    sale_type = ""
    if sale_pod_type == "DT":
        sale_type = "DRIVE-THRU"
    else:
        if order_t.get("sale_type") != 'EAT_IN':
            sale_type = (order_t.get("sale_type")).replace('_', ' ').title()
            if sale_type.upper() == "APP":
                pickup_type_element = _get_xml_node_value(order_t, "PICKUP_TYPE").upper()

                if pickup_type_element is not None:
                    pickup_type_element = pickup_type_element.get("value", "") \
                        if hasattr(pickup_type_element, 'get') else pickup_type_element
                    if pickup_type_element.upper() == "TAKE_OUT":
                        sale_type = "VIAGEM"

                    if pickup_type_element.upper() == "EAT_IN":
                        sale_type = ""

            if "TAKE" in sale_type.upper():
                sale_type = "VIAGEM"

    if sale_type != "":
        sale_type = _center_text(sale_type, '*')
        report.write("\n%s" % sale_type)

    return report


def _create_qrcode(qr_data):
    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=5,
        border=4,
    )

    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image()
    img = img.convert("RGB")
    img = printer_wrapper.image(img)

    return img.strip()


def _add_additional_comments(report, production_order):
    tab_add_info = production_order.findall(".//Property[@key='TAB_ADD_INFO']")
    if tab_add_info and len(tab_add_info) > 0:
        tab_add_info_text = tab_add_info[0].attrib["value"]
        report.write("\n{}".format(SMALL_SEPARATOR))

        if len(tab_add_info_text) > COLS:
            report.write("\n\n%s" % tab_add_info_text[:COLS])
            report.write("\n%s" % tab_add_info_text[COLS:2*COLS])
        else:
            report.write("\n\n%s" % tab_add_info_text)

        report.write("\n\n{}".format(SMALL_SEPARATOR))

    return report


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


def _remove_accents(text):
    return normalize('NFKD', unicode(text)).encode('ASCII', 'ignore')


def _center_text(text, sep=" "):
    line_size = COLS
    text = " %s " % text
    inicio = sep * int((line_size - len(text)) / 2)
    meio = inicio + text
    fim = sep * (line_size - len(meio))

    return meio + fim


def _get_first_printed_time(production_order):
    production_items = production_order.findall(".//Items") or []
    for item in production_items:
        serverd_tags = item.findall(".//TagHistory/TagEvent[@tag='served']") or []
        if len(serverd_tags) > 0:
            return serverd_tags[0].attrib["timestamp"]

    return None
