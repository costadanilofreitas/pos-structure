# -*- coding: utf-8 -*-
import time
import threading
import base64
import cfgtools
import json
import logging

from datetime import datetime
from decimal import Decimal
from xml.etree import cElementTree as eTree
import pyscripts
import persistence
import re
import sys

import helper
import sysactions
from actions.delivery.print_original_delivery import print_original_delivery
from systools import sys_log_info, sys_log_debug, sys_log_exception, sys_log_error
from msgbus import TK_EVT_EVENT, TK_FISCAL_CMD, TK_SYS_NAK, TK_ACCOUNT_EFTACTIVITY, \
    TK_ACCOUNT_GIFTCARDACTIVITY, TK_POS_SETDEFSERVICE, TK_SYS_ACK, TK_SYS_CHECKFORUPDATES, \
    TK_POS_USERLOGIN, TK_POS_LISTUSERS, TK_I18N_GETLANGS, TK_POS_SETLANG, TK_CDRAWER_OPEN, \
    TK_HV_GLOBALRESTART, TK_GENESIS_LISTPKGS, TK_GENESIS_APPLYUPDATE, FM_STRING, FM_PARAM, \
    FM_XML, TK_PERSIST_SEQUENCER_INCREMENT, MBException, SE_NOTFOUND, TK_POS_BUSINESSEND, \
    TK_PRN_GETSTATUS, TK_PRN_PRINT, TK_DRV_IOCTL
from posot import OrderTaker, OrderTakerException, ClearOptionException
from sysdefs import eft_commands
from sysactions import StopAction, AuthenticationFailed, action, send_message, get_model, get_podtype, \
    get_tender_type, get_business_period, check_genesis_error, get_operator_session, get_posot, get_used_service, \
    get_cfg, has_operator_opened, get_current_operator, has_current_order, get_current_order, check_drawer, \
    check_operator_logged, check_current_order, show_info_message, show_messagebox, \
    show_confirmation, show_listbox, show_keyboard, show_order_preview, show_text_preview, close_asynch_dialog, \
    print_text, print_report, set_custom, get_custom, translate_message, format_amount, \
    get_last_order, get_line_product_name, get_clearOptionsInfo, authenticate_user, is_valid_date, get_poslist, \
    get_pricelist, get_storewide_config, on_before_total, format_date, get_posfunction, is_day_blocked, \
    show_custom_dialog, read_scanner, is_day_opened, show_any_dialog

from actions.functions.do_store_order import doStoreOrder
from pyscriptscache import cache as _cache
from pos_model import TenderType
from poslistener import get_updated_sale_line_defaults
from bustoken import TK_SITEF_ADD_PAYMENT, TK_SITEF_CANCEL_PAYMENT, TK_FISCALWRAPPER_PROCESS_REQUEST, \
    TK_FISCALWRAPPER_SEARCH_REQUEST, TK_KDSMONITOR_STATUS_REQUEST, TK_FISCALWRAPPER_REPRINT, \
    TK_MAINTENANCE_TERMINATE_REQUEST, TK_MAINTENANCE_RESTART_REQUEST, TK_PROD_PURGE, \
    TK_FISCALWRAPPER_SEFAZ_CONNECTIVITY, TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST, TK_SITEF_CONNECTIVITY_TEST, \
    TK_FISCALWRAPPER_SAT_PROCESS_PAYMENT, TK_FISCALWRAPPER_SAT_PAYMENT_STATUS, TK_FISCALWRAPPER_GET_NF_TYPE, \
    TK_FISCALWRAPPER_RE_SIGN_XML, TK_FISCALWRAPPER_SITUATION, TK_MAINTENANCE_RECREATE_FILE_NUMBER, \
    TK_BKOFFICEUPLOADER_SEND_BKOFFICE_ORDER, TK_RUPTURA_GET_ENABLED, TK_RUPTURA_GET_DISABLED, TK_RUPTURA_UPDATE_ITEMS, \
    TK_BLACKLIST_CHECK_STRING, TK_REMOTE_ORDER_OPEN_STORE, TK_REMOTE_ORDER_CLOSE_STORE, TK_REMOTE_ORDER_GET_STORE, \
    TK_FISCALWRAPPER_PRINT_DONATION_COUPON
from fiscalprinter import fpcmds
from manager.reports import report_action

from model.customexception import DeliveryCouponPrintError

from actions.delivery import create_delivery_manual_order_json

logger = logging.getLogger("PosActions")

import actions
from actions import *
actions.set_mb_context(pyscripts.mbcontext)


import manager
# noinspection PyUnresolvedReferences
from ui import get_product_nav
# noinspection PyUnresolvedReferences
from manager import openday, check_business_day
import manager.users
# noinspection PyUnresolvedReferences
from manager.users import change_user_password, createuser, inactivateuser, removeuser
import manager.reports
# noinspection PyUnresolvedReferences
from manager.reports import speedOfServiceReport, hourlySalesReport, cashReport, extendedReport, checkoutReport, \
    employeesClockedInReport
from old_helper import config_logger, convert_from_utf_to_localtime, validar_cpf, validar_cnpj, round_half_away_from_zero
from mw_helper import show_message_dialog, show_message_options_dialog, show_numpad_dialog, \
    show_filtered_list_box_dialog
from actions.util import get_authorization, get_drawer_amount, do_set_drawer_status, check_sangria, is_sangria_enable, \
    get_menu_user_logged
from actions.config import get_customer_info_config, get_keyboard_comments_config, \
    get_min_value_to_ask_bordereau_justify_config
from actions.models import UserLevels
from actions.products.get_products_with_measure_unit import get_products_with_measure_unit_cache, is_a_product_with_measure_unit
from actions.functions.do_recall_order import do_recall_order
from actions.functions.do_back_from_total import do_back_from_total
from actions.void.utils import void_order
from utilfunctions import get_customer_doc_after_paid
from actions.pos.check_table_status import has_tab_or_tables_opened

from custom_sysactions import block_action_if_pos_is_blocked, user_authorized_to_execute_action
from threads import UpdatePosBlockedState

from peripherals.scale import WeightComparer, PosScaleEvents
from peripherals.scanner import sell_product_by_barcode


USECS_PER_SEC = 1000000

debug_path = '../python/pycharm-debug.egg'
if os.path.exists(debug_path):
    try:
        sys.path.index(debug_path)
    except ValueError:
        sys.path.append(debug_path)
    # noinspection PyUnresolvedReferences
    try:
        import pydevd
    except NameError:
        pass

manager.mbcontext = pyscripts.mbcontext
manager.users.mbcontext = pyscripts.mbcontext
manager.reports.mbcontext = pyscripts.mbcontext

sysactions.DATE_FMT = "%d/%m/%Y"
sysactions.get_pricelist.DEFAULT = "EI"

# Tender types
TENDER_CASH = "0"
TENDER_CREDIT_CARD = "2"
TENDER_CREDIT_AMEX = "5"
TENDER_CREDIT_VISA = "9"
TENDER_CREDIT_MASTERCARD = "10"
TENDER_CREDIT_DISCOVER = "11"

SIGNED_IN_USER = "SIGNED_IN_USER"
ASSIGNED_USER = "ASSIGNED_USER"

comment_map = {
    "ONSIDE": "[OnSide]",
    "EXTRA": "[Extra]",
    "LIGHT": "[Light]",
    "$ONSIDE": "[OnSide]",
    "$EXTRA": "[Extra]",
    "$LIGHT": "[Light]"
}

# Paper Cutter
GS = b'\x1d'
_CUT_PAPER = lambda m: GS + b'V' + m
PAPER_FULL_CUT = _CUT_PAPER(b'\x00')  # Full cut paper
PAPER_PART_CUT = _CUT_PAPER(b'\x01')  # Partial cut paper
PAPER_FEED_CUT = _CUT_PAPER(b'\x01')  # Partial cut paper
PAPER_EMPTY_SPACE = "\n\n\n\n\n\n"

# Message-bus context
mbcontext = pyscripts.mbcontext  # type: MBEasyContext
# Tuple of registered POS
poslist = ()
# Store ID
store_id = None
sell_categories = {}
# Store-wide parameter indicating if this is a 24-hours store
is24HoursStore = False

# NF Type (SAT, NFCE or PAF)
nf_type = None

_eft_events = []
# List of pending tandem events
_tandem_events = []
# Indicates that a scanner's automatic sale function is paused for a specific POS, used during
# price lookup, or non-product scans. Key is POS id, value True or False.
scanner_sale_paused = {}
# Set of recall-by-picture listeners
_recall_listeners = set()
# Dictionaries that maps booth numbers to POS ids (and vice-versa)
booth_pos_mapping = {}
pos_booth_mapping = {}
# Holds a set of product codes that match the "Subst" tag
subst_products = set()
# Item composition cache
_item_comp_cache = {}

# Default Options Cache
_default_options_cache = {}
# Option Items Cache
_options_cache = {}
# Must Be Modified Cache
_must_modify = {}
# Product list cache, with prices and barcodes

# Barcode to product mapping

comment_mods = []
productPrices = {}
cancela = False

lock_tender = threading.Lock()
tendering = {}

lock_recall = threading.Lock()
recalling = []

# limit values to sangria
sangria_levels = None
is_sangria_enabled_config = True
max_transfer_value = 0
show_all_transfer = False

keyboard_comments = {}
customer_info_config = {}
scale_ticket_mode = ''
ask_for_delivery_courier = True
ask_for_delivery_payment = True

pos_scale_events = PosScaleEvents()
pos_scale_dialogs = []
waiting_scale = False


#
# Main function - called by the pyscripts module
#
def main():
    helper.import_pydevd(os.environ["LOADERCFG"], 9123)

    # Subscribes event callbacks
    sysactions.initialize()

    pyscripts.subscribe_event_listener("DIALOG_RESP", _dialog_resp_received)
    pyscripts.subscribe_event_listener("SITEF", _sitef_processing_received)
    persistence.Driver().open(mbcontext).select("SELECT 1")

    # Loads POS configuration
    load_posconfig()
    # Loads SQLite cache
    force_sqlite_cache()
    # Check for any genesis error and notify the users
    threading.Timer(5.0, check_genesis_error).start()

    get_products_with_measure_unit_cache()

    global lock_tender
    with lock_tender:
        global tendering
        for pos_id in poslist:
            tendering[int(pos_id)] = False

    update_pos_blocked_state = UpdatePosBlockedState(poslist)
    update_pos_blocked_state.daemon = True
    update_pos_blocked_state.start()

    config_logger(os.environ["LOADERCFG"], 'PosActions')
    config_logger(os.environ["LOADERCFG"], 'TableActions')


def _join(dic1, dic2):
    d = dict(dic1)
    d.update(dic2)
    return d


def _dialog_resp_received(params):
    """Callback called by pyscripts module"""
    xml, subject, type = params[:3]
    dialog = eTree.XML(xml).find("Dialog")
    dlg_id = str(dialog.get("id"))
    response = str(dialog.findtext("Response"))
    for eft_evt in _eft_events:
        if str(eft_evt[1]) == dlg_id and response == "0":
            pos_id, order_id = eft_evt[2:4]
            sys_log_debug("Pressionada tecla anula. Cancelando pagamento Sitef no POS %s - Order %s" % (str(pos_id), str(order_id)))
            mbcontext.MB_EasySendMessage("Sitef%02d" % int(pos_id), token=TK_SITEF_CANCEL_PAYMENT, format=FM_PARAM, data="%s;%s" % (str(pos_id), str(order_id)))

            close_asynch_dialog(pos_id, dlg_id)

    if dlg_id in pos_scale_dialogs:
        pos_scale_dialogs.remove(dlg_id)

    return None


def _sitef_processing_received(params):
    data, subject, p_type, async, pos_id = params[:5]
    if p_type == "PROCESS_STARTED":
        for eft_evt in _eft_events:
            if eft_evt[2] == pos_id:
                model = get_model(pos_id)
                pod_function = get_posfunction(model) if get_podtype(model) in ("DT", "FC") else get_podtype(model)
                # Cashless processing started for this POS... Change the current dialog box to CANCEL
                if pod_function not in ("TT", "OT"):
                    message = "$READ_QR_CODE" if data == "122" else "$EFT_SWIPE_CARD"
                    dlg_id = show_messagebox(pos_id, message, "$EFT", "swipecard", buttons="$CANCEL", timeout=180000, asynch=True)
                    eft_evt[1] = dlg_id
                break
    if p_type == "PROCESS_ENDED":
        for eft_evt in _eft_events:
            if eft_evt[2] == pos_id and eft_evt[1] is not None:
                close_asynch_dialog(pos_id, eft_evt[1])
                break
    if p_type == "PROCESS_FINISHED":
        for eft_evt in _eft_events:
            _eft_events.remove(eft_evt)
            if eft_evt[2] == pos_id and eft_evt[1] is not None:
                close_asynch_dialog(pos_id, eft_evt[1])
                break
    return None


def populate_combo_taxes(posid):
    BEGIN_TRANSACTION = ["BEGIN TRANSACTION", "UPDATE fiscalinfo.FiscalDEnabled SET Enabled=0"]
    COMMIT_TRANSACTION = ["UPDATE fiscalinfo.FiscalDEnabled SET Enabled=1", "COMMIT TRANSACTION"]

    query = """
        INSERT OR REPLACE INTO taxcalc.ProductTaxCategory(ItemId, TaxCgyId)
        SELECT PI.ItemId, V1.TaxCgyId
            FROM (
                SELECT P.ItemId, P.ProductCode, PTC.TaxCgyId
                FROM sysproddb.ProductItem P
                LEFT JOIN taxcalc.ProductTaxCategory PTC ON PTC.ItemId=P.ItemId
                WHERE P.RecursionLevel=1 AND PTC.TaxCgyId IS NOT NULL
            ) V1
        JOIN sysproddb.ProductItem PI ON PI.ProductCode=V1.ProductCode
        WHERE PI.RecursionLevel>1;
        INSERT OR REPLACE INTO fiscalinfo.FiscalProductCatalogChangesCounter SELECT * FROM productdb.ProductCatalogChangesCounter;

        DELETE FROM fiscalinfo.FiscalProductDB
        WHERE EXISTS (
            SELECT 1 FROM productdb.ProductCatalogChangesCounter A
            LEFT JOIN fiscalinfo.FiscalProductCatalogChangesCounter B
            WHERE A.ChangesCount!=COALESCE(B.ChangesCount,-1) OR A.ChangesDateTime!=COALESCE(B.ChangesDateTime,''));

        INSERT OR REPLACE INTO fiscalinfo.FiscalProductDB(ProductCode,ProductName,UnitPrice,TaxFiscalIndex,FiscalCategory,TaxRate,IAT,IPPT,MeasureUnit)
        SELECT ProductCode,ProductName,UnitPrice,TaxFiscalIndex,FiscalCategory,TaxRate,IAT,IPPT,MeasureUnit
        FROM
            (SELECT
                    Price.ProductCode AS ProductCode,
                    Product.ProductName AS ProductName,
                    Price.DefaultUnitPrice as UnitPrice,
                    TaxRule.TaxFiscalIndex AS TaxFiscalIndex,
                    TaxCategory.TaxCgyDescr AS FiscalCategory,
                    tdscale(TaxRule.TaxRate,2,0) AS TaxRate,
                    COALESCE(IAT.CustomParamValue,'T') AS IAT,
                    COALESCE(IPPT.CustomParamValue,'P') AS IPPT,
                    COALESCE(PKP.MeasureUnit,'UN') AS MeasureUnit
                FROM
                    Price Price
                LEFT JOIN taxcalc.ProductTaxCategory ProductTaxCategory
                    ON ProductTaxCategory.ItemId=(Price.Context || "." || Price.ProductCode)
                LEFT JOIN taxcalc.TaxCategory TaxCategory
                    ON TaxCategory.TaxCgyId=ProductTaxCategory.TaxCgyId
                LEFT JOIN taxcalc.TaxRule TaxRule
                    ON TaxRule.TaxCgyId=ProductTaxCategory.TaxCgyId
                LEFT JOIN Product
                    ON Price.ProductCode=Product.ProductCode
                LEFT JOIN productdb.ProductKernelParams PKP
                    ON PKP.ProductCode=Product.ProductCode
                LEFT JOIN productdb.ProductCustomParams IAT
                    ON IAT.ProductCode=Product.ProductCode AND IAT.CustomParamId='IAT'
                LEFT JOIN productdb.ProductCustomParams IPPT
                    ON IPPT.ProductCode=Product.ProductCode AND IPPT.CustomParamId='IPPT'
                WHERE CURRENT_TIMESTAMP BETWEEN Price.ValidFrom AND Price.ValidThru
            ) FiscalProductsView
        WHERE EXISTS (
            SELECT 1 FROM productdb.ProductCatalogChangesCounter A
            LEFT JOIN fiscalinfo.FiscalProductCatalogChangesCounter B
            WHERE A.ChangesCount!=COALESCE(B.ChangesCount,-1) OR A.ChangesDateTime!=COALESCE(B.ChangesDateTime,'')
        );

        INSERT INTO fiscalinfo.FiscalProductCatalogChangesCounter SELECT * FROM productdb.ProductCatalogChangesCounter;
    """

    queries = [query]
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext, dbname=str(posid))
        queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
        conn.query("\0".join(queries))
    except Exception as _:
        logger.exception("ERRO CRIANDO FISCALINFO DATABASE INFORMATION")
        sys_log_exception("ERRO CRIANDO FISCALINFO DATABASE INFORMATION")
        if conn:
            conn.query('''ROLLBACK TRANSACTION;''')
    finally:
        if conn:
            conn.close()


