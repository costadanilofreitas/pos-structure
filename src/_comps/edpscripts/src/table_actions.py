# -*- coding: utf-8 -*-
import os
import json

import iso8601
import pyscripts
import cfgtools
import sysactions
import logging
import base64

from typing import Union

import reportactions

from datetime import date, datetime, timedelta
from decimal import Decimal

from actions.login.signin_user import sign_in_user
from actions.models import UserLevels, SaleTypes
from actions.config import get_customer_info_config
from actions.models.mw_sys_errors import MwSysErrors
from actions.util import get_authorization, is_user_already_logged, get_drawer_amount, \
    do_set_drawer_status, check_sangria, is_sangria_enable
from application.domain import I18nImpl, TenderIdEnum, SaleLine
from application.domain.config import StaticConfig, StaticConfigJsonEncoder
from application.interactor import CreateTableOrderInteractor, DoChangeTipInteractor, \
    StartServiceInteractor, TotalTableInteractor, ReopenTableInteractor, CloseTableInteractor, \
    SetTableAvailableInteractor, ChooseLineSeatInteractor

from application.interactor.service.impl import TableReleaserImpl
from application.repository.impl import MwI18nRepository
from cfgtools import Group, Key
from actions.login.unpause_user import unpause_user
from msgbusboundary import MsgBusTableService as tableService, MsgBusOrderManager
from msgbusboundary.ui import MsgBusScreenChanger, MsgBusListBox
from old_helper import round_half_away_from_zero, convert_from_utf_to_localtime

from sysactions import \
    action, \
    get_posot, \
    get_model, \
    change_screen, \
    show_messagebox, \
    AuthenticationFailed, \
    get_user_information, \
    print_report, \
    send_message, \
    get_current_order, \
    format_amount, \
    set_custom, \
    get_custom, \
    get_poslist, \
    translate_message, \
    get_current_operator, \
    get_business_period, \
    get_line_product_name, \
    can_void_line, \
    get_storewide_config, \
    get_posfunction, \
    get_podtype, \
    get_operator_session, \
    has_current_order, \
    StopAction

from msgbus import FM_PARAM, TK_SYS_ACK, TK_PRN_PRINT, MBMessage, TK_POS_BUSINESSEND, TK_POS_BUSINESSBEGIN, \
    TK_PERSIST_SEQUENCER_RESET, MBTimeout, MBException
from systools import sys_log_error, sys_log_exception, sys_log_info
from tablemgrapi import get_posts, TableServiceException
from xml.etree import cElementTree as eTree
from bustoken import TK_FISCALWRAPPER_PROCESS_REQUEST, TK_SITEF_ADD_PAYMENT, TK_REMOTE_ORDER_GET_STORED_ORDERS, \
    TK_REMOTE_ORDER_GET_VOIDED_ORDERS, TK_REMOTE_ORDER_GET_CONFIRMED_ORDERS
from helper import get_valid_pricelists
import mw_helper
from pos_model import TableStatus
from pospromotions import apply_discount, clean_discounts_and_payments
from actions.eft import finish_eft_transactions
from actions.util.get_menu_user_logged import get_menu_manager_authenticated_user, set_menu_manager_authenticated_user
from actions.void.utils import void_order
from actions.util.list_users import list_all_opened_users
from actions.pos import has_tab_or_tables_opened, pos_must_be_blocked
from actions.delivery import get_remote_order_status
from utilfunctions import get_customer_doc_after_paid, update_custom_properties, get_void_reason
from custom_sysactions import user_authorized_to_execute_action, initialize_manager_authorizations, \
    block_action_if_pos_is_blocked

DELIVERY_STORED_ORDERS = {}
DELIVERY_VOIDED_ORDERS = {}
selected_tables = {}
max_number_of_seats = None
max_number_of_tab_digits = None  # type: Union[None, int]
set_table_available_automatically = None
enable_payment_by_seat = None
tip_rate = None
can_open_table_from_another_operator = None
can_see_table_from_another_operator = None
enable_tab_btns = None
fetch_stored_orders_timeout = None
bordereau_enabled = None
print_operator_copy = None
print_tef_customer_receipt = True
print_tef_merchant_receipt = False
print_merchant_receipt = False
hide_unpriced_items_from_total_report = True
production_courses = []
sat_info = {}
print_pre_account_after_send_order = False
can_close_operator_with_opened_table = False
min_level_needed_to_see_all_tables = None  # type: Union[None, int]
transfer_table_allowed_status = None
join_table_allowed_status = None

mbcontext = pyscripts.mbcontext
logger = logging.getLogger("TableActions")

HAS_REMOTE_ORDER = mbcontext.MB_LocateService(mbcontext.hv_service, 'RemoteOrder', maxretries=1)


def main():
    try:
        _get_config()

        # This forces a POS Model update with current Store Tables layout
        for pos_id in get_poslist():
            model = get_model(pos_id)
            posts = get_posts(model)
            posts.storePicture(forceupdate=True)

    except TableServiceException, e:
        sys_log_error("Error initializing list of tables: %s" % str(e))


def _get_config():
    global max_number_of_seats
    global max_number_of_tab_digits
    global set_table_available_automatically
    global enable_payment_by_seat
    global tip_rate
    global can_open_table_from_another_operator
    global can_see_table_from_another_operator
    global fetch_stored_orders_timeout
    global bordereau_enabled
    global print_operator_copy
    global print_tef_merchant_receipt
    global print_tef_customer_receipt
    global print_merchant_receipt
    global hide_unpriced_items_from_total_report
    global print_pre_account_after_send_order
    global can_close_operator_with_opened_table
    global min_level_needed_to_see_all_tables
    global transfer_table_allowed_status
    global join_table_allowed_status

    print_merchant_receipt = get_storewide_config("Store.PrintMerchantReceipt", defval="False").lower() == "true"

    config = cfgtools.read(os.environ["LOADERCFG"])
    min_level_needed_to_see_all_tables = int(config.find_value("Customizations/MinLevelNeededToSeeAllTables") or 20)
    hide_unpriced_items_from_total_report = (config.find_value(
        "Customizations.HideUnpricedItemsFromTotalReport") or "true").lower() == "true"
    max_number_of_seats = int(config.find_value("Customizations.MaxNumberOfSeats")) \
        if config.find_value("Customizations.MaxNumberOfSeats") is not None else 99
    max_number_of_tab_digits = int(config.find_value("Customizations.MaxNumberOfTabDigits")) \
        if config.find_value("Customizations.MaxNumberOfTabDigits") is not None else 4
    set_table_available_automatically = \
        (config.find_value("Customizations.SetTableAvailableAutomatically") or "true").lower() == "true"
    enable_payment_by_seat = get_storewide_config("Store.PaymentBySeat", defval="false").lower() == "true"
    tip_rate = get_storewide_config("Store.TipRate", defval="10")
    can_open_table_from_another_operator = \
        (config.find_value("Customizations.CanOpenTableFromAnotherOperator") or "true").lower() == "true"
    can_see_table_from_another_operator = \
        (config.find_value("Customizations.CanSeeTableFromAnotherOperator") or "true").lower() == "true"
    bordereau_enabled = (config.find_value("Customizations.BordereauEnabled") or "false").lower() == "true"
    print_operator_copy = (config.find_value("Customizations.PrintOperatorCopy") or "false").lower() == "true"

    print_tef_customer_receipt = config.find_value("Customizations.PrintTefCustomerReceipt", "false").lower() == "true"
    print_tef_merchant_receipt = config.find_value("Customizations.PrintTefMerchantReceipt", "false").lower() == "true"

    print_pre_account_after_send_order = config.find_value("Customizations.PrintPreAccountAfterSendOrder",
                                                           "false").lower() == "true"
    can_close_operator_with_opened_table = config.find_value("Customizations.CanCloseOperatorWithOpenedTable",
                                                             "false").lower() == "true"

    transfer_table_allowed_status = config.find_values("Customizations/TableStatusForAction/do_transfer_table")

    join_table_allowed_status = config.find_values("Customizations/TableStatusForAction/do_join_table")

    initialize_manager_authorizations(config)
    get_production_courses_config(config)


@action
def get_static_config(pos_id):
    global enable_tab_btns
    global fetch_stored_orders_timeout

    config = cfgtools.read(os.environ["LOADERCFG"])

    enable_tab_btns = (config.find_value("Customizations.EnableTabBtns") or "true").lower() == "true"
    enabled_tags = _get_enabled_tags(config)
    price_override_enabled = _get_enable_price_override(pos_id)
    show_in_dashboard = sysactions.get_cfg(pos_id).key("ShowInDashboard").values \
        if sysactions.get_cfg(pos_id).key("ShowInDashboard") is not None else []
    available_sale_types = _get_available_sale_types(pos_id)
    idle_alert_time, idle_alert_time_warning, time_to_alert_table_opened, \
    time_to_alert_recall_delivery_is_idle = get_alert_times_config(config)
    cancel_timeout_window, screen_timeout = get_screen_timeout_config(pos_id)
    products_screen_dimensions = get_products_screen_dimensions_config(pos_id)
    spinner_config = get_spinner_config(config)
    enable_pre_start_sale = get_pre_start_sale_config(pos_id)
    special_menus = _get_special_menus(config)

    from posactions import get_tender_types
    tender_types = get_tender_types()

    can_edit_order = (config.find_value("Customizations.CanEditOrder") or "true").lower() == "true"
    get_sat_config(pos_id, config)
    navigation_config = get_navigation_config(config)

    show_cash_in_and_cash_out = config.find_value("Customizations.ShowCashInAndCashOut", "true").lower() == "true"

    cash_payment_enabled = config.find_value("Customizations.CashPaymentEnabled", "true").lower() == "true"

    discounts_enabled = config.find_value("Customizations.DiscountsEnabled", "true").lower() == "true"

    bill_payment_enabled = config.find_value("Customizations.BillPaymentEnabled", "true").lower() == "true"

    production_courses_dict = _get_production_courses_dict()

    totem_config = _get_totem_config(config)

    recall_button = _get_recall_button_config(config)

    operator_button = _get_operator_button_config(config)

    special_modifiers = _get_special_modifiers(config)

    show_ruptured_products = _get_show_ruptured_products(pos_id)

    delivery_sound = _get_delivery_sound(pos_id)

    delivery_address = _get_delivery_address(config)

    fetch_stored_orders_timeout = _get_fetch_stored_orders_timeout(pos_id)

    pos_navigation = _get_pos_navigation(pos_id)

    remote_order_status_config = _get_remote_order_status_config(config)

    return json.dumps(StaticConfig(time_to_alert_table_opened,
                                   time_to_alert_recall_delivery_is_idle,
                                   idle_alert_time,
                                   idle_alert_time_warning,
                                   recall_button,
                                   operator_button,
                                   special_menus,
                                   enabled_tags,
                                   screen_timeout,
                                   cancel_timeout_window,
                                   show_in_dashboard,
                                   products_screen_dimensions,
                                   spinner_config,
                                   enable_tab_btns,
                                   enable_pre_start_sale,
                                   available_sale_types,
                                   fetch_stored_orders_timeout,
                                   tender_types,
                                   price_override_enabled,
                                   can_open_table_from_another_operator,
                                   can_edit_order,
                                   sat_info,
                                   navigation_config,
                                   show_cash_in_and_cash_out,
                                   production_courses_dict,
                                   min_level_needed_to_see_all_tables,
                                   totem_config,
                                   cash_payment_enabled,
                                   discounts_enabled,
                                   bill_payment_enabled,
                                   special_modifiers,
                                   show_ruptured_products,
                                   pos_navigation,
                                   remote_order_status_config,
                                   delivery_sound,
                                   delivery_address),
                      cls=StaticConfigJsonEncoder)


def _get_show_ruptured_products(pos_id):
    return (sysactions.get_cfg(pos_id).key_value("ShowRupturedProducts") or "true").lower() == "true"


def _get_enable_price_override(pos_id):
    return (sysactions.get_cfg(pos_id).key_value("EnablePriceOverride") or "false").lower() == "true"


def _get_pos_navigation(pos_id):
    return sysactions.get_cfg(pos_id).key_value("Navigation") or ""


def _get_production_courses_dict():
    production_courses_dict = {}
    for course in production_courses:
        key = course.split('|')[0]
        value = course.split('|')[1]
        production_courses_dict[key] = value

    return production_courses_dict


