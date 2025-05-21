# -*- coding: utf-8 -*-
import json
from xml.etree import cElementTree as eTree

from sysactions import action, get_model, get_posot, get_operator_session, StopAction, translate_message, \
    show_confirmation, get_current_order

from bustoken import TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION
from msgbus import FM_PARAM, TK_SYS_ACK
from sysactions import show_messagebox
from systools import sys_log_exception


from actions.functions.do_store_order import doStoreOrder
from model.customexception import SendOrderToProductionError
from .. import logger
from .. import mb_context


@action
def produce_delivery_order(pos_id, order_id, manual_recall='false', warn_inconsistencies='false'):
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    session = get_operator_session(model)

    if not _validate_manual_order(model, pos_ot, pos_id, order_id, warn_inconsistencies.lower() != 'false'):
        return
    
    try:
        manual_recall = manual_recall.lower() == 'true'
        if manual_recall:
            doStoreOrder(pos_id, show_popup=False)

        msg = mb_context.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION, FM_PARAM, order_id)
        if msg.token == TK_SYS_ACK:
            show_messagebox(pos_id, "$ORDER_PRODUCED")
        else:
            raise SendOrderToProductionError("$ERROR_SENDING_REMOTE_ORDER_TO_PRODUCTION|{}".format(msg.data))
    except Exception as ex:
        sys_log_exception("Error producing delivery order")
        logger.error(ex)

        show_messagebox(pos_id, message=ex.message)
        
        if manual_recall:
            pos_ot.recallOrder(int(pos_id), int(order_id), session)
            
        raise StopAction()
    
    
def _validate_manual_order(model, pos_ot, pos_id, order_id, warn_inconsistencies):
    try:
        order_picture = eTree.XML(pos_ot.orderPicture(pos_id, order_id))
        manual_order = order_picture.find("Order")
        remote_order_json_text = order_picture.find(".//OrderProperty[@key='REMOTE_ORDER_JSON']").get("value", None)
        if not remote_order_json_text or not warn_inconsistencies:
            return True
    
        remote_json = json.loads(remote_order_json_text)
    
        order_items_quantity = _get_order_items_quantity(manual_order)
        order_total_value = _get_order_total_value(manual_order)
        json_items_quantity = _get_json_items_quantity(remote_json)
        json_total_value = _get_json_total_value(remote_json)
        
        items_quantity_is_different, quantity_diff = _items_quantity_is_different(order_items_quantity, json_items_quantity)
        value_is_different, value_diff = _value_is_different(order_total_value, json_total_value)
    
        if items_quantity_is_different or value_is_different:
            _confirm_order_difference(model, pos_id, remote_json)
            _validate_value_difference(model, pos_id, value_diff, order_total_value, json_total_value)

    except StopAction:
        return False
    except Exception as _:
        logger.exception("Error validating manual order")
        return False

    return True


def _get_json_total_discounts_values(remote_json):
    discounts = 0
    vouchers = remote_json.get("vouchers")
    if not vouchers:
        return discounts
    store_discount = vouchers.get("store")
    if not store_discount:
        return discounts
    for discount_type in store_discount:
        discount_value = float(store_discount.get(discount_type))
        discounts += discount_value
        
    return discounts


def _validate_value_difference(model, pos_id, value_diff, order_total_value, json_total_value):
    message = "$CONFIRM_MANUAL_ORDER_DISCOUNT" if value_diff > 0 else "$CONFIRM_MANUAL_ORDER_ADDITION"
    message = message + "|{0}|{1}|{2}".format(_format_currency(model, order_total_value),
                                              _format_currency(model, json_total_value),
                                              _format_currency(model, abs(value_diff)))
    if not show_confirmation(pos_id, message):
        raise StopAction()
    
    _apply_difference_discount(pos_id, value_diff)


def _apply_difference_discount(pos_id, value_diff):
    from pospromotions import apply_amount_discount
    
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    order = get_current_order(model)
    apply_amount_discount(pos_id, pos_ot, order, discount_type=1, discount_value=float(value_diff))


def _confirm_order_difference(model, pos_id, remote_json):
    partner_order_id = _get_json_order_id(remote_json)
    message = translate_message(model, "DELIVERY_RECALL_WARNING")
    message = message.format(
        partner_order_id,
        remote_json.get("partner", "").upper(),
        str(_get_json_items_quantity(remote_json)),
        _format_currency(model, _get_json_total_value(remote_json))
    )
    if not show_confirmation(pos_id, message):
        raise StopAction()


def _format_currency(model, value):
    currency_symbol = translate_message(model, "L10N_CURRENCY_SYMBOL")
    return "{0} {1:.2f}".format(currency_symbol, value)


def _items_quantity_is_different(order_items_quantity, json_items_quantity):
    is_different = not (order_items_quantity == json_items_quantity)
    value_diff = order_items_quantity - json_items_quantity
    
    return is_different, value_diff


def _value_is_different(order_total_value, json_total_value):
    is_different = not (order_total_value == json_total_value)
    value_diff = order_total_value - json_total_value

    return is_different, value_diff


def _get_order_total_value(manual_order):
    manual_order_total = float(manual_order.get("totalAfterDiscount", 0)) + float(manual_order.get("taxTotal", 0))
    return manual_order_total


def _get_json_total_value(remote_json):
    json_total_discounts_value = _get_json_total_discounts_values(remote_json)
    json_total_value = float(remote_json.get("subTotal", 0))
    delivery_fee_value = float(remote_json.get("deliveryFee", 0))
    
    return json_total_value + delivery_fee_value - json_total_discounts_value


def _get_order_items_quantity(manual_order):
    manual_order_sale_line_qty = len(
            [line for line in manual_order.findall(".//SaleLine") if (int(line.get("qty", "0")) > 0)]
    )
    
    return manual_order_sale_line_qty


def _get_json_items_quantity(remote_json):
    remote_json_sale_line_qty = len(
            [line for line in remote_json.get("items", []) if (int(line.get("quantity", "0")) > 0)]
    )
    
    return remote_json_sale_line_qty


def _get_json_order_id(remote_json):
    return remote_json.get("shortReference", "")