def load_posconfig():
    global poslist
    global store_id
    global sell_categories
    global is24HoursStore
    global sangria_levels
    global is_sangria_enabled_config
    global max_transfer_value
    global show_all_transfer
    global round_donation_enabled
    global round_donation_pod_types
    global round_donation_payment_types
    global round_donation_institution
    global round_donation_cnpj
    global round_donation_site
    global set_product_quantity_pre
    global skim_digit_limit
    global picklist_reprint_type
    global customer_info_config
    global print_merchant_receipt
    global keyboard_comments
    global scale_ticket_mode
    global ask_for_delivery_courier
    global ask_for_delivery_payment

    config = cfgtools.read(os.environ["LOADERCFG"])

    print_merchant_receipt = get_storewide_config("Store.PrintMerchantReceipt", defval="False").lower() == "true"

    # Store-wide config
    is_sangria_enabled_config = get_storewide_config("Store.IsSangriaEnabled", defval="true").lower() == "true"
    sangria_levels = get_storewide_config("Store.SangriaLevels", defval="250;500;1000")
    max_transfer_value = float(get_storewide_config("Store.MaxTransfer", defval="0"))
    show_all_transfer = get_storewide_config("Store.ShowAllTransfer", defval="false").lower() == "true"

    is24HoursStore = get_storewide_config("Store.Is24Hours", defval="false").lower() == "true"
    manager.is24HoursStore = is24HoursStore

    round_donation_enabled = get_storewide_config("Store.RoundDonationInfo.RoundDonationEnabled", defval="false").lower() == "true"
    round_donation_pod_types = get_storewide_config("Store.RoundDonationInfo.RoundDonationPodTypes", defval="FC;DT;KK;DS").split(';')
    round_donation_payment_types = get_storewide_config("Store.RoundDonationInfo.RoundDonationPaymentTypes", defval="0").split(';')
    round_donation_institution = get_storewide_config("Store.RoundDonationInfo.RoundDonationInstitution")
    round_donation_cnpj = get_storewide_config("Store.RoundDonationInfo.RoundDonationCNPJ")
    round_donation_site = get_storewide_config("Store.RoundDonationInfo.RoundDonationSite")

    picklist_reprint_type = config.find_value("Reprint.PicklistReprintType") or "production_pick_list"
    auto_generate_skim_number = (config.find_value("Customizations.AutoGenerateSkimNumber") or "true").lower() == "true"
    scale_ticket_mode = (config.find_value("Customizations.ScaleTicketMode") or "price").lower()
    ask_for_delivery_courier = config.find_value( "Customizations.DeliveryConfigurations.AskForDeliveryCourier",
                                                  "true").lower() == "true"
    ask_for_delivery_payment = config.find_value("Customizations.DeliveryConfigurations.AskForDeliveryPayment",
                                                 "true").lower() == "true"

    skim_digit_limit_cfg = get_storewide_config("Store.SkimDigitLimit", defval="4-30")
    skim_digit_limit = {"min": int(skim_digit_limit_cfg.split("-")[0]),
                        "max": int(skim_digit_limit_cfg.split("-")[1])}

    store_id = get_storewide_config("Store.Id")
    manager.reports.store_id = store_id
    set_product_quantity_pre = True

    poslist = get_poslist()
    manager.reports.poslist = poslist
    manager.poslist = poslist

    min_value_to_ask_bordereau_justify_config = get_min_value_to_ask_bordereau_justify_config(config)

    actions.set_pos_config(PosConfig(max_transfer_value,
                                     skim_digit_limit,
                                     sangria_levels,
                                     auto_generate_skim_number,
                                     store_id,
                                     min_value_to_ask_bordereau_justify_config))

    for posid in poslist:
        model = get_model(posid)
        booth = int(model.find("PosState").get("booth"))
        if booth > 0:
            booth_pos_mapping[int(booth)] = int(posid)
            pos_booth_mapping[int(posid)] = int(booth)

        sell_categories[posid] = []
        podtype = get_podtype(model)
        list_categories = get_cfg(posid).key_value("listCategories", '''SORVETE,SHAKE,AGUA,SOBREMESA''' if podtype == "KK" else [])
        if type(list_categories) is not list and len(list_categories) > 0:
            sell_categories[posid] = list_categories.split(',')

        customer_info_config[posid] = get_customer_info_config(posid)

    keyboard_comments = get_keyboard_comments_config(config)


def force_sqlite_cache():
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext)
        for posid in poslist:
            try:
                conn.set_dbname(str(posid))
                conn.select("SELECT count(1) from sysproddb.ProductItem LIMIT 600000")
            except:
                pass
    except:
        pass
    finally:
        if conn:
            conn.close()


def request_eft(pos_id, model, eft_command, is_credit, amount, swipe=False, timeout=180000, eft_service=None, display_via_api=False, is_mercadopago=False):
    # Find the EFT associated to this POS
    order = model.find("CurrentOrder/Order")
    last_totaled = order.findall("StateHistory/State[@state='TOTALED']")[-1].get("timestamp").replace("-", "").replace(":", "")

    if is_credit:
        tender_type = 1
    else:
        tender_type = 122 if is_mercadopago else 2

    order_id = order.get("orderId")
    tender_seq_id = len(order.find("TenderHistory").findall("Tender"))
    data_fiscal = last_totaled[:8]
    hora_fiscal = last_totaled[9:15]
    operador = model.find("Operator").get("id")
    eft_name = get_used_service(model, "eft")

    dialog_id = show_message_dialog(pos_id, "$INFORMATION", "$WAITING_SITEF_ADD_PAYMENT", "NOCONFIRM", True)
    try:
        sitef_comp_name = "Sitef%02d" % int(pos_id)
        evt_data = [eft_name, None, pos_id, order_id]
        _eft_events.append(evt_data)

        ret = mbcontext.MB_EasySendMessage(sitef_comp_name, token=TK_SITEF_ADD_PAYMENT, format=FM_PARAM, data="%s;%s;%s;%s;%s;%s;%s;%s;%s" % (str(pos_id), str(order_id), str(operador), str(tender_type), str(amount), data_fiscal, hora_fiscal, tender_seq_id, display_via_api))
        if ret.token != TK_SYS_ACK:
            return
        else:
            return ret.data
    except:
        show_messagebox(pos_id, "$ERROR_PROCESSING_TEF", "$EFT", asynch=True, buttons="$OK")
    finally:
        close_asynch_dialog(pos_id, dialog_id)


def register_eft_activity(posid, session, activity_type, success_flag, amount="", result_xml="", authcode="", orderid="", cardno=""):
    payload = "\0".join(map(str, [session, activity_type, success_flag, amount, result_xml, authcode, orderid, cardno]))
    msg = send_message("account%d" % int(posid, 10), TK_ACCOUNT_EFTACTIVITY, FM_PARAM, payload)
    return msg.token != TK_SYS_NAK


def register_gift_activity(posid, session, activity_type, description, amount, authcode, orderid, cardno):
    payload = "\0".join([session, activity_type, description, amount, authcode, orderid, cardno])
    msg = send_message("account%d" % int(posid, 10), TK_ACCOUNT_GIFTCARDACTIVITY, FM_PARAM, payload)
    return msg.token != TK_SYS_NAK


def handle_electronic_payment(posid, model, tenderid, amount, xml_order, tendertype, tender_seq_id=None, id_fila=None):
    session = get_operator_session(model)
    order_id = xml_order.get("orderId")
    order_type = xml_order.get("type")
    current_op = get_current_operator(model)
    userid = current_op.get("id") if current_op else ""
    period = get_business_period(model)
    refund = (order_type == "REFUND")
    eft_xml = None
    eft_command = None

    if order_type not in ("SALE", "REFUND"):
        # Nothing to do...
        return tenderid, amount

    amt = None
    xml = None
    logger.debug(tendertype["electronicType"])

    try:
        # Ensure the amount is correct
        amt = "%.2f" % float(amount)
        tax = "%.2f" % float(xml_order.get("taxTotal") or 0)
        is_credit = (tendertype["electronicType"] == "CREDIT_CARD")
        if refund:
            eft_command = str(eft_commands.EFT_CREDITREFUND if is_credit else eft_commands.EFT_DEBITREFUND)
            eft_data = "\0".join([eft_command, posid, userid, amt, period, tax, order_id])
        else:
            eft_command = str(eft_commands.EFT_CREDITSALE if is_credit else eft_commands.EFT_DEBITSALE)
            eft_data = "\0".join([eft_command, posid, userid, amt, tax, order_id, period])

        tenderid = tendertype["electronicTypeId"]
        eft_xml = request_eft(posid, model, eft_data, is_credit, amt, is_mercadopago=tendertype["descr"] == "MERCADO PAGO")
        logger.info(eft_xml)
    except Exception as ex:
        sys_log_exception("Error processing credit-card. posid: %s - Erro %s" % (posid, str(ex)))

    # Check if the credit card was processed
    if not eft_xml or eTree.XML(eft_xml).get("Result") != "0":
        # Register the activity
        register_eft_activity(posid, session, activity_type=str(eft_command), success_flag='0', result_xml=eft_xml or "", orderid=order_id)
        if eft_xml:
            xml = eTree.XML(eft_xml)
            response = xml.get("Result") or "(none)"
            if tendertype["electronicType"] in "CREDIT_CARD":
                show_messagebox(posid, message="$CREDIT_CARD_NOT_PROCESSED|%s" % response.encode('utf-8'))

            if tendertype["electronicType"] in "DEBIT_CARD":
                show_messagebox(posid, message="$DEBIT_CARD_NOT_PROCESSED|%s" % response.encode('utf-8'))
        raise StopAction()
    else:
        # Success
        xml = eTree.XML(eft_xml)
        cardno, authcode, approved_amt, media, payment_amt, adq, exp_date, nsu, owner_name, last_digits = map(xml.get, ("CardNumber", "AuthCode", "ApprovedAmount", "Media", "ApprovedAmount", "IdAuth", "ExpirationDate", "NSU", "OwnerName", "LastDigits"))
        if not approved_amt:
            approved_amt = amt
        try:
            exp_date = exp_date or 'Indefinida'
            owner_name = owner_name or 'Indefinida'
            last_digits = last_digits or 'Indefinida'
            register_after = register_eft_after_payment(posid, order_id, tender_seq_id, authcode, cardno, owner_name, exp_date, adq, nsu, payment_amt, id_fila, media, last_digits)
            if register_after is None:
                show_messagebox(posid, "$ERROR", "Erro ao registrar dados do pagamento no Integrador Sefaz")
            elif "ERROR" in register_after:
                show_messagebox(posid, "$ERROR", "Erro ao registrar dados do pagamento no Integrador Sefaz: %s" % register_after)

            # Register the activity
            register_eft_activity(posid, session, activity_type=str(eft_command), success_flag='1', amount=approved_amt, result_xml=eft_xml, authcode=authcode or "", cardno=cardno or "", orderid=order_id)

            if float(approved_amt) != float(amt):
                try:
                    msg = "$CASHLESS_PARTIAL_APPROVAL_WARNING|%s|%s" % (format_amount(model, approved_amt, True), format_amount(model, amount, True))
                    show_message_dialog(posid, message=msg, assync=True)
                except:
                    pass
                finally:
                    amount = approved_amt
        except Exception as ex:
            sys_log_exception("Unexpected error after processing electronic payment - Error %s", str(ex))

    return tenderid, amount, xml


def register_eft_before_payment(posid, orderid, tender_seq_id, payment_amt, order_amt):
    payload = "\0".join(map(str, [posid, orderid, tender_seq_id, payment_amt, order_amt]))
    msg = send_message("FiscalWrapper", TK_FISCALWRAPPER_SAT_PROCESS_PAYMENT, FM_PARAM, payload)
    if msg.token == TK_SYS_ACK:
        return msg.data
    else:
        return None


def register_eft_after_payment(posid, orderid, tender_seq_id, auth_code, card_bin, owner_name, exp_date, adq, nsu, payment_amt, id_fila, brand, last_digits):
    payload = "\0".join(map(str, [posid, orderid, tender_seq_id, auth_code, card_bin, owner_name, exp_date, adq, nsu, payment_amt, id_fila, brand, last_digits]))
    msg = send_message("FiscalWrapper", TK_FISCALWRAPPER_SAT_PAYMENT_STATUS, FM_PARAM, payload)
    if msg.token == TK_SYS_ACK:
        return msg.data
    else:
        return None


@action
def doSale(pos_id, item_id, qty="1", size="", sale_type="EAT_IN", price_list='', pos_ot=None):
    model = get_model(pos_id)
    pos_ot = get_posot(model) if pos_ot is None else pos_ot
    pod_type = get_podtype(model)
    period = get_business_period(model)
    session = get_operator_session(model)

    is_new_order = None
    try:
        if not price_list:
            price_list = get_pricelist(model) if pod_type != "DL" and sale_type != "DELIVERY" else "EI.DL"
        else:
            price_list = "EI." + price_list

        sale_type = "DRIVE_THRU" if (pod_type == "DT") else sale_type

        pos_function = get_posfunction(model)
        is_new_order = not has_current_order(model)

        # Do NOT proceed if there is already an opened Order and not PartCode was provided
        if not is_new_order and item_id is None:
            return

        order_properties_dict = {}
        if is_new_order is True:
            if is_sangria_enable() and pod_type != "TT":
                set_drawer_status = do_set_drawer_status(pos_id, get_drawer_amount(pos_id, period, session))
                if set_drawer_status:
                    return
            order_properties_dict = new_order_properties(pod_type, pos_function, pos_id, pos_ot)

        order_created = False
        if is_new_order:
            order_created = process_new_order(model, pod_type, pos_function, pos_id, pos_ot, price_list, sale_type)

        if is_new_order is True and order_created is False and item_id is None:
            sale = pos_ot.createOrder(int(pos_id), pricelist=price_list, saletype=sale_type)
        else:
            apply_def_opts = True
            if pod_type == 'TT':
                apply_def_opts = False
            sale = pos_ot.doSale(int(pos_id), item_id, price_list, qty, True, size, sale_type, '0', apply_def_opts)
        if qty != "1":
            doChangeQuantity(int(pos_id), None, '1')

        if sale_type not in ("EAT_IN", "TAKE_OUT", "DRIVE_THRU"):
            pos_ot.updateOrderProperties(pos_id, saletype=sale_type)

        if len(order_properties_dict) > 0:
            pos_ot.setOrderCustomProperties(order_properties_dict)
        return sale

    except StopAction as _:
        return

    except Exception as ex:
        if is_new_order:
            model = get_model(pos_id)
            if has_current_order(model):
                void_order(pos_id, void_reason=7)

        show_messagebox(pos_id, message="ERRO AO INICIAR A VENDA - {}".format(ex.message))
        sys_log_exception('Error in doSale - new order: {} - '.format(is_new_order), ex)


def process_new_order(model, pod_type, pos_function, pos_id, pos_ot, price_list, sale_type):
    logger.debug("--- doSale start new order ---")
    check_new_order(model, pos_id)
    return offer_multi_order(model, pod_type, pos_id, pos_ot, pos_function, price_list, sale_type)


def new_order_properties(pod_type, pos_function, pos_id, pos_ot):
    logger.debug("--- doSale get_nf_type PAF ---")

    dict_sale = {}
    is_paf = get_nf_type(pos_id) == "PAF"
    request_customer_info = "onStart" in customer_info_config[int(pos_id)]['document'] or "onStart" in customer_info_config[int(pos_id)]['name']
    if request_customer_info or is_paf:
        logger.debug("--- doSale before customer info ---")
        customer_doc = None
        if "onStart" in customer_info_config[int(pos_id)]['document']:
            customer_doc = get_customer_doc(pos_id, pos_ot)
        customer_name = None
        if "onStart" in customer_info_config[int(pos_id)]['name']:
            customer_name = get_customer_name(pos_id, pos_ot)
        pre_sale = None
        if is_paf:
            get_and_fill_customer_address(pos_id, pos_ot)
            pre_sale = get_paf_pre_sale(pod_type, pos_ot, pos_function)
        logger.debug("--- doSale after customer info ---")
        dict_sale = update_custom_properties(customer_doc, customer_name, pre_sale)

    return dict_sale


def check_new_order(model, pos_id):
    check_operator_logged(pos_id, model=model, can_be_blocked=True)

    # check if skim is needed before new order
    check_sangria(model, pos_id)

    # check if the drawer should be closed before starting an order
    logger.debug("--- doSale check_drawer ---")
    if get_cfg(pos_id).key_value("needToCloseDrawer", "true") == "true":
        check_drawer(pos_id, model)


def offer_multi_order(model, pod_type, pos_id, pos_ot, pos_function, price_list, sale_type):
    if pod_type == "DT" and pos_function == "CS" and get_last_order(model):
        buttons = "$SAME_CAR|$NEW_CAR|$CANCEL"
        index = show_messagebox(pos_id, message="$DO_YOU_WANT_SAME_OR_NEW_CAR", title="$SAME_CAR", buttons=buttons)
        if index in (None, 2):
            raise StopAction()  # User cancelled, or timeout

        if index == 1:
            return False

        check_current_order(pos_id, model=model, need_order=False)
        try:
            last_order = get_last_order(model)
            if not last_order:
                show_info_message(pos_id, "$NO_PREVIOUS_ORDER_FOR_MULTIORDER", msgtype="warning")
                raise StopAction()

            logger.debug("--- doSale before posot.createOrder ---")
            order_id = last_order["orderId"]
            pos_ot.createOrder(int(pos_id), pricelist=price_list, multiorderid=order_id, saletype=sale_type)
            logger.debug("--- doSale after posot.createOrder ---")

        except OrderTakerException as ex:
            # show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
            #                  msgtype="critical")
            show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                            icon="error")
            raise StopAction()
        else:
            return True

    return False


def update_custom_properties(customer_doc=None, customer_name=None, pre_sale=None):
    dict_sale = {}

    if customer_doc:
        dict_sale.update({"CUSTOMER_DOC": customer_doc})
    if customer_name:
        dict_sale.update({"CUSTOMER_NAME": customer_name})
    if pre_sale:
        dict_sale.update({"PRE_VENDA": pre_sale})

    return dict_sale