def _get_special_menus(config):
    special_menus = config.find_values("Customizations/SpecialMenusCatalogs")
    if special_menus is not None:
        price_lists = get_valid_pricelists(mbcontext)
        for catalog in special_menus:
            if catalog.split(':')[1] not in price_lists:
                special_menus.remove(catalog)
    return special_menus


def _get_enabled_tags(config):
    enabled_tags = []
    enabled_tags_group = config.find_group("Customizations.EnabledTags")  # type: Group
    if enabled_tags_group is not None and enabled_tags_group.keys is not None:
        for key in enabled_tags_group.keys:  # type: Key
            enabled_tags.append(key.name)
    return enabled_tags


def _get_available_sale_types(pos_id):
    loaded_sale_types = sysactions.get_cfg(pos_id).find_values("saleType") or ['EI', 'TO']
    current_available_sale_types = []
    for sale_type in loaded_sale_types:
        if '|' in sale_type:
            current_available_sale_types.append([SaleTypes.get_name(s) for s in sale_type.split('|')])
        else:
            current_available_sale_types.append([SaleTypes.get_name(sale_type)])

    return current_available_sale_types


def get_pre_start_sale_config(pos_id):
    customer_info_config = get_customer_info_config(pos_id)

    pre_start_sale_enabled = False
    if "onStart" in customer_info_config['document'] or "onStart" in customer_info_config['name']:
        pre_start_sale_enabled = True

    return pre_start_sale_enabled


def get_sat_config(pos_id, config):
    global sat_info
    from posactions import get_nf_type

    sat_info["enabled"] = False
    sat_info["timeout"] = 0

    if get_nf_type(pos_id) == 'SAT':
        sat_info["enabled"] = True
        sat_info["timeout"] = int(config.find_value("Customizations/UpdateSatInfoInterval") or 60)


CACHED_STORED_ORDERS = []
LAST_STORED_ORDER_CACHE = None


def get_orders_grouped_by_sale_type(length_only, delivery_order_ids):
    global CACHED_STORED_ORDERS
    global DELIVERY_STORED_ORDERS
    global DELIVERY_VOIDED_ORDERS

    orders_grouped_by_sale_type = {}
    if delivery_order_ids:
        orders_grouped_by_sale_type['DeliveryIds'] = []

        for order in DELIVERY_STORED_ORDERS:
            if order['id'] not in orders_grouped_by_sale_type['DeliveryIds']:
                orders_grouped_by_sale_type['DeliveryIds'].append(order['id'])

        for order in DELIVERY_VOIDED_ORDERS:
            if order['id'] not in orders_grouped_by_sale_type['DeliveryIds']:
                orders_grouped_by_sale_type['DeliveryIds'].append(order['id'])
    if length_only:
        for order in CACHED_STORED_ORDERS:
            if order['saleType'] not in orders_grouped_by_sale_type:
                orders_grouped_by_sale_type[order['saleType']] = 1
            else:
                orders_grouped_by_sale_type[order['saleType']] += 1
        return json.dumps(orders_grouped_by_sale_type)
    return json.dumps(CACHED_STORED_ORDERS)


@action
def get_stored_orders(pos_id, length_only='false', update_cache='false', delivery_order_ids='false'):
    global LAST_STORED_ORDER_CACHE
    global CACHED_STORED_ORDERS
    global DELIVERY_STORED_ORDERS
    global DELIVERY_VOIDED_ORDERS

    length_only = length_only != 'false'
    update_cache = update_cache != 'false'
    delivery_order_ids = delivery_order_ids != 'false'

    try:
        datetime_now = datetime.now()

        if LAST_STORED_ORDER_CACHE is None:
            LAST_STORED_ORDER_CACHE = datetime_now

        cache_datetime_limit = LAST_STORED_ORDER_CACHE + timedelta(seconds=fetch_stored_orders_timeout)
        if update_cache or (not CACHED_STORED_ORDERS or datetime_now > cache_datetime_limit):
            renewed_stored_orders = []
            model = get_model(pos_id)
            posot = get_posot(model)

            all_stored_orders = posot.listOrders(state="STORED")
            for order in all_stored_orders:
                if order["podType"] in ["FC", "FL"] and order["priceList"] != "DL":
                    renewed_stored_orders.append(order)
            if HAS_REMOTE_ORDER:
                get_delivery_stored_orders(pos_id, False)
                get_delivery_errors_orders(pos_id, False)
            for order in DELIVERY_STORED_ORDERS:
                if order['id'] not in [int(x['orderId']) for x in renewed_stored_orders if 'orderId' in x]:
                    renewed_stored_orders.append(order)
            for order in DELIVERY_VOIDED_ORDERS:
                if order['id'] not in [int(x['orderId']) for x in renewed_stored_orders if 'orderId' in x]:
                    renewed_stored_orders.append(order)

            CACHED_STORED_ORDERS = renewed_stored_orders
            LAST_STORED_ORDER_CACHE = datetime_now

    except Exception as _:
        message = "Error getting list of stored orders"
        logger.exception(message)
        sys_log_exception(message)

    finally:
        return get_orders_grouped_by_sale_type(length_only, delivery_order_ids)


@action
def get_delivery_stored_orders(_=None, return_json=True):
    try:
        return_paid_orders = True
        msg = mbcontext.MB_EasySendMessage("RemoteOrder",
                                           TK_REMOTE_ORDER_GET_STORED_ORDERS,
                                           FM_PARAM,
                                           str(return_paid_orders))
        if msg.token != TK_SYS_ACK:
            logger.error("Error retrieving stored orders: " + msg.data)
            return ""

        return get_delivery_orders(msg, return_json, True)
    except Exception as _:
        return


@action
def get_delivery_errors_orders(_, return_json=True):
    try:
        msg = mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_GET_VOIDED_ORDERS)
        if msg.token != TK_SYS_ACK:
            logger.error("Error retrieving error orders: " + msg.data)
            return ""

        return get_delivery_orders(msg, return_json, renew_voided_global=True)
    except Exception as _:
        return


@action
def get_delivery_confirmed_orders(_, return_json=True):
    try:
        msg = mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_GET_CONFIRMED_ORDERS)
        if msg.token != TK_SYS_ACK:
            logger.error("Error retrieving confirmed orders: " + msg.data)
            return ""

        return get_delivery_orders(msg, return_json)
    except Exception as _:
        return


def get_delivery_orders(msg, return_json, renew_stored_global=False, renew_voided_global=False):
    global DELIVERY_STORED_ORDERS
    global DELIVERY_VOIDED_ORDERS
    orders = []
    if msg.data:
        orders = [order for order in json.loads(msg.data) if not order_has_brothers(order)]
        for order in orders[:]:

            out_of_schedule_time = False
            if "SCHEDULE_TIME" in order["customProps"]:
                schedule_time = iso8601.parse_date(order["customProps"]["SCHEDULE_TIME"])
                now = convert_from_utf_to_localtime(datetime.utcnow())
                schedule_time = convert_from_utf_to_localtime(schedule_time)
                delta = schedule_time - now
                out_of_schedule_time = delta > timedelta(hours=1)
                order["customProps"]["SCHEDULE_TIME"] = schedule_time.strftime("%H:%M:%S")

            if out_of_schedule_time:
                orders.remove(order)

            if 'SHORT_REFERENCE' in order['customProps']:
                order['idDescription'] = str(order['id']) + " / " + order['customProps']['SHORT_REFERENCE']
            else:
                order['idDescription'] = str(order['id']) + " / "
            order['remoteId'] = str(order['remoteId'])

            if order['receiveTime'] is not None:
                formatted_date = datetime.strptime(order['receiveTime'], "%Y-%m-%dT%H:%M:%SZ")
                receive_time = convert_from_utf_to_localtime(formatted_date)
                order['receiveTime'] = receive_time.strftime("%d/%m/%Y %H:%M:%S")
            order['saleType'] = "DELIVERY"

            if 'PARTNER' in order['customProps']:
                order['partner'] = order['customProps']['PARTNER']
                if 'BRAND' in order['customProps']:
                    order['partner'] += " - " + order['customProps']['BRAND']

            if 'DELIVERY_ERROR_TYPE' in order['customProps']:
                order['deliveryErrorType'] = order['customProps']['DELIVERY_ERROR_TYPE']
    if renew_stored_global:
        DELIVERY_STORED_ORDERS = orders
    if renew_voided_global:
        DELIVERY_VOIDED_ORDERS = orders
    if not return_json:
        return orders
    return json.dumps(orders)


def order_has_brothers(order):
    props = order["customProps"]
    if props \
            and "GROUPED_ORDERS_QTY" in props \
            and props["GROUPED_ORDERS_QTY"] != '1' \
            and props["FATHER_REMOTE_ID"] != order['remoteId']:
        return True
    return False


def get_alert_times_config(config):
    time_to_alert_table_opened = int(config.find_value("Customizations.TimeToAlertAfterTableOpened")) \
        if config.find_value("Customizations.TimeToAlertAfterTableOpened") is not None else 99
    time_to_alert_table_is_idle = int(config.find_value("Customizations.TimeToAlertTableIsIdle")) \
        if config.find_value("Customizations.TimeToAlertTableIsIdle") is not None else 99
    time_to_alert_table_is_idle_warning = int(config.find_value("Customizations.TimeToAlertTableIsIdleWarning")) \
        if config.find_value("Customizations.TimeToAlertTableIsIdleWarning") is not None else 99
    time_to_alert_recall_delivery_is_idle = int(config.find_value("Customizations.TimeToAlertRecallDeliveryIsIdle")) \
        if config.find_value("Customizations.TimeToAlertRecallDeliveryIsIdle") is not None else 99

    return time_to_alert_table_is_idle, time_to_alert_table_is_idle_warning, time_to_alert_table_opened, \
           time_to_alert_recall_delivery_is_idle


def get_screen_timeout_config(pos_id):
    screen_timeout = \
        int(sysactions.get_cfg(pos_id).find_group("TimeoutConfigurations").key_value("ScreenTimeout")) \
            if sysactions.get_cfg(pos_id).find_group("TimeoutConfigurations") is not None and \
               sysactions.get_cfg(pos_id).find_group("TimeoutConfigurations").key_value("ScreenTimeout") is not None \
            else -1
    cancel_timeout_window = \
        int(sysactions.get_cfg(pos_id).find_group("TimeoutConfigurations").key_value("CancelTimeoutWindow")) \
            if sysactions.get_cfg(pos_id).find_group("TimeoutConfigurations") is not None and \
               sysactions.get_cfg(pos_id).find_group("TimeoutConfigurations").key_value(
                   "CancelTimeoutWindow") is not None \
            else -1
    return cancel_timeout_window, screen_timeout


def get_default_navigation_config(pos_id):
    default_navigation = ""
    if sysactions.get_cfg(pos_id).key_value("DefaultNavigation") is not None:
        default_navigation = sysactions.get_cfg(pos_id).key_value("DefaultNavigation")

    return default_navigation


def get_spinner_config(config):
    spinner_enabled = config.find_value("Customizations/Spinner/Enabled").lower() == 'true' \
        if config.find_value("Customizations/Spinner/Enabled") is not None else True
    spinner_type = config.find_value("Customizations/Spinner/Type") \
        if config.find_value("Customizations/Spinner/Type") is not None else "defaultSpinner"
    spinner_config = {"enabled": spinner_enabled, "type": spinner_type}
    return spinner_config


def get_navigation_config(config):
    show_barcode_screen = config.find_value("Customizations/NavigationConfig/ShowBarcodeScreen").lower() == 'true' \
        if config.find_value("Customizations/NavigationConfig/ShowBarcodeScreen") is not None else False
    show_search_screen = config.find_value("Customizations/NavigationConfig/ShowSearchScreen").lower() == 'true' \
        if config.find_value("Customizations/NavigationConfig/ShowSearchScreen") is not None else False
    navigation_config = {"showBarcodeScreen": show_barcode_screen, "showSearchScreen": show_search_screen}
    return navigation_config


def _get_recall_button_config(config):
    recall_enabled = config.find_value("Customizations/HeaderConfig/RecallButton", "true").lower() == 'true'

    return recall_enabled


def _get_operator_button_config(config):
    operator_enabled = config.find_value("Customizations/HeaderConfig/OperatorButton", "true").lower() == 'true'

    return operator_enabled


def _get_remote_order_status_config(config):
    group_path = "Customizations/DeliveryStatusOnFooter/"
    enabled = (config.find_value(group_path + "Enabled") or "false").lower() == "true"
    fetch_timeout = int(config.find_value(group_path + "FetchRemoteOrderStatusTimeout") or 10)

    remote_order_store_status = json.loads(get_remote_order_status())

    remote_order_status_config = {"enabled": enabled,
                                  "isOnline": remote_order_store_status.get("isOnline"),
                                  "isOpened": remote_order_store_status.get("isOpened"),
                                  "lastExternalContact": remote_order_store_status.get("lastExternalContact"),
                                  "closedSince": remote_order_store_status.get("closedSince"),
                                  "fetchTimeout": fetch_timeout}

    return remote_order_status_config


def _get_delivery_sound(pos_id):
    return (sysactions.get_cfg(pos_id).key_value("DeliverySound") or "false").lower() == "true"


def _get_delivery_address(config):
    delivery_address = config.find_value("Customizations/DeliveryAddress", "false").lower() == 'true'

    return delivery_address


def _get_fetch_stored_orders_timeout(pos_id):
    return int(sysactions.get_cfg(pos_id).key_value("UpdateStoredOrdersCacheDuration") or 90)


def _get_special_modifiers(config):
    special_modifiers = config.find_values("Customizations/SpecialModifiers") \
        if config.find_values("Customizations/SpecialModifiers") is not None else []

    return special_modifiers


def _get_totem_config(config):
    show_barcode, show_search = _get_totem_navigation_config(config)
    welcome_bg_format, show_popup = _get_totem_welcome_config(config)
    sale_type_show_image = _get_totem_sale_type_show_image(config)
    horizontal_banner, banner_side = _get_totem_banner_config(config)
    confirmation_timeout = _get_totem_confirmation_config(config)

    navigation_config = {
        "navigation": {
            "showSearchScreen": show_barcode,
            "showBarcodeScreen": show_search
        },
        "welcomeScreen": {
            "backgroundFormat": welcome_bg_format,
            "showPopup": show_popup
        },
        "saleType": {
            "showImage": sale_type_show_image
        },
        "banner": {
            "horizontal": horizontal_banner,
            "side": banner_side
        },
        "confirmationScreen": {
            "timeout": confirmation_timeout
        }
    }

    return navigation_config


def _get_totem_navigation_config(config):
    navigation_path = "TotemConfig/Navigation/"
    show_barcode = config.find_value(navigation_path + "ShowBarcodeScreen", "true").lower() == 'true'
    show_search = config.find_value(navigation_path + "ShowSearchScreen", "true").lower() == 'true'

    return show_barcode, show_search


def _get_totem_welcome_config(config):
    welcome_path = "TotemConfig/WelcomeScreen/"
    bg_format = config.find_value(welcome_path + "BackgroundFormat")
    show_popup = config.find_value(welcome_path + "ShowPopup", "true").lower() == 'true'

    return bg_format if bg_format is not None else "image", show_popup


def _get_totem_sale_type_show_image(config):
    sale_type_path = "TotemConfig/SaleType/"
    show_image = config.find_value(sale_type_path + "ShowImage", "false").lower() == 'true'

    return show_image


def _get_totem_banner_config(config):
    banner_path = "TotemConfig/Banner/"
    horizontal = config.find_value(banner_path + "Horizontal", "false").lower() == 'true'
    side = config.find_value(banner_path + "Side")

    return horizontal, side if side is not None else "left"


def _get_totem_confirmation_config(config):
    confirmation_path = "TotemConfig/ConfirmationScreen/"
    timeout = config.find_value(confirmation_path + "Timeout")

    return int(timeout) if timeout is not None else 10


def get_production_courses_config(config):
    global production_courses

    production_courses = config.find_values("Customizations/ProductionCourses") \
        if config.find_values("Customizations/ProductionCourses") is not None else []


def get_products_screen_dimensions_config(pos_id):
    products_screen_rows = sysactions.get_cfg(pos_id).find_value("ProductsScreenDimension/Rows", "9")
    products_screen_columns = sysactions.get_cfg(pos_id).find_value("ProductsScreenDimension/Columns", "9")
    products_screen_dimensions = {"rows": products_screen_rows, "columns": products_screen_columns}

    return products_screen_dimensions


def _get_authorization(pos_id, min_level=UserLevels.MANAGER.value, model=None):
    if not model:
        model = get_model(pos_id)

    if not get_authorization(pos_id, min_level=min_level, model=model)[0]:
        return False

    return True


@action
@block_action_if_pos_is_blocked
def create_table_order(pos_id, table_id, price_list=None):
    model = get_model(pos_id)
    check_sangria(model, pos_id)
    order_manager = MsgBusOrderManager()
    screen_changer = MsgBusScreenChanger()
    if price_list:
        price_list = 'EI.' + price_list
    else:
        price_list = 'EI'
    create_table_order_interactor = CreateTableOrderInteractor(tableService(), screen_changer, order_manager)
    status_order = create_table_order_interactor.execute(pos_id, table_id, price_list)

    return status_order


@action
@block_action_if_pos_is_blocked
def start_service(pos_id, table_id, service_seats=None):
    if service_seats is None:
        service_seats = _get_service_seats_number(pos_id)
        if not service_seats:
            deselect_table(pos_id)
            return False

    elif not _number_of_seats_is_valid(service_seats):
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$MAX_NUMBER_OF_SEATS")
        return True

    try:
        start_table_service_interactor = StartServiceInteractor(MsgBusScreenChanger(),
                                                                tableService(),
                                                                TableReleaserImpl(tableService()))
        table_picture = start_table_service_interactor.execute(pos_id, table_id, service_seats, False)
    except Exception as _:
        logger.exception("Error starting table")
        sys_log_exception("Error starting table")
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$TABLE_NOT_AVAILABLE")
        return False

    create_table_modified_event(pos_id, table_picture)
    return True


def create_table_modified_event(pos_id, table_picture):
    event_xml = """<Event subject="POS{}" type="TABLE_MODIFIED">
                           <TABLE_MODIFIED>
                           {}
                       </TABLE_MODIFIED>
                   </Event>""".format(pos_id, table_picture)

    mbcontext.MB_EasyEvtSend("POS{}".format(int(pos_id)), "TableSelected", event_xml)


@action
def store_table_order(pos_id, table_id, tab_id=None):
    from posactions import list_open_options
    model = get_model(pos_id)
    order = model.find("CurrentOrder/Order")

    # Check if there is ANY item in the Sale
    sale_lines = order.findall("SaleLine")
    deleted_line_numbers = map(lambda x: x.get("lineNumber"),
                               filter(lambda x: x.get("level") == "0" and x.get("qty") == "0", sale_lines))
    active_sale_lines = filter(lambda x: x.get("lineNumber") not in deleted_line_numbers, sale_lines)
    if not active_sale_lines:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$THERE_NO_ITEMS_IN_ORDER")
        return False

    # Get the order type from the order to check if it is a REFUND, WASTE or a normal SALE
    order_type = order.get("type")
    if order_type != "REFUND":  # Ignore choices verification for REFUND
        option = list_open_options(order)
        if option is not None:
            prod_name = get_line_product_name(model, int(option.get("lineNumber")))
            mw_helper.show_message_dialog(pos_id, "$INFORMATION",
                                          "$NEED_TO_RESOLVE_OPTION|%s" % (prod_name.encode("UTF-8")))
            return False

    if order.get("totalGross") is None or float(order.get("totalGross")) == 0:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$ORDER_HAS_NO_VALUE")
        return False

    if tab_id is not None:
        pos_ot = sysactions.get_posot(model)
        pos_ot.setOrderCustomProperty("TAB_ID", value=tab_id, orderid=order.get("orderId"))
        _set_tab_additional_info(model, order, pos_id, pos_ot)

    _set_order_hold_items(active_sale_lines, order, pos_id, table_id)

    try:
        success = tableService().store_service(pos_id, table_id)
        if success:
            create_table_modified_event(pos_id, '0')

            if print_pre_account_after_send_order:
                total_report(pos_id, table_id, True)
        return success
    except Exception as ex:
        table_picture = tableService().get_table_picture(pos_id, table_id)
        create_table_modified_event(pos_id, table_picture)
        mw_helper.show_message_dialog(pos_id, "$ERROR", ex.message)


def _set_tab_additional_info(model, order, pos_id, pos_ot):
    from posactions import _is_changing_order
    if not _is_changing_order(model):
        additional_info = None
        while not additional_info:
            additional_info = sysactions.show_keyboard(pos_id, "$TAB_ADDITIONAL_INFO", title="$TAB_ADDITIONAL_INFO",
                                                       numpad=False)
            if additional_info is None:
                raise StopAction()
            if additional_info == "":
                response = sysactions.show_confirmation(pos_id, "$TAB_ADDITIONAL_INFO_NONE")
                if response:
                    break
        if additional_info:
            pos_ot.setOrderCustomProperty("TAB_ADD_INFO", value=additional_info, orderid=order.get("orderId"))


def _set_order_hold_items(active_sale_lines, order, pos_id, table_id):
    has_hold_items = False
    order_id = order.get("orderId")
    hold_orders = tableService().get_table_custom_property(pos_id, "ORDERS_HOLD_ITEMS", tableid=table_id)
    hold_orders = json.loads(hold_orders["ORDERS_HOLD_ITEMS"]) if "ORDERS_HOLD_ITEMS" in hold_orders else []

    for sale_line in active_sale_lines:
        if int(sale_line.get("level")) > 0:
            continue

        custom_property_list = [] if not sale_line.get("customProperties") \
            else json.loads(sale_line.get("customProperties"))

        if "hold" in custom_property_list:
            has_hold_items = True

            if order_id not in hold_orders:
                hold_orders.append(order_id)
                hold_orders = json.dumps(hold_orders)
                _set_orders_hold_items(pos_id, table_id, hold_orders)
                break

    if not has_hold_items and order_id in hold_orders:
        hold_orders.remove(order_id)
        hold_orders = json.dumps(hold_orders)
        _set_orders_hold_items(pos_id, table_id, hold_orders)


@action
@user_authorized_to_execute_action
def edit_table_order(pos_id, order_id):
    tableService().set_current_order(pos_id, order_id)
    return "0"


@action
@user_authorized_to_execute_action
def cancel_table_order(pos_id, order_id, table_id):
    void_reason = get_void_reason(pos_id)
    if void_reason is None:
        return False

    model = get_model(pos_id)
    pos_ot = get_posot(model)

    tableService().void_service_order(pos_id, table_id, order_id)

    pos_ot.setOrderCustomProperties(void_reason, str(order_id))

    selected_table = tableService().get_selected_table(pos_id)
    _set_orders_hold_items(pos_id, selected_table.id)
    table_picture = tableService().get_table_picture(pos_id, selected_table.id)
    create_table_modified_event(pos_id, table_picture)

    return True


@action
@user_authorized_to_execute_action
def cancel_current_table_order(pos_id):
    void_reason = get_void_reason(pos_id)
    if void_reason is None:
        return False

    model = get_model(pos_id)
    pos_ot = get_posot(model)

    if not void_order(pos_id, void_reason=void_reason):
        pos_ot.storeOrder(pos_id)

    selected_table = tableService().get_selected_table(pos_id)
    _set_orders_hold_items(pos_id, selected_table.id)
    table_picture = tableService().get_table_picture(pos_id, selected_table.id)
    create_table_modified_event(pos_id, table_picture)

    return True


@action
def print_table_order(pos_id, order_id):
    return "0"