def get_paf_pre_sale(pod_type, pos_ot, pos_function):
    pre_sales = None
    if pod_type == "OT" or pos_function == "OT":
        msg = send_message("Persistence", TK_PERSIST_SEQUENCER_INCREMENT, FM_PARAM, "PafPreVenda", 600 * USECS_PER_SEC)
        if msg.token == TK_SYS_NAK:
            raise Exception("Error incrementing mandatory sequence [PafPreVenda] on Persistence")
        pre_sales = str(msg.data.split('\0')[0])
        if pos_ot.additionalInfo:
            pos_ot.additionalInfo += "|PreVenda=%s" % pre_sales
        else:
            pos_ot.additionalInfo = "PreVenda=%s" % pre_sales
    return pre_sales


def get_and_fill_customer_address(pos_id, pos_ot):
    customer_address = show_keyboard(pos_id, "Digite o endereço do cliente", defvalue="", title="", numpad=False)
    if customer_address not in (None, ""):
        customer_address = customer_address.translate(None, '-+[]/;.|<>:?{}=_()*&^%$#@!').upper()
    else:
        customer_address = ""

    fill_additional_info(pos_ot, "ADDRESS", customer_address)


def get_customer_doc(pos_id, pos_ot, default_doc=""):
    valid = False
    customer_doc = ""
    while not valid:
        message = "(somente números)"
        title = "Digite o CPF/CNPJ"
        customer_doc = show_keyboard(pos_id, message, title=title, mask="CPF_CNPJ", numpad=True, defvalue=default_doc)
        if customer_doc is None:
            raise StopAction()
        if customer_doc == "":
            customer_doc = ""
            break
        valid = validate_document(customer_doc)
        if not valid:
            show_messagebox(pos_id, "$INVALID_CPF_CNPJ")

    fill_additional_info(pos_ot, "CPF", customer_doc)
    return customer_doc


def validate_document(customer_doc):
    valid = False
    if len(customer_doc) <= 11:
        valid = validar_cpf(customer_doc)
    elif len(customer_doc) > 11:
        valid = validar_cnpj(customer_doc)
    return valid


def get_customer_name(pos_id, pos_ot, default_name=""):
    valid = False
    customer_name = ""
    while not valid:
        if default_name and isinstance(default_name, unicode):
            default_name = default_name.encode("utf-8")
        customer_name = show_keyboard(pos_id, "Digite o nome do cliente", defvalue=default_name, title="", nopad=True)
        if customer_name is None:
            raise StopAction()
        if customer_name == "":
            customer_name = ""
            break
        customer_name = customer_name.translate(None, '-+[]/;.|<>:?{}=_()*&^%$#@!,').upper()
        valid = check_customer_name(pos_id, customer_name)

    fill_additional_info(pos_ot, "NAME", customer_name)
    return customer_name


def fill_additional_info(pos_ot, properties, value):
    if pos_ot.additionalInfo:
        pos_ot.additionalInfo += "|"
    else:
        pos_ot.additionalInfo = ""
    pos_ot.additionalInfo += "{0}={1}".format(properties, value)


def customer_doc_is_required(order_xml, pod_function):
    if pod_function == "OT":
        return False, ""

    return _check_custom_properties(order_xml, "CUSTOMER_DOC")


def customer_name_is_required(order_xml):
    return _check_custom_properties(order_xml, "CUSTOMER_NAME")


def _check_custom_properties(order_xml, property_name):
    for prop in order_xml.findall("CustomOrderProperties/OrderProperty"):
        key, value = prop.get("key"), prop.get("value")
        if key == property_name:
            if value == "":
                return True, ""
            return False, value
    return True, ""


@action
def doStartOrder(pos_id, sale_type="EAT_IN"):
    doSale(pos_id, None, "", "", sale_type)


@action
def get_nf_type(posid=1, *args):
    global nf_type
    if not nf_type:
        ret = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_GET_NF_TYPE, format=FM_PARAM, data=None)
        # Processamento Finalizado com Sucesso
        if ret.token == TK_SYS_ACK:
            nf_type = ret.data.upper()
            manager.nf_type = nf_type
            # Populate taxes for combos
            if nf_type == "PAF":
                populate_combo_taxes(posid)
    return nf_type


def _get_weight_qty(pos_id):
    weight_qty = get_scale_weight(int(pos_id))
    if weight_qty is None:
        weight_qty = show_keyboard(pos_id, "$TYPE_WEIGHT_QTY", title="", mask="weight", defvalue="0.000", numpad=True)
    if weight_qty in (None, "", "."):
        raise StopAction()
    if weight_qty == "0":
        raise StopAction()

    return str(float(weight_qty))


def get_scale_weight(pos_id):
    model = get_model(pos_id)
    scale_name = get_used_service(model, "scale")
    weight = scale_wait_data(pos_id, scale_name)
    return weight


def scale_wait_data(pos_id, service_name, timeout=2000):
    weight_comparer = WeightComparer()
    scale_event = pos_scale_events.create_scale_event(pos_id, service_name)
    dialog_id = None

    try:
        while True:
            if not start_measuring_weight(service_name):
                return None

            if dialog_id is None:
                dialog_id = show_messagebox(pos_id, "$WAIT_SCALE_WEIGHT", buttons="$CANCEL", asynch=True)
                pos_scale_dialogs.append(str(dialog_id))
            elif str(dialog_id) not in pos_scale_dialogs:
                return ""

            scale_event.wait(float(timeout/1000.0))
            if scale_event.weight is None:
                return None

            if scale_event.weight > 0 and weight_comparer.is_weight_equal_to_previous(scale_event.weight):
                close_asynch_dialog(pos_id, dialog_id)
                dialog_id = None

                selected_option = show_messagebox(
                    pos_id,
                    message="$CONFIRM_SCALE_WEIGHT|{0}".format("%.3f" % scale_event.weight),
                    buttons="$OK|$GET_WEIGHT_AGAIN|$CANCEL")

                if selected_option == 0:
                    return scale_event.weight
                elif selected_option == 2:
                    return ""
    finally:
        if pos_id in pos_scale_events.get_wait_pos_id_event_dict():
            pos_scale_events.finish_event(scale_event)

        if dialog_id is not None:
            close_asynch_dialog(pos_id, dialog_id)


def start_measuring_weight(service_name):
    try:
        msg = send_message(service_name, TK_DRV_IOCTL, FM_PARAM, "")
        if msg.token == TK_SYS_ACK:
            return True
        else:
            return False
    except MBException as _:
        sys_log_exception("Erro comunicando com a balança")
        return False


@action
@block_action_if_pos_is_blocked
def doCompleteOption(pos_id, context, part_code, qty="1", line_number="", size="", sale_type="EAT_IN", subst='', seat='', pricelist='', comment=None, *args):
    model = get_model(pos_id)
    if _is_changing_order(model) and is_table_service(model):
        show_messagebox(pos_id, message="$CANNOT_ADD_ITEMS_IN_AN_OPENED_ORDER", icon="error")
        raise StopAction()

    global waiting_scale
    if is_a_product_with_measure_unit(part_code):
        if waiting_scale:
            return

        try:
            waiting_scale = True
            qty = _get_weight_qty(pos_id)
        finally:
            waiting_scale = False

    list_categories = sell_categories[int(pos_id)]
    pos_ot = get_posot(model)
    sale_type = sale_type or "EAT_IN"
    sale_xml = None

    try:
        pos_ot.blkopnotify = True
        if subst:
            doClearOptionItem(pos_id, line_number, subst, pos_ot)

        if len(list_categories) > 0:
            if _cache.is_not_order_kiosk(part_code, get_podtype(model) or None, list_categories):
                show_info_message(pos_id, '$KIOSK_NOT_SALE', msgtype='error')
                raise StopAction()

        sale_xml = doOption(pos_id, context, part_code, qty, line_number, size, sale_type, pricelist, comment, pos_ot, args)
        if sale_xml is None:
            return

        if sale_xml not in ["", None, True, False]:
            sale = eTree.XML(sale_xml)
            part_code = sale.get("partCode")
            line_number = sale.get("lineNumber")
            item_id = sale.get("itemId")

            if seat not in ('', '0'):
                pos_ot.setOrderCustomProperty("seat", seat, "", line_number, item_id, "0", part_code)

        if qty != "1":
            doChangeQuantity(int(pos_id), None, '1')

        return sale_xml
    finally:
        pos_ot.blkopnotify = False
        if sale_xml or qty == '0':
            pos_ot.updateOrderProperties(pos_id)


@action
def doOption(pos_id, context, part_code, qty="", line_number="", size="", sale_type="EAT_IN", pricelist ='', comment=None, pos_ot=None, *args):
    model = get_model(pos_id)
    item_id = context + "." + part_code
    try:
        try:
            check_operator_logged(pos_id, model=model, can_be_blocked=False)
        except StopAction:
            if get_podtype(model) != 'TT':
                raise
            # should never run this code since kiosk always open order before
            if not has_current_order(model):
                from actions.kiosk import do_start_kiosk_order
                do_start_kiosk_order(pos_id)
        item_qty = qty or "1"

        if context == '1':
            # Options not solved OR there are remaining items to sell
            sale_xml = doSale(pos_id, item_id, item_qty, size, sale_type, pricelist, pos_ot)
            return sale_xml
        elif has_current_order(model):
            pos_ot = get_posot(model) if pos_ot is None else pos_ot

            # Try to resolve an open option
            option_done = pos_ot.doOption(int(pos_id), item_id, item_qty, line_number, (size or '@'), True)
            if option_done:
                curr_line = get_order_saleline(pos_id, context, part_code, line_number)
                remove_custom_comment(pos_ot, curr_line)

                if comment not in [None, '']:
                    level = str(int(option_done[0].get("level")) + 1) if option_done else curr_line[0].get("level")
                    add_custom_comment(pos_ot, context, part_code, line_number, level, comment_map[comment])

                return True

    except OrderTakerException as ex:
        sys_log_exception("Error processing [doOption]")
        show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()))
    return False