@action
def select_table(pos_id, table_id=None):
    model = get_model(pos_id)

    if table_id is None:
        table_id = _get_table_id(pos_id, model)
        if table_id is None:
            return False

    try:
        table_picture = eTree.XML(tableService().get_table_picture(pos_id, table_id))
    except TableServiceException as _:
        logger.exception("Error getting order picture")
        try:
            tableService().recall_service(pos_id, table_id)
        except:
            logger.error("Error recalling service as expected")
        try:
            deselect_table(pos_id)
        except:
            logger.exception("Error deselecting table?????")
            raise
        return False

    if table_picture.get('currentPOSId') is not None and table_picture.get('currentPOSId') != pos_id:
        message = "$TABLE_OPENED_IN_ANOTHER_POS|{}".format(table_picture.get('currentPOSId'))
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", message)
        return False

    if get_posfunction(model) == "OT" and int(table_picture.get('status')) == TableStatus.TOTALIZED.value:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$POS_CANNOT_OPEN_THIS_TABLE")
        return False

    if int(table_picture.get('status')) == TableStatus.AVAILABLE.value:
        return start_service(pos_id, table_id)

    if int(table_picture.get('status')) == TableStatus.CLOSED.value:
        ret = _process_closed_table(pos_id, table_id)
        if ret:
            create_table_modified_event(pos_id, ret)
            return True
        return False

    if not can_open_table_from_another_operator and not get_posfunction(model) == "CS":
        pos_user = model.find("./Operator").get("id")
        if int(table_picture.get('status')) == TableStatus.LINKED.value:
            parent_table_id = table_picture.get("parentLinkedTableId")
            parent_table_picture = eTree.XML(tableService().get_table_picture(pos_id, parent_table_id))
            table_user_id = parent_table_picture.get('userId')
        else:
            table_user_id = table_picture.get('userId')

        if table_user_id and table_user_id != pos_user:
            pos_user_level = get_user_level(pos_user)
            table_user_id_level = get_user_level(table_user_id)

            if pos_user_level < min_level_needed_to_see_all_tables and pos_user_level <= table_user_id_level:
                mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$TABLE_OPENED_BY_ANOTHER_OPERATOR")
                return False

    if int(table_picture.get('status')) == TableStatus.LINKED.value:
        linked_table_id = table_picture.get("parentLinkedTableId")
        ret = mw_helper.show_message_options_dialog(pos_id, "$GO_TO_LINKED_TABLE|$CANCEL", "$INFORMATION",
                                                    "$LINKED_TABLE_ALERT|{}".format(linked_table_id))
        if ret == 1:
            return False
        table_id = linked_table_id

    table_picture = tableService().recall_service(pos_id, table_id)
    create_table_modified_event(pos_id, table_picture)
    return True


@action
@user_authorized_to_execute_action
def do_apply_discounts(pos_id, table_id, auth_data):
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    order = get_current_order(model)

    if order.get('state') == "STORED":
        pos_ot.recallOrder(pos_id, int(order.get('orderId')))

    if order.get('state') != "TOTALED":
        pos_ot.doTotal(int(pos_id))

    if apply_discount(pos_id, auth_data):
        table_picture = tableService().get_table_picture(pos_id, table_id)
        create_table_modified_event(pos_id, table_picture)
        return True

    return False


@action
@user_authorized_to_execute_action
def do_clean_discounts(pos_id, table_id):
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    table_picture = eTree.XML(tableService().get_table_picture(pos_id, table_id))
    table_order = table_picture.findall(".//Order")[0]

    if clean_discounts_and_payments(pos_id, pos_ot, table_order):
        show_messagebox(pos_id, message="$DISCOUNTS_CLEANED")
        create_table_modified_event(pos_id, tableService().get_table_picture(pos_id, table_id))
        return True

    mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$WIHOUT_DISCOUNTS_TO_CLEAN")
    return False


def clean_table_discounts(pos_id, table_id, table_orders):
    model = get_model(pos_id)
    pos_ot = get_posot(model)

    lines_to_void = {}
    for order in table_orders:
        lines_to_void = get_lines_with_discount(order, lines_to_void)

    if len(lines_to_void) > 0:
        model = get_model(pos_id)
        pos_ot = get_posot(model)
        pos_ot.blkopnotify = True

        for order_id in lines_to_void:
            pos_ot.voidLine(int(pos_id), "|".join(lines_to_void[order_id]))
            pos_ot.clearDiscount()
    else:
        pos_ot.clearDiscount()

    return tableService().get_table_picture(pos_id, table_id)


def get_lines_with_discount(order, lines_to_void=None):
    if lines_to_void is None:
        lines_to_void = {}
    sale_lines = order.findall(".//SaleLine")
    for sale_line in sale_lines:
        item_type = sale_line.get("itemType")
        qty = float(sale_line.get('qty'))
        if item_type == "COUPON" and qty > 0:
            line_number = sale_line.get("lineNumber")
            order_id = int(order.get("orderId"))
            if order_id in lines_to_void:
                lines_to_void[order_id].append(line_number)
            else:
                lines_to_void[order_id] = [line_number]
    return lines_to_void


@action
def deselect_table(pos_id, pre_selected_option=False):
    try:
        tables = list(tableService().list_tables(pos_id))
        selected_table = tableService().get_selected_table(pos_id, tables)
        if not selected_table:
            create_table_modified_event(pos_id, '0')
            return True

        try:
            table_picture = eTree.XML(tableService().get_table_picture(pos_id, selected_table.id))
            is_a_tab = tableService().is_a_tab(pos_id, selected_table.id, table_picture)

            if is_a_tab and not pre_selected_option:
                slice_source_id = table_picture.get("sliceSourceTableId")

                if slice_source_id:
                    options = "$BACK_FROM_SOURCE_TABLE|$DESELECT_TABLE|$CANCEL"
                    ret = mw_helper.show_message_options_dialog(pos_id, options, "$INFORMATION",
                                                                "$CHOOSE_DESELECT_TYPE")
                    if ret == 2:
                        raise StopAction()
                    if ret == 0:
                        return do_transfer_table(pos_id, selected_table.id, slice_source_id, move_to_destination=True)

            _check_if_tab_id_is_required(pos_id, selected_table.id, table_picture)

            if not _check_if_order_have_tenders_and_clean(pos_id, table_picture, "$CLEAN_TENDERS_TO_DESELECT"):
                return False

        except TableServiceException as _:
            logger.exception("Error getting table picture")

        try:
            for table in tables:
                if pos_id == table.current_pos_id:
                    tableService().store_service(pos_id, str(table.id))
        except TableServiceException as _:
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$COULD_NOT_DESELECT_TABLE")
            logger.exception("Error getting table picture")
            return False

        create_table_modified_event(pos_id, '0')
        return True
    except sysactions.StopAction:
        return False


def _check_if_tab_id_is_required(pos_id, table_id, table_picture=None):
    if not table_picture:
        table_picture = eTree.fromstring(tableService().get_table_picture(pos_id, table_id))

    table_description = table_picture.get("typeDescr")

    if table_description == "Tab":
        tab_id = tableService().get_table_custom_property(pos_id, "TAB_ID", tableid=table_id)
        if tab_id:
            return

        valid = False
        while not valid:
            while True:
                tab_id = mw_helper.show_numpad_dialog(pos_id, "$TYPE_TAB_ID")
                if tab_id is None:
                    raise sysactions.StopAction()
                if tab_id == "":
                    continue

                if len(str(tab_id)) > max_number_of_tab_digits:
                    mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$MAX_NUMBER_OF_DIGITS")
                    continue
                break

            try:
                tableService().tab_id_is_valid(pos_id, tab_id)
            except Exception as ex:
                mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$" + ex.message)
                continue
            tableService().set_table_custom_property(pos_id, "TAB_ID", tab_id, table_id)
            valid = True

    return


@action
@block_action_if_pos_is_blocked
def open_tab(pos_id):
    while True:
        tab_id = mw_helper.show_numpad_dialog(pos_id, "$TYPE_TAB_ID")
        if tab_id is None:
            return False

        if tab_id == "" or tab_id == "NaN":
            continue

        if len(str(tab_id)) > max_number_of_tab_digits:
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$MAX_NUMBER_OF_DIGITS")
            continue

        try:
            tableService().tab_id_is_valid(pos_id, tab_id)
        except Exception as ex:
            if ex.message == 'TAB_ALREADY_EXISTS':
                mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$TAB_ALREADY_EXISTS")
                continue
            return False

        break

    interactor = StartServiceInteractor(MsgBusScreenChanger(), tableService(), TableReleaserImpl(tableService()))
    table_picture = interactor.execute(pos_id, with_order=False, tab_id=tab_id)

    create_table_modified_event(pos_id, table_picture)
    return True


@action
def select_table_or_tab(pos_id, table_id):
    return select_table(pos_id, table_id)


@action
def navigate_to_manager_menu(pos_id):
    ret, user_id = login_prompt_user(pos_id, UserLevels.MANAGER.value)
    if ret and user_id:
        set_menu_manager_authenticated_user(user_id)
    return ret


@action
def navigate_to_operator_menu(pos_id):
    model = get_model(pos_id)
    operator = model.find("Operator")
    user_control_type = model.find("WorkingMode").get("usrCtrlType")
    operator_state = None
    if operator is not None:
        operator_state = operator.get("state")

    if operator_state == "LOGGEDIN":
        return True

    if operator_state == "PAUSED" and user_control_type != 'TS':
        user_id = parser_session_id(operator.get("sessionId"))['user']
        return unpause_user(pos_id, user_id)

    if pos_must_be_blocked(pos_id) and operator_state not in ["OPENED", "PAUSED", "LOGGEDIN"]:
        return show_messagebox(pos_id, "$POS_BLOCKED")

    ret, user_id = login_prompt_user(pos_id, UserLevels.OPERATOR.value, True)
    return ret


def parser_session_id(session_id):
    parsed_session_id = {}

    for data in session_id.split(','):
        data_split = data.split('=')
        parsed_session_id[data_split[0]] = data_split[1]

    return parsed_session_id


def login_prompt_user(pos_id, min_level, login=False):
    try:
        ret, user_data = get_authorization(pos_id, min_level)
        if ret:
            user_id = user_data[0]
            password = user_data[1]
            if login:
                if is_user_already_logged(pos_id, user_id, block_by_working_mode=True):
                    return False, user_id
                return sign_in_user(pos_id, user_id, password), user_id

            return True, user_id
        return False, None

    except AuthenticationFailed as ex:
        show_messagebox(pos_id, "$%s" % ex.message)
        return False, None


@action
def navigate_to_order(pos_id):
    change_screen(pos_id, "10000")
    return True


@action
def do_total_table(pos_id, table_id):
    model = get_model(pos_id)
    check_sangria(model, pos_id)
    config = cfgtools.read(os.environ["LOADERCFG"])
    print_total_report = (config.find_value("Customizations.PrintTotalReportOnTableTotal") or "false").lower() == "true"

    if enable_payment_by_seat:
        table_picture = eTree.XML(tableService().get_table_picture(pos_id, table_id))
        table_orders = table_picture.findall(".//Order")

        seats_placed = True
        service_seats = int(table_picture.get("serviceSeats"))
        if service_seats > 1:
            for order in table_orders:
                sale_lines = order.findall(".//SaleLine")
                for sale_line in sale_lines:
                    properties = json.loads(sale_line.get("customProperties")) if sale_line.get(
                        "customProperties") else ""
                    if not properties or 'seat' not in properties:
                        seats_placed = False
                        break
        else:
            seats_placed = False
    else:
        seats_placed = False

    per_seat = False
    print_pre_account_by = "TABLE"
    if seats_placed:
        resp = mw_helper.show_message_options_dialog(pos_id, "$YES|$NO", "$CONFIRM", "$SEAT_SPLIT_CONFIRMATION")
        if resp is None:
            return False

        if resp == 0:
            per_seat = True
            print_pre_account_by = "SEAT"

    if print_total_report:
        reportactions.print_report(pos_id, "table_report", True, table_id, print_pre_account_by)
    total_table_interactor = TotalTableInteractor(tableService())
    table_picture = total_table_interactor.execute(pos_id, table_id, tip_rate, per_seat)

    if get_posfunction(model) == "OT":
        return deselect_table(pos_id)

    create_table_modified_event(pos_id, table_picture)
    return True


@action
def reopen_table(pos_id, table_id):
    try:
        table_picture = eTree.XML(tableService().get_table_picture(pos_id, table_id))
        slice_source_id = table_picture.get("sliceSourceTableId")

        if tableService().is_a_tab(pos_id, table_id, table_picture) and slice_source_id:
            options = "$BACK_FROM_SOURCE_TABLE|$REOPEN_TABLE|$CANCEL"
            ret = mw_helper.show_message_options_dialog(pos_id, options, "$INFORMATION", "$CHOOSE_REOPEN_TYPE")
            if ret == 2:
                raise StopAction()
            if ret == 0:
                return do_transfer_table(pos_id, table_id, slice_source_id, move_to_destination=True)

        if not _check_if_order_have_tenders_and_clean(pos_id, table_picture, "$CLEAN_TENDERS_TO_DESELECT"):
            return False

        model = get_model(pos_id)
        pos_ot = get_posot(model)
        order = get_current_order(model)
        clean_order_discounts(pos_id, pos_ot, order)

        reopen_table_interactor = ReopenTableInteractor(tableService())
        table_picture = reopen_table_interactor.execute(pos_id, table_id)
        create_table_modified_event(pos_id, table_picture)
        return True

    except sysactions.StopAction:
        return False


def _check_if_order_have_tenders_and_clean(pos_id, table_picture, msg="$CLEAR_TENDER_CONFIRMATION"):
    table_orders = table_picture.findall(".//Order")
    for order in table_orders:
        state_history = order.findall(".//StateHistory/State")
        for state in state_history:
            if state.get("state") == "PAID":
                return True

    table_tenders = table_picture.findall(".//TenderHistory/Tender")
    if table_tenders and not do_clear_service_tenders(pos_id, table_picture.get("id"), msg):
        return False
    return True


@action
def open_day(pos_id):
    pos_list = tableService().get_exclusive_pos_list(user_control_type="TS")
    error_dict = {}

    _fill_pos_list_with_can_open_day_pos(pos_list, error_dict)

    model = get_model(pos_id)
    error_messages = _parse_error_messages(model, error_dict)

    if len(pos_list) == 0:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$HAS_NO_POS_TO_OPEN")
        return False

    if len(error_messages) > 0:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$CANOT_OPEN_DAYS|{}".format("\\".join(error_messages)))

    confirmation_message = "$CONFIRM_OPEN_DAY|{}".format("POS {}".format(pos_list))
    resp = mw_helper.show_message_options_dialog(pos_id, "$OK|$CANCEL", "$INFORMATION", confirmation_message)
    if resp is None or resp == 1:
        return False

    try:
        sys_log_info("Opening business day for POS's: {}".format(pos_list))
        today = date.today().strftime("%Y%m%d")
        error_dict = {}
        successful_pos_id = []

        for pos_no in pos_list:
            _perform_open_day(pos_no, successful_pos_id, today, error_dict)

        if len(error_dict) > 0:
            error_messages = _parse_error_messages(model, error_dict)
            mw_helper.show_message_dialog(pos_id, "$INFORMATION",
                                          "$ERROR_OPENING_DAYS|{}".format("\\".join(error_messages)))

        if len(successful_pos_id) > 0:
            report_pos_id = "|".join(map(str, successful_pos_id))
            menu_manager_user = get_menu_manager_authenticated_user()
            print_report(pos_id, model, True, "dayOpen_report", pos_id, today, report_pos_id, "true", menu_manager_user)

        send_message("Persistence", TK_PERSIST_SEQUENCER_RESET, format=FM_PARAM, data="TraySetNameGen")
    except sysactions.StopAction as _:
        return False
    except Exception as ex:
        mw_helper.show_message_dialog(pos_id, "$ERROR", "$ERROR_OPENING_DAY|{}".format(ex.message))


def _perform_open_day(pos_id, sucessed_pos_id, today, error_dict):
    try:
        sys_log_info("Opening business day on POS id: [%s]" % pos_id)
        msg = send_message("POS%d" % int(pos_id), TK_POS_BUSINESSBEGIN, FM_PARAM, "%s\0%s" % (str(pos_id), today),
                           timeout=3600 * 1000000)
        if msg.token == TK_SYS_ACK:
            sucessed_pos_id.append(pos_id)
        else:
            sys_log_exception("Error opening business day on pos id: %s" % pos_id)
            errors = msg.data.split('\0')
            errormsg = errors[1] if len(errors) > 1 else errors[0] if len(errors) > 0 else errors
            _fill_error_dict(error_dict, pos_id, errormsg)

    except Exception as ex:
        sys_log_exception("Error opening business day on pos id: %s" % pos_id)
        _fill_error_dict(error_dict, pos_id, ex.message)


def _parse_error_messages(model, error_dict):
    error_messages = []
    if len(error_dict) > 0:
        for key in error_dict:
            if key in MwSysErrors.list_values():
                msg = translate_message(model, MwSysErrors.get_name(key))
            else:
                msg = str(key)

            error_messages.append("POS {}".format(error_dict[key]) + (" - {}".format(msg)))
    return error_messages


def _fill_error_dict(error_dict, pos_id, error_message):
    error_message = error_message.split("\0")[0]
    if error_message not in error_dict:
        error_dict[error_message] = [pos_id]
    else:
        error_dict[error_message].append(pos_id)
    return error_dict


@action
def change_line_seat(pos_id, sale_line_json, seat_number):
    sale_line_list = json.loads(sale_line_json)

    for sale_line in sale_line_list:
        MsgBusOrderManager().change_line_seat(pos_id, SaleLine.load_info(seat_number, sale_line), seat_number)

    table_id = tableService().get_current_table_id(pos_id)
    table_picture = tableService().get_table_picture(pos_id, table_id)

    create_table_modified_event(pos_id, table_picture)
    return True


@action
def do_merge_items(pos_id, sale_line_json):
    sale_line_list = json.loads(sale_line_json)
    sale_line_list = filter(lambda x: x.get("level") == 0, sale_line_list)

    model = get_model(pos_id)
    pos_ot = get_posot(model)

    try:
        merge_line = None
        quantity = 0
        fraction_from = None
        order_id = None
        for sale_line in sale_line_list:
            order_id = sale_line['orderId'] if order_id is None else order_id
            fraction_from = sale_line["fractionFrom"] if fraction_from is None else fraction_from

            if fraction_from != sale_line["fractionFrom"]:
                mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$SELECT_ALL_PARTS")
                return False

            if order_id != sale_line['orderId']:
                mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$CANNOT_MERGE")
                return False

            quantity += float(sale_line["qty"])
            line_number = sale_line["lineNumber"]
            merge_line = sale_line if merge_line is None or line_number < merge_line["lineNumber"] else merge_line
        else:
            if quantity != 1.0 or len(sale_line_list) <= 1:
                mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$SELECT_ALL_PARTS")
                return False

        pos_ot.blkopnotify = True
        pos_ot.recallOrder(pos_id, merge_line["orderId"])
        pos_ot.revertsFractionatedOrderLine(int(pos_id), merge_line["lineNumber"])
        pos_ot.storeOrder(pos_id)
    finally:
        model = get_model(pos_id)
        if has_current_order(model):
            pos_ot.storeOrder(pos_id)
        pos_ot.blkopnotify = False

    table_id = tableService().get_current_table_id(pos_id)
    table_picture = tableService().get_table_picture(pos_id, table_id)

    create_table_modified_event(pos_id, table_picture)
    return True


@action
def do_split_items(pos_id, sale_line_json):
    sale_line_list = json.loads(sale_line_json)
    sale_line_list = filter(lambda x: x.get("level") == 0, sale_line_list)

    if len(sale_line_list) < 1:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$NO_LINE_SELECTED")
        return False

    for sale_line in sale_line_list:
        if sale_line['fractionFrom'] is not None:
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$CANNOT_FRACTION_TWICE")
            return False

    table_id = tableService().get_current_table_id(pos_id)
    fraction_qty = sysactions.show_keyboard(pos_id, "", title="$FRACTION_QTY", mask="INTEGER", numpad=True)
    if fraction_qty is None:
        return False

    if fraction_qty == "" or int(fraction_qty) <= 1:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$INVALID_FRACTION_QTY")
        return False

    model = get_model(pos_id)
    pos_ot = get_posot(model)

    try:
        pos_ot.blkopnotify = True
        for sale_line in sale_line_list:
            pos_ot.recallOrder(pos_id, sale_line["orderId"])
            pos_ot.fractionateOrderLine(int(pos_id), sale_line["lineNumber"], int(fraction_qty))
            pos_ot.storeOrder(pos_id)
    finally:
        model = get_model(pos_id)
        if has_current_order(model):
            pos_ot.storeOrder(pos_id)
        pos_ot.blkopnotify = False

    table_picture = tableService().get_table_picture(pos_id, table_id)
    create_table_modified_event(pos_id, table_picture)
    return True


@action
@user_authorized_to_execute_action
def do_slice_service(pos_id, table_id, sale_lines):
    try:
        sale_lines = json.loads(sale_lines)
        orders = []
        for line in sale_lines:
            if line['orderId'] not in orders and float(line['qty']) > 0:
                orders.append(line['orderId'])

        if len(orders) == 0:
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$NO_ORDER_TO_SLICE")
            return False

        new_setup = []
        for order_id in orders:
            setup = {'originalOrderId': order_id, 'lineNumbers': []}
            for line in sale_lines:
                if line['orderId'] == order_id:
                    line_number = line['lineNumber']
                    if line_number not in setup['lineNumbers']:
                        setup['lineNumbers'].append(line_number)
            new_setup.append(setup)

        new_table = tableService().slice_service(pos_id, json.dumps(new_setup), table_id)

        release_all_tables(pos_id)
        tableService().recall_service(pos_id, new_table['tableId'])

        total_table_interactor = TotalTableInteractor(tableService())
        table_picture = total_table_interactor.execute(pos_id, new_table['tableId'], tip_rate, False)

        create_table_modified_event(pos_id, table_picture)
        return True

    except Exception as ex:
        sys_log_exception("Error slicing service")
        mw_helper.show_message_dialog(pos_id, "$ERROR", ex.message)

    return False


def release_all_tables(pos_id, tables=None):
    if tables is None:
        tables = tableService().list_tables(pos_id)

    for table in tables:
        if pos_id == table.current_pos_id:
            tableService().store_service(pos_id, str(table.id))


@action
def do_table_tender(pos_id, tender_id, amount, flag='', seats='', local_payment_data=None, danfe_type=''):
    if local_payment_data == "":
        local_payment_data = None

    model = get_model(pos_id)

    from posactions import get_tender_type
    tender_type = get_tender_type(pos_id, model, tender_id, amount)
    if tender_type is None:
        return False

    tender_descr = tender_type["descr"]
    tender_value = format_amount(model, amount) + " - " + flag if flag else format_amount(model, amount)
    message = "$CONFIRM_PAYMENT_RECEIVED|%s|%s" % (tender_descr, tender_value)
    tender_type_id = tender_type["id"]

    table_id = tableService().get_current_table_id(pos_id)
    table_picture = tableService().get_table_picture(pos_id, table_id)
    table_picture_xml = eTree.XML(table_picture)

    due_amout = table_picture_xml.get("dueAmount")
    if seats:
        table_orders = table_picture_xml.findall(".//Order")
        for order in table_orders:
            split_id = order.find(".//OrderProperty[@key='SPLIT_KEY']").get('value')
            if split_id == seats:
                due_amout = order.get("dueAmount")

    if float(amount) > float(due_amout) and tender_type_id != 0:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$TENDERS_ARE_BIGGER_THEN_DUE_AMOUNT")
        return False

    tender_details = ""
    if (tender_type_id == 1 or tender_type_id == 2) and local_payment_data is None:
        ret = request_eft(pos_id, model, tender_type_id, amount)
        if ret is None:
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$ERROR_PROCESSING_TEF")
            return False

        xml = eTree.XML(ret)
        tender_details = json.dumps({"CNPJAuth": xml.attrib["CNPJAuth"],
                                     "TransactionProcessor": xml.attrib["TransactionProcessor"],
                                     "Bandeira": xml.attrib["Bandeira"],
                                     "IdAuth": xml.attrib["IdAuth"],
                                     "AuthCode": xml.attrib["AuthCode"],
                                     "ReceiptCustomer": xml.attrib["ReceiptCustomer"],
                                     "ReceiptMerchant": xml.attrib["ReceiptMerchant"]})
    else:
        if local_payment_data is None:
            resp = mw_helper.show_message_options_dialog(pos_id, "$OK|$CANCEL", "$CONFIRM", message)
            if resp is None or resp == 1:
                return False

            if tender_type_id != 0:
                tender_details = json.dumps({
                    "Bandeira": flag,
                    "CNPJAuth": "",
                    "AuthCode": ""
                })
        else:
            payment_data = json.loads(local_payment_data)
            tender_details = json.dumps({"CNPJAuth": payment_data["CNPJAuth"],
                                         "TransactionProcessor": payment_data["TransactionProcessor"],
                                         "Bandeira": payment_data["Bandeira"],
                                         "IdAuth": payment_data["IdAuth"],
                                         "AuthCode": payment_data["AuthCode"],
                                         "ReceiptCustomer": payment_data["ReceiptCustomer"],
                                         "ReceiptMerchant": payment_data["ReceiptMerchant"]})

    logger.info("Tender details: {}".format(tender_details))
    table_picture = perform_table_tender(pos_id, tender_type_id, amount, seats, tender_details, table_id, table_picture)

    if tender_type_id == 0 and float(amount) >= float(due_amout):
        change = float(amount) - float(due_amout)
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$MONEY_CHANGE|%s" % (format_amount(model, change)))

    if float(amount) >= float(due_amout):
        return close_table(pos_id, table_id, danfe_type)

    create_table_modified_event(pos_id, table_picture)
    return True