@action
def doClearOption(posid, line_number="", qty="", *args):
    model = get_model(int(posid))
    check_current_order(posid, model=model, need_order=True)
    lines = get_clearOptionsInfo(model, line_number)
    if not lines:
        return  # Nothing to clear
    to_clear = lines[0]
    if len(lines) > 1:
        options = [str(line.get("productName")) for line in lines]
        index = show_listbox(posid, options, message="Selecione uma opção para limpar")
        if index is None:
            return  # The user cancelled - or timed-out
        to_clear = lines[index]
    # Clear the option
    pos_ot = get_posot(model)
    try:
        item_id = "%s.%s" % (to_clear.get("itemId"), to_clear.get("partCode"))
        pos_ot.clearOption(posid, line_number, qty, item_id)
        return True
    except ClearOptionException, e:
        sys_log_exception("Could not clear option")
        show_messagebox(posid, message="Error %s" % e, icon="error")
    except OrderTakerException, ex:
        show_messagebox(posid, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")


@action
def doChangeSaleType(posid, saletype, *args):
    model = get_model(posid)
    posot = get_posot(model)
    check_operator_logged(posid, model=model, can_be_blocked=False)

    if has_current_order(model):
        # Set the sale type on the order
        posot.updateOrderProperties(posid, saletype=saletype)
    return True


def list_open_options(order):
    j = 0
    sale_lines = order.findall("SaleLine")
    for i in range(0, len(sale_lines)):
        if i < j or j >= len(sale_lines):
            continue

        line = sale_lines[i]
        if line.get("qty") == "0":
            for j in range(i + 1, len(sale_lines)):
                option_son_line = sale_lines[j]
                if int(line.get("level")) >= int(option_son_line.get("level")):
                    break
        elif line.get("itemType") == "OPTION" and int(line.get("chosenQty")) < int(line.get("defaultQty")):
            return line

    return None
# END list_open_options


@action
def doTotal(pos_id, screen_number="", dlg_id=None, is_recall=False, is_kiosk="False", is_local_delivery="False", *args):
    logger.debug("Totalizando Order - POS %s" % pos_id)
    is_kiosk = is_kiosk and is_kiosk.lower() == "true"

    model = get_model(pos_id)
    posot = get_posot(model)

    pod_function = get_posfunction(model) if get_podtype(model) in ("DT", "FC") else get_podtype(model)
    request_customer_info = "onTotal" in customer_info_config[int(pos_id)]['document'] or "onTotal" in customer_info_config[int(pos_id)]['name']

    if get_nf_type(pos_id) != "PAF" and not is_kiosk and not is_recall and request_customer_info:
        get_document = "onTotal" in customer_info_config[int(pos_id)]['document']
        get_name = "onTotal" in customer_info_config[int(pos_id)]['name']
        fill_customer_properties(model, pod_function, pos_id, posot, get_doc=get_document, get_name=get_name)

    if is_day_blocked(model):
        # show_info_message(pos_id, "$POS_IS_BLOCKED_BY_TIME", msgtype="critical")
        show_messagebox(pos_id, message="$POS_IS_BLOCKED_BY_TIME", icon="error")
        return

    # Waits a maximum of 1,5 seconds for the order to "arrive" at the POS model
    time_limit = (time.time() + 1.0)
    while (time.time() < time_limit) and (not has_current_order(get_model(pos_id))):
        time.sleep(0.1)
    logger.debug("Order Carregada - POS %s" % pos_id)

    check_current_order(pos_id, model=model, need_order=True)
    order = model.find("CurrentOrder/Order")

    # Check if there is ANY item in the Sale
    sale_lines = order.findall("SaleLine")
    deleted_line_numbers = map(lambda x: x.get("lineNumber"), filter(lambda x: x.get("level") == "0" and x.get("qty") == "0", sale_lines))
    active_sale_lines = filter(lambda x: x.get("lineNumber") not in deleted_line_numbers, sale_lines)

    if not active_sale_lines:
        show_messagebox(pos_id, "$HAS_NO_ITEMS_IN_ORDER", title="")
        return

    # Get the order type from the order to check if it is a REFUND, WASTE or a normal SALE
    order_type = order.get("type")
    if order_type != "REFUND":  # Ignore choices verification for REFUND
        if not on_before_total(pos_id, model):
            return

        option = list_open_options(order)
        if option is not None:
            prod_name = get_line_product_name(model, int(option.get("lineNumber")))
            # show_info_message(pos_id, "$NEED_TO_RESOLVE_OPTION|%s" % (prod_name.encode("UTF-8")), msgtype="critical")
            show_messagebox(pos_id, message="$NEED_TO_RESOLVE_OPTION|%s" % (prod_name.encode("UTF-8")), icon="error")
            return

    logger.debug("Order Verificada - Pronta para Totalizar - POS %s" % pos_id)
    try:
        # Totalize the order
        posot.doTotal(int(pos_id))
        logger.debug("Core Total OK - POS %s" % pos_id)

        # Check if Order is already PAID (Previuos tenders are bigger than current due amount)
        xml_order = eTree.XML(posot.orderPicture(pos_id))
        due_amount = float(xml_order.get("dueAmount"))

        if due_amount < 0:
            show_messagebox(pos_id, message="$TENDERS_ARE_BIGGER_THEN_DUE_AMOUNT", icon="warning")
            do_back_from_total(pos_id)
            return "Error"

        if screen_number:
            if pod_function == "OT":
                doStoreOrder(pos_id, "false")
                return

    except StopAction as _:
        raise

    except Exception as ex:
        show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")
        if is_recall:
            raise ex

    finally:
        logger.debug("Order Totalizada - POS %s" % pos_id)

    return True


def fill_customer_properties(model, pod_function, pos_id, pos_ot, get_doc=False, get_name=False, force=False):
    order_xml = get_current_order(model)

    customer_doc = None
    default_doc = None
    if get_doc:
        is_required, default_doc = customer_doc_is_required(order_xml, pod_function)
        if force or is_required:
            customer_doc = get_customer_doc(pos_id, pos_ot, default_doc)

    customer_name = None
    default_name = None
    if get_name:
        is_required, default_name = customer_name_is_required(order_xml)
        if force or is_required:
            customer_name = get_customer_name(pos_id, pos_ot, default_name)

    if (customer_doc == default_doc) and (customer_name == default_name):
        return

    order_properties_dict = update_custom_properties(customer_doc, customer_name)
    for prop in order_properties_dict.keys():
        if order_properties_dict[prop] is None:
            pos_ot.setOrderCustomProperty(prop)
            del order_properties_dict[prop]

    if len(order_properties_dict) > 0:
        pos_ot.setOrderCustomProperties(order_properties_dict)


@action
def doTender(pos_id,
             amount,
             tender_type_id="0",
             offline="false",
             need_confirmation="false",
             is_kiosk='false',
             danfe_type='',
             local_payment_data='',
             *args):
    logger.debug("--- doTender START ---")

    payment_data = None
    if local_payment_data != "":
        payment_data = json.loads(local_payment_data)

    is_kiosk = (is_kiosk or 'false').lower() == 'true'

    if is_kiosk:
        show_info_message(pos_id, "AGUARDE", msgtype="info")

    # Inline function to Cancel current Order and Delete Payments
    def cancel_sale_and_payments(error_message=""):
        if get_nf_type(pos_id) == "PAF":
            data = '\x00'.join(map(str, [fpcmds.FPRN_SALECANCEL, '', '', '']))
            try:
                mbcontext.MB_EasySendMessage("FiscalPrinter%s" % pos_id, TK_FISCAL_CMD, format=FM_PARAM, data=data)
            except MBException:
                time.sleep(0.5)
                mbcontext.MB_EasySendMessage("FiscalPrinter%s" % pos_id, TK_FISCAL_CMD, format=FM_PARAM, data=data)
        close_asynch_dialog(pos_id, dlgid) if dlgid else None
        show_message_dialog(pos_id, "$ERROR", "$CANCELED_SALE|{0}".format(error_message))
        posot.clearTenders(int(pos_id))
        void_order(pos_id, void_reason=8)

    model = get_model(pos_id)
    check_current_order(pos_id, model=model, need_order=True)
    posot = get_posot(model)

    # Inline function to confirm last payment and set order to PAID
    def tender_and_finalize():
        while True:
            dlgid = None
            try:
                model = get_model(pos_id)
                check_current_order(pos_id, model=model, need_order=True)
                xml_order = get_current_order(model)
                customer_name = ""
                for prop in xml_order.findall("CustomOrderProperties/OrderProperty"):
                    key, value = prop.get("key"), prop.get("value")
                    if key == "CUSTOMER_NAME":
                        customer_name = value
                        break

                logger.debug("--- doTender before 'Processando pagamento' 2 ---")

                dlgid = show_message_dialog(pos_id, "$PLEASE_WAIT", "$PROCESSING_PAYMENT_DATA", "NOCONFIRM", True)

                if round_donation_value > 0.0:
                    posot.setOrderCustomProperty("DONATION_VALUE", str(round_donation_value))

                logger.debug("--- doTender before posot.doTender 2 ---")
                posot.doTender(int(pos_id), tender_type_id, amount, 0, res["tenderId"])
                logger.debug("--- doTender after posot.doTender 2 ---")

                close_asynch_dialog(pos_id, dlgid)

                if round_donation_value > 0.0:
                    _do_print_donation(model, pos_id, order_id, customer_name, format(round_donation_value, '.2f').replace(".", ","), round_donation_institution, round_donation_cnpj, round_donation_site)

                break
            except OrderTakerException as ex:
                show_message_dialog(pos_id, "$ERROR", "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()))

                # Erro Fiscal (Normalmente falha de comunicação com a impressora) - PopUp (Tentar Novamente ou Cancelar)
                try_again_response = show_message_options_dialog(pos_id,
                                                                 "Tentar Novamente|Cancelar",
                                                                 "$ERROR",
                                                                 "Ocorreu um erro finalizando a venda")

                # 0 -> Tentar Novamente / 1 -> Cancelar
                if try_again_response != 0:
                    cancel_sale_and_payments("Cancelamento solicitado pelo usuário")
                    break
                else:
                    time.sleep(2)
            finally:
                if dlgid:
                    close_asynch_dialog(pos_id, dlgid)
    # END

    global lock_tender
    with lock_tender:
        global tendering
        if tendering[int(pos_id)]:
            logger.info("PosId {0} with tender locked".format(pos_id))
            sys_log_error("PosId {0} with tender locked".format(pos_id))
            return
        else:
            tendering[int(pos_id)] = True

    dlgid = None
    try:
        model = get_model(pos_id)
        check_current_order(pos_id, model=model, need_order=True)
        posot = get_posot(model)
        period = get_business_period(model)
        session = get_operator_session(model)
        pod_type = get_podtype(model)
        round_donation_value = 0.0

        xml_order = get_current_order(model)
        if xml_order.get("state") != "TOTALED":
            show_message_dialog(pos_id, message="FiscalMode PAF but no PafEcfListener found")
            return

        due_amount = xml_order.get("dueAmount")

        total_gross = xml_order.get("totalGross")
        order_due = float(due_amount)
        order_id = xml_order.get("orderId")
        order_type = xml_order.get("type")

        tender_type = get_tender_type(pos_id, model, tender_type_id, amount)
        if tender_type is None:
            return

        if amount == "Exact":
            amount = due_amount

        if amount in (None, "", ".") or float(amount) <= 0:
            show_message_dialog(pos_id, message="Valor devido deve ser informado!")
            return

        if need_confirmation == "true":
            message = "Confirma recebimento em {0}: {1}".format(tender_type['descr'], format_amount(model, amount))
            ret = show_message_options_dialog(pos_id, "$OK|$CANCEL", message=message)
            if ret is None or ret == 1:
                return

        decimal_len = abs(Decimal(xml_order.get("dueAmount")).as_tuple().exponent)
        if decimal_len > 2:
            difference = abs(float(xml_order.get("dueAmount")) - round_half_away_from_zero(float(xml_order.get("dueAmount")), 2))
            amount = str(float(amount) + difference)

            # If the tender will close the sale and we have an index pin pad,
        tender_seq_id = len(xml_order.findall("TenderHistory/Tender")) + 1

        ignore_payment = False
        previous_tender_id = None
        tender_type_id = tender_type["id"]
        if float(due_amount) <= 0:
            logger.error("Tentativa de pagamento para pedido ja pago. Tratando situacao")
            previous_tender = xml_order.findall("TenderHistory/Tender")[-1]
            previous_tender_type = previous_tender.get("tenderType")
            if previous_tender_type != tender_type_id:
                cancel_sale_and_payments("Erro processando venda. Por favor, tente novamente.")
                return

            previous_tender_amount = previous_tender.get("tenderAmount")
            if float(previous_tender_amount) >= float(amount) or int(tender_type_id) in (TenderType.credit, TenderType.debit):
                ignore_payment = True
                res = previous_tender.attrib
                amount = previous_tender_amount
                res['dueAmount'] = xml_order.get("dueAmount")
                res['totalAmount'] = xml_order.get("totalAmount")
            else:
                previous_tender_id = int(previous_tender.get("tenderId"))
                order_due = float(previous_tender_amount) + float(due_amount)

        if not ignore_payment:
            change = 0

            def _is_donation_enable():
                if round_donation_enabled is False:
                    return False

                if tender_seq_id != 1:
                    return False

                if pod_type not in round_donation_pod_types:
                    return False

                if tender_type_id not in round_donation_payment_types:
                    return False

                return True

            def _do_round_donation():
                if _is_donation_enable():
                    donation_value = round(order_due % 1, 2)
                    if donation_value == 0.0:
                        return 0.0

                    donation_value = 1 - donation_value
                    donation_message = "$PARTICIPATE_ROUND_PROJECT_BODY|$L10N_CURRENCY_SYMBOL|{}"\
                        .format(format(donation_value, '.2f'))

                    dret = show_message_options_dialog(pos_id, "$YES|$NO", "$ROUND_PROJECT_TITLE", donation_message)
                    if dret == 0:
                        return round(donation_value, 2)

                return 0.0

            # Check the maximum change
            if (amount != "") and (float(amount) > order_due):
                if tender_type["electronicTypeId"] in (1, 2):
                    show_message_dialog(pos_id, message="Valor para pagamento com cartão não pode ser superior ao devido!")
                    return

                if order_type == "REFUND":
                    show_message_dialog(pos_id, message="$NO_CHANGE_ALLOWED_IN_REFUND")
                    return

                change += float(amount) - order_due
                change_limit = tender_type['changeLimit']

                if change_limit and change > float(change_limit):
                    change_limit = float(change_limit)
                    if change_limit > 0:
                        msg = "$MAXIMUM_CHANGE_ALLOWED|%s|%s" % (format_amount(model, change_limit), format_amount(model, change))
                        show_message_dialog(pos_id, message=msg)
                    else:
                        show_message_dialog(pos_id, message="$AMOUNT_GREATER_THAN_DUE")
                    return

                # Arredondar Dinheiro
                round_donation_value = _do_round_donation()
                if round_donation_value > 0.0:
                    change -= round_donation_value

                show_message_dialog(pos_id, message="$MONEY_CHANGE|R$%.2f" % abs(change))

            elif (amount != "") and float(due_amount) == float(amount) and tender_type["electronicTypeId"] in (1, 2):
                # Arredondar Cartão de Crédito
                round_donation_value = _do_round_donation()
                if round_donation_value > 0.0:
                    amount = format(float(amount) + round_donation_value, '.2f')

            xml = None

            # Process electronic payments
            id_fila = None
            if offline.lower() == "false" and tender_type["electronicTypeId"] not in (0, 3) and payment_data is None:
                # Sends message to SAT/MFE/VFP-e to register payment data. If it returns error, the sale should be CANCELLED
                id_fila = register_eft_before_payment(pos_id, order_id, tender_seq_id, amount, total_gross)
                if id_fila is None:
                    show_message_dialog(pos_id, "$ERROR", "Erro ao iniciar pagamento no Integrador Sefaz")
                    return
                elif "ERROR" in id_fila:
                    show_message_dialog(pos_id, "$ERROR", "Erro ao iniciar pagamento no Integrador Sefaz: %s" % id_fila)
                    return
                tender_type_id, amount, xml = handle_electronic_payment(pos_id, model, tender_type_id, amount, xml_order, tender_type, tender_seq_id, id_fila)
            elif payment_data is not None:
                eft_command = eft_commands.EFT_DEBITSALE if int(tender_type_id) == TenderType.debit else eft_commands.EFT_CREDITSALE
                register_eft_activity(pos_id,
                                      session,
                                      activity_type=str(eft_command),
                                      success_flag='1',
                                      result_xml=local_payment_data,
                                      orderid=order_id)

            logger.debug("--- doTender before 'Processando pagamento' ---")

            dlgid = show_message_dialog(pos_id, "$PLEASE_WAIT", "$PROCESSING_PAYMENT_DATA", "NOCONFIRM", True)

            tender_seq_id = len(xml_order.findall("TenderHistory/Tender")) + 1

            #  PAF: We need to save all payment activities to be printed when order is paid
            if get_nf_type(pos_id) == "PAF" and tender_type["electronicTypeId"] not in (0, 3):
                logger.debug("--- doTender before PAF save all payments activities ---")
                conn = None
                try:
                    TENDER_CREDIT_CARD = "2"
                    TENDER_DEBIT_CARD = "3"
                    tender_id = (TENDER_CREDIT_CARD if tender_type["electronicType"] == "CREDIT_CARD" else TENDER_DEBIT_CARD)
                    # insert the [fiscalinfo.ElectronicTransactions] data
                    conn = persistence.Driver().open(mbcontext, dbname=str(pos_id))
                    queries = []
                    queries.append("""INSERT OR REPLACE INTO fiscalinfo.ElectronicTransactions(PosId,OrderId,Sequence,TenderId,TenderDescr,Amount,XmlData)
                        VALUES (%d,%d,%s,%d,%s,'%s','%s')""" % (
                        int(pos_id), int(order_id),
                        "\n(SELECT count() FROM fiscalinfo.ElectronicTransactions WHERE PosId=%d AND OrderId=%d)\n" % (
                        int(pos_id), int(order_id)),
                        int(tender_id),
                        "\n(SELECT TenderDescr FROM productdb.TenderType WHERE TenderId=%d)\n" % (int(tender_id) - 1),
                        conn.escape(amount), conn.escape(eTree.tostring(xml)))
                                   )
                    BEGIN_TRANSACTION = ["BEGIN TRANSACTION", "UPDATE fiscalinfo.FiscalDEnabled SET Enabled=0"]
                    COMMIT_TRANSACTION = ["UPDATE fiscalinfo.FiscalDEnabled SET Enabled=1", "COMMIT TRANSACTION"]
                    queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                    conn.query("\0".join(queries))
                except Exception as ex:
                    show_message_dialog(pos_id, message="Erro armazenando dados do pagamento: %s" % str(ex))
                finally:
                    if conn:
                        conn.close()
                logger.debug("--- doTender after PAF save all payments activities ---")

            tender_details = ""
            if tender_type["electronicTypeId"] in (1, 2):
                if payment_data is not None:
                    tender_details = json.dumps({"CNPJAuth": payment_data["CNPJAuth"],
                                                 "TransactionProcessor": payment_data["TransactionProcessor"],
                                                 "Bandeira": payment_data["Bandeira"],
                                                 "IdAuth": payment_data["IdAuth"],
                                                 "AuthCode": payment_data["AuthCode"],
                                                 "ReceiptCustomer": payment_data["ReceiptCustomer"],
                                                 "ReceiptMerchant": payment_data["ReceiptMerchant"]})
                else:
                    tender_details = json.dumps({"CNPJAuth": xml.attrib["CNPJAuth"],
                                                 "TransactionProcessor": xml.attrib["TransactionProcessor"],
                                                 "Bandeira": xml.attrib["Bandeira"],
                                                 "IdAuth": xml.attrib["IdAuth"],
                                                 "AuthCode": xml.attrib["AuthCode"],
                                                 "ReceiptCustomer": xml.attrib["ReceiptCustomer"],
                                                 "ReceiptMerchant": xml.attrib["ReceiptMerchant"]}
                    )

            # Do Tender - DO NOT SET ORDER TO PAID
            logger.debug("--- doTender before posot.doTender ---")
            res = posot.doTender(int(pos_id), tender_type_id, amount, True, previous_tender_id, tenderdetail=tender_details)
            logger.debug("--- doTender after posot.doTender ---")

            # Fecha Mensagem de Processando Pagamento
            close_asynch_dialog(pos_id, dlgid) if dlgid else None
            logger.debug("--- doTender after 'Processando pagamento' ---")

            if float(res["dueAmount"]) > 0:
                return

        pos_ot = get_posot(model)
        doc = get_customer_doc_after_paid(pos_id, pos_ot)
        order_properties_dict = update_custom_properties(customer_doc=doc)
        if len(order_properties_dict) > 0:
            order = get_current_order(model)
            pos_ot.setOrderCustomProperties(order_properties_dict, orderid=order.get("orderId"))

        logger.debug("--- doTender after 'Processando pagamento 2' ---")
        while True:
            logger.debug("--- doTender before PROCESSING_FISCAL_DATA ---")
            try:
                dlgid = show_message_dialog(pos_id, "$PROCESSING", "$PROCESSING_FISCAL_DATA", "NOCONFIRM", True)
                if danfe_type == "":
                    data = pos_id + '\0' + order_id
                else:
                    data = '\0'.join([pos_id, order_id, danfe_type])
                ret = mbcontext.MB_EasySendMessage("FiscalWrapper",
                                                   TK_FISCALWRAPPER_PROCESS_REQUEST,
                                                   format=FM_PARAM,
                                                   data=data,
                                                   timeout=180000000)

                # Processamento Finalizado com Sucesso
                if ret.token == TK_SYS_ACK:
                    if get_nf_type(pos_id) != "PAF":
                        try:
                            current_printer = get_used_service(model, "printer")
                            msg = mbcontext.MB_EasySendMessage(current_printer,
                                                               TK_PRN_PRINT,
                                                               format=FM_PARAM,
                                                               data=ret.data,
                                                               timeout=20000000)  # type: MBMessage
                            if msg.token != TK_SYS_ACK and not is_kiosk:
                                close_asynch_dialog(pos_id, dlgid) if dlgid else None
                                show_message_dialog(pos_id, "$INFORMATION", "$ERROR_PRINT_NFE|%s" % msg.data)
                        except Exception as ex:
                            if not is_kiosk:
                                close_asynch_dialog(pos_id, dlgid) if dlgid else None
                                show_message_dialog(pos_id, "$INFORMATION", "$ERROR_PRINT_NFE|%s" % repr(ex))

                    if float(res["totalAmount"]) > 0 and tender_type["openDrawer"] != 0:
                        doOpenDrawer(pos_id)
                    if not is_kiosk:
                        close_asynch_dialog(pos_id, dlgid) if dlgid else None

                    # Confirm Tender - Set Order to PAID
                    logger.debug("--- doTender before tender_and_finalize ---")
                    tender_and_finalize()
                    logger.debug("--- doTender after tender_and_finalize ---")

                    break

                # Ocorreu um Erro
                if ret.data in ("Certificado da Loja Expirado", "Falha na Leitura da Validade do Certificado NFCE"):
                    cancel_sale_and_payments("Certificado da Loja Expirado")
                    break

                parts = ret.data.split('\0')

                if len(parts) < 2:
                    cancel_sale_and_payments(ret.data)
                    break
                elif len(parts) < 5:
                    cancel_sale_and_payments(parts[1])
                    break

                fiscal_ok, message, orderid, data_fiscal, hora_fiscal = ret.data.split('\0')

                # Fiscal OK - Erro na DANFE - Venda conluida sem volta - Apenas informa o usuário
                if fiscal_ok == "True":
                    if not is_kiosk:
                        show_message_dialog(pos_id, "$INFORMATION", "$ERROR_PRINT_NFE|%s" % msg.data)
                        close_asynch_dialog(pos_id, dlgid) if dlgid else None
                        if float(res["totalAmount"]) > 0:
                            doOpenDrawer(pos_id)

                    # Confirm Tender - Set Order to PAID
                    tender_and_finalize()
                    break

                # Erro Fiscal (Falha ao enviar para SEFAZ) - PopUp (Tentar Novamente ou Cancelar)
                try_again_response = 1
                if not is_kiosk:
                    try_again_response = show_message_options_dialog(pos_id, "Tentar Novamente|Cancelar", "$ERROR", "$ERROR_SEND_NFE|%s" % message)

                # 0 -> Tentar Novamente / 1 -> Cancelar
                if try_again_response != 0:
                    cancel_sale_and_payments("Cancelamento solicitado pelo Usuário")
                    break
                elif is_kiosk:
                    show_message_dialog(pos_id, message="Erro processando dados fiscais. Tentando novamente...")
                    time.sleep(1)
                    try_again_response += 1
            except Exception:
                logger.exception("Erro processando CUPOM Fiscal")
                cancel_sale_and_payments("Erro processando CUPOM Fiscal")
                break
            finally:
                close_asynch_dialog(pos_id, dlgid) if dlgid else None
                time.sleep(0.2)
                logger.debug("--- doTender after PROCESSING_FISCAL_DATA ---")

        if is_sangria_enable() and pod_type != "TT":
            do_set_drawer_status(pos_id, get_drawer_amount(pos_id, period, session), xml_order.get("state"), get_custom(model, "sangria_level_1_alert"))

        print_tef_receipts(pos_id)
        
        if _is_delivery_sale_type(xml_order):
            create_delivery_manual_order_json(pos_ot, xml_order)
            print_original_delivery(pos_id, order_id)

    except DeliveryCouponPrintError as ex:
        sys_log_exception(ex.message)
    except OrderTakerException as ex:
        show_message_dialog(pos_id, "$ERROR", "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()))
    finally:
        with lock_tender:
            tendering[int(pos_id)] = False
            close_asynch_dialog(pos_id, dlgid) if dlgid else None

    logger.debug("--- doTender END ---")


def _is_delivery_sale_type(xml_order):
    return xml_order.get("saleType", "") == "3"


def print_tef_receipts(pos_id):
    try:
        model = get_model(pos_id)
        tenders = get_current_order(model).findall("TenderHistory/Tender")
        electronic_tenders = []
        for tender in tenders:
            if int(tender.get("tenderType")) in (1, 2):
                electronic_tenders.append(tender)

        if len(electronic_tenders) == 0:
            return

        current_printer = get_used_service(model, "printer")
        if print_merchant_receipt:
            for tender in electronic_tenders:
                receipt = base64.b64decode(json.loads(tender.get("tenderDetail"))["ReceiptMerchant"])
                receipt += PAPER_EMPTY_SPACE + PAPER_PART_CUT
                mbcontext.MB_EasySendMessage(current_printer,
                                             TK_PRN_PRINT,
                                             format=FM_PARAM,
                                             data=receipt,
                                             timeout=30000000)

        response = show_confirmation(pos_id, "$WANT_TO_PRINT_CUSTOMER_RECEIPT")
        if not response:
            return

        for tender in electronic_tenders:
            receipt = base64.b64decode(json.loads(tender.get("tenderDetail"))["ReceiptCustomer"])
            receipt += PAPER_EMPTY_SPACE + PAPER_PART_CUT
            mbcontext.MB_EasySendMessage(current_printer,
                                         TK_PRN_PRINT,
                                         format=FM_PARAM,
                                         data=receipt,
                                         timeout=30000000)
    except Exception as _:
        logger.exception("Error printing TEF receipts")


def _get_tender_type(pos_id, tender_type_id):
    all_tender_types = get_tender_types()
    tender_types = [tender for tender in all_tender_types if (tender["parentId"] is not None and tender["parentId"] == int(tender_type_id))]
    if len(tender_types) != 0:
        if len(tender_types) == 1:
            return tender_types[0]
        else:
            options = [tender["descr"] for tender in tender_types]
            selected_option = show_filtered_list_box_dialog(pos_id, options, "$SELECT_PAYMENT_TYPE", mask="NOFILTER")
            if selected_option is None:
                return None

            tender_type_id = tender_types[selected_option]["id"]
    else:
        return [tender for tender in all_tender_types if tender["id"] == int(tender_type_id)][0]

    return [tender for tender in tender_types if tender["id"] == tender_type_id][0]


@action
def doRecallNext(pos_id, screen_number="", order_id="", totalize=False, originator_pos_id=None, order_business_period=None, *args):
    logger.debug("Recall pedido - Order %s - PosId %s" % (order_id, pos_id))

    global lock_recall
    global recalling
    with lock_recall:
        if order_id in recalling:
            show_messagebox(pos_id, message="Pedido número %s já recuperado em outro caixa" % order_id, icon="critical")
            sys_log_error("PosId {} - Order {} - Already in Recall".format(pos_id, order_id))
            logger.debug("Recall sendo recuperado em outro caixa - Order %s - PosId %s" % (order_id, pos_id))
            return
        else:
            recalling.append(order_id)

    try:
        model = get_model(pos_id)

        # TODO: Read this configuration from loader
        closing_day = False
        if not closing_day and order_business_period is not None:
            current_business_day = datetime.strptime(get_business_period(model), "%Y%m%d")
            order_business_period = datetime.strptime(order_business_period, "%Y%m%d")

            if current_business_day > order_business_period:
                if show_confirmation(pos_id, message="Pedido salvo em dia de negócio anterior ao atual. Recupere-o em outro caixa ou apague-o.", buttons="Apagar|$CANCEL"):
                    try:
                        do_recall_order(pos_id, order_id)
                        void_order(pos_id, void_reason=6)

                        return True
                    except BaseException as _:
                        sys_log_exception("Erro ao apagar pedido")
                        logger.debug("Erro void order recall pedido - Order %s - PosId %s" % (order_id, pos_id))
                        show_messagebox(pos_id, message="Erro ao tentar apagar pedido", icon="error")
                return

            if order_business_period > current_business_day:
                show_messagebox(pos_id, "Pedido foi salvo em um dia de negócio posterior ao atual. Por favor abra um novo dia de negócio.")
                logger.debug("Recall pedido foi salvo em um dia de negócio posterior ao atual - Order %s - PosId %s" % (order_id, pos_id))
                return

            check_operator_logged(pos_id, model=model, can_be_blocked=False)
            check_current_order(pos_id, model=model, need_order=False)

        period = get_business_period(model)
        session = get_operator_session(model)

        if is_sangria_enable() and do_set_drawer_status(pos_id, get_drawer_amount(pos_id, period, session)):
            logger.debug("Recall pedido sangria - Order %s - PosId %s" % (order_id, pos_id))
            return

        try:
            pod_function = get_posfunction(model) if get_podtype(model) in ("DT", "FC") else get_podtype(model)
            posot = get_posot(model)

            do_recall_order(pos_id, order_id, originator_pos_id)
            logger.debug("Pedido Totalizado - Order %s" % order_id)
            time.sleep(0.1)  # Kernel delayed time for model update
            model = get_model(pos_id)

            try:
                if _is_delivery_order(model):
                    print_original_delivery(pos_id, order_id)
            except Exception as _:
                logger.error("Error printing partner delivery coupon for order {}".format(str(order_id)))

            request_customer_info = "onRecall" in customer_info_config[int(pos_id)]['document'] or "onRecall" in customer_info_config[int(pos_id)]['name']

            if totalize == "true" and get_nf_type(pos_id) != "PAF" and request_customer_info:
                get_document = "onRecall" in customer_info_config[int(pos_id)]['document']
                get_name = "onRecall" in customer_info_config[int(pos_id)]['name']
                fill_customer_properties(model, pod_function, pos_id, posot, get_doc=get_document, get_name=get_name)

            if totalize == 'true':
                doTotal(pos_id, screen_number, None, True, *args)

            logger.debug("Recall finalizado - Order %s - PosId %s" % (order_id, pos_id))

            return True

        except StopAction as _:
            raise

        except OrderTakerException as e:
            if get_nf_type(pos_id) == "PAF":
                show_info_message(pos_id, "Erro ao recuperar pedido: %s" % (e.getErrorDescr()), msgtype="critical")
                show_messagebox(pos_id, message="Erro ao recuperar pedido: %s" % (e.getErrorDescr()), icon="critical")
                logger.debug("Erro ao recuperar pedido - Order %s - PosId %s - %s" % (order_id, pos_id,
                                                                                      e.getErrorDescr()))
            else:
                show_messagebox(pos_id, message="Pedido número %s já recuperado em outro caixa" % order_id)
                logger.debug("Recall pedido já recuperado em outro caixa - Order %s - PosId %s" % (order_id, pos_id))

            sys_log_info("$ERROR_CODE_INFO|%d|%s - POS %s" % (e.getErrorCode(), e.getErrorDescr(), pos_id))
        except Exception as ex:
            sys_log_exception("Erro recuperando pedido - %s" % str(ex))
            logger.debug("Recall error - Order %s - PosId %s" % (order_id, pos_id))

    finally:
        with lock_recall:
            if order_id in recalling:
                recalling.remove(order_id)


def _is_delivery_order(model):
    order = model.find("CurrentOrder/Order")
    if not order:
        return False

    return order.find("CustomOrderProperties/OrderProperty[@key='REMOTE_ORDER_ID']") is not None


@action
def activateUser(posid, *args):
    current_op = get_current_operator(get_model(posid))
    current_id = current_op.get("id") if current_op else None
    check_business_day(posid, can_be_blocked=False)

    msg = send_message("POS%d" % int(posid), TK_POS_LISTUSERS, FM_PARAM, posid)
    if msg.token == TK_SYS_NAK:
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        return

    xml = eTree.XML(msg.data)
    opened_users = [tag for tag in xml.findall("User") if (not tag.get("closeTime")) and (tag.get("id") != current_id)]
    if not opened_users:
        return

    opened_users.sort(key=lambda tag: tag.get("id"))
    options = ["%s - %s" % (tag.get("id"), (tag.get("name")).encode("utf-8")) for tag in opened_users]
    index = show_listbox(posid, options, message="Selecione um operador para ativar")
    if index is None:
        return

    userid = opened_users[index].get("id")
    username = (opened_users[index].get("name")).encode("utf-8")
    passwd = show_keyboard(posid, message="$ENTER_PASSWORD|%s" % userid, title="$USER_AUTHENTICATION", is_password=True, numpad=True)
    if passwd is None:
        return
    if not show_confirmation(posid, message="Confirme operador ativo\%s - %s" % (userid, username)):
        return

    try:
        userinfo = authenticate_user(userid, passwd)
    except AuthenticationFailed as ex:
        show_info_message(posid, "$%s" % ex.message, msgtype="error")
        return

    longusername = userinfo["LongName"]
    msg = send_message("POS%d" % int(posid), TK_POS_USERLOGIN, FM_PARAM, "%s\0%s\0%s" % (posid, userid, longusername))
    if msg.token == TK_SYS_NAK:
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        return
    show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")


@action
def doOpenDrawer(posid, check_oper="true", *args):
    def thread_open_drawer(drawer):
        try:
            send_message(drawer.get("name"), TK_CDRAWER_OPEN)
            show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
        except MBException:
            show_info_message(posid, "$ERROR_OPEN_DRAWER", msgtype="warning")

    model = get_model(posid)
    if check_oper == "true":
        check_operator_logged(posid, model=model, can_be_blocked=False)

    drawers = model.findall("CashDrawer")
    for drawer in drawers:
        from threading import Thread
        open_drawer_thread = Thread(target=thread_open_drawer, args=(drawer,))
        open_drawer_thread.daemon = True
        open_drawer_thread.start()


@action
def doChangePrinter(posid, *args):
    model = get_model(posid)
    current_printer = get_used_service(model, "printer")
    if not current_printer:
        show_info_message(posid, "$NO_CONFIGURED_PRINTERS", msgtype="warning")
        return
    options = get_used_service(model, "printer", get_all=True)
    index = show_listbox(posid, options, defvalue=options.index(current_printer))
    if index is None:
        return
    printername = options[index]
    msg = send_message("POS%d" % int(posid), TK_POS_SETDEFSERVICE, FM_PARAM, "%s\0printer\0%s" % (posid, printername))
    if msg.token == TK_SYS_ACK:
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
    else:
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")


@action
def notImplemented(posid, *args):
    show_messagebox(posid, "$FEATURE_NOT_IMPLEMENTED_YET")


@action
def dayOpenReport(posid, store_wide="false", *args):
    model = get_model(posid)
    period = get_business_period(model)
    if period is None:
        return
    if not is_valid_date(period):
        show_messagebox(posid, message="$INVALID_DATE", icon="error")
        return
    menu_manager_user = get_menu_user_logged.get_menu_manager_authenticated_user()
    print_report(posid, model, True, "dayOpen_report", posid, period, store_wide, menu_manager_user)


@action
def requestQuantity(posid, sale_line='', *args):
    while True:
        amount = show_keyboard(posid, "Digite a quantidade:", title="", mask="INTEGER", numpad=True)
        if amount and '.' in amount:
            continue

        if amount not in (None, "", "NaN"):
            if int(amount) > 99:
                show_messagebox(posid, message="Quantidade máxima de itens excedida", icon="info")
                amount = None

            model = get_model(posid)
            if has_current_order(model):
                doChangeQuantity(posid, sale_line, amount, 'true')

        return amount or ""


@action
def storewideRestart(pos_id, *args):
    selected_pos_id = show_keyboard(pos_id, "$TYPE_REPORT_POS", title="", defvalue="0", mask="INTEGER", numpad=True)

    if selected_pos_id in (None, "", "."):
        return
    if selected_pos_id == "0":
        if not show_confirmation(pos_id, message="$CONFIRM_STOREWIDE_RESTART"):
            return

        show_messagebox(pos_id, "$PLEASE_WAIT_ALL_NODES_RESTART")
        mbcontext.MB_SendMessage(mbcontext.hv_service, TK_HV_GLOBALRESTART)

    if int(selected_pos_id) not in poslist:
        show_info_message(pos_id, "Numero de POS inválido", msgtype="critical")
        return
    confirm = show_confirmation(pos_id,
                                message="Você tem certeza que deseja fechar o POS%s?\n OBS: Essa operação pode demorar alguns segundos" % selected_pos_id,
                                title="Alerta",
                                buttons="$OK|$CANCEL")
    if not confirm:
        return

    try:
        msg = mbcontext.MB_EasySendMessage("Maintenance%02d" % int(selected_pos_id), TK_MAINTENANCE_RESTART_REQUEST, format=FM_PARAM, data=pos_id, timeout=10000 * 1000)
        if msg.token == TK_SYS_NAK:
            show_messagebox(pos_id, "%s" % msg.data)
    except Exception as ex:
        if "NOTFOUND" in ex.message:
            if int(selected_pos_id) == 0:
                pos_msg = "servidor."
            else:
                pos_msg = "POS{}.".format(selected_pos_id)
            show_messagebox(pos_id, "Componente de manutenção não encontrado para o {}".format(pos_msg))
        else:
            show_messagebox(pos_id, "Erro reiniciando POS{}.\n{}".format(selected_pos_id, ex.message))


@action
def doKill(pos_id, show_message=True):
    if show_message:
        confirm = show_confirmation(pos_id,
                                    message="Você tem certeza que deseja fechar o sistema?\n OBS: Essa operação pode demorar alguns segundos",
                                    title="Alerta",
                                    buttons="$OK|$CANCEL")
        if not confirm:
            return

    try:
        msg = mbcontext.MB_EasySendMessage("Maintenance%02d" % int(pos_id), TK_MAINTENANCE_TERMINATE_REQUEST, format=FM_PARAM, data=pos_id, timeout=10000 * 1000)
        if msg.token == TK_SYS_NAK:
            show_messagebox(pos_id, "%s" % msg.data)
    except Exception as ex:
        if "NOTFOUND" in ex.message:
            show_messagebox(pos_id, "Componente de manutenção não encontrado para o POS{}".format(pos_id))
        else:
            show_messagebox(pos_id, "Erro ao tentar fechar o sistema: {}".format(ex.message))


@action
def doOrderPicture(posid, orderid, *args):
    try:
        picture = OrderTaker(posid, mbcontext).orderPicture(orderid=orderid)
        order = eTree.tostring(eTree.XML(picture).find("Order"), encoding="UTF-8")
        return (FM_XML, order)
    except:
        sys_log_exception("Error taking order picture for order %s" % orderid)
        return ""


def get_timestamp():
    """Return the last update timestamp if available."""
    timestamp = None
    try:
        with open("../genesis/.genpkg_timestamp", "r") as f:
            timestamp = f.read()
    except:
        pass

    return timestamp


def get_install_date():
    """Retrieve install date: the creation date of the current working dir <install_dir>/bin."""
    t = time.strptime(time.ctime(os.path.getctime(os.getcwd())))
    return "%04d-%02d-%02d" % (t.tm_year, t.tm_mon, t.tm_mday)


def day_is_closed_in_all_pos(source_pos_id):
    opened_pos = []

    for pos_id in poslist:
        model = get_model(pos_id)
        if sysactions.get_model(pos_id).find("WorkingMode").get("usrCtrlType") == "QSR":
            if sysactions.get_cfg(pos_id).find_values("saleType") == ["DL"]:
                from table_actions import get_delivery_stored_orders
                delivery_stored_orders = json.loads(get_delivery_stored_orders())
                if delivery_stored_orders:
                    for order in delivery_stored_orders:
                        if order['businessPeriod'] == get_business_period(model):
                            show_messagebox(source_pos_id, "$HAS_DELIVERY_ORDERS_IN_PROGRESS")
                            return False
            else:
                if has_current_order(model):
                    show_messagebox(source_pos_id, "$THERE_IS_AN_OPENED_ORDER_ON_POS|{}".format(pos_id))
                    return False

        elif is_day_opened(model):
            opened_pos.append(pos_id)

    if len(opened_pos) > 0:
        show_messagebox(source_pos_id, "$NEED_TO_CLOSE_DAY_IN_ALL_POS|{}".format(opened_pos))
        return False

    return True


@action
def doCheckUpdates(posid, show_msg="yes", *args):
    if not day_is_closed_in_all_pos(posid):
        return

    try:
        # List available update packages on GenesisServer
        msg = send_message("GenesisServer", TK_GENESIS_LISTPKGS, FM_STRING, "updates")
        if msg.token == TK_SYS_NAK:
            show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
            return
    except MBException as e:
        if e.errorcode != SE_NOTFOUND:
            sys_log_exception("Error checking for updates!")
            show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        return

    # Parse the XML response
    xml = eTree.XML(msg.data)
    qty = len(xml.findall("Package"))

    if show_msg == "yes":
        if qty == 0:
            show_messagebox(posid, message="$NO_UPDATES_FOUND")
            return
        if qty == 1 and not show_confirmation(posid, message="$CONFIRM_SINGLE_UPDATE"):
                return
        if qty > 1 and not show_confirmation(posid, message="$CONFIRM_MULTIPLE_UPDATES|%d" % qty):
                return

    # Begin the update process
    message = "$APPLYING_SINGLE_UPDATE" if qty == 1 else "$APPLYING_MULTIPLE_UPDATES"
    dlgid = show_messagebox(posid, message=message, buttons="", asynch=True, timeout=720000)
    pkgs = [str(pkg.get("path")) for pkg in xml.findall("Package")]

    try:
        # Request the update (12 minutes timeout)
        msg = send_message("GenesisServer", TK_GENESIS_APPLYUPDATE, FM_PARAM, '\0'.join(pkgs), timeout=720000000)
    finally:
        close_asynch_dialog(posid, dlgid)

    if msg.token == TK_SYS_NAK:
        show_messagebox(posid, message="$OPERATION_FAILED", icon="error")
        return

    # register installed version
    timestamp = get_timestamp()
    install_date = get_install_date()

    try:
        updmsg = mbcontext.MB_EasySendMessage("GAECHANNEL", TK_SYS_CHECKFORUPDATES, format=FM_STRING, data=json.dumps({"timestamp": timestamp, "installDate": install_date}), timeout=5000000)
        sys_log_debug("[AutoUpd] TK_SYS_CHECKFORUPDATES: %s" % updmsg.data)
    except:
        sys_log_exception("Failed to acquire updates")

    show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")

    if show_msg == "yes":
        if not show_confirmation(posid, icon="success", message="$SYSTEM_UPDATE_SUCCESS", timeout=300000):
            return

    # Store Wide Restart
    show_info_message(posid, "$PLEASE_WAIT_ALL_NODES_RESTART", msgtype="info")
    mbcontext.MB_SendMessage(mbcontext.hv_service, TK_HV_GLOBALRESTART)
    return True


@action
def doSetCustomerName(pos_id):
    model = get_model(pos_id)
    pod_function = get_posfunction(model)
    pos_ot = get_posot(model)
    fill_customer_properties(model, pod_function, pos_id, pos_ot, get_name=True, force=True)


@action
def closedOrders(pos_id, request_authorization="true", allpos="false", requestdate="false", danfe_type="", *args):
    model = get_model(pos_id)
    pos_ot = get_posot(model)

    try:
        if request_authorization == "true" and \
                not get_authorization(pos_id, min_level=UserLevels.MANAGER.value, model=model)[0]:
                return False

        if requestdate.lower() == "true":
            date_to_find = show_keyboard(pos_id, "$TYPE_DATE", title="", mask="DATE", numpad=True)
            if date_to_find is None:
                return False
            if not is_valid_date(date_to_find):
                show_messagebox(pos_id, message="$INVALID_DATE", icon="error")
                return False
            tmp_date = time.strptime(date_to_find, "%Y%m%d")
        else:
            tmp_date = time.localtime()

        originator_id = ""
        if allpos.lower() != "true":
            originator_id = "POS%04d" % int(pos_id)

        since_date = time.strftime("%Y-%m-%dT00:00:00", tmp_date)
        until_date = time.strftime("%Y-%m-%dT23:59:59", tmp_date)

        orders = pos_ot.listOrders(
            state="PAID",
            since=since_date,
            until=until_date,
            showTenders=True,
            instnbr=int(pos_id) if allpos.lower() != "true" else "",
            originatorid=originator_id)

        if not orders:
            show_messagebox(pos_id, message="$NO_ORDERS_FOUND", icon="warning")
            return False

        orders = sorted(orders, key=lambda x: map(int, re.findall('\d+', x['custom_properties']['FISCALIZATION_DATE'] if 'custom_properties' in x else x['createdAt'])), reverse=True)

        base_url = "/mwapp/services/PosController/POS{}/?token=TK_POS_EXECUTEACTION&format=2&isBase64=true&payload="
        base_url = base_url.format(int(pos_id))

        preview_data = []
        for order in orders:
            order_id = order["orderId"]
            order_pos_id = int(order["originatorId"][3:])
            tenders = order["tender_history"]
            order_gross = sum([float(x.get("tenderAmount")) - float(x.get("changeAmount") or '0.0') for x in tenders])
            order_type = order["podType"]

            properties = order["custom_properties"]
            order_date = properties['FISCALIZATION_DATE'] if "FISCALIZATION_DATE" in properties else None
            if order_date is None:
                order_date = order.get("createdAt")

            order_date = convert_from_utf_to_localtime(datetime.strptime(order_date, "%Y-%m-%dT%H:%M:%S"))
            order_time = order_date.strftime('%H:%M')

            partner = ""
            if 'custom_properties' in order:
                partner = properties["PARTNER"] if "PARTNER" in properties else ""

            description = "{}{:02} #{:04} {} R${:.2f}"
            description = description.format(order_type, order_pos_id, int(order_id) % 10000, order_time, order_gross)
            if partner != "":
                short_reference = properties["SHORT_REFERENCE"] if "SHORT_REFERENCE" in properties else order_id
                if partner.upper() == "APP":
                    description += " APP-{}".format(short_reference)
                else:
                    description += " DLY-{}".format(short_reference)
            else:
                table_id = properties["TABLE_ID"] if "TABLE_ID" in properties else ""
                if table_id != "":
                    if "TAB-" in table_id:
                        description += " TAB-{:04}".format(int(table_id.replace("TAB-", "")))
                    else:
                        description += " MESA-{:03}".format(int(table_id))

            payload = base64.b64encode("\0".join(("doOrderPicture", pos_id, order_id)))
            url = base_url + payload
            preview_data.append((order_id, description, url))

        if not preview_data:
            show_messagebox(pos_id, message="$NO_ORDERS_FOUND", icon="warning")
            return

        while True:
            selected = show_order_preview(pos_id,
                                          preview_data,
                                          "$REPRINT_ORDER_SELECT",
                                          buttons="CANCEL|PICKLIST|COUPON",
                                          onthefly=True)
            if (selected is None) or (selected[0] == "0"):
                return

            order_type = filter(lambda x: x["orderId"] == selected[1], orders)[0]["podType"]
            selected_order = filter(lambda x: x["orderId"] == selected[1], orders)[0]

            can_reprint_pod_types = get_storewide_config("Store.CanReprintPodTypes", defval="FC;DS;KK;DT;OT;TT;DL;TS").split(";")
            reprint_orders_i18n = "$REPRINT_ORDERS"
            if order_type not in can_reprint_pod_types or get_nf_type(pos_id) == "PAF":
                show_messagebox(pos_id, "$REPRINT_FORBIDDEN", title=reprint_orders_i18n)
                continue

            if (selected is None) or (selected[0] == "1"):
                try:
                    model = sysactions.get_model(pos_id)
                    order_pict = pos_ot.orderPicture("", selected[1])
                    data = sysactions.print_report(pos_id, model, False, picklist_reprint_type, order_pict)
                    if data is True:
                        show_messagebox(pos_id, message="$OPERATION_SUCCEEDED", icon="success")
                    else:
                        show_messagebox(pos_id, "$OPERATION_FAILURE", title=reprint_orders_i18n, icon="error", buttons="$OK")
                except Exception as ex:
                    show_messagebox(pos_id, "$ERROR_REPRINT_PICKLIST|{}".format(ex.message), title=reprint_orders_i18n, icon="error", buttons="$OK")
                continue

            orderid = selected[1]
            try:
                if danfe_type == "":
                    data = pos_id + '\0' + orderid
                else:
                    data = '\0'.join([pos_id, orderid, danfe_type])
                msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_REPRINT, format=FM_PARAM, data=data)
                if not msg.token == TK_SYS_ACK:
                    if msg.data and "False" not in msg.data:
                        error_msg = "$ERROR_REPRINT_NFE|{}".format(msg.data)
                    else:
                        error_msg = "$OPERATION_FAILURE"
                    show_messagebox(pos_id, message=error_msg, icon="error")
                else:
                    try:
                        current_printer = get_used_service(model, "printer")
                        msg = mbcontext.MB_EasySendMessage(current_printer, TK_PRN_PRINT, format=FM_PARAM, data=msg.data, timeout=10000000)  # type: MBMessage
                        if msg.token != TK_SYS_ACK:
                            show_messagebox(pos_id, "$ERROR_REPRINT_NFE|%s" % msg.data, title=reprint_orders_i18n, icon="error", buttons="$OK")
                        else:
                            donation_value = _get_custom_property_value_by_key("DONATION_VALUE", selected_order["custom_properties"])
                            if donation_value is not None:
                                donation_value = float(donation_value.replace(",", "."))
                                donation_value = format(donation_value, '.2f').replace(",", ".")
                                customer_name = _get_custom_property_value_by_key("CUSTOMER_NAME", selected_order["custom_properties"]) or ""
                                _do_print_donation(model, pos_id, orderid, customer_name, donation_value, round_donation_institution, round_donation_cnpj, round_donation_site)

                            show_messagebox(pos_id, message="$OPERATION_SUCCEEDED", icon="success")
                    except Exception as ex:
                        show_messagebox(pos_id, "$ERROR_REPRINT_NFE|%s" % repr(ex), title=reprint_orders_i18n, icon="error", buttons="$OK")
            except Exception as ex:
                sys_log_exception("Could not print Receipt for voided order - Error: %s" % str(ex))

    except OrderTakerException as ex:
        show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")


@action
def do_preview_order(pos_id, order_id):
    model = get_model(pos_id)
    preview_data = []
    pos_ot = get_posot(model)
    order_pict = pos_ot.orderPicture(orderid=order_id)
    order = eTree.XML(order_pict).find("Order")
    order_pos_id = int(order.attrib["originatorId"][3:])
    order_gross = float(order.attrib["totalGross"])
    order_created_date = datetime.strptime(str(order.attrib["createdAt"]), "%Y-%m-%dT%H:%M:%S.%f")
    order_timestamp = order_created_date.strftime('%H:%M')
    order_type = str(order.attrib["podType"])

    description = "{}{:02} #{:04} {} R${:.2f}".format(order_type, order_pos_id, int(order_id) % 10000, order_timestamp, order_gross)

    buttons = "CANCEL"
    if order.find(".//OrderProperty[@key='PARTNER']") is not None:
        buttons = "CANCEL|PRINT_DELIVERY"
        partner = order.find(".//OrderProperty[@key='PARTNER']").get("value").upper()
        if partner != "":
            description += " - DLV [{}]".format(partner)

    base_url = "/mwapp/services/PosController/POS%d/?token=TK_POS_EXECUTEACTION&format=2&isBase64=true&payload=" % int(pos_id)
    payload = base64.b64encode("\0".join(("doOrderPicture", pos_id, order_id)))
    url = base_url + payload
    preview_data.append((order_id, description, url))

    ret = show_order_preview(pos_id, preview_data, "Pedido %s" % order_id, buttons=buttons, onthefly=True)
    if ret and len(ret) > 1:
        print_original_delivery(pos_id, ret[1])


@action
def doReprintTef(pos_id, *args):
    """
    Reprints last TEF coupon paid in this POS
    """
    wait_dlg_id = show_messagebox(pos_id, "$PLEASE_WAIT", "$REPRINTING_RECEIPT", buttons="", asynch=True)
    try:
        model = get_model(pos_id)
        check_operator_logged(pos_id, model=model, can_be_blocked=False)
        check_current_order(pos_id, model, need_order=False)
        drv = persistence.Driver()
        conn = None
        try:
            conn = drv.open(mbcontext, service_name="FiscalPersistence")
            query = """SELECT p1.OrderId, p1.TenderSeqId, p1.ReceiptMerchant
                FROM fiscal.PaymentData p1
                INNER JOIN (
                    SELECT MAX(OrderId) OrderId
                    FROM fiscal.PaymentData
                ) p2 ON p1.OrderId = p2.OrderId
                ORDER BY p1.TenderSeqId desc"""
            cursor = conn.select(query)
            printed = False
            for line in cursor:
                if line.get_entry("ReceiptMerchant"):
                    print_text(pos_id, model, line.get_entry("ReceiptMerchant"))
                    printed = True
                    break
            if printed:
                show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")
            else:
                show_messagebox(pos_id, message="Não há comprovante para ser impresso", icon="warning")
        finally:
            if conn:
                conn.close()
    except Exception as ex:
        show_messagebox(pos_id, message="Impossivel imprimir ultimo cupom: %s" % str(ex), icon="error")
        sys_log_exception("Could not print Receipt for order")
    finally:
        close_asynch_dialog(pos_id, wait_dlg_id)


def _do_print_donation(model, pos_id, order_id, customer_name, donation_value, donation_institution, donation_cnpj, donation_site):
    try:
        params = '\x00'.join(map(str, [pos_id, order_id, customer_name, donation_value, donation_institution, donation_cnpj, donation_site]))
        msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_PRINT_DONATION_COUPON, FM_PARAM, params)
        if msg.token != TK_SYS_ACK:
            raise Exception(msg.data)
        print_text(pos_id, model, msg.data)
    except Exception as ex:
        show_messagebox(pos_id, (sysactions.translate_message(model, "PRINTER_DONATION_ERROR", ex)))
        msg = "Could not print donation coupon"
        logger.exception(msg)
        sys_log_exception(msg)


@action
def doReprintOrder(pos_id, order_id, *args):
    """
    Reprints PICKLIST and Fiscal Receipt for specific order
    """
    model = get_model(pos_id)
    posot = get_posot(model)
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext, str(pos_id))
        conn.query("DELETE FROM CurrentOrderItem WHERE OrderId = {}".format(order_id))
    except Exception as _:
        logger.exception("Erro limpando Current Order DB")
    finally:
        if conn:
            conn.close()

    _reprint_fiscal_coupon(model, order_id, pos_id)

    try:
        order_pict = posot.orderPicture("", order_id)
        # fix order pict to print picklist correctly
        dict_list = []
        order = eTree.XML(order_pict)

        for line in order.findall("Order/SaleLine"):
            line_number = line.get('lineNumber')
            item_id = line.get('itemId')
            part_code = line.get('partCode')
            level = line.get('level')
            get_updated_sale_line_defaults(dict_list, order_id, int(line_number), item_id, part_code, line.get('qty'), int(level), get_podtype(model), model=model)
            for corrected_line in dict_list:
                corrected_line_dict = json.loads(corrected_line)
                if corrected_line_dict['line_number'] == line_number and \
                   corrected_line_dict['item_id'] == item_id and \
                   corrected_line_dict['part_code'] == part_code and \
                   corrected_line_dict['level'] == level:
                    line_orig_qty = line.get('qty')
                    line.set('addedQty', str(max(0, float(line_orig_qty) - float(corrected_line_dict['default_qty']))))
                    line.set('defaultQty', corrected_line_dict['default_qty'])
        data = sysactions.print_report(pos_id, model, False, picklist_reprint_type, eTree.tostring(order))
        if not data:
            sys_log_error("Exception reprinting Picklist for order %s" % order_id)
    except Exception as _:
        sys_log_exception("Exception reprinting Picklist for order %s" % order_id)