def perform_table_tender(pos_id, tender_type_id, amount, seats, tender_details, table_id, table_picture):
    # type: (str, TenderIdEnum, str, str, str, str, str) -> str
    amount = float(amount)
    order_ids = []
    orders = tableService().get_table_orders(pos_id, table_id, table_picture)
    seats = map(int, seats.split(',')) if seats != '' and seats is not None else []

    for order in orders:
        if order.tip_percentage > 13.0 and tender_type_id in [TenderIdEnum.CREDIT_CARD, TenderIdEnum.DEBIT_CARD]:
            show_messagebox(pos_id, "$TIP_PERCENTAGE_NOT_ALLOWED")
            return tableService().get_table_picture(pos_id, table_id)

        custom_order_properties = order.get_custom_property_by_key("SPLIT_KEY")
        seat_number = None
        if custom_order_properties is not None and custom_order_properties != "SingleOrder":
            seat_number = int(custom_order_properties)

        if len(seats) > 0 and seat_number is not None:
            try:
                if seat_number in seats:
                    order_ids.append(order.order_id)
            except ValueError:
                pass

        decimal_len = abs(Decimal(str(order.due_amount)).as_tuple().exponent)
        if decimal_len > 2:
            difference = abs(order.due_amount - round_half_away_from_zero(order.due_amount, 2))
            amount += difference

    return tableService().register_service_tender(pos_id, table_id, tender_type_id, amount, order_ids, tender_details)


def _verify_sangria(pos_id):
    model = get_model(pos_id)
    pod_type = get_podtype(model)
    if is_sangria_enable() and pod_type != "TT":
        period = get_business_period(model)
        session = get_operator_session(model)
        xml_order = get_current_order(model)
        do_set_drawer_status(pos_id, get_drawer_amount(pos_id, period, session), xml_order.get("state"),
                             get_custom(model, "sangria_level_1_alert"))


def request_eft(pos_id, model, tender_type, amount):
    order = model.find("CurrentOrder/Order")
    last_totaled = order \
        .findall("StateHistory/State[@state='TOTALED']")[-1] \
        .get("timestamp") \
        .replace("-", "") \
        .replace(":", "")

    order_id = order.get("orderId")
    tender_seq_id = len(order.find("TenderHistory").findall("Tender"))
    data_fiscal = last_totaled[:8]
    hora_fiscal = last_totaled[9:15]
    operador = model.find("Operator").get("id")

    ret = mbcontext.MB_EasySendMessage(
        "Sitef%02d" % int(pos_id),
        token=TK_SITEF_ADD_PAYMENT,
        format=FM_PARAM,
        data="%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
            str(pos_id),
            str(order_id),
            str(operador),
            str(tender_type),
            str(amount),
            data_fiscal,
            hora_fiscal,
            tender_seq_id,
            False))

    if ret.token != TK_SYS_ACK:
        return None
    else:
        ret_xml = eTree.XML(ret.data)
        status = ret_xml.get("Result")
        if status == "0":
            return ret.data
        else:
            return None


@action
@user_authorized_to_execute_action
def do_transfer_table(pos_id, source_table_id, destination_table_id=None, move_to_destination=False):
    model = get_model(pos_id)
    service_seats = ""
    table_picture = eTree.XML(tableService().get_table_picture(pos_id, source_table_id))

    if not destination_table_id:
        table_list = [(str(table.id), int(table.status))
                      for table in tableService().list_tables(pos_id)
                      if str(table.status) in transfer_table_allowed_status
                      and "TAB" not in table.id
                      and source_table_id not in table.id]

        selected_table = select_table_by_dialog(pos_id, model, table_list=table_list)
        if selected_table is None:
            return False

        destination_table_id = selected_table[0]

        service_seats = _get_service_seats_number(pos_id)
        if not service_seats:
            return False
    else:
        table_status = int(table_picture.get("status"))
        if table_status == TableStatus.TOTALIZED.value:
            if not _check_if_order_have_tenders_and_clean(pos_id, table_picture):
                return False
            reopen_table_interactor = ReopenTableInteractor(tableService())
            reopen_table_interactor.execute(pos_id, source_table_id)

    pos_ts = get_posts(model)
    user_id = model.find("Operator").get("id")
    linked_tables = table_picture.get("linkedTables").split(",") if table_picture.get("linkedTables") else []

    pos_ts.moveTable(user_id, source_table_id, destination_table_id, service_seats)
    _check_if_table_need_to_be_available_automatically(pos_id, source_table_id, table_picture, linked_tables)
    release_all_tables(pos_id)

    if move_to_destination is False:
        table_picture = '0'
    else:
        table_picture = tableService().recall_service(pos_id, destination_table_id)

    create_table_modified_event(pos_id, table_picture)
    return True


@action
@user_authorized_to_execute_action
def do_join_table(pos_id, source_table_id):
    model = get_model(pos_id)

    is_tab = source_table_id.startswith('TAB')

    if enable_tab_btns and not is_tab:
        order_type_to_show = mw_helper.show_message_options_dialog(pos_id,
                                                                   "$TABS|$TABLES|$CANCEL",
                                                                   "$INFORMATION",
                                                                   "$CHOOSE_ORDER_TYPE")

        if order_type_to_show in (None, 2):
            return False
    else:
        order_type_to_show = 0 if is_tab else 1

    tables_list = tableService().list_tables(pos_id)

    if order_type_to_show == 0:
        tab_list = [({str(x.id): x.tab_id}, int(x.status))
                    for x in tables_list
                    if str(x.status) in join_table_allowed_status
                    and "TAB" in x.id
                    and source_table_id != x.id]
        selected_table = select_table_by_dialog(pos_id, model, tab_list=tab_list)
    else:
        table_list = [(str(x.id), int(x.status))
                      for x in tables_list
                      if str(x.status) in join_table_allowed_status
                      and "TAB" not in x.id
                      and source_table_id != x.id]
        selected_table = select_table_by_dialog(pos_id, model, table_list=table_list)

    if selected_table is None:
        return False

    pos_ts = get_posts(model)
    user_id = model.find("Operator").get("id")

    if not is_tab:
        service_seats = _get_service_seats_number(pos_id)
        if not service_seats:
            return False

        pos_ts.joinTables(user_id, selected_table[0], source_table_id, service_seats)

    else:
        pos_ts.joinTables(user_id, selected_table[0], source_table_id)

    table_picture = tableService().get_table_picture(pos_id, source_table_id)
    create_table_modified_event(pos_id, table_picture)
    return True


@action
def do_abandon_table(pos_id, table_id):
    resp = mw_helper.show_message_options_dialog(pos_id, "$YES|$NO", "$INFORMATION", "$ABANDON_TABLE_CONFIRMATION")
    if resp is None or resp == 1:
        return False

    model = get_model(pos_id)
    pos_ts = get_posts(model)
    user_id = model.find("Operator").get("id")
    table_picture = eTree.XML(tableService().get_table_picture(pos_id, table_id))
    linked_tables = table_picture.get("linkedTables").split(",") if table_picture.get("linkedTables") else []

    pos_ts.abandonService(user_id, table_id)

    _check_if_table_need_to_be_available_automatically(pos_id, table_id, table_picture, linked_tables)

    create_table_modified_event(pos_id, '0')
    return True


@action
def close_table(pos_id, table_id, danfe_type=''):
    model = get_model(pos_id)
    wait_dlg_id = None
    table_picture = tableService().get_table_picture(pos_id, table_id)

    try:
        table_orders = eTree.XML(table_picture).findall(".//Order")
        for order in table_orders:
            wait_dlg_id = order_fiscalizer(model, order, pos_id, wait_dlg_id, danfe_type)

        wait_dlg_id = table_finalizer(pos_id, table_id, wait_dlg_id)
        wait_dlg_id = print_tef_receipts(pos_id, wait_dlg_id)
        _check_if_table_need_to_be_available_automatically(pos_id, table_id, table_picture)
        _verify_sangria(pos_id)
        table_picture = '0'

    except sysactions.StopAction as _:
        return True
    except Exception as ex:
        logger.exception("Error while closing data")
        sysactions.close_asynch_dialog(pos_id, wait_dlg_id)
        mw_helper.show_message_dialog(pos_id, "$ERROR", "$ERROR_SEND_NFE|%s" % ex.message)
        return True
    finally:
        create_table_modified_event(pos_id, table_picture)
        sysactions.close_asynch_dialog(pos_id, wait_dlg_id)

    return True


def print_tef_receipts(pos_id, wait_dlg_id):
    dialog_closed = False
    try:
        model = get_model(pos_id)
        tenders = get_current_order(model).findall("TenderHistory/Tender")
        electronic_tenders = []
        for tender in tenders:
            if int(tender.get("tenderType")) in (1, 2):
                electronic_tenders.append(tender)

        if len(electronic_tenders) == 0:
            return wait_dlg_id

        sysactions.close_asynch_dialog(pos_id, wait_dlg_id)
        dialog_closed = True
        current_printer = sysactions.get_used_service(model, "printer")
        if print_merchant_receipt:
            for tender in electronic_tenders:
                receipt = base64.b64decode(json.loads(tender.get("tenderDetail"))["ReceiptMerchant"])
                mbcontext.MB_EasySendMessage(current_printer,
                                             TK_PRN_PRINT,
                                             format=FM_PARAM,
                                             data=receipt,
                                             timeout=30000000)
                sysactions.show_confirmation(pos_id, "$PRESS_OK_TO_CONTINUE", buttons="$OK")

        response = sysactions.show_confirmation(pos_id, "$WANT_TO_PRINT_CUSTOMER_RECEIPT")
        if not response:
            return wait_dlg_id

        for tender in electronic_tenders:
            receipt = base64.b64decode(json.loads(tender.get("tenderDetail"))["ReceiptCustomer"])
            mbcontext.MB_EasySendMessage(current_printer,
                                         TK_PRN_PRINT,
                                         format=FM_PARAM,
                                         data=receipt,
                                         timeout=30000000)
            sysactions.show_confirmation(pos_id, "$PRESS_OK_TO_CONTINUE", buttons="$OK")
    except:
        logger.exception("Error printing TEF receipts")
    finally:
        if dialog_closed:
            wait_dlg_id = mw_helper.show_message_dialog(pos_id,
                                                        "$PLEASE_WAIT",
                                                        "$PROCESSING_PAYMENT_DATA",
                                                        "NOCONFIRM",
                                                        True)
            return wait_dlg_id


def _check_if_table_need_to_be_available_automatically(pos_id, table_id, table_picture=None, linked_tables=None):
    if not table_picture:
        table_picture = eTree.XML(tableService().get_table_picture(pos_id, table_id))

    if type(table_picture) in [str, unicode]:
        table_picture = eTree.XML(table_picture)

    if set_table_available_automatically and not tableService().is_a_tab(pos_id, table_id, table_picture):
        if linked_tables is None:
            linked_tables = table_picture.get("linkedTables").split(",") if table_picture.get("linkedTables") else []

        for table in linked_tables:
            set_available(pos_id, table)
        set_available(pos_id, table_id)


def table_finalizer(pos_id, table_id, wait_dlg_id):
    close_table_interactor = CloseTableInteractor(tableService())
    close_table_interactor.execute(pos_id, table_id)

    sysactions.close_asynch_dialog(pos_id, wait_dlg_id)
    return wait_dlg_id


def order_fiscalizer(model, order, pos_id, wait_dlg_id, danfe_type):
    try:
        pos_ot = get_posot(model)
        sysactions.close_asynch_dialog(pos_id, wait_dlg_id)
        doc = get_customer_doc_after_paid(pos_id, pos_ot)
        if doc is None:
            raise StopAction()

        wait_dlg_id = mw_helper.show_message_dialog(pos_id, "$PLEASE_WAIT", "$PROCESSING_PAYMENT_DATA", "NOCONFIRM",
                                                    True)
        order_properties_dict = update_custom_properties(customer_doc=doc)
        if len(order_properties_dict) > 0:
            pos_ot.setOrderCustomProperties(order_properties_dict, orderid=order.get("orderId"))

        seat_number = order.find(".//CustomOrderProperties/OrderProperty[@key='SPLIT_KEY']").get('value')

        if seat_number != "SingleOrder":
            sysactions.close_asynch_dialog(pos_id, wait_dlg_id)
            message = "$PROCESSING_PAYMENT_SEAT|%s" % seat_number
            wait_dlg_id = mw_helper.show_message_dialog(pos_id, "$PLEASE_WAIT", message)

        order_id = order.attrib['orderId']
        if danfe_type == "":
            data = pos_id + '\0' + order_id
        else:
            data = '\0'.join([pos_id, order_id, danfe_type])
        ret = mbcontext.MB_EasySendMessage("FiscalWrapper",
                                           TK_FISCALWRAPPER_PROCESS_REQUEST,
                                           format=FM_PARAM,
                                           data=data,
                                           timeout=180 * 1000000)  # type: MBMessage

        if ret.token == TK_SYS_ACK:
            try:
                current_printer = sysactions.get_used_service(model, "printer")
                logger.info("Current printer: {}".format(current_printer))
                msg = mbcontext.MB_EasySendMessage(
                    current_printer,
                    TK_PRN_PRINT,
                    format=FM_PARAM,
                    data=ret.data,
                    timeout=30 * 1000000)  # type: MBMessage

                if msg.token != TK_SYS_ACK:
                    raise PrinterError(msg.data)
                else:
                    logger.info("Imprimiu corretamente")

            except (MBException, MBTimeout) as ex:
                raise PrinterError(ex)
        else:
            fiscal_ok, message = ret.data.split('\0')
            if fiscal_ok == "OK":
                raise PrinterError(message)
            else:
                raise Exception(message)

        return wait_dlg_id

    except sysactions.StopAction as _:
        raise
    except PrinterError as ex:
        sysactions.close_asynch_dialog(pos_id, wait_dlg_id)
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$ERROR_PRINT_NFE|%s" % ex)
    except Exception as ex:
        sysactions.close_asynch_dialog(pos_id, wait_dlg_id)
        raise ex


@action
def set_available(pos_id, table_id):
    if not tableService().is_a_tab(pos_id, table_id):
        set_table_available = SetTableAvailableInteractor(tableService())
        set_table_available.execute(pos_id, table_id)


def check_valid_line(pos_id, model, line_number=None):
    if not line_number:
        return False

    if not can_void_line(model, line_number):
        return False

    return True


def set_custom_production_tag(pos_id,
                              sale_line_json,
                              hold='clear',
                              fire='clear',
                              dont_make='clear',
                              change_production_course='clear',
                              high_priority='clear'):
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    sale_line = json.loads(sale_line_json)

    if "lineNumber" not in sale_line:
        show_messagebox(pos_id, message="$NEED_TO_HAVE_ITEM", icon="error")
        return False

    if not check_valid_line(pos_id, model, sale_line["lineNumber"]):
        show_messagebox(pos_id, message="$NEED_TO_HAVE_ITEM", icon="error")
        return False

    args = (sale_line["lineNumber"], sale_line["itemId"], sale_line["level"], sale_line["partCode"])

    pos_ot.blkopnotify = True
    try:
        pos_ot.setOrderCustomProperty("hold", hold, '', *args)
        pos_ot.setOrderCustomProperty("fire", fire, '', *args)
        pos_ot.setOrderCustomProperty("dont_make", dont_make, '', *args)
        pos_ot.setOrderCustomProperty("course", change_production_course, '', *args)
        pos_ot.setOrderCustomProperty("highPriority", high_priority, '', *args)
    finally:
        pos_ot.blkopnotify = False
        pos_ot.updateOrderProperties(pos_id)

    return True


@action
def do_hold_item(pos_id, sale_line_json):
    return set_custom_production_tag(pos_id, sale_line_json, hold='true')


@action
def do_fire_item(pos_id, sale_line_json):
    return set_custom_production_tag(pos_id, sale_line_json, fire='true')


@action
def do_high_priority_item(pos_id, sale_line_json):
    return set_custom_production_tag(pos_id, sale_line_json, high_priority='true')


@action
def dont_make_item(pos_id, sale_line_json):
    return set_custom_production_tag(pos_id, sale_line_json, dont_make='true')


@action
def change_production_course_item(pos_id, sale_line_json):
    if len(production_courses) == 0:
        return
    if len(production_courses) == 1:
        selected_option = production_courses[0].split("|")[0]
    else:
        options = "|".join([x.split("|")[1] for x in production_courses])
        course = mw_helper.show_filtered_list_box_dialog(pos_id, options, "$SELECT_A_COURSE", "", "NOFILTER")
        if course is None:
            return

        selected_option = production_courses[course].split("|")[0]

    return set_custom_production_tag(pos_id, sale_line_json, change_production_course=selected_option)


@action
def do_clean_item_tags(pos_id, sale_line_json, comment_id=None):
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    if comment_id is not None and comment_id != '-1':
        pos_ot.delComment(comment_id)

    return set_custom_production_tag(pos_id, sale_line_json)


@action
def do_unlink_table(pos_id, source_table_id):
    model = get_model(pos_id)
    table_picture = eTree.XML(tableService().get_table_picture(pos_id, source_table_id))

    linked_tables_id = table_picture.get("linkedTables")
    if not linked_tables_id:
        return

    linked_tables_id = linked_tables_id.split(",")
    if len(linked_tables_id) == 1:
        resp = mw_helper.show_message_options_dialog(pos_id, "$YES|$NO", "$INFORMATION", "$UNLINK_TABLE_CONFIRMATION")
        if resp is None or resp == 1:
            return False
        table_to_unlink = linked_tables_id[0]
    else:
        selected_table = select_table_by_dialog(pos_id, model, table_list=linked_tables_id)
        if selected_table is None:
            return False
        table_to_unlink = selected_table

    pos_ts = get_posts(model)
    user_id = model.find("Operator").get("id")
    pos_ts.unlinkTables(user_id, source_table_id, table_to_unlink)

    _check_if_table_need_to_be_available_automatically(pos_id, table_to_unlink)
    table_picture = tableService().get_table_picture(pos_id, source_table_id)

    create_table_modified_event(pos_id, table_picture)
    return True


@action
def choose_line_seat(pos_id, sale_line):
    choose_line_seat_interactor = ChooseLineSeatInteractor(
        tableService(),
        I18nImpl(MwI18nRepository(pos_id)),
        MsgBusListBox())

    choose_line_seat_interactor.execute(pos_id, sale_line)


@action
def start_tab(pos_id, tab_number, seats):
    model = get_model(pos_id)
    pos_ts = get_posts(model)

    user_id = model.find("Operator").get("id")

    business_period = model.find("PosState").get("period")
    business_period = business_period[0:4] + "-" + business_period[4:6] + "-" + business_period[6:8]

    ret = pos_ts.startService(user_id, business_period, '', seats)
    pos_ts.setCustomProperty("tabNumber", tab_number, ret["tableId"], ret["serviceId"])
    return pos_ts.getTablePicture(ret["tableId"])


@action
def get_operator_data(pos_id, user_id):
    model = get_model(pos_id)
    current_operator = get_current_operator(model).get("id")

    if current_operator == user_id:
        return json.dumps({"result": "SameUser"})

    user_xml = get_user_information(user_id)
    if user_xml is None:
        return json.dumps({"result": None})

    user_list = eTree.XML(user_xml).findall("user")
    user_filter = filter(lambda x: x.get("UserId") == str(user_id), user_list)
    if user_filter in [None, [], ""]:
        return json.dumps({"result": None})

    name = user_filter[0].get("LongName")
    return json.dumps({"result": {"name": name}})


@action
@user_authorized_to_execute_action
def change_table_operator(pos_id, table_id):
    model = get_model(pos_id)
    current_operator_id = get_current_operator(model).get("id")

    filtered_operators = filter_operators(pos_id, current_operator_id)

    if not filtered_operators:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$ERROR_CHANGING_OPERATOR")
        return False

    operators_ids, operators_text = _split_operators_ids_and_formatted_text(filtered_operators)

    chosen_index = mw_helper.show_filtered_list_box_dialog(pos_id, operators_text, "$TRANSFER_TO_WHICH_OPERATOR")
    if chosen_index is None:
        return False

    operator_id = str(operators_ids[chosen_index])
    try:
        operator_data = json.loads(get_operator_data(pos_id, operator_id))
        if operator_id not in [x.get("id") for x in list_all_opened_users(pos_id)]:
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$OPERATOR_IS_NOT_OPENED")
            return False
        if not operator_data:
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$ERROR_RETRIEVING_USER_DATA|{}".format(operator_id))
            return False
        elif operator_data['result'] is None:
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$INVALID_USER_ENTERED|{}".format(operator_id))
            return False
        elif operator_data['result'] == "SameUser":
            mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$SAME_USER_TRANSFER")
            return False
        else:
            resp = mw_helper.show_message_options_dialog(pos_id,
                                                         "$YES|$NO",
                                                         "$INFORMATION",
                                                         "$CONFIRM_TRANSFER_TABLE|{}".format(
                                                             operator_data['result']['name']))
            if resp is None or resp == 1:
                return False

        pos_ts = get_posts(model)

        pos_ts.changeTableUser(operator_id, table_id)
        return deselect_table(pos_id)
    except Exception as _:
        logger.exception("Error changing table operator - pos_id: {}, table_id: {}".format(pos_id, table_id))
        mw_helper.show_message_dialog(pos_id, "$ERROR", "$ERROR_RETRIEVING_USER_DATA|{}".format(operator_id))


def filter_operators(pos_id, current_operator_id):
    opened_operators = list_all_opened_users(pos_id)
    operators = [_format_operator(o) for o in opened_operators if _is_valid_operator(o, current_operator_id)]
    return _sort_operators_by_name(operators)


def _sort_operators_by_name(formatted_operators):
    return sorted(formatted_operators, key=lambda t: t[1])


def _is_valid_operator(o, current_operator_id):
    return _isnt_current_operator(o, current_operator_id) and _operator_isnt_above_manager(o)


def _isnt_current_operator(operator, current_operator_id):
    return operator.get("id", "") != current_operator_id


def _operator_isnt_above_manager(o):
    return int(o.get("level")) <= UserLevels.MANAGER.value


def _format_operator(o):
    operator_id = o.get("id", "")
    operator_name = o.get("name", "")
    return operator_id, "{} - {}".format(operator_name, operator_id)


def _split_operators_ids_and_formatted_text(filtered_operators):
    return map(list, zip(*filtered_operators))


@action
def do_change_table_seats(pos_id, table_id=None):
    try:
        service_seats = _get_service_seats_number(pos_id)
        if not service_seats:
            return False

        model = get_model(pos_id)
        pos_ts = get_posts(model)
        user_id = model.find("Operator").get("id")
        pos_ts.changeNumberOfSeats(user_id, service_seats, table_id)

        table_picture = tableService().get_table_picture(pos_id, table_id)
        create_table_modified_event(pos_id, table_picture)
        return True
    except Exception as _:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$ERROR_CHANGING_SEATS")

    return False


@action
def do_clear_service_tenders(pos_id, table_id, msg="$CLEAR_TENDER_CONFIRMATION"):
    resp = mw_helper.show_message_options_dialog(pos_id, "$YES|$NO", "$INFORMATION", msg)
    if resp is None or resp == 1:
        return False

    table_picture = clean_table_payments(pos_id, table_id)
    create_table_modified_event(pos_id, table_picture)
    return True


def clean_order_discounts(pos_id, pos_ot, order):
    lines_to_void = get_lines_with_discount(order)
    if len(lines_to_void) > 0 or float(order.get("discountAmount")) > 0:
        ret = show_messagebox(pos_id, "$CONFIRM_CLEAN_DISCOUNT", buttons="$YES|$NO")
        if ret != 0:
            raise StopAction()

        if len(lines_to_void) > 0:
            for order_id in lines_to_void:
                pos_ot.voidLine(int(pos_id), "|".join(lines_to_void[order_id]))

        pos_ot.clearDiscount()