def _reprint_fiscal_coupon(model, order_id, pos_id):
    try:
        msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_REPRINT, format=FM_PARAM,
                                           data=str('\x00'.join(map(str, [pos_id, order_id]))))
        if not msg.token == TK_SYS_ACK:
            sys_log_error("Could not recreate Fiscal Coupon for order %s - Error: %s" % (order_id, str(msg.data)))
            raise StopAction()
        else:
            current_printer = get_used_service(model, "printer")
            msg = mbcontext.MB_EasySendMessage(current_printer, TK_PRN_PRINT, format=FM_PARAM, data=msg.data,
                                               timeout=10000000)  # type: MBMessage
            if msg.token != TK_SYS_ACK:
                sys_log_error("Could not reprint Fiscal Coupon for order %s - Error: %s" % (order_id, str(msg.data)))
                raise StopAction()
    except Exception as _:
        sys_log_exception("Exception recreating Fiscal Coupon for order %s" % order_id)
        raise StopAction()


@action
def doChangeQuantity(posid, line_numbers, qty, is_absolute='false'):
    model = get_model(posid)
    posot = get_posot(model)
    pod_function = get_posfunction(model) if get_podtype(model) in ("DT", "FC") else get_podtype(model)
    is_absolute = (is_absolute or 'false').lower() == 'true'

    if set_product_quantity_pre and pod_function != "TT":
        set_custom(posid, "pre_quantity", qty)
        return True

    check_current_order(posid, model=model, need_order=True)
    if not line_numbers:
        return True

    line_numbers = line_numbers.split('|')
    try:
        all_lines = get_current_order(model).findall("SaleLine")
        intqty = int(qty or 0)
        to_void = []
        # change only first line
        lines = filter(lambda x: x is not None, [line if line.get("level") == "0" and line.get("lineNumber") in line_numbers else None for line in all_lines])
        excess = sum([int(x.get("qty")) for x in lines[1:]]) if is_absolute else 0

        for i, line in enumerate(line_numbers):
            lnbr = line_numbers[i]
            sale_line = filter(lambda x: x is not None, [line if line.get("level") == "0" and line.get("lineNumber") == lnbr else None for line in all_lines])[0]
            found_qty = int(sale_line.get("qty")) if (not is_absolute or i != 0) else 0
            if found_qty == 0 and (not is_absolute or i != 0):
                continue

            qty_to_change = found_qty + intqty - excess
            if qty_to_change == 0 and \
                    pod_function != "TT" and \
                    not get_authorization(posid, min_level=UserLevels.MANAGER.value, model=model, insert_auth=True)[0]:
                    return

            if qty_to_change < 0:
                to_void.append(lnbr)
                excess = 0
                intqty = qty_to_change
            else:
                posot.changeLineItemQty(posid, lnbr, qty_to_change)
                break

        if to_void:
            posot.voidLine(posid, "|".join(to_void))
    except OrderTakerException as ex:
        show_messagebox(posid, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")


@action
def doSetCustomerDocument(pos_id):
    model = get_model(pos_id)
    pod_function = get_posfunction(model)
    pos_ot = get_posot(model)
    fill_customer_properties(model, pod_function, pos_id, pos_ot, get_doc=True, force=True)


@action
def doSearchSatModules(pos_id):
    msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_SEARCH_REQUEST, format=FM_PARAM, data=pos_id)
    model = get_model(pos_id)
    if msg.token == TK_SYS_ACK:
        print_report(pos_id, model, True, "sats_report", pos_id, msg.data)
    else:
        show_info_message(pos_id, "%s" % msg.data, msgtype="error")


@action
def doGetKDSstatus(pos_id):
    msg = mbcontext.MB_EasySendMessage("KdsMonitor", TK_KDSMONITOR_STATUS_REQUEST, format=FM_PARAM, data=pos_id)
    model = get_model(pos_id)
    if msg.token == TK_SYS_ACK:
        print_report(pos_id, model, True, "kds_report", pos_id, msg.data)
    else:
        show_info_message(pos_id, "%s" % msg.data, msgtype="error")


@action
def purge_kds_orders(pos_id):
    try:
        confirmation = show_confirmation(pos_id, message="$KDS_CLEANUP_MESSAGE")
        if not confirmation:
            return

        msg = mbcontext.MB_EasySendMessage("ProductionSystem", TK_PROD_PURGE, format=FM_PARAM, timeout=5 * 1000000)
        if msg.token == TK_SYS_ACK:
            show_messagebox(pos_id, "KDSs limpos com sucesso")
            return
    except Exception as _:
        pass

    show_messagebox(pos_id, "Erro ao limpar KDSs", title="$ERROR", icon="error")


@action
def doGetPrinterStatus(pos_id):
    printer_info_list = []

    # PickList 1 - Hardcoded Name Store
    printer_info = ["Pick List: "]
    printer_ok_message = "Impressora OK"
    printer_not_ok_message = "Falha na Impressora"
    try:
        msg = mbcontext.MB_EasySendMessage("printerpl-1", TK_PRN_GETSTATUS, FM_PARAM, None)
        if msg.data == "0":
            printer_info.append(printer_ok_message)
        else:
            printer_info.append(printer_not_ok_message)
    except:
        printer_info.append(printer_not_ok_message)
    printer_info_list.append(printer_info)

    # PickList 2 - Hardcoded Name for Delivery
    printer_info = ["Delivery : "]
    try:
        msg = mbcontext.MB_EasySendMessage("printerpl-2", TK_PRN_GETSTATUS, FM_PARAM, None)
        if msg.data == "0":
            printer_info.append(printer_ok_message)
        else:
            printer_info.append(printer_not_ok_message)
    except:
        printer_info.append(printer_not_ok_message)
    printer_info_list.append(printer_info)

    # POS Printer Tests
    for pos in sorted(poslist):
        printer_info = ["POS %s   : " % str(pos).zfill(2)]
        try:
            model = get_model(pos)
            pod_function = sysactions.get_cfg(pos).key_value('pod')
            if pod_function in ("OT", "DL"):
                continue

            printer = get_used_service(model, "printer")
            msg = mbcontext.MB_EasySendMessage(printer, TK_PRN_GETSTATUS, FM_PARAM, None)

            if msg.data == "0":
                printer_info.append(printer_ok_message)
            else:
                printer_info.append(printer_not_ok_message)
        except:
            printer_info.append(printer_not_ok_message)
        printer_info_list.append(printer_info)

    model = get_model(pos_id)
    print_report(pos_id, model, True, "printer_report", pos_id, printer_info_list)