def clean_table_payments(pos_id, table_id):
    logger.info("Cleaning payments of table: {}-{}".format(table_id, pos_id))
    model = get_model(pos_id)
    pos_ts = get_posts(model)
    user_id = model.find("Operator").get("id")
    order = model.find(".//Order")
    finish_eft_transactions(pos_id, order, "0")
    table_picture = eTree.XML(pos_ts.clearServiceTenders(user_id, table_id))

    return eTree.tostring(table_picture)


@action
@user_authorized_to_execute_action
def do_change_tip(pos_id, table_id):
    model = get_model(pos_id)

    options = ['PERCENTAGE', 'VALUE']
    options = map(lambda x: translate_message(model, x), options)

    tip_type = mw_helper.show_filtered_list_box_dialog(pos_id, "|".join(options), "$SELECT_SPECIAL_CATALOG", "",
                                                       "NOFILTER")
    if tip_type is None:
        return False

    title = "$SELECT_TIP_PERCENTAGE" if tip_type == 0 else "$SELECT_TIP_VALUE"
    mask = "CURRENCY" if tip_type == 1 else "NUMBER"

    tip_value = mw_helper.show_numpad_dialog(pos_id, title, "", mask)
    if tip_value is None:
        return False

    percentage = ""
    amount = ""
    if tip_type == 0:
        percentage = tip_value or 0
    else:
        amount = tip_value or 0

    do_change_tip_interactor = DoChangeTipInteractor(tableService())
    table_picture = do_change_tip_interactor.execute(pos_id, table_id, str(percentage), str(amount))

    create_table_modified_event(pos_id, table_picture)
    return True


@action
def total_report(pos_id, table_id, force_print_by_table=False):
    print_pre_account_by = "TABLE"

    if not force_print_by_table and some_seat_has_item(pos_id, table_id):
        option_selected = mw_helper.show_message_options_dialog(pos_id,
                                                                "$SEATS|$TABLE",
                                                                "$INFORMATION",
                                                                "$PRE_ACCOUNT_BY_SEAT_OR_BY_TABLE")

        if option_selected is None:
            return

        if option_selected == 0:
            print_pre_account_by = "SEATS"

    reportactions.print_report(pos_id, "table_report", not force_print_by_table, table_id, print_pre_account_by,
                               hide_unpriced_items_from_total_report)


class PrinterError(Exception):
    def __init__(self, message):
        super(PrinterError, self).__init__(message)


@action
def get_special_catalog(pos_id):
    model = get_model(pos_id)
    special_catalog = get_custom(model, 'Special Catalog Enabled')

    if special_catalog is None:
        return '{}'

    return special_catalog


@action
def get_floor_plan(_):
    try:
        config = cfgtools.read(os.environ["LOADERCFG"])
        floor_plan_paths = config.find_values("Customizations/FloorPlanJsonPath") or []

        for path in floor_plan_paths:
            try:
                if path != "":
                    with open(path, mode="rb") as json_file:
                        data = json_file.read()
                        break
            except Exception as _:
                continue

        if data is None:
            return '{}'

        return data
    except Exception as _:
        return '{}'


def _format_pricelist_for_special_catalog(pos_id):
    price_lists = get_valid_pricelists(mbcontext)
    model = get_model(pos_id)
    price_lists.remove('EI')
    if 'DT' in price_lists:
        price_lists.remove('DT')
    if 'DL' in price_lists:
        price_lists.remove('DL')
    price_lists.insert(0, translate_message(model, 'NONE'))

    return price_lists


@action
def doSpecialCatalog(pos_id):
    price_lists = _format_pricelist_for_special_catalog(pos_id)
    # @TODO create a multi-value select box and parse it as value1.value2 "HH.LM"

    index = mw_helper.show_filtered_list_box_dialog(pos_id, "|".join(price_lists), "$SELECT_SPECIAL_CATALOG", "",
                                                    "NOFILTER")
    if index is None:
        return False

    if index > 0:
        special_catalog = price_lists[index]
    else:
        special_catalog = ''

    pos_list = get_poslist()
    for pos_number in pos_list:
        set_custom(pos_number, 'Special Catalog Enabled', special_catalog, True)
    return True


@action
def doSpecialTableCatalog(pos_id):
    selected_table = tableService().get_selected_table(pos_id)
    if not select_table:
        return False

    price_lists = _format_pricelist_for_special_catalog(pos_id)
    # @TODO create a multi-value select box and parse it as value1.value2 "HH.LM"

    index = mw_helper.show_filtered_list_box_dialog(pos_id, "|".join(price_lists), "$SELECT_SPECIAL_CATALOG", "",
                                                    "NOFILTER")
    if index is None:
        return False

    if index > 0:
        special_catalog = price_lists[index]
    else:
        special_catalog = ''

    tableService().set_table_custom_property(pos_id, "SpecialCatalog", special_catalog, selected_table.id)
    table_picture = tableService().get_table_picture(pos_id, selected_table.id)

    create_table_modified_event(pos_id, table_picture)
    return True


@action
def getMyTable(pos_id):
    try:
        selected_table = tableService().get_selected_table(pos_id)
        if selected_table:
            return tableService().get_table_picture(pos_id, selected_table.id)
    except TableServiceException as _:
        sys_log_exception("Error getting Current Table")

    return '{}'


@action
def get_table_picture(pos_id, table_id):
    try:
        model = get_model(pos_id)
        current_operator = get_current_operator(model)
        table_picture = tableService().get_table_picture(pos_id, table_id)

        if current_operator is None:
            create_table_modified_event(pos_id, table_picture)
            return True

        current_operator_id = current_operator.get("id")
        current_operator_level = current_operator.get("level")
        if current_operator_level is None:
            current_operator_level = eTree.XML(get_user_information(current_operator_id)).find("user").get("Level")
        current_operator_level = int(current_operator_level)

        table_picture_xml = eTree.XML(table_picture)
        table_user = table_picture_xml.get("userId")
        table_user_level = get_user_level(table_user)
        pos_function = model.find("WorkingMode").get("posFunction")

        if table_user_level is None and int(table_picture_xml.get('status')) != TableStatus.AVAILABLE.value:
            return

        can_open_table = current_operator_id != table_user and current_operator_level <= table_user_level
        if can_open_table and pos_function != 'CS' and not can_see_table_from_another_operator:
            return False

        create_table_modified_event(pos_id, table_picture)
        return True
    except TableServiceException as _:
        sysactions.show_messagebox(pos_id, "$GETTING_TOTALED_TABLE")
        return False


@action
@user_authorized_to_execute_action
def get_manager_authorization(pos_id):
    return True


def _number_of_seats_is_valid(seats):
    return int(seats) <= max_number_of_seats


def _check_if_pos_have_a_operator_oppened(users_list, pos_id=None, model=None):
    operator = model.find("./Operator")

    if operator is None:
        return

    if operator.get("state") not in ["OPENED", "PAUSED", "LOGGEDIN"]:
        return

    operator_id = operator.get("id")
    operator_name = eTree.XML(sysactions.get_user_information(operator_id)).find(".//user").get("UserName")

    if not pos_id:
        pos_id = model.get("posId")

    operator_tuple = (pos_id, operator_id, operator_name)
    if operator_tuple not in users_list:
        users_list.append(operator_tuple)


def _fill_pos_list_with_can_open_day_pos(pos_list, error_dict):
    for pos_id in list(pos_list):
        model = get_model(pos_id)
        if model.find("PosState").get("state") not in ["CLOSED", "UNDEFINED"]:
            if model.find("PosState").get("period") != datetime.today().strftime('%Y%m%d'):
                can_open_day = translate_message(model, "DAY_IS_NOT_CLOSED")
            else:
                can_open_day = translate_message(model, "DAY_IS_ALREADY_OPENED")

            _fill_error_dict(error_dict, pos_id, can_open_day)
            pos_list.remove(pos_id)


def select_table_by_dialog(pos_id, model, table_list=None, tab_list=None):
    tables = []
    options = []

    if tab_list is not None:
        sorted_tabs = sorted(tab_list, key=lambda tup: int(tup[0].items()[0][1]))
        tables.extend(sorted_tabs)
        for table in sorted_tabs:
            if isinstance(table, tuple):
                table_status = translate_message(model, TableStatus.get_status_label(table[1]))
                table_message = translate_message(model,
                                                  'TAB_INFORMATION2',
                                                  str(table[0].values()[0].zfill(3)), table_status)
            else:
                table_message = translate_message(model, 'TAB_INFORMATION', table.zfill(3))

            options.append(table_message)

    if table_list is not None:
        single_message = translate_message(model, 'TABLE_INFORMATION')
        status_message = translate_message(model, 'TABLE_INFORMATION2')

        sorted_tables = sorted(table_list, key=lambda tup: int(tup[0]))
        sorted_tables = sorted(sorted_tables, key=lambda tup: int(tup[1]), reverse=True)
        tables.extend(sorted_tables)
        table_status = {}
        for table in sorted_tables:
            if isinstance(table, tuple):
                status = TableStatus.get_status_label(table[1])
                if status not in table_status:
                    table_status[status] = translate_message(model, status)
                table_message = status_message.format(table[0].zfill(3), table_status[status])
            else:
                table_message = single_message.format(table.zfill(3))

            options.append(table_message)

    if len(options) < 1:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$NO_OPTIONS_TO_SHOW")
        return None

    infotext = "|".join(options) if hasattr(options, '__iter__') else str(options)

    table_index = mw_helper.show_filtered_list_box_dialog(pos_id, infotext, "$SELECT_TABLE", "", "")
    if table_index is None:
        return None

    if isinstance(tables[int(table_index)][0], dict):
        return tables[int(table_index)][0].items()[0]

    return tables[int(table_index)]


def _get_table_id(pos_id, model):
    table_list = []
    tab_list = []
    for table in tableService().list_tables(pos_id):
        if table.tab_id is None and "TAB" not in table.id:
            if not (get_posfunction(model) == "CS" and table.status == TableStatus.AVAILABLE.value) \
                    and not (get_posfunction(model) == "OT" and table.status == TableStatus.TOTALIZED.value):
                table_list.extend([(str(table.id), int(table.status))])
        elif table.tab_id is not None and int(table.status) != 7:
            tab_list.extend([({str(table.id): table.tab_id}, int(table.status))])

    selected_table = select_table_by_dialog(pos_id, model, table_list=table_list, tab_list=tab_list)
    if selected_table is None:
        return

    table_id = selected_table[0]

    return table_id


def _get_service_seats_number(pos_id):
    service_seats = sysactions.show_keyboard(pos_id, "", title="$SELECT_QUANTITY_OF_SEATS", mask="INTEGER", numpad=True)
    if service_seats is None:
        return None

    if service_seats == "" or service_seats == "NaN" or int(service_seats) == 0:
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$INVALID_NUMBER_OF_SEATS")
        return None

    if not _number_of_seats_is_valid(service_seats):
        mw_helper.show_message_dialog(pos_id, "$INFORMATION", "$MAX_NUMBER_OF_SEATS")
        return None

    return service_seats


def _process_closed_table(pos_id, table_id):
    resp = mw_helper.show_message_options_dialog(pos_id, "$OK|$CANCEL", "$INFORMATION", "$CONFIRM_SET_AVAILABLE")
    if resp is None or resp == 1:
        return False

    set_available(pos_id, table_id)
    return True


def some_seat_has_item(pos_id, table_id):
    table_picture = eTree.XML(tableService().get_table_picture(pos_id, table_id))
    table_orders = table_picture.findall(".//Order")
    service_seats = int(table_picture.get("serviceSeats"))
    if service_seats > 1:
        for order in table_orders:
            sale_lines = order.findall(".//SaleLine")
            for sale_line in sale_lines:
                properties = json.loads(sale_line.get("customProperties")) if sale_line.get("customProperties") else ""
                if properties and "seat" in properties and properties["seat"] != "0":
                    return True
    return False


def get_user_level(user_id):
    if user_id is None:
        return None

    user_xml_str = get_user_information(user_id)
    user_xml = eTree.XML(user_xml_str)
    user_element = user_xml.find("user")
    user_level = int(user_element.attrib["Level"])
    return user_level


def _set_orders_hold_items(pos_id, table_id, hold_items=None):
    tableService().set_table_custom_property(pos_id, "ORDERS_HOLD_ITEMS", propvalue=hold_items, tableid=table_id)