@action
def doCheckSEFAZ(pos_id):
    msg = None
    try:
        msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_SEFAZ_CONNECTIVITY, format=FM_PARAM, data="%s" % pos_id, timeout=10000 * 1000)

        if msg.token == TK_SYS_ACK:
            show_info_message(pos_id, msg.data, msgtype="success")
        else:
            show_info_message(pos_id, msg.data, msgtype="error")

    except:
        if msg is not None:
            show_info_message(pos_id, msg.data, msgtype="error")
        else:
            show_info_message(pos_id, "Falha no Componente Fiscal", msgtype="error")


@action
def doGetPigeonVersions(pos_id):
    model = get_model(pos_id)
    not_version_message = "Não Versionado"
    try:
        with open("../data/server/bundles/pigeoncomp/.componentversion") as f:
            componentversion = f.read()
    except Exception as ex:
        logger.debug(pos_id, "Arquivo de versão de componente não encontrado", ex)
        componentversion = not_version_message
    try:
        with open("../data/server/bundles/pigeoncomp/.coreversion") as f:
            coreversion = f.read()
    except Exception as ex:
        logger.debug(pos_id, "Arquivo de versão de core não encontrado")
        coreversion = not_version_message
    try:
        with open("../data/server/bundles/pigeoncomp/.priceversion") as f:
            priceversion = f.read()
    except Exception as ex:
        logger.debug(pos_id, "Arquivo de versão de preço não encontrado")
        priceversion = not_version_message
    print_report(pos_id, model, True, "versions_report", pos_id, "%s;%s;%s" % (componentversion, coreversion, priceversion))


@action
def get_sat_status(pos_id, print_informations='true'):
    msg = mbcontext.MB_EasySendMessage("FiscalWrapper",
                                       TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST,
                                       format=FM_PARAM,
                                       data=pos_id)
    if print_informations.lower() == 'true':
        model = get_model(pos_id)
        if msg.token == TK_SYS_ACK:
            print_report(pos_id, model, True, "sats_op_report", pos_id, msg.data)
        else:
            show_info_message(pos_id, "%s" % msg.data, msgtype="error")
    else:
        return msg.token == TK_SYS_ACK and "ERROR" not in msg.data


@action
def doPurgeStoredOrders(pos_id):
    model = get_model(pos_id)
    podtype = get_podtype(model)
    posot = get_posot(model)

    orders = posot.listOrders(state="STORED", podtype=podtype)

    if not orders:
        if podtype == "DT":
            show_info_message(pos_id, "Não há pedidos salvos no drive", msgtype="warning")
        else:
            show_info_message(pos_id, "Não há pedidos salvos na loja", msgtype="warning")
        return
    try:
        for order in orders:
            order_id = order.get("orderId")
            do_recall_order(pos_id, order_id, check_date=False)
            void_order(pos_id, void_reason=6)
        show_info_message(pos_id, "Pedidos salvos apagados", msgtype="success")
    except Exception as _:
        show_info_message(pos_id, "Erro ao tentar apagar pedidos salvos", msgtype="error")

@action
def doCheckSiTef(pos_id):
    get_model(pos_id)
    date = str(datetime.now())
    data_fiscal = date[:10]
    hora_fiscal = date[11:19]

    try:
        msg = mbcontext.MB_EasySendMessage("Sitef%02d" % int(pos_id), token=TK_SITEF_CONNECTIVITY_TEST, format=FM_PARAM, data="%s;%s;%s" % (str(pos_id), data_fiscal, hora_fiscal))
        if msg.token == TK_SYS_NAK:
            show_info_message(pos_id, "%s" % msg.data, msgtype="error")
        else:
            show_info_message(pos_id, "SITEF OK", msgtype="success")
    except Exception:
        show_info_message(pos_id, "Serviço Sitef%02d não encontrado" % int(pos_id), msgtype="error")


@action
def doReSignXML(posid):
    try:
        msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_RE_SIGN_XML, format=FM_PARAM, data=posid)
        if msg.token == TK_SYS_ACK:
            show_info_message(posid, msg.data, msgtype="success")
        else:
            show_info_message(posid, msg.data, msgtype="error")
    except Exception as _:
        show_info_message(posid, "$ERROR", msgtype="error")


@action
def doFixSefazProtocol(pos_id):
    initial_date = show_keyboard(pos_id, "$TYPE_INITIAL_DATE", title="", mask="DATE", numpad=True)
    if initial_date is None:
        return
    if not is_valid_date(initial_date):
        show_info_message(pos_id, "$INVALID_DATE", msgtype="error")
        return None

    final_date = show_keyboard(pos_id, "$TYPE_INITIAL_DATE", title="", mask="DATE", numpad=True)
    if final_date is None:
        return
    if not is_valid_date(final_date):
        show_info_message(pos_id, "$INVALID_DATE", msgtype="error")
        return None

    try:
        msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_SITUATION, format=FM_PARAM, data='\0'.join([initial_date, final_date]))
        if msg.token == TK_SYS_ACK:
            show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")
        else:
            show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
    except Exception:
        show_info_message(pos_id, "$ERROR", msgtype="error")


@action
def doRecreateXMLFiscal(posid, *args):
    try:
        number = show_keyboard(posid, "Digite o order ID", title="", mask="INTEGER", numpad=True)
        msg = mbcontext.MB_EasySendMessage("Maintenance%02d" % 0, TK_MAINTENANCE_RECREATE_FILE_NUMBER, format=FM_PARAM, data=str(number), timeout=10000 * 1000)
        if msg.token == TK_SYS_NAK:
            show_info_message(posid, "%s" % msg.data, msgtype="error")
            return

        show_info_message(posid, msg.data, msgtype="success")
    except Exception:
        show_info_message(posid, "$ERROR", msgtype="error")


@action
def doReportBKOffice(pos_id, *args):
    data, print_list, json_data = [], [], []

    model = get_model(pos_id)
    pos_ot = get_posot(model)

    period = show_keyboard(pos_id, "$TYPE_DATE", title="", mask="DATE", numpad=True)
    if period is None:
        return
    if not is_valid_date(period):
        show_info_message(pos_id, "$INVALID_DATE", msgtype="error")
        return

    bk_office_date = '-'.join(i for i in [period[:4], period[4:6], period[6:8]])
    query_transfer = "SELECT PosId, OrderId, datetime(DataNota, 'unixepoch') as date, OrderPicture  FROM fiscal.FiscalData WHERE date(datetime(datanota, 'unixepoch')) == '{0}' AND SentToBKOffice <> 1 AND SentToNfce = 1".format(bk_office_date)

    paid_orders = [int(x['orderId']) for x in pos_ot.listOrders(state="PAID")]

    orders = []
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext, service_name="FiscalPersistence")
        cursor = conn.select(query_transfer)
        for row in cursor:
            pos_id, order_id, date_fiscal, order_picture = map(row.get_entry, ("PosId", "OrderId", "date", "OrderPicture"))
            if int(order_id) in paid_orders:
                orders.append((pos_id, order_id, date_fiscal, order_picture))
    finally:
        if conn:
            conn.close()

    separator = "{}".format("*" * 35)

    if len(orders) == 0:
        show_info_message(pos_id, "Nenhum pedido pendente encontrado", msgtype="warning")
        return

    for order in orders:
        pos_id, order_id, date_fiscal, order_picture = order
        json_data.append([order_id, {"order_id": order_id}, order_id])

        order_pict = eTree.XML(base64.b64decode(order_picture))

        if order_pict.tag == 'Orders':
            order_pict = order_pict.find('Order')

        value_order = order_pict.attrib['totalGross']

        date = '/'.join(i for i in [date_fiscal[8:10], date_fiscal[5:7], date_fiscal[:4]])
        hour = date_fiscal.split(" ")[1]
        date_formated = "{} {}".format(date, hour)

        title = "Pedido# {0} - {1}".format(order_id, hour)

        formated_msg = "{}\n" \
                       "\nPedido: {}" \
                       "\nPOS...: {}" \
                       "\nData..: {}" \
                       "\nValor.: R${}" \
                       "\n\n{}"\
            .format(separator, order_id, pos_id, date_formated, value_order, separator)

        data.append([order_id, title, formated_msg])
        print_list.append([order_id, formated_msg])

    index = show_text_preview(pos_id, data, title='Selecione um item:', buttons='Enviar|$PRINT|$CANCEL', defvalue='', onthefly=False, timeout=120000)

    if index is None:
        return

    if int(index[0]) == 0:
        bk_office_response = _sending_order_to_bk_office(index, json_data, pos_id)

    if int(index[0]) == 1:
        try:
            message = None

            for bk_office_response in print_list:
                try:
                    if bk_office_response[0] == index[1]:
                        message = str(bk_office_response[1])
                except Exception as _:
                    continue

            if message is not None:
                printer = "printer%s" % pos_id
                bk_office_response = None

                try:
                    bk_office_response = mbcontext.MB_EasySendMessage(printer, TK_PRN_PRINT, FM_PARAM, message)
                except MBException:
                    time.sleep(0.5)
                    bk_office_response = mbcontext.MB_EasySendMessage(printer, TK_PRN_PRINT, FM_PARAM, message)
                finally:
                    if bk_office_response and bk_office_response.token == TK_SYS_ACK:
                        show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")
                    else:
                        show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
        except Exception as _:
            show_info_message(pos_id, "Erro ao imprimir relatório", msgtype="error")


def _sending_order_to_bk_office(index, json_data, pos_id):
    wait_dlg_id = show_messagebox(pos_id, "$SENDING_ORDER_TO_BKOFFICE", "$WAIT_MESSAGE", buttons="", asynch=True)
    try:
        obj = {}
        for data in json_data:
            try:
                if data[0] == index[1]:
                    obj = data[1]
            except:
                continue

        msg = mbcontext.MB_EasySendMessage("BKOfficeUploader", TK_BKOFFICEUPLOADER_SEND_BKOFFICE_ORDER, data=str(obj),
                                           format=FM_PARAM, timeout=-1)
        msg = eval(msg.data)
        if msg.get('status'):
            show_info_message(pos_id, msg.get('msg').encode('utf-8'), msgtype="success")
        else:
            show_info_message(pos_id, msg.get('msg').encode('utf-8'), msgtype="error")
    except Exception as _:
        show_info_message(pos_id, "Falha de comunicação com o servidor", msgtype="error")
    finally:
        close_asynch_dialog(pos_id, wait_dlg_id)

    return msg


@action
def rupturaItens(pos_id, *args):
    model = get_model(pos_id)
    conn = None
    dialog_timeout = 600000
    try:
        try:
            enabled_data = None
            disabled_data = None

            # get enabled products from ruptura component
            msg = send_message("Ruptura", TK_RUPTURA_GET_ENABLED, FM_STRING, "")
            if msg.token == TK_SYS_NAK:
                raise Exception()
            enabled_data = json.loads(msg.data)
            enabled_ingredients = [{'product_code': k, 'product_name': v} for k, v in enabled_data.iteritems()]

            # get disabled products from ruptura component
            msg = send_message("Ruptura", TK_RUPTURA_GET_DISABLED, FM_STRING, "")
            if msg.token == TK_SYS_NAK:
                raise Exception()
            disabled_data = json.loads(msg.data)
            disabled_ingredients = [{'product_code': k, 'product_name': v} for k, v in disabled_data.iteritems()]
        except BaseException as e:
            logger.exception('[rupturaItens] Exception {}'.format(e))
            show_messagebox(pos_id, "Erro ao obter os dados", "$INFORMATION", buttons="Sair")
            return

        set_custom(pos_id, "RUPTURE_ENABLED_ITEMS", json.dumps(enabled_ingredients))
        set_custom(pos_id, "RUPTURE_DISABLED_ITEMS", json.dumps(disabled_ingredients))
        time.sleep(0.1)
        ret = show_custom_dialog(pos_id, "rupture_items", custom_dlg_timeout=dialog_timeout)
        while ret:
            wait_dlg_id = show_messagebox(pos_id, "Aguarde...", "RUPTURA DE ITENS", buttons="", asynch=True)
            parsed_ret = ret.split("|")
            command = parsed_ret[0]

            if command == "search":
                close_asynch_dialog(pos_id, wait_dlg_id)
                search_filter = show_keyboard(pos_id, "Buscar itens")
                wait_dlg_id = show_messagebox(pos_id, "Aguarde...", "RUPTURA DE ITENS", buttons="", asynch=True)
                if search_filter is not None:
                    search_filter = search_filter.lower()
                    set_custom(pos_id, "RUPTURE_SEARCH_VALUE", search_filter)
                    time.sleep(0.1)  # Kernel delayed time for model update
                close_asynch_dialog(pos_id, wait_dlg_id)
                ret = show_custom_dialog(pos_id, "rupture_items", custom_dlg_timeout=dialog_timeout)
            elif command == "search_clean":
                set_custom(pos_id, "RUPTURE_SEARCH_VALUE", "")
                time.sleep(0.1)  # Kernel delayed time for model update
                close_asynch_dialog(pos_id, wait_dlg_id)
                ret = show_custom_dialog(pos_id, "rupture_items", custom_dlg_timeout=dialog_timeout)
            elif command == "enabled":
                for product in enabled_ingredients:
                    if product["product_code"] == parsed_ret[1]:
                        disabled_ingredients.append(product)
                        enabled_ingredients.remove(product)
                        break
                set_custom(pos_id, "RUPTURE_ENABLED_ITEMS", json.dumps(enabled_ingredients))
                set_custom(pos_id, "RUPTURE_DISABLED_ITEMS", json.dumps(disabled_ingredients))
                time.sleep(0.3)  # Kernel delayed time for model update
                close_asynch_dialog(pos_id, wait_dlg_id)
                ret = show_custom_dialog(pos_id, "rupture_items", custom_dlg_timeout=dialog_timeout)
            elif command == "disabled":
                for product in disabled_ingredients:
                    if product["product_code"] == parsed_ret[1]:
                        enabled_ingredients.append(product)
                        disabled_ingredients.remove(product)
                        break
                set_custom(pos_id, "RUPTURE_ENABLED_ITEMS", json.dumps(enabled_ingredients))
                set_custom(pos_id, "RUPTURE_DISABLED_ITEMS", json.dumps(disabled_ingredients))
                time.sleep(0.3)  # Kernel delayed time for model update
                close_asynch_dialog(pos_id, wait_dlg_id)
                ret = show_custom_dialog(pos_id, "rupture_items", custom_dlg_timeout=dialog_timeout)
            elif command == "save":
                try:
                    user_id = '{} / {}'.format(get_custom(model, 'Last Manager ID'), get_operator_session(model))
                    # save rupture data using ruptura component
                    msg = send_message(
                        "Ruptura",
                        TK_RUPTURA_UPDATE_ITEMS,
                        FM_PARAM,
                        '\0'.join(map(str, [json.dumps({'enabled': enabled_ingredients, 'disabled': disabled_ingredients}), user_id, pos_id]))
                    )
                    if msg.token == TK_SYS_NAK:
                        raise Exception(msg.data)

                except BaseException as e:
                    logger.exception('[rupturaItens] Exception {}'.format(e))
                    show_messagebox(pos_id, "Erro ao salvar os dados", "$INFORMATION", buttons="Sair")
                    return
                finally:
                    close_asynch_dialog(pos_id, wait_dlg_id)
                ret = show_custom_dialog(pos_id, "rupture_items", custom_dlg_timeout=dialog_timeout)
            elif command == "cancel":
                close_asynch_dialog(pos_id, wait_dlg_id)
                set_custom(pos_id, "RUPTURE_SEARCH_VALUE", "")
                break
            else:
                close_asynch_dialog(pos_id, wait_dlg_id)
                break
        return
    finally:
        if conn:
            conn.close()


def check_customer_name(posid, customer_name):
    try:
        msg = send_message('Blacklist', TK_BLACKLIST_CHECK_STRING, FM_PARAM, customer_name)
        if msg.token == TK_SYS_ACK:
            safe_string = (msg.data or 'false').lower() == 'true'
            if not safe_string:
                show_messagebox(posid, message="$BLOCKED_NAME_MESSAGE", title="$BLOCKED_NAME_MESSAGE_TITLE", buttons="$OK")
                return False
    except BaseException as _:
        logger.error("Erro consultando componente Blacklist")
        return True
    return True


def _get_custom_property_value_by_key(property_key, custom_properties):
    filtered_custom_properties = filter(lambda x: x[0] == property_key, custom_properties.items())
    if len(filtered_custom_properties) == 1:
        return filtered_custom_properties[0][1]
    else:
        return None


@action
def doClearOptionItem(pos_id, linenumber="", item_id="", pos_ot=None, clean_all_options="false"):
    model = get_model(pos_id)
    if _is_changing_order(model) and is_table_service(model):
        show_messagebox(pos_id, message="$CANNOT_REMOVE_ITEMS_IN_AN_OPENED_ORDER", icon="error")
        raise StopAction()

    clean_all_options = clean_all_options.lower() == 'true'
    check_current_order(pos_id, model=model, need_order=True)
    if not linenumber or not item_id:
        show_messagebox(pos_id, message="Select the line to clear", icon="error")
        raise StopAction()

    blkopnotify = False
    if pos_ot is None or pos_ot == '':
        pos_ot = get_posot(model)
        pos_ot.blkopnotify = True
        blkopnotify = True

    try:
        item_id_list = [item_id]
        if clean_all_options:
            item_id_list = _get_items_to_clean(item_id, model, pos_ot)

        for item_id in item_id_list:
            pos_ot.clearOption(pos_id, linenumber, "", item_id)

    except ClearOptionException, e:
        sys_log_exception("Could not clear option")
        show_info_message(pos_id, "Error %s" % e, msgtype="error")
    except OrderTakerException, e:
        show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), icon="error")
    finally:
        if blkopnotify:
            pos_ot.blkopnotify = False
            pos_ot.updateOrderProperties(pos_id)


def _get_items_to_clean(item_id, model, pos_ot):
    try:
        item_id_list = []
        order_id = int(model.find("CurrentOrder/Order").get("orderId"))
        order_pict = pos_ot.orderPicture("", order_id)

        current_item_item_id = ".".join(item_id.split(".")[:-1])
        current_item_part_code = item_id.split(".")[-1:][0]
        current_sale_lines = eTree.XML(order_pict).findall(".//SaleLine[@itemId='{}'][@partCode='{}']".format(
            current_item_item_id, current_item_part_code))[0]

        if current_sale_lines.get("itemType") == 'OPTION':
            parent_item_id = item_id
        else:
            parent_item_id = ".".join(item_id.split(".")[:-1])

        if parent_item_id != "":
            sale_lines = eTree.XML(order_pict).findall(".//SaleLine[@itemId='{}']".format(parent_item_id))
            for sale_line in sale_lines:
                item_id_list.append(parent_item_id + "." + sale_line.get('partCode'))

        return item_id_list
    except Exception as _:
        return [item_id]


def remove_custom_comment(pos_ot, curr_line):
    comment_keys = comment_map.keys()
    line_exists = curr_line and len(curr_line) > 0

    comments = {}
    if line_exists:
        for comment in curr_line[0].findall("Comment"):
            comments[comment.get("comment")] = comment.get("commentId")

    for comment_key in comment_keys:
        comment_text = comment_map[comment_key]
        if comment_text in comments.keys():
            pos_ot.delComment(comments[comment_text])
            del comments[comment_text]


def add_custom_comment(pos_ot, item_id, part_code, line_number, level, comment):
    pos_ot.addComment(line_number, item_id, level, part_code, comment)


def get_order_saleline(pos_id, item_id, part_code, line_number):
    model = get_model(pos_id)
    def is_same_line(sl):
        return sl.get("itemId") == item_id and sl.get("partCode") == part_code and sl.get("lineNumber") == line_number

    order = model.find("CurrentOrder/Order")
    return filter(lambda sl: is_same_line(sl), order.findall("SaleLine"))


@action
def doModifier(pos_id, item_id, level, part_code, qty, line_number, modtype=''):
    model = get_model(pos_id)
    pos_ot = get_posot(model)
    pos_ot.blkopnotify = True

    next_level = int(level) + 1
    removing = int(qty) == 0 or not modtype
    pos_ot.changeModifier(pos_id, line_number, item_id, next_level, part_code, qty)

    curr_line = get_order_saleline(pos_id, item_id, part_code, line_number)
    line_exists = curr_line and len(curr_line) > 0

    comment_keys = comment_map.keys()
    if modtype in comment_keys or removing:
        remove_custom_comment(pos_ot, curr_line)

        if not removing:
            if not line_exists:
                pos_ot.changeModifier(pos_id, line_number, item_id, next_level, part_code, 0)
                pos_ot.changeModifier(pos_id, line_number, item_id, next_level, part_code, qty)

            add_custom_comment(pos_ot, item_id, part_code, line_number, next_level, comment_map[modtype])

    doChangeQuantity(int(pos_id), None, '1')
    pos_ot.blkopnotify = False
    pos_ot.updateOrderProperties(pos_id)


@action
def doToggleMirrorScreen(posid):
    model = get_model(posid)
    value = "false" if get_custom(model, "MIRROR_SCREEN", "false") == "true" else "true"
    set_custom(posid, "MIRROR_SCREEN", value, persist=True)


@action
def doChangeLanguage(posid, *args):
    # Retrieve the list of languages from the I18N service
    msg = send_message("I18N", TK_I18N_GETLANGS)
    if msg.token == TK_SYS_ACK:
        options = msg.data.split('\0')
        if options and not options[len(options) - 1]:
            options.pop()  # Last element is empty... remove it!
        # Find out the current POS language
        try:
            model = get_model(posid)
            current_index = options.index(str(model.find("Language").get("name")))
        except:
            current_index = 0  # default value
        index = show_listbox(posid, options, defvalue=current_index)
        if index is None:
            return  # User canceled
        lang = options[index]
        # Set the new language on PosController
        msg = send_message("POS%d" % int(posid), TK_POS_SETLANG, FM_PARAM, "%s\0%s" % (posid, lang))
        if msg.token == TK_SYS_ACK:
            # Wait some time for the UI to reload
            show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
            return
    # Failed
    show_info_message(posid, "$OPERATION_FAILED", msgtype="error")


@action
def doScanTab(pos_id, timeout=45, store_order=True, message="Por favor, pegue sua ficha de consumo e posicione o código de barras da ficha no leitor abaixo.", title="Envie seu pedido", *args):
    global scanner_sale_paused
    model = get_model(pos_id)
    posot = get_posot(model)
    services = get_used_service(model, "scanner", get_all=True)
    scanner = None
    for svc in services:
        if "scanner" in svc:
            scanner = svc
            break
    if scanner is None:
        show_info_message(pos_id, "$NO_SCANNER_CONFIGURED", title="$ERROR", msgtype="critical")
        return
    timeout = timeout * 1000
    while True:
        # send direct command to the scanner in order to turn it on
        mbcontext.MB_EasySendMessage(scanner, token=TK_DRV_IOCTL, format=FM_PARAM, data="\x16T\x0d")
        dlg_id = show_messagebox(pos_id, message=message, title=title, buttons="$CANCEL", asynch=True, timeout=timeout, focus=False)
        try:
            scanner_sale_paused[int(pos_id)] = True
            barcode = read_scanner(scanner, timeout, dlg_id)
            if barcode is None:
                # user cancelled, turn scanner off
                mbcontext.MB_EasySendMessage(scanner, token=TK_DRV_IOCTL, format=FM_PARAM, data="\x16U\x0d")
                return
            if len(barcode) == 0:
                raise Exception('Error reading barcode')
            barcode = base64.b64decode(barcode).strip()
            # save the tab custom property and store the order
            posot.setOrderCustomProperty("TAB", barcode[-3:])
            if store_order:
                posot.storeOrder(pos_id)
            return
        except:
            show_messagebox(pos_id, message="Erro de leitura, tente novamente", icon="error", timeout=180000)
        finally:
            scanner_sale_paused[int(pos_id)] = False
            close_asynch_dialog(pos_id, dlg_id)


@action
def incrementLine(posid, line_number=None):
    if line_number is None:
        show_info_message(posid, "$SELECT_LINE_FIRST", msgtype="warning")
        return

    model = get_model(posid)
    check_current_order(posid, model=model, need_order=True)

    try:
        posot = get_posot(model)
        order_xml = get_current_order(model)
        line = order_xml.find('SaleLine[@level="0"][@lineNumber="{}"]'.format(line_number))
        if line is None:
            sys_log_error('Line {} not found for order {}'.format(line_number, order_xml.get('orderId')))
            return

        qty = int(line.get('qty'))
        posot.blkopnotify = True
        posot.changeLineItemQty(int(posid), line_number, int(qty + 1))
        posot.blkopnotify = False
        posot.splitOrderLine(int(posid), line_number, qty)
    except OrderTakerException, e:
        # show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
        show_messagebox(posid, message="$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()),
                        icon="error")


@action
def enterTabNumber(posid, *args):

    model = get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    posot = get_posot(model)
    order = get_current_order(model)
    tab = order.find('CustomOrderProperties/OrderProperty[@key="TAB"]')
    if tab is not None:
        saved_tab_number = tab.get('value')
    else:
        saved_tab_number = ''

    tab_number = show_keyboard(posid, "$ENTER_TAB_NUMBER", defvalue=saved_tab_number, mask="INTEGER", numpad=True)
    if tab_number in (None, ""):
        return
    posot.setOrderCustomProperty("TAB", tab_number)


@action
def doUpdateBlacklist(posid):
    mbcontext.MB_EasySendMessage("Blacklist", TK_EVT_EVENT, data='\0UpdateBlacklist')
    show_info_message(posid, "$BLACKLIST_UPDATE_STARTED")


@action
def doSyncDeliveryMenu(posid):
    mbcontext.MB_EasySendMessage("Ruptura", TK_EVT_EVENT, data='\0FullRuptureRequest')
    show_info_message(posid, "$DELIVERY_SYNC_STARTED")


@action
def doRuptureCleanup(posid):
    mbcontext.MB_EasySendMessage("Ruptura", TK_EVT_EVENT, data='\0CleanRupture\0%s' % posid)
    show_info_message(posid, "$RUPTURE_CLEANUP_STARTED")


@action
def isPyscriptsOnline(posid):
    return True


@action
@user_authorized_to_execute_action
def doOverwritePrice(posid, line_number, item_price, itemid, level, partcode, hard_mode='false'):
    if line_number in [None, '0']:
        show_info_message(posid, "$SELECT_LINE_FIRST", msgtype="warning")
        return

    logger.info(hard_mode)
    model = get_model(posid)
    posot = get_posot(model)

    message = "$NEW_PRICE_TO_APPLY"
    if hard_mode == 'false':
        message = "$NEW_PRICE_OR_ZERO"

    new_price = show_keyboard(posid, message, title="$OVERWRITE_PRICE", mask="CURRENCY", numpad=True, timeout=720000)
    new_price = round(float(new_price), 2) if new_price else None
    if new_price is None:
        return

    if hard_mode == 'false':
        if new_price == 0.0:
            try:
                posot.clearDiscount('1', line_number, itemid, level, partcode)
            except OrderTakerException, e:
                error_message = "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr())
                show_messagebox(posid, message=error_message, icon="critical")
                raise
        else:
            oldprice = round(float(item_price), 2) if item_price else 0.0
            discountamt = str(round(oldprice - new_price, 2))
            # posot.priceOverwrite(posid, line_number, newprice)
            if discountamt > 0.0:
                try:
                    posot.applyDiscount('1', discountamt, line_number, itemid, level, partcode)
                except OrderTakerException, e:
                    error_message = "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr())
                    show_messagebox(posid, message=error_message, icon="critical")
                    raise
    else:
        try:
            posot.priceOverwrite(posid, line_number, new_price)
        except OrderTakerException, e:
            error_message = "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr())
            show_messagebox(posid, message=error_message, icon="critical")
            raise

    return True


@action
def do_comment(posid, line, level, item_id, part_code, comment_id="-1", comment=None):
    model = get_model(posid)
    posot = get_posot(model)
    comment_id = None if comment_id == "-1" else comment_id

    if not line:
        show_messagebox(posid, message="$NO_LINE_SELECTED", icon="critical")
        return

    default_message = ""
    message = "$ADD_COMMENT"
    if comment_id:
        message = "$EDIT_COMMENT"
        # get the current comment id text
        model = get_model(posid)
        order = model.find("CurrentOrder/Order")
        for sl in order.findall("SaleLine"):
            for line_comment in sl.findall("Comment"):
                if line_comment.get("commentId") == comment_id:
                    default_message = line_comment.get("comment")
                    break

    if comment is None:
        comments = keyboard_comments["do_comment"] if "do_comment" in keyboard_comments else []
        comments = "|".join(comments)
        comment = show_keyboard(posid, message, defvalue=default_message, title="", numpad=False, infotext=comments)

    if comment is None:
        return

    if comment_id:
        if comment == "":
            posot.delComment(comment_id)
        else:
            posot.updComment(comment_id, comment)
    elif comment != "":
        posot.addComment(line, item_id, level, part_code, comment)


def _check_if_operator_is_logged(pos_id, model, need_logged=True, can_be_blocked=True):
    if model is None:
        model = get_model(pos_id)
    if need_logged:
        check_business_day(pos_id, model)

    is_logged = _has_operator_logged(model)

    if need_logged and not is_logged:
        show_messagebox(pos_id, message='$NEED_TO_LOGIN_FIRST', icon='warning')
        raise StopAction()
    elif is_logged and not need_logged:
        show_messagebox(pos_id, message='$NEED_TO_LOGOFF_FIRST', icon='warning')
        raise StopAction()
    if not can_be_blocked and is_day_blocked(model):
        show_messagebox(pos_id, message='$POS_IS_BLOCKED_BY_TIME', icon='error')
        raise StopAction()


def _has_operator_logged(model):
    for op in model.findall('Operator'):
        if op.get('state') in ['LOGGEDIN', 'PAUSED']:
            return True

    return False


def get_tender_types():
    all_tender_types = sysactions.get_tender_types()
    tender_types = [tender for _, tender in all_tender_types.items()]
    for tender_type in tender_types:
        tender_type["showInFC"] = True if tender_type["id"] < 100 else False
        parent_id = "parentId "
        if parent_id in tender_type:
            tender_type["parentId"] = tender_type[parent_id]
            del tender_type[parent_id]

        has_child = False
        for tender_type_aux in tender_types:
            if "parentId" in tender_type_aux and tender_type_aux["parentId"] == tender_type["id"]:
                has_child = True
                break

        tender_type["hasChild"] = has_child

    try:
        tender_types = sorted(tender_types, key=lambda k: k['id'])
    except Exception as _:
        logger.exception("Error ordering tender types")

    return tender_types


def get_tender_type(pos_id, model, tender_type_id, amount):
    tender_type = _get_tender_type(pos_id, tender_type_id)
    if tender_type is None:
        return None

    if int(tender_type["electronicTypeId"]) > 2:
        show_message_dialog(pos_id, message="$PAYMENT_NOT_IMPLEMENTED|{}".format(tender_type["descr"]))
        return None

    if tender_type['needAuth'] and not get_authorization(pos_id, min_level=UserLevels.MANAGER.value, model=model)[0]:
        return None

    if amount in ("CashAmount", "EnterAmount"):
        amount = show_numpad_dialog(pos_id, "$LABEL_CASH_AMOUNT_TENDERED", mask="CURRENCY")
        if amount in (None, "", ".") or float(amount) <= 0:
            return

    return tender_type


def _update_blocked_pos_state(pos_id):
    pass


@action
def do_ask_barcode(pos_id):
    barcode = show_keyboard(pos_id, "$TYPE_BARCODE", title="", mask="INTEGER", defvalue="", numpad=True, timeout=1800000)
    if barcode in (None, ''):
        return
    return sell_product_by_barcode(pos_id, barcode, True)


@action
def do_sell_product_by_barcode(pos_id, barcode_number, check_consistency=False, received_qty="1"):
    return sell_product_by_barcode(pos_id, barcode_number, check_consistency, received_qty)


def _is_changing_order(model):
    current_order = get_current_order(model)
    if not current_order:
        return False

    if current_order.get("state") != "IN_PROGRESS":
        return False

    state_history = current_order.findall(".//StateHistory/State")
    for state in state_history:
        if state.get("state") == "STORED":
            return True

    return False


def is_table_service(model):
    order_properties = model.findall(".//CustomOrderProperties/OrderProperty")
    for order_property in order_properties:
        if order_property.get("key") == "TABLE_ID":
            return True
