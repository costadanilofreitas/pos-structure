# -*- coding: utf-8 -*-
# Python module responsible to handle POS actions
# All actions are broad-casted by the PosController using a "POS_ACTION" event subject
#
# Copyright (C) 2008-2012 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

# Python standard modules
import time
import threading
import base64
import cfgtools
import json
import logging
import constants
from datetime import datetime, timedelta
from decimal import Decimal as D
from xml.etree.ElementTree import ElementTree, Element
from xml.etree import cElementTree as etree
import pyscripts
import persistence
import requests
import sysactions
import re
import sys
import os

from systools import sys_log_info, sys_log_debug, sys_log_exception, sys_log_error
from msgbus import TK_EFT_REQUEST, TK_EVT_EVENT, TK_FISCAL_CMD, TK_SYS_NAK, TK_ACCOUNT_EFTACTIVITY, TK_ACCOUNT_GIFTCARDACTIVITY, TK_POS_SETDEFSERVICE, TK_SYS_ACK, TK_SYS_CHECKFORUPDATES, \
    TK_POS_SETRECALLDATA, TK_POS_USERLOGOUT, TK_POS_USERLOGIN, TK_POS_LISTUSERS, TK_POS_SETFUNCTION, TK_POS_USEROPEN, TK_I18N_GETLANGS, TK_POS_SETLANG, TK_CMP_TERM_NOW, \
    TK_POS_SETPOD, TK_CDRAWER_OPEN, TK_POS_SETMODIFIERSDATA, TK_ACCOUNT_TRANSFER, TK_HV_GLOBALRESTART, TK_GENESIS_LISTPKGS, TK_GENESIS_APPLYUPDATE, TK_CASHLESS_REPORT, \
    FM_STRING, FM_PARAM, FM_XML, TK_PERSIST_SEQUENCER_INCREMENT, MBException, SE_NOTFOUND, MBEasyContext, TK_POS_BUSINESSEND, TK_POS_GETSTATE, TK_PRN_GETSTATUS, TK_PRN_PRINT, TK_DRV_IOCTL
import bustoken
import datetime
from posot import OrderTaker, OrderTakerException, ClearOptionException
from sysdefs import eft
from sysactions import StopAction, AuthenticationFailed, action, send_message, change_mainscreen, change_screen, get_model, get_podtype, get_tender_type, \
    get_business_period, check_genesis_error, get_operator_session, get_posot, get_used_service, get_cfg, \
    has_operator_opened, get_current_operator, has_current_order, get_current_order, check_drawer, check_business_day, check_operator_logged, \
    check_current_order, show_info_message, show_messagebox, show_confirmation, show_listbox, show_keyboard, show_order_preview, show_text_preview, \
    close_asynch_dialog, generate_report, print_text, print_report, set_custom, get_custom, clear_custom, translate_message, format_amount, get_last_order, \
    get_line_product_name, get_clearOptionsInfo, can_void_line, get_user_information, authenticate_user, is_valid_date, calculate_giftcards_amount, get_poslist, \
    get_pricelist, check_main_screen, get_storewide_config, on_before_total, read_msr, format_date, get_posfunction, is_day_blocked, show_custom_dialog, read_scanner
from sysact_bk import validar_cpf, validar_cnpj
from persistence import Driver as DBDriver
from pyscriptscache import cache as _cache
from pos_model import TenderType
from poslistener import insert_options_and_defaults, update_options_and_defaults, delete_options_and_defaults, get_updated_sale_line_defaults
from bustoken import TK_SITEF_ADD_PAYMENT, TK_SITEF_CANCEL_PAYMENT, TK_SITEF_FINISH_PAYMENT, TK_FISCALWRAPPER_PROCESS_REQUEST, TK_FISCALWRAPPER_SEARCH_REQUEST,\
    TK_KDSMONITOR_STATUS_REQUEST, TK_FISCALWRAPPER_REPRINT, TK_MAINTENANCE_TERMINATE_REQUEST, TK_MAINTENANCE_RESTART_REQUEST, TK_PROD_PURGE, TK_FISCALWRAPPER_SEFAZ_CONNECTIVITY, \
    TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST, TK_SITEF_CONNECTIVITY_TEST, TK_FISCALWRAPPER_SAT_PROCESS_PAYMENT, TK_FISCALWRAPPER_SAT_PAYMENT_STATUS, TK_FISCALWRAPPER_CANCEL_ORDER, \
    TK_FISCALWRAPPER_GET_NF_TYPE, TK_DAILYGOALS_UPDATE_GOALS, TK_BKOFFICEUPLOADER_SEND_SANGRIA, TK_FISCALWRAPPER_RE_SIGN_XML, TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION, TK_FISCALWRAPPER_SITUATION, \
    TK_MAINTENANCE_RECREATE_FILE_NUMBER, TK_BKOFFICEUPLOADER_SEND_BKOFFICE_ORDER, TK_RUPTURA_GET_ENABLED, TK_RUPTURA_GET_DISABLED, TK_RUPTURA_UPDATE_ITEMS, TK_DISCOUNT_APPLY, TK_DISCOUNT_CLEAR, \
    TK_BLACKLIST_CHECK_STRING, TK_BLACKLIST_FILTER_STRING, TK_REMOTE_ORDER_OPEN_STORE, TK_REMOTE_ORDER_CLOSE_STORE, \
    TK_REMOTE_ORDER_GET_STORE, TK_VERIFY_PAF_ECF_LISTENER, TK_POS_FUNCTION_CHANGED
from fiscalprinter import fpcmds, FPException, fp, fpreadout

import manager
# noinspection PyUnresolvedReferences
from manager import openday
import manager.users
# noinspection PyUnresolvedReferences
from manager.users import changepass, createuser, inactivateuser, removeuser
import manager.reports
# noinspection PyUnresolvedReferences
from manager.reports import speedOfServiceReport, hourlySalesReport, cashReport, extendedReport, checkoutReport, checkoutReport, employeesClockedInReport
from helper import get_date_difference_GMT_timezone, config_logger, read_swconfig, ClicheHelper, \
    convert_from_utf_to_localtime
from shutil import copy2

# usecs per second
USECS_PER_SEC = 1000000

debug_path = '../python/pycharm-debug.egg'
if os.path.exists(debug_path):
    try:
        sys.path.index(debug_path)
    except ValueError:
        sys.path.append(debug_path)
    # noinspection PyUnresolvedReferences
    import pydevd

manager.mbcontext = pyscripts.mbcontext
manager.users.mbcontext = pyscripts.mbcontext
manager.reports.mbcontext = pyscripts.mbcontext
logger = logging.getLogger("PosActions")

#
# Constants
#
sysactions.DATE_FMT = "%d/%m/%Y"
sysactions.get_pricelist.DEFAULT = "EI"

# Authorization levels
LEVEL_SUPERVISOR = 10
LEVEL_MANAGER = 20
LEVEL_SYSTEM = 30

# Tender types
TENDER_CASH = "0"
TENDER_CREDIT_CARD = "2"
TENDER_CREDIT_AMEX = "5"
TENDER_CREDIT_VISA = "9"
TENDER_CREDIT_MASTERCARD = "10"
TENDER_CREDIT_DISCOVER = "11"

SIGNED_IN_USER = "SIGNED_IN_USER"
ASSIGNED_USER = "ASSIGNED_USER"


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
_scanner_sale_paused = {}
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
_products_cache = None
# Barcode to product mapping
_product_by_barcode = {}

comment_mods = []
productPrices = {}
cancela = False

# Receipt
dbd = DBDriver()

lock_tender = threading.Lock()
tendering = {}

lock_recall = threading.Lock()
recalling = []

# limit values to sangria
sangria_levels = None
max_transfer_value = 0
show_all_transfer = False

cliche = []


def get_authorization(posid, min_level=None, model=None, timeout=60000, can_bypass_reader=False, is_login=True, insert_auth=False, order_id=None, display_title="$USER_AUTHENTICATION"):
    from sysact_bk import get_authorization as get_authorization_original

    try:
        ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(posid), bustoken.TK_FPR_OK)
        if ret.token == TK_SYS_ACK:
            # Temos o leitor e ele esta operacional, vamos pedir as impressoes do usuario
            ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(posid), bustoken.TK_FPR_AUTHORIZE_USER, format=FM_PARAM, data=posid)
            if ret.token == bustoken.TK_FPR_TIMEOUT and can_bypass_reader:
                return get_authorization_original(posid, 30, model, timeout, is_login, display_title=display_title)
            if ret.token != TK_SYS_ACK:
                # Erro cadastrando impressao digital
                show_info_message(posid, "Erro realizando a leitura da digital. Tente novamente.", msgtype="error")
                return
            elif ret.data == "":
                # Leitura da impressao OK mas usuario nao cadastrado
                show_info_message(posid, "Usuário não identificado a partir da digital. Tente novamente.", msgtype="error")
                return
            else:
                # Usuario identificado
                user_id = ret.data
                try:
                    user_xml_str = get_user_information(user_id)
                except Exception as ex:
                    show_messagebox(posid, message="Impressao digital associada a usuario que nao esta cadastrado", icon="error")
                    #show_info_message(posid, "Impressao digital associada a usuario que nao esta cadastrado", msgtype="error")
                    return

                # Se identificamos o usuario pela digital, pegamos a informacao dele e constuimos o objeto
                # igual a autenticacao por usuario e senha faz
                if user_xml_str is None:
                    show_messagebox(posid, message="Impressao digital associada a usuario que nao esta cadastrado",
                                    icon="error")
                    #show_info_message(posid, "Impressao digital associada a usuario que nao esta cadastrado", msgtype="error")
                    return

                user_xml = etree.XML(user_xml_str)
                user_element = user_xml.find("user")
                user_level = int(user_element.attrib["Level"])
                if user_level < min_level:
                    show_messagebox(posid, message="Acesso negado", icon="error")
                    #show_info_message(posid, "Acesso negado", msgtype="error")
                    return False
                else:
                    set_custom(posid, 'Authorization Level', user_level)
                    return True

    except MBException as e:
        if e.errorcode == 2:  # NOT_FOUND, servico de FingerPrint nao disponivel
            pass
        else:
            pass

    # Se chegamos aqui, nao temos leitor de impressao digital ativo, fallback para a forma tradicional
    response = get_authorization_original(posid, min_level, model, timeout, is_login, display_title=display_title)
    if response and insert_auth:
        model = get_model(posid)
        posot = get_posot(model)
        user_id = get_custom(model, 'Last Manager ID')
        if not order_id:
            order = model.find("CurrentOrder/Order")
            order_id = order.get("orderId")
        posot.setOrderCustomProperty("AUTHENTICATION_USER", user_id, order_id)
    logger.debug(response)
    return response


def _join(dic1, dic2):
    d = dict(dic1)
    d.update(dic2)
    return d


def _ordermodified_received(params):
    """Callback called by pyscripts module"""
    posid = params[4]
    for tandem_evt in _tandem_events:
        if str(tandem_evt[2]) == posid:
            tandem_evt[0].set()
            tandem_evt[3] = "got"
            _tandem_events.remove(tandem_evt)
            break
    if _recall_listeners:
        xml, subject, type = params[:3]
        if type in ("STORED", "RECALLED"):
            for posid in tuple(_recall_listeners):
                # This will only update the model, and not change the screen
                try:
                    showRecallByPicture(posid, screenNumber="")
                except StopAction:
                    pass


def _dialog_resp_received(params):
    """Callback called by pyscripts module"""
    xml, subject, type = params[:3]
    dialog = etree.XML(xml).find("Dialog")
    dlg_id = str(dialog.get("id"))
    response = str(dialog.findtext("Response"))
    dialog_evt = None
    for eft_evt in _eft_events:
        if str(eft_evt[1]) == dlg_id and response == "0":
            pos_id, order_id = eft_evt[2:4]
            sys_log_debug("Pressionada tecla anula. Cancelando pagamento Sitef no POS %s - Order %s" % (str(pos_id), str(order_id)))
            ret = mbcontext.MB_EasySendMessage("Sitef%02d" % int(pos_id), token=TK_SITEF_CANCEL_PAYMENT, format=FM_PARAM, data="%s;%s" % (str(pos_id), str(order_id)))

            close_asynch_dialog(pos_id, dlg_id)
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
                    dlg_id = show_messagebox(pos_id, "$EFT_SWIPE_CARD", "$EFT", "swipecard", buttons="$CANCEL", timeout=180000, asynch=True)
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


def _device_data_event_received(params):
    """
    When a scanner event is received, we should try so sell the item on the POS or, if price
    lookup mode is on, just ignore and let the sysactions handle the scanner dialog
    """
    global _product_by_barcode, _scanner_sale_paused
    data, subject, p_type, asynch, pos_id = params[:5]
    try:
        device = etree.XML(data).find("Device")
        device_name = str(device.get("name"))
        if not device_name.startswith("scanner"):
            # just processing scanner events, ignoring other devices
            return
        # extract POS id from device name
        # XXX: we are assuming that the device name is scannerXX where XX is the destination POS number
        pos_id = int(device_name[7:])
        if pos_id in _scanner_sale_paused and _scanner_sale_paused[pos_id]:
            # scanner sale is paused, don't try to sell
            return
        barcode = base64.b64decode(device.text).strip()
        if barcode and barcode in _product_by_barcode:
            doSale(str(pos_id), "1." + _product_by_barcode[barcode]['plu'])
        else:
            sys_log_info("Scanned barcode {0} not found on the product database!".format(barcode))
    except:
        sys_log_exception('Exception processing device data event')


#
# Main function - called by the pyscripts module
#
def main():
    # pydevd.settrace('localhost', port=9123, stdoutToServer=True, stderrToServer=True, suspend=False)

    # Subscribes event callbacks
    sysactions.initialize()

    pyscripts.subscribe_event_listener("DIALOG_RESP", _dialog_resp_received)
    pyscripts.subscribe_event_listener("ORDER_MODIFIED", _ordermodified_received)
    pyscripts.subscribe_event_listener("SITEF", _sitef_processing_received)
    pyscripts.subscribe_event_listener("DEVICE_DATA", _device_data_event_received)

    # Wait for the persistence layer to startup
    persistence.Driver().open(mbcontext).select("SELECT 1")

    # Loads POS configuration
    load_posconfig()
    # Loads SQLite cache
    force_sqlite_cache()
    # Check for any genesis error and notify the users
    threading.Timer(5.0, check_genesis_error).start()

    global cliche
    cliche = ClicheHelper(mbcontext).get_cliche()

    global lock_tender
    with lock_tender:
        global tendering
        for posid in poslist:
            tendering[int(posid)] = False

    config_logger(os.environ["LOADERCFG"], 'PosActions')


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
    except Exception as ex:
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
    global max_transfer_value
    global show_all_transfer
    global round_donation_enabled
    global round_donation_pod_types
    global round_donation_payment_types
    global round_donation_institution
    global round_donation_cnpj
    global round_donation_site
    global void_line_authorization
    global void_order_authorization
    global void_last_order_btn
    global set_product_quantity_pre
    global skim_digit_limit
    global picklist_reprint_type
    global update_vtt_url

    config = cfgtools.read(os.environ["LOADERCFG"])

    # Store-wide config
    sangria_levels = get_storewide_config("Store.SangriaLevels", defval="250;500;1000")
    max_transfer_value = float(get_storewide_config("Store.MaxTranfer", defval="1200"))
    show_all_transfer = get_storewide_config("Store.ShowAllTransfer", defval="false").lower() == "true"

    is24HoursStore = get_storewide_config("Store.Is24Hours", defval="false").lower() == "true"
    manager.is24HoursStore = is24HoursStore

    round_donation_enabled = get_storewide_config("Store.RoundDonationInfo.RoundDonationEnabled", defval="false").lower() == "true"
    round_donation_pod_types = get_storewide_config("Store.RoundDonationInfo.RoundDonationPodTypes", defval="FC;DT;KK;DS").split(';')
    round_donation_payment_types = get_storewide_config("Store.RoundDonationInfo.RoundDonationPaymentTypes", defval="0").split(';')
    round_donation_institution = get_storewide_config("Store.RoundDonationInfo.RoundDonationInstitution")
    round_donation_cnpj = get_storewide_config("Store.RoundDonationInfo.RoundDonationCNPJ")
    round_donation_site = get_storewide_config("Store.RoundDonationInfo.RoundDonationSite")

    void_line_authorization = get_storewide_config("Store.VoidLineAuthorization", defval="false").lower() == "true"
    void_order_authorization = get_storewide_config("Store.VoidOrderAuthorization", defval="false").lower() == "true"
    void_last_order_btn = get_storewide_config("Store.VoidLastOrderBtn", defval="false").lower() == "true"

    update_vtt_url = config.find_value("UpdateVtt.UpdateVttURL")
    picklist_reprint_type = config.find_value("Reprint.PicklistReprintType") or "production_pick_list"

    skim_digit_limit_cfg = get_storewide_config("Store.SkimDigitLimit", defval="4-30")
    skim_digit_limit = {"min": int(skim_digit_limit_cfg.split("-")[0]),
                        "max": int(skim_digit_limit_cfg.split("-")[1])}

    dt_lanes = "2"
    try:
        dt_lanes = str(int(get_storewide_config("Store.DTLanes", defval="2")))
    except:
        sys_log_exception("Error reading [Store.DTLanes]")

    store_id = get_storewide_config("Store.Id")
    manager.reports.store_id = store_id

    set_product_quantity_pre = False
    if get_nf_type() == "PAF":
        set_product_quantity_pre = True
    else:
        set_product_quantity_pre = get_storewide_config("Store.SetProductQuantity", defval="pos").lower() == "pre"

    poslist = get_poslist()
    manager.reports.poslist = poslist
    manager.poslist = poslist
    for posid in poslist:
        model = get_model(posid)
        # Check the "DT_LANES" custom parameter
        if get_custom(model, "DT_LANES") != dt_lanes:
            set_custom(posid, "DT_LANES", dt_lanes, persist=True)
        # Constructs the booth numbers mapping
        booth = int(model.find("PosState").get("booth"))
        if booth > 0:
            booth_pos_mapping[int(booth)] = int(posid)
            pos_booth_mapping[int(posid)] = int(booth)

        sell_categories[posid] = []
        podtype = get_podtype(model)
        list_categories = get_cfg(posid).key_value("listCategories", '''SORVETE,SHAKE,AGUA,SOBREMESA''' if podtype == "KK" else [])
        if type(list_categories) is not list and len(list_categories) > 0:
            sell_categories[posid] = list_categories.split(',')


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


#
# Helper functions
#
def tandem_wait_nextbooth(posid, nextposid, timeout=60000):
    evt = threading.Event()
    evt.clear()
    dialogid = show_messagebox(posid, "$WAITING_NEXT_TANDEM_BOOTH", buttons="$OVERRIDE|$CANCEL", timeout=timeout, asynch=True)
    try:
        evtdata = [evt, dialogid, nextposid, None]
        _tandem_events.append(evtdata)
        # this timeout is in seconds
        evt.wait(float(timeout) / 1000)
        # evtdata[3] now contains one of: [None: timeout] - ["0": OVERRIDE] - ["1": CANCEL] - ["got": got new order from next booth]
        return evtdata[3] not in (None, "1")
    finally:
        close_asynch_dialog(posid, dialogid)


def request_eft(pos_id, model, eft_command, is_credit, amount, swipe=False, timeout=180000, eft_service=None, display_via_api=False):
    # Find the EFT associated to this POS
    order = model.find("CurrentOrder/Order")
    last_totaled = order.findall("StateHistory/State[@state='TOTALED']")[-1].get("timestamp").replace("-", "").replace(":", "")

    if is_credit:
        tender_type = 1
    else:
        tender_type = 2

    order_id = order.get("orderId")
    tender_seq_id = len(order.find("TenderHistory").findall("Tender"))
    data_fiscal = last_totaled[:8]
    hora_fiscal = last_totaled[9:15]
    operador = model.find("Operator").get("id")
    eft_name = get_used_service(model, "eft")
    dlg_id = None
    try:
        # Start a Dialog with Processing
        dlg_id = show_messagebox(pos_id, message="$PLEASE_WAIT", title="$EFT", icon="info", buttons="", asynch=True, timeout=180000)
        evt_data = [eft_name, None, pos_id, order_id]
        _eft_events.append(evt_data)

        ret = mbcontext.MB_EasySendMessage("Sitef%02d" % int(pos_id), token=TK_SITEF_ADD_PAYMENT, format=FM_PARAM, data="%s;%s;%s;%s;%s;%s;%s;%s;%s" % (str(pos_id), str(order_id), str(operador), str(tender_type), str(amount), data_fiscal, hora_fiscal, tender_seq_id, display_via_api))
        if ret.token != TK_SYS_ACK:
            return None
        else:
            return ret.data
    except:
        show_messagebox(pos_id, message="Serviço TEF Indisponível", title="$EFT", icon="info", buttons="$OK", asynch=True)
        sys_log_exception("Error Processing TEF")
    finally:
        if dlg_id:
            close_asynch_dialog(pos_id, dlg_id)


def register_eft_activity(posid, session, activity_type, success_flag, amount="", result_xml="", authcode="", orderid="", cardno=""):
    payload = "\0".join(map(str, [session, activity_type, success_flag, amount, result_xml, authcode, orderid, cardno]))
    msg = send_message("account%d" % int(posid, 10), TK_ACCOUNT_EFTACTIVITY, FM_PARAM, payload)
    return msg.token != TK_SYS_NAK


def request_gift(posid, model, gift_command, amount=0, order_id=0, validate=True, timeout=600000):
    # Find the MSR associated to this POS
    msr_name = get_used_service(model, "msr")
    if not msr_name:
        show_info_message(posid, "$NO_CONFIGURED_MSR", msgtype="warning")
        return None
    # Read tracks from the card reader
    dlgid = show_messagebox(posid, "$SWIPE_GIFT_CARD", "$MAGNETIC_STRIPE_READER", "swipecard", "$CANCEL", timeout, asynch=True, focus=False)
    tracks = None
    try:
        # Read tracks from the card reader
        tracks = read_msr(msr_name, timeout, dlgid)
    finally:
        close_asynch_dialog(posid, dlgid)
    if not tracks:
        return None
    # Card number is on track #2 - decode it from base64
    card_number = base64.b64decode(tracks[1])
    # Ensure the amount is correct
    amt = "%.2f" % float(amount)
    dlgid = show_messagebox(posid, "$PROCESSING_GIFT_CARD", "$PLEASE_WAIT", "info", "", timeout, True)
    # Send the gift request to the driver
    try:
        msg = send_message("gift_processor", TK_EFT_REQUEST, FM_PARAM, "%s\0%s\0%s\0%s" % (gift_command, card_number, amt, order_id), timeout=timeout * 1000)
    except:
        msg = None
    finally:
        close_asynch_dialog(posid, dlgid)
    if not msg or msg.token == TK_SYS_NAK:
        show_messagebox(posid, message="$GIFT_ERROR|%s|%s" % ("0", "Communication error"), icon="error")
        #show_info_message(posid, "$GIFT_ERROR|%s|%s" % ("0", "Communication error"), msgtype="error")
        return None
    # Parse the response XML
    gift_xml = etree.XML(msg.data)
    if validate:
        rescode = gift_xml.get("result")
        if int(rescode) != 0:
            reason = gift_xml.get("reason") or "(none)"
            show_messagebox(posid, message="$GIFT_ERROR|%s|%s" % (rescode, reason), icon="error")
            #show_info_message(posid, "$GIFT_ERROR|%s|%s" % (rescode, reason), msgtype="error")
            return None
    # Sets a "masked" card number
    cardnbr = "%s*****%s*" % (card_number[0:6], card_number[10:len(card_number) - 1])
    gift_xml.set("cardnbr", cardnbr)
    if amount:
        gift_xml.set("amount", amt)
    # Success - register this activity on account if necessary
    gift_command = int(gift_command)
    if gift_command in (eft.EFT_GIFTACTIVATE, eft.EFT_GIFTREDEEM, eft.EFT_GIFTADDVALUE):
        session = get_operator_session(model) or ""
        descr = "GC Activation" if gift_command == eft.EFT_GIFTACTIVATE else "GC Increment" if gift_command == eft.EFT_GIFTADDVALUE else "GC Redemption"
        authcode = gift_xml.get("authorization") or ""
        orderid = str(order_id or "")
        register_gift_activity(posid, session, str(gift_command), descr, amt, authcode, orderid, cardnbr)
    gift_xml = etree.tostring(gift_xml, "UTF-8")
    return gift_xml


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

    if tendertype["electronicType"] == "GIFT_CARD":  # GIFT_CARD - command # 12
        if calculate_giftcards_amount(model) > 0:
            show_info_message(posid, "$PAYMENT_WITH_GIFT_NOT_ALLOWED", msgtype="warning")
            raise StopAction()
        if refund:
            gift_command = eft.EFT_GIFTADDVALUE
            receipt_type = "GIFT INCREMENT (REFUND)"
        else:
            gift_command = eft.EFT_GIFTREDEEM
            receipt_type = "GIFT SALE"
        gift_xml = request_gift(posid, model, gift_command, amount=amount, order_id=order_id)
        if gift_xml:
            show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
            print_report(posid, model, False, "gift_receipt", receipt_type, gift_xml)
        else:
            # Failed
            raise StopAction()

    amt = None
    xml = None
    if tendertype["electronicType"] in ("CREDIT_CARD", "DEBIT_CARD"):
        try:
            # Ensure the amount is correct
            amt = "%.2f" % float(amount)
            tax = "%.2f" % float(xml_order.get("taxTotal") or 0)
            is_credit = (tendertype["electronicType"] == "CREDIT_CARD")
            if refund:
                eft_command = str(eft.EFT_CREDITREFUND if is_credit else eft.EFT_DEBITREFUND)
                # slip_type = "REFUND"
                eft_data = "\0".join([eft_command, posid, userid, amt, period, tax, order_id])
            else:
                eft_command = str(eft.EFT_CREDITSALE if is_credit else eft.EFT_DEBITSALE)
                # slip_type = "SALE"
                eft_data = "\0".join([eft_command, posid, userid, amt, tax, order_id, period])

            # card_type = "CREDIT" if is_credit else "DEBIT"
            # Send the EFT request to the driver

            # eft_xml = '<EftXml Media="VISA" Result="CAPTURED" CardNumber="4111111111111111" AuthCode="123456" ApprovedAmount="' + amt + '"/>'
            tenderid = tendertype["electronicTypeId"]
            eft_xml = request_eft(posid, model, eft_data, is_credit, amt)
        except Exception as ex:
            sys_log_exception("Error processing credit-card. posid: %s - Erro %s" % (posid, str(ex)))
        # Check if the credit card was processed
        if not eft_xml or etree.XML(eft_xml).get("Result") != "0":
            # Register the activity
            register_eft_activity(posid, session, activity_type=str(eft_command), success_flag='0', result_xml=eft_xml or "", orderid=order_id)
            if eft_xml:
                xml = etree.XML(eft_xml)
                response = xml.get("Result") or "(none)"
                if tendertype["electronicType"] in "CREDIT_CARD":
                    show_messagebox(posid, message="$CREDIT_CARD_NOT_PROCESSED|%s" % response.encode('utf-8'), icon="error", timeout=180000)

                if tendertype["electronicType"] in "DEBIT_CARD":
                    show_messagebox(posid, message="$DEBIT_CARD_NOT_PROCESSED|%s" % response.encode('utf-8'), icon="error", timeout=180000)
            raise StopAction()
        else:
            # Success
            xml = etree.XML(eft_xml)
            cardno, authcode, approved_amt, media, payment_amt, adq, exp_date, nsu, owner_name, last_digits = map(xml.get, ("CardNumber", "AuthCode", "ApprovedAmount", "Media", "ApprovedAmount", "IdAuth", "ExpirationDate", "NSU", "OwnerName", "LastDigits"))
            if not approved_amt:
                approved_amt = amt
            try:
                exp_date = exp_date or 'Indefinida'
                owner_name = owner_name or 'Indefinida'
                last_digits = last_digits or 'Indefinida'
                register_after = register_eft_after_payment(posid, order_id, tender_seq_id, authcode, cardno, owner_name, exp_date, adq, nsu, payment_amt, id_fila, media, last_digits)
                if register_after is None:
                    show_messagebox(posid, "Erro ao registrar dados do pagamento no Integrador Sefaz", "$ERROR", 'error')
                elif "ERROR" in register_after:
                    show_messagebox(posid, "Erro ao registrar dados do pagamento no Integrador Sefaz: %s" % register_after, "$ERROR", 'error')

                # Register the activity
                register_eft_activity(posid, session, activity_type=str(eft_command), success_flag='1', amount=approved_amt, result_xml=eft_xml, authcode=authcode or "", cardno=cardno or "", orderid=order_id)

                if float(approved_amt) != float(amt):
                    try:
                        # Display a warning message for partial approvals
                        show_messagebox(posid, message="$CASHLESS_PARTIAL_APPROVAL_WARNING|%s|%s" % (format_amount(model, approved_amt, True), format_amount(model, amount, True)), icon="warning", asynch=True)
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

#
# Action handlers
#
@action
def doSale(pos_id, part_code, qty="", size="", sale_type="EAT_IN", *args):
    """ doSale(posid, pcode, qty="", size="")
    Sells an item, creating a new order for it if necessary
    @param pos_id: POS id
    @param part_code: Product code to sell
    @param qty: Optional quantity to sell (default: 1)
    @param size: Optional product size (dimension)
    @param sale_type: Optional type of sale (default: EAT_IN)
    """

    logger.debug("--- doSale START ---")

    if not pafecflistenter_component_found(pos_id):
        return

    model = get_model(pos_id)

    pos_ot = get_posot(model)
    pod_type = get_podtype(model)

    dlg_id = None
    is_new_order = None
    try:
        logger.debug("--- doSale before popup 'Processando cupom fiscal' ---")
        if get_nf_type(pos_id) == "PAF":
            dlg_id = show_messagebox(pos_id, "$PROCESSING_FISCAL_DATA", title="$PROCESSING", buttons="", asynch=True, timeout=180000, focus=False)

        logger.debug("--- doSale before get pricelist ---")
        price_list = get_pricelist(model) if pod_type != "DL" else "DL"
        sale_type = "DRIVE_THRU" if (pod_type == "DT") else sale_type

        pos_function = get_posfunction(model)
        is_new_order = not has_current_order(model)

        # Do NOT proceed if there is already an opened Order and not PartCode was provided
        if not is_new_order and part_code is None:
            return

        order_properties_dict = {}
        if is_new_order is True:
            order_properties_dict = new_order_properties(pod_type, pos_function, pos_id, pos_ot)

        order_created = False
        if is_new_order:
            order_created = process_new_order(model, pod_type, pos_function, pos_id, pos_ot, price_list, sale_type)

        logger.debug("--- doSale before retrieve quantity ---")
        qty = retrieve_quantity(model, qty) or '1'

        if is_new_order is True and order_created is False and part_code is None:
            logger.debug("--- doSale before posot.createOrder ---")
            sale = pos_ot.createOrder(int(pos_id), pricelist=price_list, saletype=sale_type)
            logger.debug("--- doSale after posot.createOrder ---")
        else:
            logger.debug("--- doSale before posot.doSale ---")
            sale = pos_ot.doSale(int(pos_id), part_code, price_list, qty, False, size, sale_type)
            logger.debug("--- doSale END ---")

        if len(order_properties_dict) > 0:
            logger.debug("--- doSale update custom properties ---")
            pos_ot.setOrderCustomProperties(order_properties_dict)

        return sale

    except Exception as ex:
        if isinstance(ex, OrderTakerException):
            if handle_order_taker_exception(pos_id, pos_ot, ex, mbcontext):
                return
            else:
                #show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                #                 msgtype="critical")
                show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")
        else:
            #show_info_message(pos_id, "ERRO AO INICIAR A VENDA - {}".format(ex._descr), msgtype="critical")
            show_messagebox(pos_id, message="ERRO AO INICIAR A VENDA - {}".format(ex._descr), icon="error")

        if is_new_order:
            model = get_model(pos_id)
            if has_current_order(model):
                void_order(pos_id)

        sys_log_exception('Error in doSale - new order: {} - '.format(is_new_order), ex)
    finally:
        if dlg_id:
            time.sleep(0.1)
            sysactions.close_asynch_dialog(pos_id, dlg_id)
            logger.debug("--- doSale after popup 'Processando cupom fiscal' ---")


def pafecflistenter_component_found(pos_id):
    if get_nf_type(pos_id) != "PAF":
        return True

    try:
        msg = mbcontext.MB_EasySendMessage("PafEcfListener", token=TK_VERIFY_PAF_ECF_LISTENER, format=FM_PARAM, data="")
        if msg.token != TK_SYS_ACK:
            #show_info_message(pos_id, "FiscalMode PAF but no PafEcfListener found", msgtype="critical")
            show_messagebox(pos_id, message="FiscalMode PAF but no PafEcfListener found", icon="error")
            return False

        return True
    except Exception as _:
        #show_info_message(pos_id, "FiscalMode PAF but no PafEcfListener found", msgtype="critical")
        show_messagebox(pos_id, message="FiscalMode PAF but no PafEcfListener found", icon="error")
        return False


def handle_synchronization_error(pos_id, pos_ot, dlgid=None):
    # type: (int, OrderTaker) -> None
    while True:
        if dlgid:
            close_asynch_dialog(pos_id, dlgid)

        show_messagebox(pos_id, "$SYNCHRONIZATION_ERROR", "$ERROR", timeout=600000)
        try:
            if not has_current_order(get_model(pos_id)):
                return 
            pos_ot.voidOrder(pos_id)
            return
        except Exception as ex:
            if isinstance(ex, OrderTakerException):
                if handle_order_taker_exception(pos_id, pos_ot, ex, mbcontext):
                    return

            logger.exception("Erro cancelando pedido")
            #show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
            #                  msgtype="critical")
            show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")


def handle_printer_validation_error(pos_id, msg):
    # type: (int, unicode) -> None
    show_messagebox(pos_id, msg, "$ERROR")


def retrieve_quantity(model, qty):
    if set_product_quantity_pre:
        pre_quantity = get_custom(model, "pre_quantity")
        qty = pre_quantity if pre_quantity is not None else 1

    return qty


def process_new_order(model, pod_type, pos_function, pos_id, pos_ot, price_list, sale_type):
    logger.debug("--- doSale start new order ---")
    check_new_order(model, pos_id)
    return offer_multi_order(model, pod_type, pos_id, pos_ot, pos_function, price_list, sale_type)


def new_order_properties(pod_type, pos_function, pos_id, pos_ot):
    logger.debug("--- doSale get_nf_type PAF ---")

    dict_sale = {}
    if get_nf_type(pos_id) == "PAF":
        logger.debug("--- doSale before customer info ---")
        customer_doc = get_customer_doc(pos_id, pos_ot)
        customer_name = get_customer_name(pos_id, pos_ot)
        get_and_fill_customer_address(pos_id, pos_ot)
        logger.debug("--- doSale after customer info ---")
        pre_sale = get_paf_pre_sale(pod_type, pos_ot, pos_function)
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


def check_sangria(model, pos_id):
    if is_sangria_enable():
        period = get_business_period(model)
        session = get_operator_session(model)
        drawer_amount = get_drawer_amount(pos_id, period, session)

        logger.debug("--- doSale doSetDrawerStatus ---")
        if doSetDrawerStatus(pos_id, drawer_amount):
            raise StopAction()


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
            #show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
            #                  msgtype="critical")
            show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                            icon="error")
            raise StopAction()
        else:
            return True

    return False


def update_custom_properties(customer_doc=None, customer_name=None, pre_sale=None):
    dict_sale = {}

    if customer_doc not in (None, ""):
        dict_sale.update({"CUSTOMER_DOC": customer_doc})
    if customer_name not in (None, ""):
        dict_sale.update({"CUSTOMER_NAME": customer_name})
    if pre_sale not in (None, ""):
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
        customer_doc = show_keyboard(pos_id, "(somente números)", title="Digite o CPF/CNPJ", numpad=True, defvalue=default_doc)
        if customer_doc in (None, ""):
            customer_doc = ""
            break
        valid = validate_document(customer_doc)
        if not valid:
            show_info_message(pos_id, "Número de CPF/CNPJ Inválido!", msgtype="critical")

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
        customer_name = show_keyboard(pos_id, "Digite o nome do cliente", defvalue=default_name, title="", numpad=False)
        if customer_name in (None, ""):
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
def doStartOrder(pos_id, sale_type="EAT_IN", *args):
    doSale(pos_id, None, "", "", sale_type, args)


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

@action
def doCompleteOption(posid, context, pcode, qty="", line_number="", size="", sale_type="EAT_IN", subst='', *args):
    logger.debug("--- doCompleteOption START ---")
    list_categories = sell_categories[int(posid)]
    if subst:
        doClearOptionItem(posid, line_number, subst)
    if len(list_categories) > 0:
        if _cache.is_not_order_kiosk(pcode, get_podtype(get_model(int(posid))) or None, list_categories):
            show_info_message(posid, '$KIOSK_NOT_SALE', msgtype='error')
            raise StopAction

    sale_xml = doOption(posid, context, pcode, qty, line_number, size, sale_type, args)
    if sale_xml is None:
        return

    logger.debug("--- waitOrder START ---")
    # Waits a maximum of 5 seconds for the order to "arrive" at the POS model
    time_limit = (time.time() + 5.0)
    while (time.time() < time_limit) and (not has_current_order(get_model(posid))):
        time.sleep(0.1)
    logger.debug("--- waitOrder END ---")

    if sale_xml not in ["", None, True, False]:
        sale_line = int(etree.XML(sale_xml).attrib['lineNumber'])
        order_line = -1

        logger.debug("--- waitNewLine START ---")
        # Waits a maximum of 5 seconds for NewLine "arrive" at POS model
        while (time.time() < time_limit) and (sale_line > order_line):
            time.sleep(0.1)
            if get_current_order(get_model(posid)).findall('SaleLine'):
                sale_lines = get_current_order(get_model(posid)).findall('SaleLine')
                order_line = int(max(sale_lines, key=lambda x: int(x.attrib['lineNumber'])).attrib['lineNumber'])
        logger.debug("--- waitNewLine START ---")

        checkShowModifierScreen(posid, sale_xml, "350")
    logger.debug("--- doCompleteOption END ---")
    return sale_xml


@action
def doOption(pos_id, context, part_code, qty="", line_number="", size="", sale_type="EAT_IN", *args):
    logger.debug("--- doOption START ---")
    model = get_model(pos_id)
    try:
        check_operator_logged(pos_id, model=model, can_be_blocked=False)
        item_qty = qty or "1"
        if has_current_order(model):
            pos_ot = get_posot(model)

            # Try to resolve an open option
            option_done = pos_ot.doOption(int(pos_id), part_code, item_qty, line_number, (size or '@'))
            if option_done:
                return True

        # Options not solved OR there are remaining items to sell
        sale_xml = doSale(pos_id, "%s.%s" % (context, part_code), item_qty, size, sale_type)
        logger.debug("--- doOption END ---")
        return sale_xml

    except OrderTakerException as ex:
        #show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
        #                  msgtype="critical")
        show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                        icon="error")
        logger.debug("--- doOption Exception END ---")
    return False


@action
def doClearOption(posid, lineNumber="", qty="", *args):
    model = get_model(int(posid))
    check_current_order(posid, model=model, need_order=True)
    lines = get_clearOptionsInfo(model, lineNumber)
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
    posot = get_posot(model)
    try:
        itemid = "%s.%s" % (to_clear.get("itemId"), to_clear.get("partCode"))
        posot.clearOption(posid, lineNumber, qty, itemid)
        return True
    except ClearOptionException, e:
        sys_log_exception("Could not clear option")
        show_info_message(posid, "Error %s" % e, msgtype="error")
    except OrderTakerException, ex:
        show_messagebox(posid, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")
        #show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), msgtype="critical")


@action
def doChangeSaleType(posid, saletype, *args):
    model = get_model(posid)
    posot = get_posot(model)
    check_operator_logged(posid, model=model, can_be_blocked=False)

    if has_current_order(model):
        # Set the sale type on the order
        posot.updateOrderProperties(posid, saletype=saletype)
    return True


def _list_open_options(order):
    # type: (str) -> Any

    # Check if there is ANY item in the Sale
    sale_lines = order.findall("SaleLine")

    j = -1
    for i in range(0, len(sale_lines)):
        if i <= j:
            continue

        line = sale_lines[i]
        if line.get("qty") == "0":
            for j in range(i + 1, len(sale_lines)):
                option_son_line = sale_lines[j]
                if int(line.get("level")) >= int(option_son_line.get("level")):
                    j -= 1
                    break

        if line.get("itemType") == "OPTION":
            option_chosen_qty = 0
            for j in range(i + 1, len(sale_lines)):
                option_son_line = sale_lines[j]

                if int(line.get("level")) >= int(option_son_line.get("level")) or option_son_line.get("itemType") == "OPTION":
                    j -= 1
                    break
                option_chosen_qty += int(option_son_line.get("qty"))

            if option_chosen_qty < int(line.get("qty")):
                return line

    return None
# END _list_open_options


def _apply_discount(order, discount_id, discount_amount, discount_pct):
    temp_insert = """INSERT OR REPLACE INTO orderdb.OrderDiscount (OrderId, LineNumber, ItemId, Level, PartCode, DiscountId, DiscountAmount)
    VALUES (%(order_id)s, %(line_number)s, '%(item_id)s', %(item_level)s, '%(part_code)s', %(discount_id)s, %(temp_amount)s)"""

    def F(value):
        if value is None:
            return 0
        return float(value)
    # END F

    # Check if there is ANY item in the Sale
    sale_lines = order.findall("SaleLine")
    priced_items = map(lambda x: x, filter(lambda x: (F(x.get("itemPrice")) != 0) and (F(x.get("qty")) != 0), sale_lines))

    total = F(order.get("totalAmount")) + F(order.get("taxTotal"))
    if discount_pct is None:
        discount_pct = discount_amount/total

    if discount_amount is None:
        discount_amount = discount_pct*total

    order_id = order.get("orderId")
    queries = []

    data = "<Order>" + etree.tostring(order) + "</Order>\0TAXCALC\0TAXCALC\0true\01\01\0"
    msg = mbcontext.MB_EasySendMessage("NTaxcalc", TK_EVT_EVENT, format=FM_PARAM, data=data)
    if not msg or msg.token == TK_SYS_NAK:
        raise Exception("No ICMS found for order")

    params = msg.data.split('\0')
    data = etree.XML(params[1])

    tax_xml = data if data.tag == "Order" else data.find("Order")
    map(lambda x: x.set("taxIndex", "0.00"), filter(lambda x: x.get("taxIndex") in ("FF", "II", "NN"), tax_xml))
    tax_temp_list = filter(lambda x: F(x.get("baseAmountAD")) != 0, tax_xml)

    applied_discount = 0
    for item in priced_items:
        # INSERT
        line_number, item_id, item_level, part_code = map(item.get, ("lineNumber", "itemId", "level", "partCode"))
        item_price, unit_price, item_qty, added_price, added_qty, multiplied_qty = map(item.get, ("itemPrice", "unitPrice", "qty", "addedUnitPrice", "addedQty", "multipliedQty"))

        theoretical_price = (F(unit_price) * F(item_qty) + F(added_price) * F(added_qty or item_qty)) * (F(multiplied_qty) / F(item_qty))
        correct_price = F(item_price) * (theoretical_price / F(item_price))
        temp_amount = "{0:.2f}".format(round(F(item_price) * discount_pct, 2))
        correct_amount = F(temp_amount) * (theoretical_price / F(item_price))

        queries.append(temp_insert % locals())
        applied_discount += correct_amount

    # Get the difference between applied and theoretical value of Discount
    tax_diff = round(applied_discount, 2) - round(float(discount_amount), 2)
    if tax_diff > 0:
        # Find MAX price Item (of Max TAX) to ADD Tax
        max_tax = (max(tax_temp_list, key=lambda x: F(x.get("taxIndex")))).get("taxIndex")
        tax_max_list = filter(lambda x: (x.get("taxIndex") == max_tax) and (F(x.get("baseAmountAD")) != 0), tax_xml)
        max_item_id = (max(tax_max_list, key=lambda x: F(x.get("baseAmountAD")))).get("itemId")
        max_item = (filter(lambda x: x.get("itemId") == max_item_id, priced_items))[0]

        line_number, item_id, item_level, part_code = map(max_item.get, ("lineNumber", "itemId", "level", "partCode"))
        item_price, unit_price, item_qty, added_price, added_qty, multiplied_qty = map(max_item.get, ("itemPrice", "unitPrice", "qty", "addedUnitPrice", "addedQty", "multipliedQty"))

        theoretical_price = (F(unit_price) * F(item_qty) + F(added_price) * F(added_qty)) * (F(multiplied_qty) / F(item_qty))
        correct_rate = theoretical_price / F(item_price)
        temp_amount = round(F(item_price) * discount_pct, 2) - tax_diff / correct_rate
        temp_amount = "{0:.2f}".format(temp_amount) if correct_rate == 1 else "{0:.5f}".format(temp_amount)
        queries.append(temp_insert % locals())
    else:
        # Find MIN price Item (of Min TAX) to SUB Tax
        min_tax = (min(tax_temp_list, key=lambda x: F(x.get("taxIndex")))).get("taxIndex")
        tax_min_list = filter(lambda x: (x.get("taxIndex") == min_tax) and (F(x.get("baseAmountAD")) != 0), tax_xml)
        min_item_id = (min(tax_min_list, key=lambda x: F(x.get("baseAmountAD")))).get("itemId")
        min_item = (filter(lambda x: x.get("itemId") == min_item_id, priced_items))[0]

        line_number, item_id, item_level, part_code = map(min_item.get, ("lineNumber", "itemId", "level", "partCode"))
        item_price, unit_price, item_qty, added_price, added_qty, multiplied_qty = map(min_item.get, ("itemPrice", "unitPrice", "qty", "addedUnitPrice", "addedQty", "multipliedQty"))

        theoretical_price = (F(unit_price) * F(item_qty) + F(added_price) * F(added_qty)) * (F(multiplied_qty) / F(item_qty))
        correct_rate = theoretical_price / F(item_price)
        temp_amount = round(F(item_price) * discount_pct, 2) - tax_diff / correct_rate
        temp_amount = "{0:.2f}".format(temp_amount) if correct_rate == 1 else "{0:.5f}".format(temp_amount)
        queries.append(temp_insert % locals())

    if queries:
        conn = None
        try:
            conn = DBDriver().open(mbcontext, dbname=str(order.get("posId")))
            conn.transaction_start()
            conn.query('''BEGIN TRANSACTION;''')
            conn.query(";".join(queries))
            conn.query('''COMMIT TRANSACTION;''')
        except Exception as ex:
            if conn:
                conn.query('''ROLLBACK TRANSACTION;''')
            raise ex
        finally:
            if conn:
                conn.close()
# END of _apply_discount


@action
def doTotal(pos_id, screen_number="", dlg_id=-1, is_recall=False, *args):
    logger.debug("Totalizando Order - POS %s" % pos_id)

    if not pafecflistenter_component_found(pos_id):
        return

    model = get_model(pos_id)
    posot = get_posot(model)
    period = get_business_period(model)
    session = get_operator_session(model)

    pod_function = get_posfunction(model) if get_podtype(model) in ("DT", "FC") else get_podtype(model)

    if is_sangria_enable() and pod_function != 'TT':
        if doSetDrawerStatus(pos_id, get_drawer_amount(pos_id, period, session)):
            return

    if is_day_blocked(model):
        #show_info_message(pos_id, "$POS_IS_BLOCKED_BY_TIME", msgtype="critical")
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
        show_info_message(pos_id, "Não Existem Itens na Venda!", msgtype="warning")
        return

    # Get the order type from the order to check if it is a REFUND, WASTE or a normal SALE
    order_type = order.get("type")
    if order_type != "REFUND":  # Ignore choices verification for REFUND
        if not on_before_total(pos_id, model):
            return

        option = _list_open_options(order)
        if option is not None:
            prod_name = get_line_product_name(model, int(option.get("lineNumber")))
            #show_info_message(pos_id, "$NEED_TO_RESOLVE_OPTION|%s" % (prod_name.encode("UTF-8")), msgtype="critical")
            show_messagebox(pos_id, message="$NEED_TO_RESOLVE_OPTION|%s" % (prod_name.encode("UTF-8")), icon="error")
            return

    logger.debug("Order Verificada - Pronta para Totalizar - POS %s" % pos_id)
    try:
        # Totalize the order
        discounts = posot.getOrderDiscounts(False)
        if discounts:
            for temp in etree.XML(discounts).findall("OrderDiscount"):
                discount_id = temp.get("discountId")

                for sale in active_sale_lines:
                    discount = _cache.get_discount(sale.get("partCode"), discount_id)

                    if discount:
                        if discount[0] not in "NULL" and float(discount[0]) != 0:
                            discount_items = filter(lambda x: x.get("partCode") == sale.get("partCode"), active_sale_lines)
                            rate = 0
                            for item in discount_items:
                                rate += float(item.get("multipliedQty"))

                            _apply_discount(order, discount_id, float(discount[0]) * rate, None)

                        if discount[1] not in "NULL" and float(discount[1]) != 0:
                            _apply_discount(order, discount_id, None, float(discount[1]))
                        continue
        logger.debug("Descontos Calculados - POS %s" % pos_id)

        # Totalize the order
        posot.doTotal(int(pos_id))
        logger.debug("Core Total OK - POS %s" % pos_id)

        # Check if Order is already PAID (Previuos tenders are bigger than current due amount)
        xml_order = etree.XML(posot.orderPicture(pos_id))
        due_amount = float(xml_order.get("dueAmount"))

        if due_amount < 0:
            # Ask if we should proceed
            show_info_message(pos_id, "$TENDERS_ARE_BIGGER_THEN_DUE_AMOUNT", msgtype="warning")
            doBackFromTotal(pos_id)
            return "Error"

        if screen_number:
            if pod_function == "OT":
                doStoreOrder(pos_id, "false")
                return
            else:
                doShowScreen(pos_id, screen_number)  # Show tender screen

        if dlg_id != -1:
            close_asynch_dialog(pos_id, dlg_id)

        if get_nf_type(pos_id) != "PAF":
            fill_customer_properties(model, pod_function, pos_id, posot, get_doc=True, get_name=True)

    except Exception as ex:
        if isinstance(ex, OrderTakerException):
            if handle_order_taker_exception(pos_id, posot, ex, mbcontext):
                return

        #show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), msgtype="critical")
        show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")
        if is_recall:
            raise ex

    finally:
        logger.debug("Order Totalizada - POS %s" % pos_id)
    return True
# END of doTotal


@action
def doWasteRefundTransaction(posid, transaction="refund", screenNumber="", *args):
    model = get_model(posid)
    posot = get_posot(model)
    last_order = get_last_order(model)
    check_operator_logged(posid, model=model, can_be_blocked=False)
    orderType = ""
    podtype = get_podtype(model)
    if transaction.upper() == "REFUND":
        orderType = "REFUND"
    elif transaction.upper() == "WASTE":
        orderType = "WASTE"

    posot.createOrder(posid, pricelist=get_pricelist(model), orderType=orderType)

    if screenNumber:
        doShowScreen(posid, screenNumber)  # Show main screen


@action
def doStoreOrder(pos_id, totalize="none", *args):
    model = get_model(pos_id)
    check_current_order(pos_id, model=model, need_order=True)

    posot = get_posot(model)
    xml_order = get_current_order(model)

    if float(xml_order.get("totalTender")) != 0:
        show_info_message(pos_id, "$ORDER_HAS_TENDERS_CANNOT_SAVE", msgtype="warning")
        return

    if get_current_order(model).get("type") != "SALE":
        show_info_message(pos_id, "$THIS_ORDER_TYPE_CANNOT_BE_STORED", msgtype="warning")
        return

    order = model.find("CurrentOrder/Order")
    # Check if there is ANY item in the Sale
    sale_lines = order.findall("SaleLine")
    deleted_line_numbers = map(lambda x: x.get("lineNumber"), filter(lambda x: x.get("level") == "0" and x.get("qty") == "0", sale_lines))
    active_sale_lines = filter(lambda x: x.get("lineNumber") not in deleted_line_numbers, sale_lines)

    if not active_sale_lines:
        show_info_message(pos_id, "Não Existem Itens na Venda!", msgtype="warning")
        return

    option = _list_open_options(order)
    if option is not None:
        prod_name = get_line_product_name(model, int(option.get("lineNumber")))
        show_info_message(pos_id, "$NEED_TO_RESOLVE_OPTION|%s" % (prod_name.encode("UTF-8")), msgtype="critical")
        return

    pod_function = get_posfunction(model) if get_podtype(model) in ("DT", "FC") else get_podtype(model)
    if totalize == "none" and pod_function == "OT":
        totalize = "true"

    if get_nf_type(pos_id) == "PAF" and not pod_function == "OT":
        show_info_message(pos_id, "$THIS_ORDER_TYPE_CANNOT_BE_STORED", msgtype="warning")
        return

    if totalize.lower() == "true":
        if doTotal(pos_id, screen_number="") == "Error":
            return

    if totalize.lower() != "true" and get_nf_type(pos_id) != "PAF":
        fill_customer_properties(model, pod_function, pos_id, posot, get_doc=True, get_name=True)

    # Pre-venda
    pre_venda = None
    if pod_function == "OT":
        for prop in order.findall("CustomOrderProperties/OrderProperty"):
            key, value = prop.get("key"), prop.get("value")
            if key == "PRE_VENDA":
                pre_venda = value
                break
    try:
        posot.storeOrder(pos_id)
        doShowScreen(pos_id, "main")  # Show main screen
        if pre_venda:
            show_messagebox(pos_id, "Pre Venda: PV%010d" % int(pre_venda))
        show_info_message(pos_id, "Pedido foi salvo!", msgtype="warning")
    except OrderTakerException as ex:
        show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                          msgtype="critical")

    order = model.find("CurrentOrder/Order")
    order_id = order.get("orderId")
    logger.debug("Pedido Salvo - Order %s - PosId %s" % (order_id, pos_id))


def fill_customer_properties(model, pod_function, pos_id, pos_ot, get_doc=False, get_name=False, force=False):
    check_current_order(pos_id, model)
    order_xml = get_current_order(model)

    customer_doc = ""
    default_doc = ""
    if get_doc:
        is_required, default_doc = customer_doc_is_required(order_xml, pod_function)
        if force or is_required:
            customer_doc = get_customer_doc(pos_id, pos_ot, default_doc)

    customer_name = ""
    default_name = ""
    if get_name:
        is_required, default_name = customer_name_is_required(order_xml)
        if force or is_required:
            customer_name = get_customer_name(pos_id, pos_ot, default_name)

    if (customer_doc == default_doc) and (customer_name == default_name):
        return

    order_properties_dict = update_custom_properties(customer_doc, customer_name)
    if len(order_properties_dict) > 0:
        pos_ot.setOrderCustomProperties(order_properties_dict)


@action
def doBackFromTotal(pos_id, void_reason=5, *args):
    default_screen = "main"
    if len(args) > 0:
        default_screen = args[0]

    model = get_model(pos_id)
    pod_function = get_posfunction(model) if get_podtype(model) == "DT" else ""
    if "CS" in pod_function:
        default_screen = "201"

    try:
        tender = model.find("CurrentOrder/Order/TenderHistory/Tender")
        if tender is not None:
            confirm = show_confirmation(pos_id, "$CANNOT_CHANGE_ORDER_WITH_PAYMENTS", timeout=180000)
            if confirm:
                if void_order_authorization:
                    if not get_authorization(pos_id, min_level=LEVEL_SUPERVISOR, model=model, insert_auth=True, display_title="$ORDER_CANCEL"):
                        return

                void_reason = get_void_reason_id(pos_id, void_reason)
                if not void_reason:
                    return

                void_order(pos_id)
                order = get_current_order(model)
                posot = get_posot(model)
                posot.setOrderCustomProperties(void_reason, order.get('orderId'))
                doShowScreen(pos_id, default_screen)  # Returns to the previous screen
        else:
            check_current_order(pos_id, model=model, need_order=True)
            get_posot(model).reopenOrder(int(pos_id))

    except OrderTakerException as ex:
        show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), msgtype="critical")

    doShowScreen(pos_id, default_screen)  # Returns to the previous screen
    return True

@action
def doChangeEFT(posid, *args):
    model = get_model(posid)
    current_eft = get_used_service(model, "eft")
    if not current_eft:
        show_info_message(posid, "$NO_CONFIGURED_EFTS", msgtype="warning")
        return
    if not get_authorization(posid, min_level=LEVEL_SUPERVISOR, model=model):
        return
    options = get_used_service(model, "eft", get_all=True)
    index = show_listbox(posid, options, defvalue=options.index(current_eft))
    if index is None:
        return  # User canceled
    eft_name = options[index]
    msg = send_message("POS%d" % int(posid), TK_POS_SETDEFSERVICE, FM_PARAM, "%s\0eft\0%s" % (posid, eft_name))
    if msg.token == TK_SYS_ACK:
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
        return eft_name
    else:
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")


@action
def doTender(pos_id, amount, tender_type_id="0", offline="false", need_confirmation="false", *args):
    logger.debug("--- doTender START ---")


    if not pafecflistenter_component_found(pos_id):
        return

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
        show_messagebox(pos_id, "$CANCELED_SALE|{0}".format(error_message), title="$ERROR", icon="error", buttons="$OK")
        posot.clearTenders(int(pos_id))
        void_order(pos_id)
        doShowScreen(pos_id, "main")
    # END

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

                dlgid = show_messagebox(pos_id, "$PROCESSING_PAYMENT_DATA", title="$PROCESSING", buttons="", asynch=True, timeout=180000)

                if round_donation_value > 0.0:
                    posot.setOrderCustomProperty("DONATION_VALUE", str(round_donation_value))

                logger.debug("--- doTender before posot.doTender 2 ---")
                posot.doTender(int(pos_id), tender_type_id, amount, 0, res["tenderId"])
                logger.debug("--- doTender after posot.doTender 2 ---")

                if round_donation_value > 0.0:
                    _do_print_donation(pos_id, order_id, customer_name, format(round_donation_value, '.2f').replace(".", ","), round_donation_institution, round_donation_cnpj, round_donation_site, cliche)

                break
            except OrderTakerException as ex:
                if isinstance(ex, OrderTakerException):
                    if handle_order_taker_exception(pos_id, posot, ex, mbcontext, dlgid):
                        return
                    else:
                        show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                                          msgtype="critical")

                # Erro Fiscal (Normalmente falha de comunicação com a impressora) - PopUp (Tentar Novamente ou Cancelar)
                try_again_response = show_messagebox(pos_id, "Ocorreu um erro finalizando a venda", title="$ERROR",
                                                     icon="error", buttons="Tentar Novamente|Cancelar")

                # 0 -> Tentar Novamente / 1 -> Cancelar
                if try_again_response != 0:
                    cancel_sale_and_payments("Cancelamento solicitado pelo Usuário")
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
            sys_log_error("PosId {0} Tendering True".format(pos_id))
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
        offline_bandeira = None

        xml_order = get_current_order(model)
        if xml_order.get("state") != "TOTALED":
            show_info_message(pos_id, "Pedido em Processamento. Tente Novamente!", msgtype="warning")
            return

        due_amount = xml_order.get("dueAmount")
        total_gross = xml_order.get("totalGross")
        order_due = float(due_amount)
        order_id = xml_order.get("orderId")
        order_type = xml_order.get("type")

        # Get information about the tender type
        tendertype = get_tender_type(tender_type_id)
        if tendertype is None:
            show_messagebox(pos_id, message="$INVALID_TENDER_TYPE|%s" % tender_type_id, icon="error")
            return

        if int(tender_type_id) == TenderType.external_card:


            valuable_bandeiras = ["1 - Débito",
                                  "2 - Visa",
                                  "3 - Mastercard",
                                  "4 - American Express",
                                  "5 - Elo",
                                  "6 - Outros Crédito",
                                  "7 - Vale Refeição"]
            valuable_to_real = {0: 99990,  # see BandeiraCartão table on fiscal_persistcomp
                                1: 1,
                                2: 2,
                                3: 4,
                                4: 31,
                                5: 99991,
                                6: 99992}

            if not offline_bandeira:
                offline_bandeira = show_listbox(pos_id, valuable_bandeiras, message="Selecione o Cartão:")
                offline_bandeira = valuable_to_real[offline_bandeira]



        # Check manager authorization
        if tendertype['needAuth'] and not get_authorization(pos_id, min_level=LEVEL_MANAGER, model=model):
            return

        if amount in ("CashAmount", "EnterAmount"):
            defvalue = ("" if amount == "CashAmount" else due_amount)
            amount = show_keyboard(pos_id, "$LABEL_CASH_AMOUNT_TENDERED", title="LABEL_CASH_AMOUNT_TENDERED", defvalue=defvalue, mask="CURRENCY", numpad=True)
            if amount in (None, "", ".") or float(amount) <= 0:
                return

        if amount == "Exact":
            amount = due_amount

        if amount in (None, "", ".") or float(amount) <= 0:
            show_info_message(pos_id, "Valor devido deve ser informado!", msgtype="warning")
            return

        if need_confirmation == "true":
            if not show_confirmation(pos_id, message="Confirma recebimento em {0}: {1}".format(tendertype['descr'].lower(), format_amount(model, amount)), buttons="$OK|$CANCEL"):
                return

        # If the tender will close the sale and we have an index pin pad,
        tender_seq_id = len(xml_order.findall("TenderHistory/Tender")) + 1

        ignore_payment = False
        previous_tender_id = None
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

                    if show_confirmation(pos_id, message=donation_message, title="$ROUND_PROJECT_TITLE"):
                        return round(donation_value, 2)

                return 0.0

            # Check the maximum change
            if (amount != "") and (float(amount) > order_due):
                if tendertype["electronicTypeId"] in (1, 2):
                    show_info_message(pos_id, "Valor para pagamento com cartão não pode ser superior ao devido!", msgtype="warning")
                    return

                if order_type == "REFUND":
                    show_info_message(pos_id, "$NO_CHANGE_ALLOWED_IN_REFUND", msgtype="warning")
                    return

                change += float(amount) - order_due
                change_limit = tendertype['changeLimit']

                if change_limit and change > float(change_limit):
                    change_limit = float(change_limit)
                    if change_limit > 0:
                        show_info_message(pos_id, "$MAXIMUM_CHANGE_ALLOWED|%s|%s" % (format_amount(model, change_limit), format_amount(model, change)), msgtype="warning")
                    else:
                        show_info_message(pos_id, "$AMOUNT_GREATER_THAN_DUE", msgtype="warning")

                    return

                # Arredondar Dinheiro
                round_donation_value = _do_round_donation()
                if round_donation_value > 0.0:
                    change -= round_donation_value

                show_messagebox(pos_id, "$MONEY_CHANGE|R$%.2f" % abs(change))

            elif (amount != "") and float(due_amount) == float(amount):
                if tendertype["electronicTypeId"] in (1, 2):
                    # Arredondar Cartão de Crédito
                    round_donation_value = _do_round_donation()
                    if round_donation_value > 0.0:
                        amount = format(float(amount) + round_donation_value, '.2f')

            xml = None

            # Process electronic payments
            id_fila = None
            if offline.lower() == "false" and tendertype["electronicTypeId"] not in (0, 3):
                # Sends message to SAT/MFE/VFP-e to register payment data. If it returns error, the sale should be CANCELLED
                id_fila = register_eft_before_payment(pos_id, order_id, tender_seq_id, amount, total_gross)
                if id_fila is None:
                    show_messagebox(pos_id, "Erro ao iniciar pagamento no Integrador Sefaz", "$ERROR", 'error')
                    return
                elif "ERROR" in id_fila:
                    show_messagebox(pos_id, "Erro ao iniciar pagamento no Integrador Sefaz: %s" % id_fila, "$ERROR", 'error')
                    return
                tender_type_id, amount, xml = handle_electronic_payment(pos_id, model, tender_type_id, amount, xml_order, tendertype, tender_seq_id, id_fila)

            logger.debug("--- doTender before 'Processando pagamento' ---")
            # Mensagem de Processando Pagamento
            dlgid = show_messagebox(pos_id, "$PROCESSING_PAYMENT_DATA", title="$PROCESSING", buttons="", asynch=True, timeout=180000)
            # If the tender will close the sale and we have an index pin pad,
            tender_seq_id = len(xml_order.findall("TenderHistory/Tender")) + 1

            conn = None
            if float(amount) - order_due > 0:
                amount_change = float(amount) - order_due
                amount_paid = float(amount) - amount_change
            else:
                amount_change = 0
                amount_paid = float(amount)

            payment_saved = False
            for retries in range(0, 3):
                try:
                    conn = DBDriver().open(mbcontext, service_name="FiscalPersistence")
                    params_fiscal = {"pos_id": pos_id, "order_id": order_id, "tender_seq_id": tender_seq_id, "type": tender_type_id, "amount": amount_paid, "change": amount_change}
                    if xml is not None:
                        params_fiscal["auth_code"] = xml.attrib["AuthCode"]
                        params_fiscal["id_auth"] = xml.attrib["IdAuth"]
                        params_fiscal["cnpj_auth"] = xml.attrib["CNPJAuth"]
                        params_fiscal["bandeira"] = xml.attrib["Bandeira"]
                        params_fiscal["receipt_merchant"] = base64.b64decode(xml.attrib["ReceiptMerchant"]).decode('iso-8859-1')
                        params_fiscal["receipt_customer"] = base64.b64decode(xml.attrib["ReceiptCustomer"]).decode('iso-8859-1')
                        params_fiscal["payment_id"] = id_fila
                    if offline_bandeira is not None:
                        params_fiscal["bandeira"] = offline_bandeira
                    conn.pquery("fiscal_savePaymentData", **params_fiscal)
                except Exception as _:
                    sys_log_exception("Erro salvando dados fiscais")
                else:
                    payment_saved = True
                    break
                finally:
                    if conn:
                        conn.close()

            if not payment_saved:
                cancel_sale_and_payments("Erro processando Pagamento")
                return

            #  PAF: We need to save all payment activities to be printed when order is paid
            if get_nf_type(pos_id) == "PAF" and tendertype["electronicTypeId"] not in (0, 3):
                logger.debug("--- doTender before PAF save all payments activities ---")
                conn = None
                try:
                    TENDER_CREDIT_CARD = "2"
                    TENDER_DEBIT_CARD = "3"
                    tender_id = (TENDER_CREDIT_CARD if tendertype["electronicType"] == "CREDIT_CARD" else TENDER_DEBIT_CARD)
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
                        conn.escape(amount), conn.escape(etree.tostring(xml)))
                                   )
                    BEGIN_TRANSACTION = ["BEGIN TRANSACTION", "UPDATE fiscalinfo.FiscalDEnabled SET Enabled=0"]
                    COMMIT_TRANSACTION = ["UPDATE fiscalinfo.FiscalDEnabled SET Enabled=1", "COMMIT TRANSACTION"]
                    queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                    conn.query("\0".join(queries))
                except Exception as ex:
                    show_messagebox(pos_id, message="Erro armazenando dados do pagamento: %s" % str(ex), icon="error")
                    #show_info_message(pos_id, "Erro armazenando dados do pagamento: %s" % str(ex), msgtype="error")
                finally:
                    if conn:
                        conn.close()
                logger.debug("--- doTender after PAF save all payments activities ---")

            # Fecha Mensagem de Processando Pagamento
            close_asynch_dialog(pos_id, dlgid) if dlgid else None
            logger.debug("--- doTender after 'Processando pagamento' ---")

            if not payment_saved:
                cancel_sale_and_payments("Erro processando Pagamento")
                return

            # Do Tender - DO NOT SET ORDER TO PAID
            logger.debug("--- doTender before posot.doTender ---")

            tender_details = ""
            if tendertype["electronicTypeId"] in (1, 2):
                tender_details = json.dumps({"CNPJAuth": xml.attrib["CNPJAuth"],
                                             "TransactionProcessor": xml.attrib["TransactionProcessor"],
                                             "Bandeira": xml.attrib["Bandeira"],
                                             "IdAuth": xml.attrib["IdAuth"],
                                             "AuthCode": xml.attrib["AuthCode"]})

            res = posot.doTender(int(pos_id), tender_type_id, amount, 1, previous_tender_id, tenderdetail=tender_details)
            logger.debug("--- doTender after posot.doTender ---")
            if float(res["dueAmount"]) > 0:
                return "success"

            # Fecha Mensagem de Processando Pagamento
            close_asynch_dialog(pos_id, dlgid) if dlgid else None

        logger.debug("--- doTender after 'Processando pagamento 2' ---")
        while True:
            logger.debug("--- doTender before PROCESSING_FISCAL_DATA ---")
            try:
                dlgid = show_messagebox(pos_id, "$PROCESSING_FISCAL_DATA", title="$PROCESSING", buttons="", asynch=True, timeout=300000)
                ret = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_PROCESS_REQUEST, format=FM_PARAM, data=pos_id, timeout=180000000)

                # Processamento Finalizado com Sucesso
                if ret.token == TK_SYS_ACK:
                    if not get_nf_type(pos_id) == "PAF":
                        try:
                            current_printer = get_used_service(model, "printer")
                            msg = mbcontext.MB_EasySendMessage(current_printer, TK_PRN_PRINT, format=FM_PARAM, data=ret.data, timeout=30000000)  # type: MBMessage
                            if msg.token != TK_SYS_ACK:
                                show_messagebox(pos_id, "$ERROR_PRINT_NFE|%s" % msg.data, title="Informação", icon="error", buttons="$OK")
                        except Exception as ex:
                            show_messagebox(pos_id, "$ERROR_PRINT_NFE|%s" % repr(ex), title="Informação", icon="error", buttons="$OK")

                    if float(res["totalAmount"]) > 0:
                        doOpenDrawer(pos_id)
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

                fiscal_ok, message, orderid, data_fiscal, hora_fiscal = ret.data.split('\0')


                # Fiscal OK - Erro na DANFE - Venda conluida sem volta - Apenas informa o usuário
                if fiscal_ok == "True":
                    show_messagebox(pos_id, "$ERROR_PRINT_NFE|%s" % message, title="Informação", icon="error", buttons="$OK")
                    close_asynch_dialog(pos_id, dlgid) if dlgid else None
                    if float(res["totalAmount"]) > 0:
                        doOpenDrawer(pos_id)

                    # Confirm Tender - Set Order to PAID
                    tender_and_finalize()
                    break

                # Erro Fiscal (Falha ao enviar para SEFAZ) - PopUp (Tentar Novamente ou Cancelar)
                try_again_response = show_messagebox(pos_id, "$ERROR_SEND_NFE|%s" % message, title="$ERROR", icon="error", buttons="Tentar Novamente|Cancelar")

                # 0 -> Tentar Novamente / 1 -> Cancelar
                if try_again_response != 0:
                    cancel_sale_and_payments("Cancelamento solicitado pelo Usuário")
                    break
            except Exception:
                logger.exception("Erro processando CUPOM Fiscal")
                cancel_sale_and_payments("Erro processando CUPOM Fiscal")
                break
            finally:
                close_asynch_dialog(pos_id, dlgid) if dlgid else None
                time.sleep(0.2)
                logger.debug("--- doTender after PROCESSING_FISCAL_DATA ---")

        if is_sangria_enable() and pod_type != "TT":
            doSetDrawerStatus(pos_id, get_drawer_amount(pos_id, period, session), xml_order.get("state"), get_custom(model, "sangria_level_1_alert"))
        doShowScreen(pos_id, "main")

    except OrderTakerException as ex:
        if isinstance(ex, OrderTakerException):
            if handle_order_taker_exception(pos_id, posot, ex, mbcontext):
                return

        show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                          msgtype="critical")
    finally:
        with lock_tender:
            tendering[int(pos_id)] = False
            close_asynch_dialog(pos_id, dlgid) if dlgid else None

    logger.debug("--- doTender END ---")


def void_order(pos_id, lastpaidorder=0, order_id='', abandon=0):
    model = get_model(pos_id)
    posot = get_posot(model)

    order_id = int(order_id) if order_id != "" else ""
    posot.voidOrder(int(pos_id), int(lastpaidorder), order_id, abandon)


@action
def doUpdateOpenTabs(pos_id, *args):
    change_screen(pos_id, "600")

# END doUpdateOpenTabs


@action
def doSendOrderToProduction(pos_id, order_id):
    dlg_id = show_messagebox(pos_id, message="$PLEASE_WAIT", title="Produzindo Pedido", icon="info", buttons="", asynch=True)
    try:
        msg = mbcontext.MB_EasySendMessage("RemoteOrder", TK_REMOTE_ORDER_SEND_ORDER_TO_PRODUCTION, FM_PARAM, str(order_id))
        if msg.token == TK_SYS_ACK:
            show_info_message(pos_id, "Pedido Enviado para Produção", msgtype="info")
        else:
            show_messagebox(pos_id, message="Erro Enviado Pedido para Produção", icon="error")
            #show_info_message(pos_id, "Erro Enviado Pedido para Produção", msgtype="error")
    finally:
        if dlg_id != -1:
            close_asynch_dialog(pos_id, dlg_id)


def verify_and_fix_business_period(pos_id):
    model = get_model(pos_id)
    operator = get_current_operator(model)

    opened_users = list_users(pos_id)

    if operator is not None and len(opened_users) == 0:
        conn = None
        try:
            conn = persistence.Driver().open(mbcontext, pos_id)
            conn.query("""UPDATE PosState SET BusinessPeriod = (SELECT MAX(BusinessPeriod) FROM UserCount WHERE POSId = '{0}' AND CloseTime is NULL) WHERE POSId = '{0}' """.format(pos_id))
            logger.debug("Fix Business Period - POS {0} %s".format(pos_id))
        except:
            sys_log_exception("Error in Fix Business Period")
            logger.debug("Error in Fix Business Period - POS {0} %s".format(pos_id))
        finally:
            if conn:
                conn.close()

        change_mainscreen(pos_id, "500", persist=True)

        def thread_restart_posctrl(pos_id):
            try:
                time.sleep(0.1)
                mbcontext.MB_EasySendMessage("POS%d" % int(pos_id), TK_CMP_TERM_NOW, timeout=600000000)
            except:
                logger.exception("Erro reiniciando Posctrl")

        from threading import Thread
        restart_posctrl_thread = Thread(target=thread_restart_posctrl, args=(pos_id,))
        restart_posctrl_thread.deamon = True
        restart_posctrl_thread.start()
        return False
    return True


def verify_and_fix_opened_users(pos_id):
    model = get_model(pos_id)
    operator = get_current_operator(model)

    opened_users = list_users(pos_id)

    if operator is None and len(opened_users) > 0:
        conn = None
        try:
            conn = persistence.Driver().open(mbcontext, pos_id)
            conn.query("""UPDATE UserCount SET CloseTime = (SELECT MAX(OpenTime) FROM UserCount WHERE POSId = '{0}') WHERE POSId = '{0}' AND CloseTime is NULL""".format(pos_id))
            logger.debug("Fix Opened User - POS {0} %s".format(pos_id))
        except:
            sys_log_exception("Error in Fix Opened User")
            logger.debug("Error in Fix Opened User - POS {0} %s".format(pos_id))
        finally:
            if conn:
                conn.close()


@action
def closeday(pos_id, store_wide="false", *args):
    """
    Closes a business day
    @param store_wide: "true" for store-wide operations
    """
    model = get_model(pos_id)
    if store_wide == "false":
        check_business_day(pos_id, model=model)
        verify_and_fix_opened_users(pos_id)
        check_operator_logged(pos_id, model=model, need_logged=False)

    if not get_nf_type(pos_id) == "PAF":
        cancel_saved_orders = get_storewide_config("Store.cancelSavedOrders", defval="false").lower() == "true"

        if cancel_saved_orders:
            posot = get_posot(model)

            orig_id = "POS00{:02d}".format(int(pos_id))
            orders = posot.listOrders(state="STORED", originatorid=orig_id)

            if len(orders) > 0:
                pedidos = show_confirmation(pos_id, message="Deseja apagar todos os pedidos salvos neste POS?", buttons="Sim|Não")

                if pedidos:
                    wait_dlg_id = show_messagebox(pos_id, "$VOIDING_STORED_ORDERS", "$DAY_CLOSURE", buttons="", asynch=True)
                    try:
                        for order in orders:
                            orig_id = int(order.get("originatorId")[3:])
                            if orig_id == int(pos_id):
                                void_order(pos_id, order_id=order.get("orderId"))
                    except Exception:
                        sys_log_exception("Erro ao apagar pedidos salvos")
                        show_messagebox(pos_id, message="Erro ao apagar pedidos salvos", icon="error")
                        #show_info_message(pos_id, "Erro ao apagar pedidos salvos", msgtype="error")
                    finally:
                        close_asynch_dialog(pos_id, wait_dlg_id)

    period = get_business_period(model)
    period_fmt = format_date(period)
    posnumbers = tuple(poslist) if (store_wide.lower() == "true") else (pos_id,)

    # Checking if all registers can be closed
    cannot_close = []
    poslist_new = []

    if len(posnumbers) > 1:
        for x in posnumbers:
            model_x = get_model(x)
            x_period = get_business_period(model_x)
            if x_period == "0":
                # POS not initialized
                cannot_close.append(translate_message(model, "DAY_CLOSE_NOT_INITIALIZED", "%02d" % int(x)))
                continue

            if period != x_period:
                # Different Business day
                cannot_close.append(translate_message(model, "DAY_CLOSE_DIF_BUSINESS_DAY", "%02d" % int(x), format_date(x_period)))
                continue

            if model_x.find("PosState").get("state") == "CLOSED":
                # Day is already closed
                cannot_close.append(translate_message(model, "DAY_CLOSE_ALREADY_CLOSED", "%02d" % int(x), format_date(x_period)))
                continue

            if has_operator_opened(model_x):
                # Operator logged in
                cannot_close.append(translate_message(model, "DAY_CLOSE_OPER_LOGGED", "%02d" % int(x), format_date(x_period)))
                continue

            # All checks OK
            poslist_new.append(x)

    if len(cannot_close) > 0:
        pos_nok = ""
        for opt in sorted(cannot_close):
            pos_nok += "%s\\" % (opt)

        if not is24HoursStore:
            # For non-24hours stores, does not allow partial close
            poslist_new = []

        message = ("$REGISTERS_NOT_CLOSED_CONFIRM|%s" % (pos_nok)) if poslist_new else ("$REGISTERS_NOT_CLOSED|%s" % (pos_nok))
        options = ("$CANCEL", "$CLOSE_OTHER_REGISTERS") if poslist_new else ("$CANCEL",)
        icon = "question" if poslist_new else "error"
        question = show_messagebox(pos_id, message=message, icon=icon, buttons="|".join(options))
        if (question is None) or (question == 0):
            return  # User cancelled, or timeout

        posnumbers = poslist_new

    # Special protection against closing "today's business day"
    today = datetime.datetime.now().strftime("%Y%m%d")
    if period == today:
        if int(datetime.datetime.now().strftime("%H"), 10) < 17:
            # Ultra-special protection against closing today before 17:00
            message = "$CLOSE_DAY_WARNING_TODAY|%s|%s" % (period_fmt, period_fmt)
        else:
            message = "$CLOSE_DAY_WARNING|%s|%s" % (period_fmt, period_fmt)

        confirm = show_confirmation(pos_id, message=message, title="Alerta", icon="warning", buttons="$CLOSE_DAY_DONT_CLOSE|$CLOSE_DAY_CLOSE_ANYWAY")
        if confirm is None or confirm:
            # Note that the buttons have been inverted on purpose on this confirmation - so True means "cancel"
            return

    else:  # Regular confirmation message
        message = "$CLOSE_DAY_CONFIRM|%s|%s" % (period_fmt, period_fmt)
        if not show_confirmation(pos_id, message=message):
            return

    wait_dlg_id = show_messagebox(pos_id, "$PLEASE_WAIT", "$DAY_CLOSURE", buttons="", asynch=True)
    try:
        posnumbers = sorted(posnumbers)
        sys_log_info("Closing business day. [Store-wide: %s] posnumbers: %s" % (store_wide, posnumbers))
        # pos_ok = []
        error = None
        for posno in posnumbers:
            try:
                sys_log_info("Closing business day on POS id: [%s]" % posno)
                msg = send_message("POS%d" % int(posno), TK_POS_BUSINESSEND, FM_PARAM, "%s" % (posno), timeout=600 * USECS_PER_SEC)
                if msg.token == TK_SYS_ACK:
                    # pos_ok.append(posno)
                    if not (get_nf_type(pos_id) == "PAF" and today != period):
                        report = generate_report("cash", posno, period, "0", "false", "0", "end_of_day")
                        close_asynch_dialog(pos_id, wait_dlg_id)
                        if report and get_podtype(model) != "OT":
                            print_text(pos_id, model, report, preview=True, force_printer=get_used_service(get_model(posno), "printer"))
                        else:
                            sys_log_exception("Error printing day-close report for POS ID: %s" % posno)

                    wait_dlg_id = show_messagebox(pos_id, "$PLEASE_WAIT", "$DAY_CLOSURE", buttons="", asynch=True)
                    show_info_message(posno, "$OPERATION_SUCCEEDED", msgtype="success")
                    if period[6:] == "01" and get_nf_type(posno) == "PAF":
                        #  End of the first day of the month. We should generate the MF and MFD files
                        show_info_message(posno, "Aguarde, gerando arquivos MF e MFD", msgtype="warning")
                        try:
                            from pafecf import pafecf_actions
                            pafecf_actions.pafArquivo(posno, "MF")
                            pafecf_actions.pafArquivo(posno, "MFD")
                            show_info_message(posno, "$OPERATION_SUCCEEDED", msgtype="success")
                        except Exception as ex:
                            show_info_message(posno, message="Ocorreu um erro: %s" % str(ex), msgtype="error")
                    continue
                else:
                    error = str(msg.data)
            except Exception:
                sys_log_exception("Error closing business day on pos id: %s" % posno)

            show_info_message(posno, "$OPERATION_FAILED", msgtype="error")
            show_messagebox(pos_id, message="$ERROR_CLOSING_BUSINESS_PERIOD|%s" % error, icon="error")
            #show_info_message(pos_id, "$ERROR_CLOSING_BUSINESS_PERIOD|%s" % error, msgtype="error")
    finally:
        close_asynch_dialog(pos_id, wait_dlg_id)


def is_last_opened_pos(posid):
    STATE_OPENED = "2"
    for pos in sysactions.get_poslist():
        if str(pos) == posid:
            continue
        msg = mbcontext.MB_EasySendMessage("POS%d" % pos, TK_POS_GETSTATE, FM_PARAM, str(pos))
        if msg.token == TK_SYS_ACK:
            period, state = msg.data.split('\0')[:2]
            if state == STATE_OPENED:
                return False
    return True


@action
def doVoidStoredOrder(pos_id, order_id="", orig_id="", void_reason=6, *args):
    dlg_id = None
    try:
        dlg_id = show_messagebox(pos_id, message="$PLEASE_WAIT", title="Apagando pedido salvo", icon="info", buttons="", asynch=True)
        model = get_model(pos_id)
        posot = get_posot(model)
        if void_order_authorization:
            close_asynch_dialog(pos_id, dlg_id) if dlg_id else None
            if not get_authorization(pos_id, min_level=LEVEL_SUPERVISOR, model=model, insert_auth=True, order_id=order_id, display_title="$ORDER_CANCEL"):
                return
            dlg_id = show_messagebox(pos_id, message="$PLEASE_WAIT", title="Apagando pedido salvo", icon="info", buttons="", asynch=True)
        void_reason = get_void_reason_id(pos_id, void_reason)
        if not void_reason:
            return

        if get_nf_type(pos_id) == "PAF":
            do_recall_order(pos_id, order_id, check_date=False)
            posot.doTotal(pos_id)
            void_order(pos_id, lastpaidorder=1)
        else:
            do_recall_order(pos_id, order_id, check_date=False)
            void_order(pos_id)

        posot.setOrderCustomProperties(void_reason, order_id)

        show_info_message(pos_id, "Pedido salvo apagado", msgtype="success")
    except Exception as _:
        show_info_message(pos_id, "Erro ao tentar apagar pedido salvo", msgtype="error")
        sys_log_exception("Erro ao apagar pedido salvo")
    finally:
        close_asynch_dialog(pos_id, dlg_id) if dlg_id else None

    doUpdateOpenTabs(pos_id)


@action
def doRecallNext(pos_id, screen_number="", order_id="", totalize=False, originator_pos_id=None, order_business_period=None, *args):
    logger.debug("Recall pedido - Order %s - PosId %s" % (order_id, pos_id))

    global lock_recall
    with lock_recall:
        global recalling
        if order_id in recalling:
            show_info_message(pos_id, "Pedido número %s já recuperado em outro caixa" % order_id, msgtype="critical")
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
            current_business_day = datetime.datetime.strptime(get_business_period(model), "%Y%m%d")
            order_business_period = datetime.datetime.strptime(order_business_period, "%Y%m%d")

            if current_business_day > order_business_period:
                if show_confirmation(pos_id, message="Pedido salvo em dia de negócio anterior ao atual. Recupere-o em outro caixa ou apague-o.", buttons="Apagar|$CANCEL"):
                    try:
                        do_recall_order(pos_id, order_id)
                        void_order(pos_id)
                        change_screen(pos_id, "600", "")  # Show tender screen
                    except BaseException as _:
                        sys_log_exception("Erro ao apagar pedido")
                        logger.debug("Erro void order recall pedido - Order %s - PosId %s" % (order_id, pos_id))
                        show_info_message(pos_id, "Erro ao tentar apagar pedido", msgtype="error")
                return

            if order_business_period > current_business_day:
                show_messagebox(pos_id, "Pedido foi salvo em um dia de negócio posterior ao atual. Por favor abra um novo dia de negócio.")
                logger.debug("Recall pedido foi salvo em um dia de negócio posterior ao atual - Order %s - PosId %s" % (order_id, pos_id))
                return

            check_operator_logged(pos_id, model=model, can_be_blocked=False)
            check_current_order(pos_id, model=model, need_order=False)

        period = get_business_period(model)
        session = get_operator_session(model)

        if is_sangria_enable():
            if doSetDrawerStatus(pos_id, get_drawer_amount(pos_id, period, session)):
                logger.debug("Recall pedido sangria - Order %s - PosId %s" % (order_id, pos_id))
                return

        dlg_id = -1
        try:
            dlg_id = show_messagebox(pos_id, message="$PLEASE_WAIT", title="Recuperando pedido", icon="info", buttons="", asynch=True)
            do_recall_order(pos_id, order_id, originator_pos_id)
            logger.debug("Pedido Totalizado - Order %s" % order_id)

            if totalize == 'true':
                doTotal(pos_id, screen_number, dlg_id, True, *args)

            logger.debug("Recall finalizado - Order %s - PosId %s" % (order_id, pos_id))
        except OrderTakerException as e:
            screen_number = "600"  # Update to the same Screen

            if get_nf_type(pos_id) == "PAF":
                show_info_message(pos_id, "Erro ao recuperar pedido: %s" % (e.getErrorDescr()),msgtype="critical")
                logger.debug("Erro ao recuperar pedido - Order %s - PosId %s - %s" % (order_id, pos_id,
                                                                                      e.getErrorDescr()))
            else:
                show_info_message(pos_id, "Pedido número %s já recuperado em outro caixa" % order_id, msgtype="critical")
                logger.debug("Recall pedido já recuperado em outro caixa - Order %s - PosId %s" % (order_id, pos_id))
                
            sys_log_info("$ERROR_CODE_INFO|%d|%s - POS %s" % (e.getErrorCode(), e.getErrorDescr(), pos_id))
        except Exception as ex:
            sys_log_exception("Erro recuperando pedido - %s" % str(ex))
            logger.debug("Recall error - Order %s - PosId %s" % (order_id, pos_id))
        finally:
            if dlg_id != -1:
                close_asynch_dialog(pos_id, dlg_id)
            if screen_number:
                # Show tender screen
                change_screen(pos_id, screen_number, "")

    finally:
        with lock_recall:
            if order_id in recalling:
                recalling.remove(order_id)


def do_recall_order(pos_id, order_id, originator_pos_id=None, check_date=True):
    model = get_model(pos_id)
    posot = get_posot(model)
    session = get_operator_session(model)
    if originator_pos_id:
        recall_pos = int(originator_pos_id[4:])
        try:
            posot.recallOrder(int(pos_id), int(order_id), session, sourceposid=str(recall_pos))
        except OrderTakerException as e:
            sys_log_info("Pedido nao encontrado no banco de origem. Procurando nos demais bancos")
            logger.exception("Error recalling order {}".format(order_id))
            posot.recallOrder(int(pos_id), int(order_id), session)
    else:
        posot.recallOrder(int(pos_id), int(order_id), session)
    logger.debug("Pedido Recuperado do MW-Core - Order %s" % order_id)

    # Waits a maximum of 5 seconds for the order to "arrive" at the POS model
    timelimit = (time.time() + 5.0)
    while (time.time() < timelimit) and (not has_current_order(get_model(pos_id))):
        time.sleep(0.1)

    logger.debug("Order Carregado no MW-Core - Order %s" % order_id)
    model = get_model(pos_id)
    order = model.find("CurrentOrder/Order")

    if check_date is True:
        # Cannot recall order older than 20 hours
        now = datetime.datetime.now()
        order_created_date = datetime.datetime.strptime(order.get("createdAt"), "%Y-%m-%dT%H:%M:%S.%f")
        if order_created_date < now - timedelta(hours=20):
            show_messagebox(pos_id, "$CANNOT_RECALL_ORDER_TOO_OLD", title="$ERROR", icon="error", buttons="$OK")
            void_order(pos_id)
            screen_number = "600"  # Update to the same Screen
            return

    sale_lines = order.findall("SaleLine")
    deleted_line_numbers = map(lambda x: x.get("lineNumber"),
                               filter(lambda x: x.get("level") == "0" and x.get("qty") == "0", sale_lines))
    active_sale_lines = filter(
        lambda x: x.get("lineNumber") not in deleted_line_numbers and _cache.get_tags_as_dict(x.get("partCode"), "Ingredients"), sale_lines)

    pod_type = get_podtype(model)
    queries = []
    for line in active_sale_lines:
        temp_query = []
        line_number = line.get("lineNumber")
        update_options_and_defaults(temp_query, order_id, line_number, line.get("itemId"), line.get("partCode"), line.get("qty"), int(line.get("level")), pod_type)
        temp_query = filter(lambda x: "DefaultQty = 0" not in x, temp_query)

        queries.extend(temp_query)

    for line_number in deleted_line_numbers:
        queries.append("""UPDATE orderdb.CurrentOrderItem SET OrderedQty = 0 where OrderId = %(order_id)s AND LineNumber = %(line_number)s""" % locals())

    queries.append("""UPDATE orderdb.CurrentOrderItem SET DefaultQty = 0 WHERE OrderId = %(order_id)s AND DefaultQty is NULL""" % locals())
    logger.debug("Queries Prontas - Order %s" % order_id)

    if queries:
        conn = None
        try:
            conn = DBDriver().open(mbcontext, dbname=str(pos_id))
            conn.transaction_start()
            conn.query('''BEGIN TRANSACTION;''')
            conn.query(";".join(queries))
            conn.query('''COMMIT TRANSACTION;''')
        except Exception as ex:
            if conn:
                conn.query('''ROLLBACK TRANSACTION;''')
            raise ex
        finally:
            if conn:
                conn.close()

    logger.debug("Produtos Default Incluidos no Pedido - Order %s" % order_id)

    # Update Custom Properties to Show DB Changes on POS
    posot.updateOrderProperties(pos_id, saletype=order.get("saleTypeDescr"))
    logger.debug("Propriedades Alteradas - Order %s" % order_id)


@action
def showRecallByPicture(posid, screenNumber="", *args):
    model = get_model(posid)
    posot = get_posot(model)
    podtype = str(get_podtype(model))
    # Subscribe this POS to "listen" to store and recall operations
    _recall_listeners.add(posid)
    try:
        # Lists all stored orders for our POD type
        orders = posot.listOrders(state="STORED", podtype=podtype)
        if orders:
            # Joins all order ids on a pipe-separated string (E.g.: "30|35|36")
            order_ids = "|".join([order["orderId"] for order in orders])
            xml = posot.orderPicture(orderid=order_ids)
        else:
            xml = ""
        # Now we have the full order picture of each order (or an empty xml)
        send_message("POS%d" % int(posid), TK_POS_SETRECALLDATA, FM_PARAM, "%s\0%s" % (posid, xml), timeout=600 * USECS_PER_SEC)
    except OrderTakerException as ex:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                          msgtype="critical")
    if screenNumber:
        # Show the recall-by-picture screen
        doShowScreen(posid, screenNumber)


def get_void_reason_id(pos_id, selected_index=None):
    void_reason_ids = range(1, 8)
    void_reason_options = ["1 - Mudou de Ideia",
                           "2 - Duplicado",
                           "3 - Venda Errada",
                           "4 - Cancelamento",
                           "5 - Cupom Cancelado",
                           "6 - Pagamento Cancelado",
                           "7 - Pedido Salvo Cancelado"]
    void_reason_to_show = void_reason_options[0:4]
    if not selected_index:
        selected_index = show_listbox(pos_id, void_reason_to_show, message="Selecione o Motivo:")

    if selected_index is None:
        return None

    void_reason_id = void_reason_ids[int(selected_index)]
    void_reason_descr = void_reason_options[int(selected_index)]
    void_reason_dict = {'VOID_REASON_ID': void_reason_id, 'VOID_REASON_DESCR': void_reason_descr}
    return void_reason_dict


@action
def doVoidSale(pos_id, getAuthorization="False", void_reason=None, force_close="False", *args):
    logger.debug("--- doVoidSale START ---")
    if not pafecflistenter_component_found(pos_id):
        return

    force_close = force_close.lower() == "true"
    if force_close and not void_last_order_btn:
        # fake message
        show_info_message(pos_id, "Erro 27: Não foi possível cancelar o pedido", msgtype="error")
        return

    model = get_model(pos_id)
    posot = get_posot(model)

    # eLanes Ticket #23 (Don't allow the void of a closed order)5813
    if not force_close:
        check_current_order(pos_id, model, need_order=True)
    order = get_current_order(model)
    dlgid = None
    try:
        logger.debug("--- doVoidSale before popup 'Processando cupom fiscal' ---")

        dlgid = show_messagebox(pos_id, "$PROCESSING_FISCAL_DATA", title="$PROCESSING", buttons="", asynch=True, timeout=180000) if get_nf_type(pos_id) == "PAF" else None
        if not order:
            return
        if order.get("state") in ("IN_PROGRESS", "TOTALED"):
            lastorder = 0
        elif order.get("state") in ("PAID",):
            lastorder = 1
        else:
            show_info_message(pos_id, "Pedido não encontrado ou já cancelado", msgtype="warning")
            return

        logger.debug("--- doVoidSale before popup authorizathion and reason ---")
        if void_order_authorization:
            if not get_authorization(pos_id, min_level=LEVEL_SUPERVISOR, model=model, insert_auth=True, display_title="$ORDER_CANCEL"):
                return

        # Let the user select a void reason ...
        void_reason = get_void_reason_id(pos_id, void_reason)
        if not void_reason:
            return
        logger.debug("--- doVoidSale after popup authorizathion and reason ---")

        if lastorder and get_nf_type(pos_id) != "PAF":
            msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_CANCEL_ORDER, format=FM_PARAM, data=pos_id)
            if not msg.token == TK_SYS_ACK:
                show_info_message(pos_id, "$ERROR_CANCEL_ORDER", msgtype="error")
                return
            else:
                show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")

        logger.debug("--- doVoidSale before posot.voidOrder ---")
        void_order(pos_id, lastpaidorder=lastorder)
        logger.debug("--- doVoidSale after posot.voidOrder ---")

        posot.setOrderCustomProperties(void_reason, order.get('orderId'))

        if force_close:
            show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")
        else:
            doShowScreen(pos_id, "main")  # Returns to the previous screen
    except Exception as ex:
        if isinstance(ex, OrderTakerException):
            if handle_order_taker_exception(pos_id, posot, ex, mbcontext):
                return

        show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), msgtype="critical")
    finally:
        if dlgid:
            time.sleep(0.1)
            sysactions.close_asynch_dialog(pos_id, dlgid)
            logger.debug("--- doSale after popup 'Processando cupom fiscal' ---")

    logger.debug("--- doVoidSale END ---")


@action
def doVoidSaleWithAuthorization(posid, *args):
    doVoidSale(posid, "True")


@action
def doVoidSaleWithConfirmation(posid, was_stored=False, *args):
    model = get_model(posid)
    # eLanes Ticket #23 (Don't allow the void of a closed order)
    check_current_order(posid, model, need_order=True)
    order = get_current_order(model)
    if was_stored == "true":
        warning_msg = "Essa venda somente pode ser cancelada no menu do gerente"
        show_info_message(posid, warning_msg, msgtype="warning")
    else:
        try:
            if not order:
                return
            if not show_confirmation(posid, message="Você tem certeza?"):
                return
            get_posot(model).voidOrder(int(posid))
            doShowScreen(posid, "main")  # Returns to the previous screen
        except OrderTakerException as ex:
            show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                              msgtype="critical")


@action
def activateUser(posid, *args):
    current_op = get_current_operator(get_model(posid))
    current_id = current_op.get("id") if current_op else None
    check_business_day(posid, need_opened=True, can_be_blocked=False)
    msg = send_message("POS%d" % int(posid), TK_POS_LISTUSERS, FM_PARAM, "%s" % (posid))
    if msg.token == TK_SYS_NAK:
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        return
    xml = etree.XML(msg.data)
    opened_users = [tag for tag in xml.findall("User") if (not tag.get("closeTime")) and (tag.get("id") != current_id)]
    if not opened_users:
        return
    opened_users.sort(key=lambda tag: tag.get("id"))
    options = ["%s - %s" % (tag.get("id"), (tag.get("name")).encode("utf-8")) for tag in opened_users]
    index = show_listbox(posid, options, message="Selecione um operador para ativar")
    if index is None:
        return  # The user cancelled - or timed-out
    userid = opened_users[index].get("id")
    username = (opened_users[index].get("name")).encode("utf-8")
    passwd = show_keyboard(posid, message="$ENTER_PASSWORD|%s" % userid, title="$USER_AUTHENTICATION", is_password=True, numpad=True)
    if passwd is None:
        return  # User cancelled, or timeout
    if not show_confirmation(posid, message="Confirme operador ativo\%s - %s" % (userid, username)):
        return  # User cancelled, or timeout
    # Verify if the user password is correct
    try:
        userinfo = authenticate_user(userid, passwd)
    except AuthenticationFailed as ex:
        show_info_message(posid, "$%s" % ex.message, msgtype="error")
        return
    longusername = userinfo["LongName"]
    # Login the user
    msg = send_message("POS%d" % int(posid), TK_POS_USERLOGIN, FM_PARAM, "%s\0%s\0%s" % (posid, userid, longusername))
    if msg.token == TK_SYS_NAK:
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        return
    show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
    doShowScreen(posid, "main")


@action
def loginuser(pos_id, *args):
    def _check_user_already_logged(pos_id, user_id):
        sql_query = "SELECT PosId FROM posctrl.UserSession WHERE OperatorId = %s AND CloseTime IS NULL" % user_id

        conn = None
        try:
            conn = DBDriver().open(mbcontext, pos_id)
            is_logged = conn.select(sql_query).get_row(0)
        except Exception:
            sys_log_exception('Exception printing logoff report: {}')
            show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
            return False
        finally:
            if conn:
                conn.close()

        if is_logged:
            pos_temp = is_logged.get_entry("PosId")
            show_info_message(pos_id, "$OPERATOR_ALREADY_LOGGED|%s" % pos_temp, msgtype="error")
            return False

        return True

    model = get_model(pos_id)
    podtype = str(get_podtype(model))
    pos_service = "POS%d" % int(pos_id)

    if get_nf_type(pos_id) == "PAF" and podtype != "OT":
        prn = FpRetry(pos_id, mbcontext)
        ecf_serial = prn.readOut(fpreadout.FR_FPSERIALNUMBER).strip()
        md5_serial = prn.readEncrypted("ECF_Serial")

        if str(md5_serial).strip() != str(ecf_serial).strip():
            sysactions.show_info_message(pos_id, "$SERIAL_PRINTER_VALIDATION_ERROR", msgtype="error")
            time.sleep(3)
            return False

    check_business_day(pos_id, need_opened=True, can_be_blocked=False)

    if has_operator_opened(model):
        # Check if multiple operators are allowed
        multioper = get_cfg(pos_id).key_value("multipleOperators", "false").lower() == "true"
        if not multioper:
            show_info_message(pos_id, "$NEED_TO_LOGOFF_FIRST", msgtype="warning")
            return False

    if podtype == "DT":
        # We are working on "DT" mode, so we need to request a pos function (OT,CS,OT/CS)
        options = ("OT", "CS", "OT/CS", "$CANCEL")
        options_label = ("Speaker", "Caixa", "Completo", "$CANCEL")

        index = show_messagebox(pos_id, message="$SELECT_POS_FUNCTION", title="$OPERATOR_OPENING", icon="question", buttons="|".join(options_label))
        if index is None:
            return  False  # timeout

        posfunction = options[index]
        if posfunction == "$CANCEL":
            return False  # User cancelled

    elif podtype == "OT":
        # We are working on "OT" function, so we need to request a pos mode (DT, "Normal")
        options = ("FC", "DT", "$CANCEL")
        options_label = ("Loja", "Drive", "$CANCEL")

        index = show_messagebox(pos_id, message="$SELECT_POS_FUNCTION", title="$OPERATOR_OPENING", icon="question", buttons="|".join(options_label))
        if index is None:
            return False  # timeout

        if options[index] == "$CANCEL":
            return False  # User cancelled

        podtype = options[index]
        posfunction = "OT"

    elif podtype == "DS":
        podtype = "FC"
        posfunction = "DS"

    else:
        posfunction = ""

    user_id = None
    try:
        ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(pos_id), bustoken.TK_FPR_OK)
        if ret.token == TK_SYS_ACK:
            # Temos o leitor e ele esta operacional, vamos pedir as impressoes do usuario
            ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(pos_id), bustoken.TK_FPR_IDENTIFY_USER, format=FM_PARAM, data=pos_id)
            if ret.token != TK_SYS_ACK:
                # Erro cadastrando impressao digital
                show_info_message(pos_id, "Erro realizando a leitura da digital. Tente novamente.", msgtype="error")
                return False
            elif ret.data == "":
                # Leitura da impressao OK mas usuario nao cadastrado
                show_info_message(pos_id, "Usuário não identificado a partir da digital. Tente novamente.", msgtype="error")
                return False
            else:
                if _check_user_already_logged(pos_id, ret.data) is False:
                    return False
    except MBException as ex:
        if ex.errorcode == 2:  # NOT_FOUND, servico de FingerPrint nao disponivel
            sys_log_info("Servico de FingerPrint Não Disponível")
        else:
            sys_log_exception("Erro get_user_information - %s" % str(ex))

    if user_id is None:
        # Request user ID and password to GUI
        user_id = show_keyboard(pos_id, "$ENTER_USER_ID", title="$OPERATOR_OPENING", mask="INTEGER", numpad=True)
        if user_id in (None, ""):
            return False  # User cancelled, or timeout
        user_id = int(user_id, 10)

        if _check_user_already_logged(pos_id, user_id) is False:
            return False

        passwd = show_keyboard(pos_id, message="$ENTER_PASSWORD|%s" % user_id, title="$OPERATOR_OPENING", is_password=True, numpad=True)
        if passwd is None:
            return False  # User cancelled, or timeout

        # Verify if the user id/password is correct
        try:
            userinfo = authenticate_user(user_id, passwd)
        except AuthenticationFailed as ex:
            show_info_message(pos_id, "$%s" % ex.message, msgtype="error")
            return False
    else:
        try:
            user_xml_str = get_user_information(user_id)
        except Exception as ex:
            show_info_message(pos_id, "Impressao digital associada a usuario que nao esta cadastrado", msgtype="error")
            sys_log_exception("Erro get_user_information - %s" % str(ex))
            return False

        # Se identificamos o usuario pela digital, pegamos a informacao dele e constuimos o objeto igual a autenticacao por usuario e senha faz
        if user_xml_str is None:
            show_info_message(pos_id, "Impressao digital associada a usuario que nao esta cadastrado", msgtype="error")
            return False

        user_xml = etree.XML(user_xml_str)
        user_element = user_xml.find("user")
        userinfo = {
            'Level': user_element.attrib["Level"],
            'UserName': user_element.attrib["UserName"],
            'LongName': user_element.attrib["LongName"]
        }

    longusername = userinfo["LongName"]

    # Request initial float to user, if not an order-taker
    list_min_values_drawer = get_storewide_config("Store.MinValuesDrawer", defval="0;50;100")

    if podtype != "OT" and posfunction != "OT":
        list_limits = [("R$%.2f" % int(x)).replace(".", ",") for x in list_min_values_drawer.split(";")]
        index = show_listbox(pos_id, list_limits, message="$ENTER_THE_INITIAL_FLOAT_AMOUNT", title="$OPERATOR_OPENING", buttons="$OK|$CANCEL", icon="info", timeout=720000)

        if index is None:
            return False  # User cancelled, or timeout

        initfloat = list_min_values_drawer.split(";")[index]
        initfloat = float(initfloat or 0.0)
    else:
        initfloat = 0.0

    if int(userinfo["Level"] or 0) < LEVEL_SUPERVISOR:
        # verificar autorização do gerente
        if not get_authorization(pos_id, min_level=LEVEL_SUPERVISOR, model=model, display_title="$OPERATOR_OPENING"):
            return False

    wait_dlg_id = show_messagebox(pos_id, "$PLEASE_WAIT", "$OPERATOR_OPENING", buttons="", asynch=True)
    try:
        # Send the open command to POS Controller
        msg = send_message(pos_service, TK_POS_USEROPEN, FM_PARAM, "%s\0%s\0%s\0%s" % (pos_id, user_id, initfloat, longusername), timeout=600 * USECS_PER_SEC)
        if msg.token == TK_SYS_NAK:
            show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
            return False

        # Send the login command to POS Controller

        msg = send_message(pos_service, TK_POS_USERLOGIN, FM_PARAM, "%s\0%s\0%s" % (pos_id, user_id, longusername), timeout=600 * USECS_PER_SEC)
        if msg.token == TK_SYS_NAK:
            show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
            return False

        if posfunction == "DS":
            check_main_screen(pos_id)

        send_message(pos_service, TK_POS_SETPOD, FM_PARAM, "%s\0%s\0" % (pos_id, podtype), timeout=600 * USECS_PER_SEC)
        send_message(pos_service, TK_POS_SETFUNCTION, FM_PARAM, "%s\0%s\0" % (pos_id, posfunction), timeout=600 * USECS_PER_SEC)

        if get_nf_type(pos_id) == "PAF":
            mbcontext.MB_EasySendMessage("PafEcfListener", token=TK_POS_FUNCTION_CHANGED, format=FM_PARAM, data=str(pos_id))

        # Check the main screen for this POD and POS Function
        if posfunction != "DS":
            check_main_screen(pos_id)

        try:
            time.sleep(1)
            mbcontext.MB_EasySendMessage("DailyGoals", TK_DAILYGOALS_UPDATE_GOALS)
        except MBException as e:
            if e.errorcode == 2:  # NOT_FOUND, servico de DailyGoals nao disponivel
                sys_log_info("[DailyGoals] Serviço Não Encontrado")
            else:
                sys_log_exception("[DailyGoals] Erro {}".format(e.errorcode))
        except Exception:
            sys_log_exception("[DailyGoals]")

        if podtype != "OT" and posfunction != "OT":
            conn = None
            if float(initfloat) == 0:
                try:
                    conn = persistence.Driver().open(mbcontext, pos_id)
                    session_initial = get_operator_session(get_model(pos_id))
                    sql = "insert into Transfer (Period, PosId, SessionId, Type, Description, Amount, TenderId) values ({}, {}, '{}', 1, 'Initial Float', '0.0', 0);".format(datetime.datetime.now().strftime('%Y%m%d'), pos_id, session_initial)

                    conn.query(sql)
                except Exception:
                    pass
                finally:
                    if conn:
                        conn.close()

            if int(initfloat) > 0:
                doOpenDrawer(pos_id)

        operator = get_current_operator(get_model(pos_id))
        operator_name = (operator.get("name")).encode('utf-8')
        operator_id = operator.get("id")
        initial_float = operator.get("initialFloat")
        period = get_business_period(model)
        close_asynch_dialog(pos_id, wait_dlg_id)
        if posfunction != "OT":
            print_report(pos_id, model, True, "loginOperator_report", pos_id, operator_id, operator_name, initial_float, period)
        doShowScreen(pos_id, "main")
        show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")

        # Enable the eLanes void security model again if necessary
        set_custom(pos_id, "VOIDAUTH_SESSION_DISABLED", "false", persist=True)

        # Processamento Finalizado com Sucesso
        save_signedin_user(pos_id, user_id, userinfo)
    finally:
        close_asynch_dialog(pos_id, wait_dlg_id)

    return True


def list_users(pos_id):
    msg = send_message("POS%d" % int(pos_id), TK_POS_LISTUSERS, FM_PARAM, "%s" % pos_id, timeout=600 * USECS_PER_SEC)
    if msg.token == TK_SYS_NAK:
        logger.error("Logoff POS %d - Erro obtendo lista de operadores logados." % int(pos_id))
        raise Exception("Fail listing Operators")

    xml = etree.XML(msg.data)
    opened_users = [tag for tag in xml.findall("User") if not tag.get("closeTime")]
    return opened_users

@action
def logoffuser(pos_id, *args):
    logger.debug("Logoff POS %d - Iniciando logoff." % int(pos_id))
    if not verify_and_fix_business_period(pos_id):
        return False

    model = get_model(pos_id)
    posot = get_posot(model)
    session_id = get_operator_session(model)
    set_custom(pos_id, "Last SessionId", session_id, persist=True)
    check_current_order(pos_id, model=model, need_order=False)

    try:
        opened_users = list_users(pos_id)
    except:
        show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
        return False

    if not opened_users:
        logger.debug("Logoff POS %d - Não há operadores logados." % int(pos_id))
        show_info_message(pos_id, "$THERE_ARE_NO_OPENED_USERS", msgtype="warning")
        return False

    if len(opened_users) > 1:
        opened_users.sort(key=lambda x: x.get("id"))
        options = [("%s - %s" % (tag.get("id"), tag.get("name"))).encode('utf-8') for tag in opened_users]
        index = show_listbox(pos_id, options)
        if index is None:
            return False  # The user cancelled - or timed-out

        userid = opened_users[index].get("id")
    else:
        userid = opened_users[0].get("id")
        logger.debug("Logoff POS %d - Obtido id do operador - %s" % (int(pos_id), userid))

    # verificar autorização do gerente
    if not get_authorization(pos_id, min_level=LEVEL_SUPERVISOR, model=model, is_login=False, display_title="$OPERATOR_CLOSURE"):
        return False

    has_to_do_transfer = True
    pod_function = get_posfunction(model) if get_podtype(model) in ("DT", "FC") else get_podtype(model)
    if pod_function == "OT":
        has_to_do_transfer = False
    if has_to_do_transfer:
        declared_amount = doTransfer(pos_id, 6)
        if not declared_amount:
            return False

    wait_dlg_id = show_messagebox(pos_id, "$PLEASE_WAIT", "$OPERATOR_CLOSURE", buttons="", asynch=True)
    try:
        pos_service = "POS%d" % int(pos_id)
        original_podtype = str(get_cfg(pos_id).find_value("pod"))
        send_message(pos_service, TK_POS_SETPOD, FM_PARAM, "%s\0%s\0" % (pos_id, original_podtype), timeout=600 * USECS_PER_SEC)

        logger.debug("Logoff POS %d - Deslogando operador %s" % (int(pos_id), userid))
        msg = send_message("POS%d" % int(pos_id), TK_POS_USERLOGOUT, FM_PARAM, "%s\0%s" % (pos_id, userid), timeout=600 * USECS_PER_SEC)
        if msg.token == TK_SYS_ACK:
            logger.debug("Logoff POS %d - Operador %s deslogado com sucesso" % (int(pos_id), userid))
            posot.resetCurrentOrder(pos_id)
            period = get_business_period(model)

            # Restore the default main screen
            change_mainscreen(pos_id, "0", persist=True)

            # Enable the eLanes void security model again if necessary
            set_custom(pos_id, "VOIDAUTH_SESSION_DISABLED", "false", persist=True)
            clear_custom(pos_id, SIGNED_IN_USER)

            change_screen(pos_id, "500")
            # print_report(posid, model, True, "cash_over_short_op_report", posid, period, userid)
            close_asynch_dialog(pos_id, wait_dlg_id)

            if get_posfunction(model) != "OT":
                print_report(pos_id, model, True, "checkout_report", pos_id, period, userid, "False", "0", "logoffuser", session_id)
            show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")
        else:
            logger.error("Logoff POS %d - Falha ao deslogar operador %s" % (int(pos_id), userid))
            show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
    finally:
        close_asynch_dialog(pos_id, wait_dlg_id)

    return True


@action
def doOpenDrawer(posid, check_oper="true", *args):
    def thread_open_drawer(drawer):
        try:
            send_message(drawer.get("name"), TK_CDRAWER_OPEN)
            show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
        except MBException:
            show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
            pass

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
        return  # User canceled
    printername = options[index]
    msg = send_message("POS%d" % int(posid), TK_POS_SETDEFSERVICE, FM_PARAM, "%s\0printer\0%s" % (posid, printername))
    if msg.token == TK_SYS_ACK:
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
    else:
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")


@action
def doVoidLine(pos_id, lineNumbers = None, *args):
    if not lineNumbers:
        return

    model = get_model(pos_id)
    check_current_order(pos_id, model=model, need_order=True)

    # Check if the line selected is ready to void or not
    if not can_void_line(model, lineNumbers):
        show_info_message(pos_id, "$NEED_TO_HAVE_ITEM_TO_VOID", msgtype="error")
        return
    dlgid = None
    try:
        if void_line_authorization:
            if not get_authorization(pos_id, min_level=LEVEL_SUPERVISOR, model=model, insert_auth=True, display_title="$ORDER_LINE_CANCEL"):
                return
        dlgid = show_messagebox(pos_id, "$PROCESSING_FISCAL_DATA", title="$PROCESSING", buttons="", asynch=True, timeout=180000) if get_nf_type(pos_id) == "PAF" else None
        get_posot(model).voidLine(int(pos_id), lineNumbers)
    except OrderTakerException as ex:
        show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                          msgtype="critical")
    except BaseException as _:
        show_info_message(pos_id, "$FISCAL_PRINTER_COMM_ERROR", msgtype="critical")
    finally:
        if dlgid:
            time.sleep(0.1)
            close_asynch_dialog(pos_id, dlgid)


@action
def doVoidLineWithAuthorization(posid, lineNumbers, *args):
    if not lineNumbers:
        return
    model = get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    if not can_void_line(model, lineNumbers):  # Check if the line selected is ready to void or not
        show_info_message(posid, "$NEED_TO_HAVE_ITEM_TO_VOID", msgtype="error")
        return
    if get_authorization(posid, min_level=LEVEL_SUPERVISOR, model=model, display_title="$ORDER_LINE_CANCEL"):
        doVoidLine(posid, lineNumbers)


@action
def doVoidLineCheckAuthorization(posid, lineNumbers, *args):
    if not lineNumbers:
        return
    model = get_model(posid)
    check_current_order(posid, model=model, need_order=True)
    if not can_void_line(model, lineNumbers):  # Check if the line selected is ready to void or not
        show_info_message(posid, "$NEED_TO_HAVE_ITEM_TO_VOID", msgtype="error")
        return

    conn = None
    try:
        posot = get_posot(model)
        order = get_current_order(model)
        line_numbers = lineNumbers.split("|")
        void_history = etree.XML(posot.voidHistory(posid))
        auth_message = None
        # 1 - If the order has been stored, ALWAYS require manager authorization
        if get_storewide_config("VoidThresholds.RecalledAuth", "true") == "true":
            for state in order.findall("StateHistory/State"):
                if state.get("state") == "STORED":
                    auth_message = "Requer autorização: Pedido recuperado"
                    break
        # 2 - Check "MaxItems"
        if not auth_message:
            max_items = int(get_storewide_config("VoidAuthThresholds.MaxItems", "3"))
            if max_items >= 0:
                void_qty = sum([int(line.get("decQty")) for line in void_history.findall("SaleLine")])
                void_qty += sum([int(line.get("qty")) for line in order.findall("SaleLine") if line.get("lineNumber") in line_numbers and int(line.get("level")) == 0])
                if void_qty > max_items:
                    auth_message = "Requer autorização: Mais de %d items cancelados" % (max_items)
        # 3 - Check "SessionMinOrders" and "SessionMaxPercentage"
        if not auth_message and get_custom(model, "VOIDAUTH_SESSION_DISABLED", "false") != "true":
            min_orders = int(get_storewide_config("VoidAuthThresholds.SessionMinOrders", "15"))
            max_percentage = int(get_storewide_config("VoidAuthThresholds.SessionMaxPercentage", "2"))
            if (min_orders >= 0) and (max_percentage >= 0):
                period = get_business_period(model)
                session = get_operator_session(model)
                sql = """
                SELECT count(OrderId) AS Orders, count(HasVoid) AS Voids FROM (
                    SELECT
                        O.OrderId,
                        CASE WHEN COALESCE(SUM(OVH.DecQty),0)>0 THEN 1 ELSE NULL END AS HasVoid
                    FROM orderdb.Orders O
                    LEFT JOIN orderdb.OrderVoidHistory OVH ON OVH.OrderId=O.OrderId
                    WHERE O.BusinessPeriod=%d AND O.OrderType=0 AND O.SessionId='%s'
                    GROUP BY O.OrderId
                )
                """ % (int(period), session)

                conn = persistence.Driver().open(mbcontext, posid)
                row = conn.select(sql).get_row(0)
                orders_qty, voids_qty = int(row.get_entry(0)), int(row.get_entry(1))
                if orders_qty and (orders_qty >= min_orders):
                    percentage = (voids_qty * 100) / orders_qty
                    if percentage > max_percentage:
                        sys_log_debug("Authorization required - orders_qty:%d, voids_qty:%d, percentage:%d" % (orders_qty, voids_qty, percentage))
                        auth_message = "Requer autorização: %d%% vendas canceladas no turno (máximo permitido: %d%%)" % (percentage, max_percentage)
        # Check if authorization is required
        if auth_message:
            show_info_message(posid, message=auth_message, msgtype="warning")
            if not get_authorization(posid, min_level=LEVEL_SUPERVISOR, model=model, display_title="$ORDER_LINE_CANCEL"):
                show_info_message(posid, message="")
                return
            show_info_message(posid, message="")
        # Void!
        doVoidLine(posid, lineNumbers)
    except OrderTakerException as ex:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                          msgtype="critical")
    finally:
        if conn:
            conn.close()


@action
def doToggleSessionVoidAuth(posid, *args):
    model = get_model(posid)
    disabled = get_custom(model, "VOIDAUTH_SESSION_DISABLED", "false") == "true"
    if disabled:
        if not show_confirmation(posid, message=r"Autorização de cancelamento DESATIVADO para esse turno de operador.", buttons="Enable|$CANCEL"):
            return
    else:
        if not show_confirmation(posid, message=r"Autorização de cancelamento ATIVADO para esse turno de operador.", buttons="Disable|$CANCEL"):
            return
    set_custom(posid, "VOIDAUTH_SESSION_DISABLED", ("false" if disabled else "true"), persist=True)
    show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")


@action
def doShowScreen(pos_id, screen, *args):
    model = get_model(pos_id)

    if screen == "main":
        screen = model.find("Screen").get("mainId")

    if model.find("Screen").get("id") != screen:
        change_screen(pos_id, screen)


@action
def doShowScreenWithCheck(posid, screen, *args):
    # Login authorization
    userid = show_keyboard(posid, "$ENTER_USER_ID", title="$USER_AUTHENTICATION", mask="INTEGER", numpad=True)
    if userid is None:
        return  # User cancelled, or timeout
    passwd = show_keyboard(posid, message="$ENTER_PASSWORD", title="$USER_AUTHENTICATION", is_password=True, numpad=True)
    if passwd is None:
        return  # User cancelled, or timeout

    # Verify the user id/password/level
    try:
        authenticate_user(userid, passwd, min_level=None)
        doShowScreen(posid, screen)
    except AuthenticationFailed as ex:
        show_info_message(posid, "$%s" % ex.message, msgtype="error")


@action
def doShowScreenWithAuthorization(posid, level=str(LEVEL_MANAGER), *args):
    model = get_model(posid)
    # Allow entering manager screen even with an order in progress
    # check_current_order(posid, model=model, need_order=False)
    return get_authorization(posid, min_level=int(level), model=model, display_title="$MENU_MANAGER")


@action
def doApplyModifiers(pos_id, modifiers_str, *args):
    temp_insert = """INSERT OR REPLACE INTO orderdb.CurrentOrderItem (OrderId, LineNumber, ItemId, Level, PartCode, OrderedQty, IncQty, DefaultQty, PriceKey, LastOrderedQty)
    VALUES (%(order_id)s, %(line_number)s, '%(item_id)s', %(temp_level)s, '%(temp_code)s', %(ordered_qty)s, %(inc_qty)s, %(default_qty)s, %(price_key)s, %(last_qty)s)"""

    model = get_model(pos_id)
    posot = get_posot(model)

    if modifiers_str:
        modifiers_xml = etree.XML(modifiers_str)  # type: Element

        salelines = modifiers_xml.get("lineNumbers")
        old_order_xml = etree.XML(posot.orderPicture(pos_id))
        order_id = old_order_xml.get("orderId")  # type: Element
        queries = []
        items = []
        for line_number in salelines.split("|"):
            for modifier in reversed(sorted(modifiers_xml.findall("Modifier"), key=lambda x: x.get("level"))):
                item_id, temp_level, temp_code, default_qty, ordered_qty, price = map(modifier.get, ("itemId", "level", "partCode", "defaultQty", "newQty", "price"))

                parent_quantity = int(filter(lambda x: x.get("level") == "0" and x.get("lineNumber") == line_number, old_order_xml)[0].get("qty"))
                modifier.set("newQty", str(int(modifier.get("newQty")) * parent_quantity))
                modifier.set("defaultQty", str(int(modifier.get("defaultQty")) * parent_quantity))

                # Used in Query
                parts_qty = ordered_qty
                # ordered_qty = ordered_qty if modifier.get("itemType") != "COMBO" else 1
                inc_qty = ordered_qty
                last_qty = "NULL"

                # Insert Item, Options and Defaults
                pod_type = get_podtype(model)
                price_key = _cache.get_best_price_key(item_id, temp_code, pod_type) or "NULL"
                queries.append(temp_insert % locals())

                if modifier.get("itemType") == "COMBO":
                    default_qty = "0"
                else:
                    if int(parts_qty) > 0 and float(price) > 0:
                        modifier.attrib["taxIndex"] = _get_tax_index(pos_id, temp_code)

                # Include Options if item is Added - Remove Options if item is Removed
                if int(parts_qty) > 0:
                    insert_options_and_defaults(queries, order_id, line_number, item_id, temp_code, parts_qty, int(temp_level), pod_type, items)
                else:
                    delete_options_and_defaults(queries, order_id, line_number, item_id, temp_code, parts_qty, int(temp_level), pod_type, items)

        if queries:
            conn = None
            try:
                conn = DBDriver().open(mbcontext, dbname=str(pos_id))
                conn.transaction_start()
                conn.query('''BEGIN TRANSACTION;''')
                conn.query(";".join(queries))
                if get_nf_type(pos_id) == "PAF" and not get_posfunction(model) == "OT" and not get_podtype(model) == "OT":
                    _send_modifiers_to_printer(pos_id, items, modifiers_xml, parent_quantity)
                conn.query('''COMMIT TRANSACTION;''')
            except Exception as ex:
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
                return
            finally:
                if conn:
                    conn.close()

        posot.updateOrderProperties(pos_id, saletype=old_order_xml.get("saleTypeDescr"))
        doShowScreen(pos_id, "-1")

        # Clears the modifiers data on the POS model
        send_message("POS%d" % int(pos_id), TK_POS_SETMODIFIERSDATA, FM_PARAM, "%s\0\0" % pos_id)


@action
def doApplyDiscount(pos_id, discount_code, need_auth="false"):
    model = get_model(pos_id)

    if need_auth in 'true' and not get_authorization(pos_id, min_level=LEVEL_MANAGER, model=model, display_title="$APPLY_DISCOUNT"):
        show_info_message(pos_id, "Falha ao autenticar usuário!", msgtype='error')
        return

    posot = get_posot(model)
    check_current_order(pos_id, model=model, need_order=True)

    data = '\0'.join([pos_id, discount_code])
    msg = mbcontext.MB_EasySendMessage("Discount", TK_DISCOUNT_APPLY, format=FM_PARAM, data=data)
    if not msg or msg.token == TK_SYS_NAK:
        show_messagebox(pos_id, message="Erro aplicando desconto: %s" % msg.data, icon="error")
    sale_type = get_current_order(model).get("saleTypeDescr")
    posot.updateOrderProperties(pos_id, saletype=sale_type)
    msg_type, msg_text = msg.data.split("|")
    show_info_message(pos_id, msg_text, msgtype=msg_type)


@action
def doClearDiscount(pos_id, need_auth="false"):
    model = get_model(pos_id)

    if need_auth in 'true' and not get_authorization(pos_id, min_level=LEVEL_MANAGER, model=model, display_title="$CLEAN_DISCOUNT"):
        show_info_message(pos_id, "Falha ao autenticar usuário!", msgtype='error')
        return

    posot = get_posot(model)
    check_current_order(pos_id, model=model, need_order=True)

    msg = mbcontext.MB_EasySendMessage("Discount", TK_DISCOUNT_CLEAR, format=FM_PARAM, data=pos_id)
    if not msg or msg.token == TK_SYS_NAK:
        show_messagebox(pos_id, message="Erro limpando desconto: %s" % msg.data, icon="error")
    sale_type = get_current_order(model).get("saleTypeDescr")
    posot.updateOrderProperties(pos_id, saletype=sale_type)
    msg_type, msg_text = msg.data.split("|")
    show_info_message(pos_id, msg_text, msgtype=msg_type)


def _send_modifiers_to_printer(pos_id, items, modifiers_xml, parent_quantity):
    for item in items:
        attribs = {}
        attribs["itemId"] = item[0]
        attribs["partCode"] = item[1]
        attribs["productName"] = item[2]
        attribs["price"] = item[3]
        attribs["lineNumber"] = item[4]
        attribs["newQty"] = str(int(item[5]) * parent_quantity)
        attribs["taxIndex"] = _get_tax_index(pos_id, item[1])
        modifiers_xml.insert(0, etree.Element("Modifier", attribs))
    msg = mbcontext.MB_EasySendMessage("fiscalhandler%s" % pos_id, TK_EVT_EVENT, format=FM_PARAM, data='\0'.join([etree.tostring(modifiers_xml), "FISCAL_MODIFIERS", "type", "notused", pos_id]))
    ret = msg.data.split('\0')
    if int(ret[0]):
        msg = "Erro ao processar modificador - %s" % (ret[0] if len(ret) == 1 else ret[1])
        show_info_message(pos_id, msg, msgtype="error")
        sys_log_error(msg)
        raise Exception(msg)


def _get_tax_index(posid, part):
    query = "SELECT t.FiscalIndex FROM Tax t LEFT JOIN ProductTax pt ON t.Code = pt.TaxCode WHERE pt.ProductCode ='%s' and name = 'ICMS'" % part
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext, service_name="FiscalPersistence")
        cursor = conn.select(query)
        for line in cursor:
            return line.get_entry("FiscalIndex") or ""
    except BaseException as _:
        raise
    finally:
        if conn:
            conn.close()


@action
def doCancelModifiers(posid, *args):
    doShowScreen(posid, "-1")
    # Clears the modifiers data on the POS model
    send_message("POS%d" % int(posid), TK_POS_SETMODIFIERSDATA, FM_PARAM, "%s\0\0" % posid)


@action
def notImplemented(posid, *args):
    show_messagebox(posid, "$FEATURE_NOT_IMPLEMENTED_YET")


def get_drawer_amount(posid, period, session):
    logger.debug("--- get_drawer_amount START ---")
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext, dbname=str(posid))
        conn.transaction_start()
        # set the period
        logger.debug("--- get_drawer_amount DELETE ReportsPeriod ---")
        conn.query("DELETE FROM temp.ReportsPeriod")
        logger.debug("--- get_drawer_amount INSERT ReportsPeriod ---")
        conn.query("INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)" % (period, period))
        logger.debug("--- get_drawer_amount SELECT Transfer ---")
        cursor = conn.select("""SELECT T.Period AS Period,
           T.SessionId AS SessionId,
           SUM(CASE WHEN T.Type=1 THEN 1 ELSE 0 END) AS InitialFloatQty,
           tdsum(CASE WHEN T.Type=1 THEN T.Amount ELSE '0.00' END) AS InitialFloatAmount,
           SUM(CASE WHEN T.Type=2 THEN 1 ELSE 0 END) AS SkimQty,
           tdsum(CASE WHEN T.Type=2 THEN T.Amount ELSE '0.00' END) AS SkimAmount,
           SUM(CASE WHEN T.Type=3 THEN 1 ELSE 0 END) AS TransferInQty,
           tdsum(CASE WHEN T.Type=3 THEN T.Amount ELSE '0.00' END) AS TransferInAmount,
           SUM(CASE WHEN T.Type=4 THEN 1 ELSE 0 END) AS TransferOutQty,
           tdsum(CASE WHEN T.Type=4 THEN T.Amount ELSE '0.00' END) AS TransferOutAmount
            FROM
                Transfer T
            WHERE T.Period = '%s'
            AND T.SessionId = '%s'
            GROUP BY Period, SessionId""" % (period, session))

        row = cursor.get_row(0)
        if row is not None:
            initialfloat = D(row.get_entry("InitialFloatAmount") or 0)
            transfer_in_amount = D(row.get_entry("TransferInAmount") or 0)
            skim_amount = D(row.get_entry("SkimAmount") or 0)
            transfer_out_amount = D(row.get_entry("TransferOutAmount") or 0)
        else:
            initialfloat = 0
            transfer_in_amount = 0
            skim_amount = 0
            transfer_out_amount = 0

        logger.debug("--- get_drawer_amount SELECT Orders ---")
        cursor_cash_drawer = conn.select("""
        	SELECT
                   tdsub(tdsum(DA.SaleCashAmount),COALESCE(tdsum(DA.SaleCashChangeAmount), 0)) AS CashGrossAmount,
                   tdsum(DA.RefundCashAmount) AS RefundCashAmount
                FROM (
                    SELECT
                        substr(Orders.SessionID, instr(Orders.SessionID, 'period=')+7) AS BusinessPeriod,
                        Orders.SessionID AS SessionID,
                        Orders.OrderId AS OrderId,
                        tdsum(CASE WHEN (Orders.OrderType=0) THEN OrderTender.ChangeAmount ELSE '0.00' END) AS SaleChangeAmount,
                        tdsum(CASE WHEN (Orders.OrderType=0 AND OrderTender.TenderId=0) THEN OrderTender.ChangeAmount ELSE '0.00' END) AS SaleCashChangeAmount,
                        tdsum(CASE WHEN (Orders.OrderType=0 AND OrderTender.TenderId=0) THEN OrderTender.TenderAmount ELSE '0.00' END) AS SaleCashAmount,
                        COALESCE(tdsum(CASE WHEN (OrderTender.TenderId=0 AND Orders.OrderType=1) THEN tdsub(OrderTender.TenderAmount,COALESCE(OrderTender.ChangeAmount,'0')) ELSE '0.00' END),'0.00') AS RefundCashAmount,
                        COALESCE(tdsum(CASE WHEN (Orders.OrderType=0 AND OrderTender.TenderId=0) THEN OrderTender.TipAmount ELSE '0.00' END),'0.00') AS TipsCashAmount
                    FROM
                        orderdb.Orders Orders
                    JOIN
                        orderdb.OrderTender OrderTender
                        ON OrderTender.OrderId=Orders.OrderId
                    WHERE Orders.StateId=5 AND Orders.OrderType IN (0,1)
                    AND substr(Orders.SessionID, instr(Orders.SessionID, 'period=')+7) = '%s'
                    AND Orders.SessionID = '%s'
                    GROUP BY Orders.BusinessPeriod, Orders.SessionId, Orders.OrderId) AS DA""" % (period, session))

        row_cash_drawer = cursor_cash_drawer.get_row(0)
        cash_gross_amount = D(row_cash_drawer.get_entry("CashGrossAmount") or 0)
        cash_refund_amount = D(row_cash_drawer.get_entry("RefundCashAmount") or 0)
        logger.debug("--- get_drawer_amount SELECT OrderCustomProperties inner Orders---")
        cursor = conn.select("""SELECT COALESCE(SUM(ocp.Value), 0) AS DonatedAmount FROM OrderCustomProperties ocp 
                                INNER JOIN Orders o 
                                ON o.OrderId = ocp.OrderId 
                                WHERE ocp.Key = 'DONATION_VALUE' 
                                AND o.BusinessPeriod = '%s' 
                                AND o.SessionId = '%s'""" % (period, session))
        row = cursor.get_row(0)
        donated_amount = D(row.get_entry("DonatedAmount") or 0)
        drawer_amount = initialfloat + cash_gross_amount + transfer_in_amount + donated_amount - (cash_refund_amount + skim_amount + transfer_out_amount)
        drawer_amount = round(drawer_amount, 2)
    except Exception as ex:
        logger.exception("--- get_drawer_amount ---")
        sys_log_exception("get_drawer_amount Error")
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        return
    finally:
        if conn:
            conn.close()
    logger.debug("--- get_drawer_amount END ---")
    return drawer_amount


@action
def doTransfer(posid, transfer_type, *args):
    model = get_model(posid)
    check_operator_logged(posid, model=model, need_logged=True, can_be_blocked=int(transfer_type) == 6)
    session = get_operator_session(model)
    operator = get_current_operator(model)
    operatorid = operator.get("id")
    period = get_business_period(model)
    ppview = True
    transfer_id = 0
    drawer_amount = round(float(get_drawer_amount(posid, period, session)), 2)
    initial_value_drawer = float(_get_initial_value_drawer(posid, session))
    get_value_drawer = round(float(drawer_amount - initial_value_drawer), 2)

    if int(transfer_type) == 2:
        drawer_amount = get_value_drawer
        descri_key = "TRANSFER_SKIM"
        ppview = False
        transfer_id = 1
    elif int(transfer_type) == 3:
        descri_key = "TRANSFER_CASH_IN"
    elif int(transfer_type) == 4:
        descri_key = "TRANSFER_CASH_OUT"
    elif int(transfer_type) == 6:
        drawer_amount = get_value_drawer
        descri_key = "DECLARED_AMOUNT"
        transfer_id = 6
        doOpenDrawer(posid, check_oper="false")  # Open the drawer
    else:
        show_info_message(posid, "$INVALID_TRANSFER_TYPE", msgtype="error")
        return

    description = translate_message(model, descri_key)

    message = "$ENTER_AMOUNT_TO_TRANSFER_TYPE|%s" % description if not int(transfer_type) == 6 else "Insira o valor presente na gaveta \\ (Sem fundo de troco)"
    amount = show_keyboard(posid, message, title="$OPERATOR_CLOSURE", mask="CURRENCY", numpad=True, timeout=720000)

    if amount is None:
        return

    if amount in ("", ".") or round(float(amount), 2) < 0 or round(float(amount), 2) > round(float(max_transfer_value), 2) or (int(transfer_type) != 6 and round(float(amount), 2) == 0):
        show_info_message(posid, "Valor Inválido. Digite um valor válido menor que R$ {0:.2f}".format(max_transfer_value), msgtype="error")
        return

    amount = round(float(amount), 2)

    if not int(transfer_type) in (3, 6):
        if amount > drawer_amount:
            show_info_message(posid, "Nao tem valor suficiente para fazer a sangria", msgtype="error")
            return

    just = ''
    buttons = "$OK|$CANCEL"

    if int(transfer_type) == 6:
        buttons = "$OK"
        if amount == drawer_amount == 0:
            skim_result = send_message("account%s" % posid, TK_ACCOUNT_TRANSFER, FM_PARAM, "%s\0%s\0%s\0%s\0%s" % (session, 5, "Final Float", initial_value_drawer, transfer_id), timeout=600 * USECS_PER_SEC)
            if skim_result.token == TK_SYS_NAK:
                show_info_message(posid, "Não foi possível efetuar sangria!", msgtype="warning")
            return True
        if not amount == drawer_amount:
            while just in (None, "", ".") or len(just) < 5:
                message = "Justifique a quebra de caixa: Valor Informado = %.02f, Valor Esperado = %.02f." % (amount, drawer_amount)
                just = show_keyboard(posid, message, timeout=720000, buttons="$OK", title="$OPERATOR_CLOSURE")  # type: str
                if just:
                    just = just.strip()
        else:
            just = "Valor Exato"

        just = "Valor Informado=%.02f; Valor Esperado=%.02f; Justificativa= %s" % (amount, drawer_amount, just)
    elif not int(transfer_type) == 3 and drawer_amount < amount:
        show_info_message(posid, "Valor da sangria não pode ser maior que o valor presente na gaveta", msgtype="error")
        return

    elif int(transfer_type) == 2:
        just = "Valor Informado=%.02f; Valor Esperado=%.02f; Justificativa=Sangria Menu Gerente" % (amount, amount)

    banana = 0
    if int(transfer_type) != 3 and amount > 0:
        valid_banana = True
        while valid_banana:
            banana = show_keyboard(posid, "Entre com o numero COMPLETO do envelope", title="$OPERATOR_CLOSURE", numpad=True, timeout=720000, buttons=buttons, mask="INTEGER")

            if banana not in (None, ""):
                if len(banana) < skim_digit_limit['min'] or len(banana) > skim_digit_limit['max']:
                    show_info_message(posid, "O numero do envelope precisa ter entre {} e {} dígitos"
                                      .format(skim_digit_limit['min'], skim_digit_limit['max']),
                                      msgtype="error")
                    continue

                valid_banana = False
            else:
                if int(transfer_type) != 6 and banana is None:
                    return
        just = just + ";envelope=%s" % banana
        just = just + ";managerID=%s" % get_custom(model, 'Last Manager ID', None)
    msg = send_message("account%s" % posid, TK_ACCOUNT_TRANSFER, FM_PARAM, "%s\0%s\0%s\0%s\0%s\0%s" % (session, int(transfer_type), descri_key, amount, transfer_id, just or "NULL"), timeout=600 * USECS_PER_SEC)

    if msg.token == TK_SYS_ACK:
        if int(transfer_type) == 6:
            skim_result = send_message("account%s" % posid, TK_ACCOUNT_TRANSFER, FM_PARAM, "%s\0%s\0%s\0%s\0%s" % (session, 2, "TRANSFER_SKIM", drawer_amount, transfer_id), timeout=600 * USECS_PER_SEC)
            if skim_result.token == TK_SYS_NAK:
                show_info_message(posid, "Não foi possível efetuar sangria!", msgtype="warning")
            skim_result = send_message("account%s" % posid, TK_ACCOUNT_TRANSFER, FM_PARAM, "%s\0%s\0%s\0%s\0%s" % (session, 5, "Final Amount", initial_value_drawer, transfer_id), timeout=600 * USECS_PER_SEC)
            if skim_result.token == TK_SYS_NAK:
                show_info_message(posid, "Não foi possível efetuar sangria!", msgtype="warning")
        else:
            doOpenDrawer(posid)  # Open the drawer
        if not get_nf_type(posid) == "PAF":
            if print_report(posid, model, ppview, "transferReport", posid, operatorid, transfer_type, amount, period, banana):
                show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")

            if (drawer_amount - amount) < float(sangria_levels.split(";")[0]):
                set_custom(posid, "sangria_level_1_alert", "0")

        return True
    else:
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")


def _get_initial_value_drawer(posid, session, *args):
    conn = None
    try:
        pos_sess_now = session.split(',')[0].split('=')[1]
        user_sess_now = session.split(',')[1].split('=')[1]
        period_sess_now = session.split(',')[3].split('=')[1]

        conn = persistence.Driver().open(mbcontext, posid)
        cursor = conn.select("select amount, sessionid from transfer where description = 'Initial Float' and posid = '{}' order by timestamp desc limit 1".format(pos_sess_now))

        if cursor.rows() > 0:
            for row in cursor:
                amount_data = float(row.get_entry(0) or 0.0)
                pos_data = row.get_entry(1).split(',')[0].split('=')[1]
                user_data = row.get_entry(1).split(',')[1].split('=')[1]
                period_data = row.get_entry(1).split(',')[3].split('=')[1]

                if pos_sess_now == pos_data and user_sess_now == user_data and period_sess_now == period_data:
                    return amount_data

        return 0
    except:
        sys_log_exception("Error in consult initial amount")
    finally:
        if conn:
            conn.close()


@action
def doCashPaidOut(posid, *args):
    def get_paid_out_amount():
        amount = show_keyboard(posid, "Digite o valor", defvalue="", mask="CURRENCY", numpad=True)
        if amount in (None, "", ".") or float(amount) <= 0:
            return None
        return amount

    model = get_model(posid)
    session = get_operator_session(model)
    ppview = True
    operator = get_current_operator(model)
    operatorid = operator.get("id")
    transfer_type = 4
    descri_key = "TRANSFER_CASH_OUT"
    period = get_business_period(model)
    paid_out_id = get_transfer_id(posid)
    if paid_out_id:
        paid_out_amount = get_paid_out_amount()
        if paid_out_amount:
            msg = send_message("account%s" % posid, TK_ACCOUNT_TRANSFER, FM_PARAM, "%s\0%s\0%s\0%s\0\0%s" % (session, int(transfer_type), descri_key, float(paid_out_amount), str(paid_out_id)))
            if msg.token == TK_SYS_ACK:
                # Open the drawer
                doOpenDrawer(posid)
                print_report(posid, model, ppview, "transferReport", posid, operatorid, transfer_type, paid_out_amount, period)
                show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
            else:
                show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        else:
            show_info_message(posid, "$OPERATION_FAILED", msgtype="error")


def get_transfer_id(pos_id):
    paid_out_ids = [1, 2, 1225, 5110, 5120, 5125, 5130, 5140, 5160, 5830, 7110, 7130, 7140, 7430, 7690, 8535]
    paid_out_options = ['Sangria - 1', 'Suprimentos - 2', 'BW TIP OUT - 1225', 'Meat - 5110', 'Seafood - 5120', 'Poultry - 5125', 'Produce - 5130',
                        'Dairy - 5140', 'Dry Goods - 5160', 'Beverage - 5830', 'Clean Supplies - 7110',
                        'office supplies - 7130', 'Paper Supplies - 7140', 'Kitchen Supply - 7430', 'Bank Out - 7690',
                        'Parking - 8535']
    selected_index = show_listbox(pos_id, paid_out_options, message="Selecione uma opção:")
    if selected_index is None:
        return None
    return paid_out_ids[selected_index]

@action
def doPrintOpenChecks(posid, *args):
    model = get_model(posid)
    posot = get_posot(model)
    orders = posot.listOrders(state="STORED")
    if not orders:
        show_messagebox(posid, "$NO_ORDERS_FOUND")
    else:
        for order in orders:
            order_xml = posot.orderPicture(orderid=order["orderId"])
            print_report(posid, model, False, "coupon_receipt", order_xml)
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")


@action
def cash_over_short(posid, store_wide="false", *args):
    model = get_model(posid)
    business_period = get_business_period(model)

    period = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)
    if period is None:
        return
    if not is_valid_date(period):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return

    if has_operator_opened(model) and business_period == period:
        show_info_message(posid, "Por favor, deslogue o operador atual.", msgtype="error")
        return

    print_report(posid, model, True, "cash_over_short_report", posid, period, 0)


@action
def dayOpenReport(posid, store_wide="false", *args):
    model = get_model(posid)
    period = get_business_period(model)
    if period is None:
        return
    if not is_valid_date(period):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return
    print_report(posid, model, True, "dayOpen_report", posid, period, store_wide,)


@action
def requestQuantity(posid, *args):
    while True:
        amount = show_keyboard(posid, "Digite a quantidade:", mask="INTEGER", numpad=True)
        if amount and '.' in amount:
            continue

        if amount not in (None, ""):
            if int(amount) > 99:
                show_info_message(posid, "Quantidade máxima de itens excedida", msgtype="info")
                amount = None

        return amount or ""


@action
def storewideRestart(posid, *args):
    selected_pos_id = show_keyboard(posid, "Digite o número do POS que deseja reiniciar ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)

    if selected_pos_id in (None, "", "."):
        return
    if selected_pos_id == "0":
        if not show_confirmation(posid, message="$CONFIRM_STOREWIDE_RESTART"):
            return

        show_info_message(posid, "$PLEASE_WAIT_ALL_NODES_RESTART", msgtype="info")
        mbcontext.MB_SendMessage(mbcontext.hv_service, TK_HV_GLOBALRESTART)

    if int(selected_pos_id) not in poslist:
        #show_info_message(posid, "Numero de POS inválido", msgtype="critical")
        show_messagebox(posid, message="Numero de POS inválido", icon="error")
        return
    confirm = show_confirmation(posid, message="Você tem certeza que deseja fechar o POS%s?\n OBS: Essa operação pode demorar alguns segundos" % selected_pos_id, title="Alerta", icon="warning", buttons="$OK|$CANCEL")
    if not confirm:
        return

    msg = mbcontext.MB_EasySendMessage("Maintenance%02d" % int(selected_pos_id), TK_MAINTENANCE_RESTART_REQUEST, format=FM_PARAM, data=posid, timeout=10000 * 1000)
    if msg.token == TK_SYS_NAK:
        show_info_message(posid, "%s" % msg.data, msgtype="error")


@action
def posRestart(posid, *args):
    pos = show_keyboard(posid, "Digite o número do POS", title="", defvalue="", mask="INTEGER", numpad=True)
    if pos in (None, "", "."):
        return

    if not show_confirmation(posid, message="Confirma a reinicialização do POS %r ?" % pos):
        return
    show_info_message(posid, "Aguarde a reinicialização do POS %r" % pos, msgtype="info")


@action
def doOrderPicture(posid, orderid, *args):
    try:
        picture = OrderTaker(posid, mbcontext).orderPicture(orderid=orderid)
        order = etree.tostring(etree.XML(picture).find("Order"), encoding="UTF-8")
        return (FM_XML, order)
    except:
        sys_log_exception("Error taking order picture for order %s" % orderid)
        return ""


@action
def doListPaidOrders(posid, limit=10, *args):
    model = get_model(posid)
    posot = get_posot(model)
    if not posot.sessionId:
        return
    try:
        # Lists all PAID orders for the given date
        orders = posot.listOrders(state="PAID", sessionid=posot.sessionId, limit=limit, decrescent=True, instnbr=posid)
        # Sort the orders by their ID
        orders.sort(key=lambda x: x["orderId"], reverse=False)
        set_custom(posid, "paidOrders", ",".join([x.get("orderId") for x in orders]))
    except OrderTakerException as ex:
        #show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
        #                  msgtype="critical")
        show_messagebox(posid, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")


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


@action
def doCheckUpdates(posid, show_msg="yes", *args):
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
    xml = etree.XML(msg.data)
    qty = len(xml.findall("Package"))

    if show_msg is "yes":
        if qty == 0:
            show_messagebox(posid, message="$NO_UPDATES_FOUND")
            return
        if qty == 1:
            if not show_confirmation(posid, message="$CONFIRM_SINGLE_UPDATE"):
                return
        if qty > 1:
            if not show_confirmation(posid, message="$CONFIRM_MULTIPLE_UPDATES|%d" % qty):
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
        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
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

    if show_msg is "yes":
        if not show_confirmation(posid, icon="success", message="$SYSTEM_UPDATE_SUCCESS", timeout=300000):
            return

    # Store Wide Restart
    show_info_message(posid, "$PLEASE_WAIT_ALL_NODES_RESTART", msgtype="info")
    mbcontext.MB_SendMessage(mbcontext.hv_service, TK_HV_GLOBALRESTART)
    return True


@action
def doSetCustom(posid, key, value, persist="false", *args):
    """ doSetCustom(posid, key, value, persist="false") -> True or False
    Sets a custom property in the POS model
    @param posid: POS id
    @param key: Custom property key
    @param value: Custom property value
    @param persist: Optional flag indicating if the operation should be persisted in the database (default: "false")
    """
    return set_custom(posid, key, value, persist.lower() == "true")


@action
def doShowMessageBox(posid, message, title="", icon="", buttons="", *args):
    kargs = {}
    if title:
        kargs["title"] = title
    if icon:
        kargs["icon"] = icon
    if buttons:
        kargs["buttons"] = buttons
    show_messagebox(posid, message, **kargs)


@action
def doSetCustomerName(pos_id):
    model = get_model(pos_id)
    pod_function = get_posfunction(model)
    pos_ot = get_posot(model)
    fill_customer_properties(model, pod_function, pos_id, pos_ot, get_name=True, force=True)


def get_index_msr(posid, model):
    services = get_used_service(model, "msr", get_all=True)
    msr = None
    for svc in services:
        if "index" in svc:
            msr = svc
            break
    return msr


@action
def doVoidPaidSale(posid, request_authorization="true", allpos="false", requestdate="false", *args):
    """
    Shows a list of PAID orders for void
    @param allpos: If "true", lists orders from all POS.
                   If "false", lists orders from this POS (both originated from this POS and paid on this POS)
    @param requestdate: If "true", requests a date and lists orders from that date (from 00:00 to 23:59).
                        If "false", lists orders from "today" (from 00:00 to 23:59)
    """
    model = get_model(posid)
    # check_operator_logged(posid, model=model, can_be_blocked=False)
    posot = get_posot(model)
    try:
        if request_authorization == "true":
            if not get_authorization(posid, min_level=LEVEL_SUPERVISOR, model=model, display_title="$PAID_ORDERS"):
                return
        # Check if we should request a date
        if requestdate.lower() == "true":
            dateToFind = show_keyboard(posid, "$ENTER_THE_DAY", mask="DATE", numpad=True)
            if dateToFind is None:
                return  # Cancelled
            if not is_valid_date(dateToFind):
                show_info_message(posid, "$INVALID_DATE", msgtype="error")
                return
            tmpDate = time.strptime(dateToFind, "%Y%m%d")
        else:
            tmpDate = time.localtime()
        # Check for which POS we should request the orders
        if allpos.lower() == "true":
            originatorid = ""
        else:
            originatorid = "POS%04d" % int(posid)
        # Calculate the "since" and "until" dates
        sinceDate = time.strftime("%Y-%m-%dT00:00:00", tmpDate)
        untilDate = time.strftime("%Y-%m-%dT23:59:59", tmpDate)
        # Lists all PAID orders for the given date

        orders = posot.listOrders(state="PAID", since=sinceDate, until=untilDate, originatorid=originatorid)
        order_ids = []
        for order in orders:
            order_ids.append(order.get("orderId"))

        for pos_temp in poslist:
            conn = None
            try:
                conn = persistence.Driver().open(mbcontext, str(pos_temp))
                conn.query("DELETE FROM CurrentOrderItem WHERE OrderId IN (" + ",".join(map(str, order_ids)) + ")")
            except Exception as ex:
                logger.exception("Erro limpando Current Order DB")
            finally:
                if conn:
                    conn.close()

        if allpos.lower() != "true":
            # If we are getting orders for this POS only, also include the orders that have been paid here (possibly not originated)
            orders2 = posot.listOrders(state="PAID", since=sinceDate, until=untilDate, instnbr=int(posid))
            ordersmap = dict([(order["orderId"], order) for order in orders])
            ordersmap.update(dict([(order["orderId"], order) for order in orders2]))
            orders = ordersmap.values()
        if not orders:
            show_info_message(posid, "$NO_ORDERS_FOUND", msgtype="warning")
            return

        enabled_reprint_pod_types = get_storewide_config("Store.CanReprintPodTypes", defval="FC;DS;KK;DT;OT;TT;DL").split(";")
        # Build the preview data to be displayed on UI
        preview_data = []
        # Sort the orders by their ID
        try:
            orders = sorted(orders, key=lambda x: map(int, re.findall('\d+', x['createdAt'])), reverse=True)
        except:
            orders = sorted(orders, key=lambda x: map(int, re.findall('\d+', x['custom_properties']['FISCALIZATION_DATE'] if 'custom_properties' in x else x['createdAt'])), reverse=True)
        # Base URL
        baseurl = "/mwapp/services/PosController/POS%d/?token=TK_POS_EXECUTEACTION&format=2&isBase64=true&payload=" % int(posid)

        for order in orders:
            order_id = order["orderId"]
            order_posid = int(order["originatorId"][3:])
            order_gross = float(order.get("totalGross", 0.00))
            order_created_date = datetime.datetime.strptime(order.get("createdAt"), "%Y-%m-%dT%H:%M:%S")
            order_timestamp = order_created_date.strftime('%H:%M')
            order_type = order["podType"]
            partner = ""
            if 'custom_properties' in order:
                partner = order["custom_properties"]["PARTNER"] if "PARTNER" in order["custom_properties"] else ""
            descr = "{}{:02} #{:04} {} R${:.2f}".format(order_type, order_posid, int(order_id) % 10000, order_timestamp, order_gross)
            if partner != "":
                short_reference = order["custom_properties"]["SHORT_REFERENCE"] if "SHORT_REFERENCE" in order["custom_properties"] else order_id
                if partner.upper() == "APP":
                    descr += " APP{}".format(short_reference)
                else:
                    descr += " DLY{}".format(short_reference)

            payload = base64.b64encode("\0".join(("doOrderPicture", posid, order_id)))
            url = baseurl + payload
            preview_data.append((order_id, descr, url))
        # Let the user select an order ...

        while True:
            selected = show_order_preview(posid, preview_data, buttons="Cupom|Picklist|$CLOSE", onthefly=True, title="Selecione um pedido para reimpressão:")
            if (selected is None) or (selected[0] == "2"):
                return  # Timeout, or the user cancelled

            order_type = filter(lambda x: x["orderId"] == selected[1], orders)[0]["podType"]
            selected_order = filter(lambda x: x["orderId"] == selected[1], orders)[0]
            if order_type not in enabled_reprint_pod_types or get_nf_type(posid) == "PAF":
                show_messagebox(posid, "$REPRINT_FORBIDDEN", title="$REPRINT_ORDERS", icon="info", buttons="$OK")
                continue

            if (selected is None) or (selected[0] == "1"):
                try:
                    model = sysactions.get_model(posid)
                    order_pict = posot.orderPicture("", selected[1])
                    data = sysactions.print_report(posid, model, False, picklist_reprint_type, order_pict)
                    if data is True:
                        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
                    else:
                        show_messagebox(posid, "$ERROR_REPRINT_PICKLIST|", title="$REPRINT_ORDERS", icon="error", buttons="$OK")
                except Exception as ex:
                    show_messagebox(posid, "$ERROR_REPRINT_PICKLIST|%s" % repr(ex), title="$REPRINT_ORDERS", icon="error", buttons="$OK")
                # Because the user may reprint more then one PICKLIST without exiting
                continue

            orderid = selected[1]
            try:
                msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_REPRINT, format=FM_PARAM, data=str('\x00'.join(map(str, [posid, orderid]))))
                if not msg.token == TK_SYS_ACK:
                    error_msg = "A operação falhou! "
                    if msg.data and "False" not in msg.data:
                        error_msg += msg.data
                    show_info_message(posid, error_msg, msgtype="error")
                else:
                    try:
                        current_printer = get_used_service(model, "printer")
                        msg = mbcontext.MB_EasySendMessage(current_printer, TK_PRN_PRINT, format=FM_PARAM, data=msg.data, timeout=10000000)  # type: MBMessage
                        if msg.token != TK_SYS_ACK:
                            show_messagebox(posid, "$ERROR_REPRINT_NFE|%s" % msg.data, title="$REPRINT_ORDERS", icon="error", buttons="$OK")
                        else:
                            donation_value = _get_custom_property_value_by_key("DONATION_VALUE", selected_order["custom_properties"])
                            if donation_value is not None:
                                donation_value = float(donation_value.replace(",", "."))
                                donation_value = format(donation_value, '.2f').replace(",", ".")
                                customer_name = _get_custom_property_value_by_key("CUSTOMER_NAME", selected_order["custom_properties"]) or ""
                                _do_print_donation(posid, orderid, customer_name, donation_value, round_donation_institution, round_donation_cnpj, round_donation_site, cliche)

                            show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
                    except Exception as ex:
                        show_messagebox(posid, "$ERROR_REPRINT_NFE|%s" % repr(ex), title="$REPRINT_ORDERS", icon="error", buttons="$OK")
            except Exception as ex:
                sys_log_exception("Could not print Receipt for voided order - Error: %s" % str(ex))

    except OrderTakerException as ex:
        # show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
        #                   msgtype="critical")
        show_messagebox(posid, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                        icon="error")


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
                show_info_message(pos_id, "Não há comprovante para ser impresso", msgtype="warning")
        finally:
            if conn:
                conn.close()
    except Exception as ex:
        show_info_message(pos_id, "Impossivel imprimir ultimo cupom: %s" % str(ex), msgtype="error")
        sys_log_exception("Could not print Receipt for order")
    finally:
        close_asynch_dialog(pos_id, wait_dlg_id)


def _do_print_donation(pos_id, order_id, customer_name, donation_value, donation_institution, donation_cnpj, donation_site, cliche):
    model = get_model(pos_id)
    try:
        report = ""
        if get_nf_type(pos_id) != "PAF":
            report += constants.LINESPACING_FUNCS[1]
            report += constants.TXT_FONT_B
            report += constants.TXT_ALIGN_CT
            for row in cliche:
                report += row + "\n"
            report += constants.SEPARATOR_DASH + "\n"
            report += constants.TXT_ALIGN_LT
            report += "%-44s   %s" % (datetime.datetime.now().strftime("%d/%m/%y"), datetime.datetime.now().strftime("%H:%M:%S")) + "\n"
            report += "NAO E DOCUMENTO FISCAL\n"
            report += constants.TXT_ALIGN_CT + constants.TXT_BOLD_ON + "COMPROVANTE NAO FISCAL" + constants.TXT_BOLD_OFF + "\n"
            report += constants.TXT_ALIGN_LT
            report += "%-12s   %46s" % (sysactions.translate_message(model, "ORDER_NUMBER", "%s" % order_id), sysactions.translate_message(model, "CLIENT_NAME", "%s" % (constants.TXT_BOLD_ON + (customer_name[:30] or sysactions.translate_message(model, "UNINFORMED")).upper() + "\n" + constants.TXT_BOLD_OFF))) + "\n"
            report += "%-44s   %s %s" % (sysactions.translate_message(model, "DONATION_VALUE"), sysactions.translate_message(model, "L10N_CURRENCY_SYMBOL"), donation_value)
            report += "\n" + constants.SEPARATOR_DASH + "\n"
            report += constants.TXT_ALIGN_CT
            report += sysactions.translate_message(model, "DONATION_INSTITUTION", "%s" % donation_institution) + "\n"
            report += sysactions.translate_message(model, "DONATION_CNPJ", "%s" % donation_cnpj) + "\n"
            report += "%s" % donation_site
        else:
            report += datetime.datetime.now().strftime("%d/%m/%y %H:%M:%S") + "\n"
            report += sysactions.translate_message(model, "ORDER_NUMBER", "%s" % order_id) + "\n"
            report += sysactions.translate_message(model, "CLIENT_NAME", "%s" % (customer_name or sysactions.translate_message(model, "UNINFORMED")).upper())
            report += "\n\n" + "%-37s   %s %s" % (sysactions.translate_message(model, "DONATION_VALUE"), sysactions.translate_message(model, "L10N_CURRENCY_SYMBOL"), donation_value)
            report += "\n------------------------------------------------\n"
            report += sysactions.translate_message(model, "DONATION_INSTITUTION", "%s" % donation_institution) + "\n"
            report += sysactions.translate_message(model, "DONATION_CNPJ", "%s" % donation_cnpj) + "\n"
            report += "%s" % donation_site
        print_text(pos_id, model, str(report))
    except Exception as ex:
        show_info_message(pos_id, (sysactions.translate_message(model, "PRINTER_DONATION_ERROR", "%s" % str(ex))), msgtype="error")
        sys_log_exception("Could not print Receipt for order")


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
    except Exception as ex:
        logger.exception("Erro limpando Current Order DB")
    finally:
        if conn:
            conn.close()
    try:
        msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_REPRINT, format=FM_PARAM, data=str('\x00'.join(map(str, [pos_id, order_id]))))
        if not msg.token == TK_SYS_ACK:
            sys_log_error("Could not recreate Fiscal Coupon for order %s - Error: %s" % (order_id, str(msg.data)))
            raise StopAction()
        else:
            current_printer = get_used_service(model, "printer")
            msg = mbcontext.MB_EasySendMessage(current_printer, TK_PRN_PRINT, format=FM_PARAM, data=msg.data, timeout=10000000)  # type: MBMessage
            if msg.token != TK_SYS_ACK:
                sys_log_error("Could not reprint Fiscal Coupon for order %s - Error: %s" % (order_id, str(msg.data)))
                raise StopAction()
    except Exception as ex:
        sys_log_exception("Exception recreating Fiscal Coupon for order %s" % order_id)
        raise StopAction()

    try:
        order_pict = posot.orderPicture("", order_id)
        # fix order pict to print picklist correctly
        dict_list = []
        order = etree.XML(order_pict)

        for line in order.findall("Order/SaleLine"):
            line_number = line.get('lineNumber')
            item_id = line.get('itemId')
            part_code = line.get('partCode')
            level = line.get('level')
            get_updated_sale_line_defaults(dict_list, order_id, int(line_number), item_id, part_code, line.get('qty'), int(level), get_podtype(model))
            for corrected_line in dict_list:
                corrected_line_dict = json.loads(corrected_line)
                if corrected_line_dict['line_number'] == line_number and \
                   corrected_line_dict['item_id'] == item_id and \
                   corrected_line_dict['part_code'] == part_code and \
                   corrected_line_dict['level'] == level:
                    line_orig_qty = line.get('qty')
                    line.set('addedQty', str(max(0, int(line_orig_qty) - int(corrected_line_dict['default_qty']))))
                    line.set('defaultQty', corrected_line_dict['default_qty'])
        data = sysactions.print_report(pos_id, model, False, picklist_reprint_type, etree.tostring(order))
        if not data:
            sys_log_error("Exception reprinting Picklist for order %s" % order_id)
    except Exception as ex:
        sys_log_exception("Exception reprinting Picklist for order %s" % order_id)


@action
def doAddOrEditComment(posid, line, level, item_id, part_code, comment_id="", comment="", only_save="false"):
    model = get_model(posid)
    posot = get_posot(model)
    comment_id = None if comment_id == "-1" else comment_id

    if only_save == "true":
        if comment_id:
            if comment == "":
                posot.delComment(comment_id)
            else:
                posot.updComment(comment_id, comment)
        elif comment != "":
            posot.addComment(line, item_id, level, part_code, comment)

    else:
        if not line:
            # show_info_message(posid, "Selecione uma linha primeiro", msgtype="critical")
            show_messagebox(posid, message="Selecione uma linha primeiro", icon="error")
            return
        defval = comment if comment else ""
        if comment_id:
            title = "Edit Comment"
            # get the current comment id text
            model = get_model(posid)
            order = model.find("CurrentOrder/Order")
            for sl in order.findall("SaleLine"):
                for comment in sl.findall("Comment"):
                    if comment.get("commentId") == comment_id:
                        defval = comment.get("comment")
                        break
        else:
            title = "Add Comment"
        comment = show_keyboard(posid, title, defvalue=defval, title="", numpad=False)
        comment = "null" if comment is None else comment

    return comment


@action
def showCustomKeyboard(posid, text=""):
    data = show_keyboard(posid, text, defvalue="", title="", numpad=False)
    return data


@action
def is_pre_product_quantity(*args):
    return set_product_quantity_pre


@action
def doChangeQuantity(posid, line_numbers, qty, is_absolute=False):
    model = get_model(posid)
    posot = get_posot(model)
    pod_function = get_posfunction(model) if get_podtype(model) in ("DT", "FC") else get_podtype(model)

    if set_product_quantity_pre:
        set_custom(posid, "pre_quantity", qty)
        return

    check_current_order(posid, model=model, need_order=True)
    if not line_numbers:
        return

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
            if qty_to_change == 0:
                if pod_function != "TT" and void_line_authorization:
                    if not get_authorization(posid, min_level=LEVEL_SUPERVISOR, model=model, insert_auth=True):
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
        # show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), msgtype="critical")
        show_messagebox(posid, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()), icon="error")

@action
def doGetItemComposition(pos_id, line_number, modifier_screen="350", qty="0", default_mod_set="", *args):
    # type: (str, str, str, str, str, list) -> None
    try:
        model = get_model(pos_id)
        xml_order = get_current_order(model)  # type: ElementTree

        # Selecionamos apenas as linhas que nos interessam (as raizes da SaleLine)
        lines = line_number.split("|")
        selected_lines = [line for line in xml_order.findall("SaleLine") if int(line.get("level")) == 0 and int(line.get("qty")) > 0 and line.get("lineNumber") in lines]  # type: list[Element]

        item_id = selected_lines[0].get("itemId") if len(selected_lines) else None
        part_code = selected_lines[0].get("partCode") if len(selected_lines) else None
        product_name = selected_lines[0].get("productName") if len(selected_lines) else None

        from modifier import get_modifiers_and_elements

        # Para cada elemento chama a função Recursiva
        modifier_sets = {}
        modifier_elem = {}
        modifier_part = {}

        pod_type = get_podtype(model)

        try:
            for selected_line in selected_lines:  # type: Element
                get_modifiers_and_elements(modifier_sets, modifier_elem, modifier_part, selected_line.get("itemId"), selected_line.get("partCode"), 0, pod_type)
        except Exception as e:
            print(e.message)

        for mod in modifier_elem:
            modifier_elem[mod].line_number = int(selected_lines[0].get("lineNumber"))
            modifier_elem[mod].level = len(modifier_elem[mod].context.split(".")) - 1
            modifier_elem[mod].json_array_tags = json.dumps(_cache.get_tags_as_str(modifier_elem[mod].part_code))

            if mod in modifier_part:
                for mod_part in modifier_part[mod]:
                    modifier_part[mod][mod_part].line_number = modifier_elem[mod].line_number
                    modifier_part[mod][mod_part].json_array_tags = json.dumps(_cache.get_tags_as_str(modifier_part[mod][mod_part].part_code))

                modifier_elem[mod].parts = modifier_part[mod]

        lines = line_number.split("|")
        selected_items = [line for line in xml_order.findall("SaleLine") if line.get("lineNumber") == lines[0]]
        for line in selected_items:
            line_item_id, line_part_code, def_qty, ord_qty = (line.get("itemId"), line.get("partCode"), line.get("defaultQty"), line.get("qty"))

            if line_item_id + "." + line_part_code in modifier_elem:
                modifier_elem[line_item_id + "." + line_part_code].def_qty = def_qty or "0"
                modifier_elem[line_item_id + "." + line_part_code].ord_qty = ord_qty

        sale_lines = xml_order.findall("SaleLine")
        deleted_line_numbers = map(lambda x: x.get("lineNumber"), filter(lambda x: x.get("level") == "0" and x.get("qty") == "0", sale_lines))
        active_item_ids = map(lambda x: x.get("itemId"), filter(lambda x: x.get("lineNumber") not in deleted_line_numbers, sale_lines))

        if modifier_elem:
            min_level = 99
            min_mod_set = ""
            for key in modifier_sets:
                if default_mod_set in modifier_sets[key].modifiers_sets and key in active_item_ids:
                    if min_level > len(modifier_sets[key].context.split(".")):
                        min_mod_set = modifier_sets[key].context + "." + default_mod_set if default_mod_set != "" else ""
                        min_level = len(modifier_sets[key].context.split("."))

            temp_item_id = "%s.%s" % (item_id, part_code)
            xml = etree.Element("Modifiers", dict(autoClose="false", qty=str(qty), lineNumbers=str(line_number), itemId=temp_item_id, productName=str(product_name), level="0", defaultModSet=min_mod_set))  # type: Element

            for key in modifier_sets:
                modifier_sets[key].line_number = int(selected_lines[0].get("lineNumber"))
                modifier_sets[key].level = len(modifier_sets[key].context.split(".")) - 1
                xml.append(modifier_sets[key].to_xml())

            send_message("POS%d" % int(pos_id), TK_POS_SETMODIFIERSDATA, FM_PARAM, "%s\0%s\0" % (pos_id, etree.tostring(xml, encoding="UTF-8")))
            doShowScreen(pos_id, modifier_screen)
        else:
            show_info_message(pos_id, "Não existem itens Modificadores cadastrados para esse produto.", msgtype="critical")
            sys_log_debug('[doGetItemComposition] No modifiers found for {0}.{1}.'.format(item_id, part_code))
    except Exception:
        sys_log_exception('[doGetItemComposition] Exception retrieving product actual composition.')


@action
def doShowScreenWithChecks(pos_id, screen, checks, *args):
    model = get_model(pos_id)
    xml_order = get_current_order(model)

    for check in checks.split('|'):
        if check == "closed_order" and has_current_order(model):
            show_info_message(pos_id, "$NEED_TO_FINISH_ORDER", msgtype="warning")
            return

        if check == "manager" and not get_authorization(pos_id, min_level=LEVEL_MANAGER, model=model):
            show_info_message(pos_id, "$ACCESS_DENIED", msgtype="warning")
            return

        if check == "untotaled" and xml_order and xml_order.get("state") == "TOTALED":
            if len(args) > 0 and globals().get(args[0]):
                globals().get(args[0])(pos_id, screen)
            return

        if check == "totaled" and ((xml_order and xml_order.get("state") != "TOTALED") or xml_order is None):
            if len(args) > 0 and globals().get(args[0]):
                globals().get(args[0])(pos_id, screen)
            return

        if check == "login" and not has_operator_opened(model):
            show_info_message(pos_id, "$NEED_TO_LOGIN_FIRST", msgtype="warning")
            screen = "500"
            break

    pod_function = get_posfunction(model) if get_podtype(model) == "DT" else ""
    if "CS" in pod_function and screen == "main":
        screen = "201"

    if len(args) == 0 or args[0] != screen:
        doShowScreen(pos_id, screen)


@action
def signInUser(pos_id, *args):
    user_id = None
    try:
        ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(pos_id), bustoken.TK_FPR_OK)
        if ret.token == TK_SYS_ACK:
            # Temos o leitor e ele esta operacional, vamos pedir as impressoes do usuario
            ret = mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(pos_id), bustoken.TK_FPR_IDENTIFY_USER, format=FM_PARAM)
            if ret.token != TK_SYS_ACK:
                # Erro cadastrando impressao digital
                show_info_message(pos_id, "Erro realizando a leitura da digital. Tente novamente.", msgtype="error")
                return
            else:
                user_id = ret.data
    except MBException as e:
        if e.errorcode == 2:  # NOT_FOUND, servico de FingerPrint nao disponivel
            pass
        else:
            pass

    if user_id is None:
        user_id = show_keyboard(pos_id, "$ENTER_USER_ID", title="$USER_AUTHENTICATION", mask="INTEGER", numpad=True)
        if user_id is None:
            return ''  # User cancelled, or timeout
        password = show_keyboard(pos_id, message="$ENTER_PASSWORD", title="$USER_AUTHENTICATION", is_password=True)
        if password is None:
            return ''  # User cancelled, or timeout
        # Verify the user id/password/level
        try:
            user = authenticate_user(user_id, password, min_level=None)
        except AuthenticationFailed as ex:
            show_info_message(pos_id, "$%s" % ex.message, msgtype="error")
            return ''
    else:
        try:
            user_xml_str = get_user_information(user_id)
        except Exception as ex:
            show_info_message(pos_id, "Impressao digital associada a usuario que nao esta cadastrado", msgtype="error")
            return

        # Se identificamos o usuario pela digital, pegamos a informacao dele e constuimos o objeto
        # igual a autenticacao por usuario e senha faz
        user_xml = etree.XML(user_xml_str)
        user_element = user_xml.find("UserInfo/user")
        user = {
            'Level': user_element.attrib["Level"],
            'UserName': user_element.attrib["UserName"],
            'LongName': user_element.attrib["LongName"]
        }

    save_signedin_user(pos_id, user_id, user)
    return user


def save_signedin_user(pos_id, user_id, user):
    user["Id"] = str(user_id)
    set_custom(pos_id, SIGNED_IN_USER, json.dumps(user), True)


@action
def signOutUser(pos_id, *args):
    clear_custom(pos_id, SIGNED_IN_USER)


@action
def getSignedInUser(pos_id, *args):
    msg = send_message("POS%d" % int(pos_id), TK_POS_LISTUSERS, FM_PARAM, "%s" % (pos_id))
    if msg.token == TK_SYS_NAK:
        return ''

    xml = etree.XML(msg.data)
    opened_users = [tag for tag in xml.findall("User") if not tag.get("closeTime")]

    if not opened_users:
        return ''

    return opened_users

@action
def checkSignedInUser(pos_id, *args):
    """
    Checks if the signed in user is the same as the logged in user.
    If the signed in user is different, but is a manager, a dialog will be displayed asking for
    confirmation. If the manager confirms, it will work as if it were the same user
    @param pos_id: pos id
    @return: True if it's the same user or if it's a manager and the action was confirmed, False otherwise
    """

    model = get_model(pos_id)
    signed_in_user_text = get_custom(model, SIGNED_IN_USER)
    if signed_in_user_text is None:
        return False
    signed_in_user = json.loads(signed_in_user_text)
    if signed_in_user is None:
        return False
    logged_in_user = get_current_operator(model)

    if signed_in_user["Id"] == logged_in_user.get("id"):
        return True

    if int(signed_in_user["Level"]) >= LEVEL_MANAGER:
        confirmed = show_confirmation(pos_id, "$CLOSE_SALE_ANOTHER_USER|{0}".format(logged_in_user.get("name")))
        return confirmed

    show_info_message(pos_id, "$CURRENT_USER_CANNOT_CLOSE_SALE", msgtype="warning")
    return False


@action
def assignUser(pos_id, *args):
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext)
        result = conn.select("select longname, userid from users where level in (5, 10, 20)")
        users = []
        ids = []
        for row in result:
            users.append(row.get_entry(0))
            ids.append(row.get_entry(1))
        conn.close()
        index = show_listbox(pos_id, users, message="$SELECT_USER", buttons="$OK|$CANCEL", icon="info")
        set_custom(pos_id, ASSIGNED_USER, json.dumps({"Id": ids[index], "Name": users[index]}), True)
    finally:
        if conn:
            conn.close()


@action
def checkShowModifierScreen(pos_id, sale_line_xml, modifier_screen):
    if sale_line_xml in ['True', 'False', ""]:
        return

    sale_line = etree.XML(sale_line_xml)
    line_number = sale_line.get("lineNumber")
    quantity = sale_line.get("qty")

    order = get_current_order(get_model(pos_id))

    sale_lines = order.findall("SaleLine")
    current_sale_lines = filter(lambda x: x.get("lineNumber") == line_number and int(x.get("qty")) != 0, sale_lines)

    model = get_model(pos_id)
    pod_type = get_podtype(model)

    for current_sale_line in current_sale_lines:
        current_product_code = current_sale_line.get("partCode")
        mod_set = _cache.get_must_modify(current_product_code, pod_type)
        if mod_set is not None:
            doGetItemComposition(pos_id, line_number, modifier_screen, quantity, mod_set)
            break


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
def getAuthorizationLevel(pos_id):
    model = get_model(pos_id)
    level = get_custom(model, 'Authorization Level', None)
    return level


@action
def doGetKDSstatus(pos_id):
    msg = mbcontext.MB_EasySendMessage("KdsMonitor", TK_KDSMONITOR_STATUS_REQUEST, format=FM_PARAM, data=pos_id)
    model = get_model(pos_id)
    if msg.token == TK_SYS_ACK:
        print_report(pos_id, model, True, "kds_report", pos_id, msg.data)
    else:
        show_info_message(pos_id, "%s" % msg.data, msgtype="error")


@action
def doKill(pos_id):
    confirm = show_confirmation(pos_id, message="Você tem certeza que deseja fechar o sistema?\n OBS: Essa operação pode demorar alguns segundos", title="Alerta", icon="warning", buttons="$OK|$CANCEL")
    if not confirm:
        return
    try:
        msg = mbcontext.MB_EasySendMessage("Maintenance%02d" % int(pos_id), TK_MAINTENANCE_TERMINATE_REQUEST, format=FM_PARAM, data=pos_id, timeout=10000 * 1000)
        if msg.token == TK_SYS_NAK:
            show_info_message(pos_id, "%s" % msg.data, msgtype="error")
    except:
        show_info_message(pos_id, "Erro ao tentar fechar o sistema", msgtype="error")


@action
def doPurgeKDSs(pos_id):
    try:
        msg = mbcontext.MB_EasySendMessage("ProductionSystem", TK_PROD_PURGE, format=FM_PARAM, data=pos_id, timeout=10000 * 1000)
        show_info_message(pos_id, "KDSs limpos com sucesso", msgtype="success")
    except:
        show_info_message(pos_id, "Erro ao limpar KDSs", msgtype="error")


@action
def doGetPrinterStatus(pos_id):
    printer_info_list = []

    # PickList 1 - Hardcoded Name Store
    printer_info = ["Pick List: "]
    try:
        msg = mbcontext.MB_EasySendMessage("printerpl-1", TK_PRN_GETSTATUS, FM_PARAM, None)
        if msg.data == "0":
            printer_info.append("Impressora OK")
        else:
            printer_info.append("Falha na Impressora")
    except:
        printer_info.append("Falha na Impressora")
    printer_info_list.append(printer_info)

    # PickList 2 - Hardcoded Name for Delivery
    printer_info = ["Delivery : "]
    try:
        msg = mbcontext.MB_EasySendMessage("printerpl-2", TK_PRN_GETSTATUS, FM_PARAM, None)
        if msg.data == "0":
            printer_info.append("Impressora OK")
        else:
            printer_info.append("Falha na Impressora")
    except:
        printer_info.append("Falha na Impressora")
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
                printer_info.append("Impressora OK")
            else:
                printer_info.append("Falha na Impressora")
        except:
            printer_info.append("Falha na Impressora")
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
    try:
        with open("../data/server/bundles/pigeoncomp/.componentversion") as f:
            componentversion = f.read()
    except Exception as ex:
        logger.debug(pos_id, "Arquivo de versão de componente não encontrado", ex)
        componentversion = "Não Versionado"
    try:
        with open("../data/server/bundles/pigeoncomp/.coreversion") as f:
            coreversion = f.read()
    except Exception as ex:
        logger.debug(pos_id, "Arquivo de versão de core não encontrado")
        coreversion = "Não Versionado"
    try:
        with open("../data/server/bundles/pigeoncomp/.priceversion") as f:
            priceversion = f.read()
    except Exception as ex:
        logger.debug(pos_id, "Arquivo de versão de preço não encontrado")
        priceversion = "Não Versionado"
    print_report(pos_id, model, True, "versions_report", pos_id, "%s;%s;%s" % (componentversion, coreversion, priceversion))


@action
def doUpdatePrice(pos_id):
    conn = None
    try:
        product_code = show_keyboard(pos_id, "Informe o código do produto", title="", mask="", numpad=True)
        if not product_code:
            show_info_message(pos_id, "Erro ao atualizar preços", msgtype="Error")
            return
        product_price = show_keyboard(pos_id, "Informe o preço do produto", title="", mask="CURRENCY", numpad=True)
        if not product_price:
            show_info_message(pos_id, "Erro ao atualizar preços", msgtype="Error")
            return

        context = product_code.replace(",", ".").split('.')
        product_code = context.pop()
        product_context = ".".join(context)

        conn = persistence.Driver().open(mbcontext, pos_id)
        sql_consulta_preco = "SELECT 1 FROM productdb.Price WHERE ProductCode = {0} and Context = '{1}' and PriceListId = 'EI' and ValidThru = '2099-12-31 00:00:00'"
        sql_consulta_preco_produto = "SELECT 1 FROM productdb.Price WHERE ProductCode = {0} and Context = '1' and PriceListId = 'EI' and ValidThru = '2099-12-31 00:00:00'"
        if product_context == '':
            cursor = conn.select(sql_consulta_preco_produto.format(product_code))
        else:
            cursor = conn.select(sql_consulta_preco.format(product_code, product_context))

        if cursor.rows() > 0:
            updatePrice(conn, product_price, product_code, product_context)
            show_info_message(pos_id, "Preços atualizados", msgtype="success")
            return

        list_show_popup = []
        list_context = []

        context_range = len(context)
        for x in xrange(context_range):
            context.pop(0)
            if context:
                product_context = ".".join(context)
                cursor = conn.select(sql_consulta_preco.format(product_code, product_context))
                if cursor.rows() > 0:
                    list_show_popup.append(product_context + "." + product_code)
                    list_context.append(product_context)
            else:
                cursor = conn.select(sql_consulta_preco_produto.format(product_code))
                if cursor.rows() > 0:
                    list_show_popup.append(product_code)
                    list_context.append("")

        if len(list_show_popup) == 0:
            show_info_message(pos_id, "Produto não encontrado", msgtype="Error")
            return

        index = show_listbox(pos_id, list_show_popup, message="Não foi encontrado o produto informado", buttons="$OK|$CANCEL")
        if index is None:
            return

        updatePrice(conn, product_price, product_code, list_context[index])
        show_info_message(pos_id, "Preços atualizados", msgtype="success")
    except Exception as ex:
        show_info_message(pos_id, "Erro ao atualizar preços", msgtype="Error")
    finally:
        if conn:
            conn.close()


def updatePrice(conn, product_price, product_code, product_context):
    sql_check_price = "SELECT AddedUnitPrice, DefaultUnitPrice FROM productdb.Price WHERE ProductCode = {0} and Context {1} and PriceListId = 'EI' and ValidThru = '2099-12-31 00:00:00'"
    if product_context == "":
        context = "= 1"
    else:
        context = "= "  + product_context

    cursor = conn.select(sql_check_price.format(product_code, context))
    if cursor.get_row(0).get_entry('AddedUnitPrice'):
        update_type = "AddedUnitPrice"
    else:
        update_type = "DefaultUnitPrice"

    sql = "UPDATE productdb.Price SET {0} = {1} WHERE ProductCode = {2} and Context {3} and ValidThru = '2099-12-31 00:00:00'".format(
        update_type, product_price, product_code, context)
    conn.select(sql)
    return


@action
def doApplyUpdatePrice(pos_id):
    dir_database = "../data/server/databases/product.db"
    dir_genesis = "../genesis/data/server/databases/product.db"
    if os.path.exists(dir_genesis):
        copy2(dir_database, dir_genesis)
    show_info_message(pos_id, "Preços atualizados, favor reiniciar o sistema", msgtype="success")


@action
def doGetSATOperationalStatus(pos_id):
    msg = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST, format=FM_PARAM, data=pos_id)
    model = get_model(pos_id)
    if msg.token == TK_SYS_ACK:
        print_report(pos_id, model, True, "sats_op_report", pos_id, msg.data)
    else:
        show_info_message(pos_id, "%s" % msg.data, msgtype="error")


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
            void_order(pos_id)
        show_info_message(pos_id, "Pedidos salvos apagados", msgtype="success")
    except Exception as _:
        show_info_message(pos_id, "Erro ao tentar apagar pedidos salvos", msgtype="error")


@action
def doPrintLogoffReport(pos_id):
    model = get_model(pos_id)
    sessions = []

    period = show_keyboard(pos_id, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)

    if period in (None, ''):
        return

    conn = None
    try:
        date_input_format = "%Y-%m-%d %H:%M:%S"
        date_output_format = "%d/%m/%Y %H:%M:%S"

        conn = DBDriver().open(mbcontext, dbname=str(pos_id))
        conn.transaction_start()

        sql = """SELECT * FROM posctrl.UserSession
                  WHERE BusinessPeriod = '%s'
                  ORDER BY CloseTime DESC
                  """ % period
        cursor = conn.select(sql)

        for row in cursor:
            id = row.get_entry("SessionId")
            pos = id.split(",")[0][4:]
            closeTime = row.get_entry("CloseTime")
            if closeTime is not None:
                openTime = convert_from_utf_to_localtime(datetime.datetime.strptime(row.get_entry("OpenTime"), date_input_format)).strftime(date_output_format)
                closeTime = convert_from_utf_to_localtime(datetime.datetime.strptime(closeTime, date_input_format)).strftime(date_output_format)
                opName = row.get_entry("OperatorName")
                descr = opName + "  " + openTime
                msg = "POS: %s\nNome do operador: %s\nHora de entrada: %s\nHora de saída: %s" % (pos, opName, openTime, closeTime)
                sessions.append((id, descr, msg))

    except Exception as e:
        sys_log_exception('Exception printing logoff report: {}'.format(e))
        show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
        return
    finally:
        if conn:
            conn.close()

    if not sessions:
        show_messagebox(pos_id, "Não há sessões encerradas", title="$ERROR", icon="error", buttons="$OK")
        return

    selected = show_text_preview(pos_id, sessions, title='$SELECT_AN_OPTION', buttons='$PRINT|$CANCEL', defvalue='', onthefly=False, timeout=120000)

    if selected is not None and selected[0] == '0':
        try:
            period = selected[4][7:15]
            userid = selected[2][5:]
            session_id = selected[1] + "," + selected[2] + "," + selected[3] + "," + selected[4]
            session_pos_id = selected[1][4:]
            print_report(pos_id, model, True, "checkout_report", session_pos_id, period, userid, "False", "0", "logoffuser", session_id)
        except Exception as e:
            show_info_message(pos_id, "Erro ao tentar reimprimir Relatório de Fechamento de Operador", msgtype="error")


@action
def doCheckSiTef(pos_id):
    get_model(pos_id)
    date = str(datetime.datetime.now())
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
def doUpdateVtt(pos_id):
    wait_dlg_id = None
    try:
        wait_dlg_id = show_messagebox(pos_id, "$PLEASE_WAIT", "$UPDATE_VTT", buttons="", asynch=True)

        response = requests.get(update_vtt_url + store_id)

        if response:
            show_messagebox(pos_id, response.text, title="$UPDATE_VTT", buttons="$OK")
        else:
            show_messagebox(pos_id, response.text, title="$ERROR", icon="error", buttons="$OK")
    except Exception as ex:
        show_messagebox(pos_id, ex, title="$ERROR", icon="error", buttons="$OK")
    finally:
        if wait_dlg_id:
            close_asynch_dialog(pos_id, wait_dlg_id)

def is_sangria_enable():
    if sangria_levels is None:
        return False
    else:
        return True

def doSetDrawerStatus(pos_id, amount, state=None, alert_level_1='0'):
    sangria_levels_list = [float(level) for level in sangria_levels.split(";")] if sangria_levels else []
    if sangria_levels_list:
        amount = float(amount)
        if amount >= sangria_levels_list[2]:
            show_messagebox(pos_id, "Caixa travado, necessario fazer a Sangria", title="$SKIM_ALERT", icon="error", buttons="$OK")
            return True
        elif state == "TOTALED" and sangria_levels_list[0] <= amount < sangria_levels_list[2]:
            if amount < sangria_levels_list[1]:
                if int(alert_level_1 or 0) == 0:
                    set_custom(pos_id, "sangria_level_1_alert", "1")
                else:
                    return False
            show_messagebox(pos_id, "Necessario fazer a Sangria", title="$SKIM_ALERT", icon="error", buttons="$OK")

    return False


@action
def doReportSangria(posid, *args):
    conn, data, print_list, json_data = None, [], [], []
    try:
        period = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)
        if period is None:
            return
        if not is_valid_date(period):
            show_info_message(posid, "$INVALID_DATE", msgtype="error")
            return

        query_transfer = "SELECT *, strftime('%s',timestamp) as ID FROM account.Transfer WHERE period='{0}'".format(period)

        conn = persistence.Driver().open(mbcontext, posid)
        cursor = conn.select(query_transfer)

        header = "{}".format("*" * 35)
        footer = "{}".format("*" * 35)

        for row in cursor:
            pos_id, amount, timestamp, session_id, gla_ccount, description, date_fiscal, ID = map(row.get_entry, ("PosId",  "Amount", "Timestamp", "SessionId", "GLAccount", "Description", "Period", "ID"))


            if gla_ccount is None:
                continue


            if description in ['DECLARED_AMOUNT', 'TRANSFER_SKIM', "TRANSFER_CASH_IN", "TRANSFER_CASH_OUT"]:
                # mounting dict to send to backoffice
                user = filter(lambda x: 'user=' in x, session_id.split(','))
                user = user[0].split("=")[1] if user[0] else ""
                number_banana = filter(lambda x: 'envelope=' in x, gla_ccount.split(';'))
                if number_banana:
                    number_banana = number_banana[0].split("=")[1] if number_banana[0] else ""

                manager_id = filter(lambda x: 'managerID=' in x, gla_ccount.split(';'))
                if manager_id:
                    manager_id = manager_id[0].split("=")[1] if manager_id[0] else ""


                date_sangria = get_date_difference_GMT_timezone(timestamp)

                json_data.append([number_banana, {
                    "amount": amount,
                    "timestamp": timestamp,
                    "session_id": session_id,
                    "gla_ccount": gla_ccount,
                    "date_fiscal": date_fiscal,
                    "pos_id": pos_id,
                    "number_banana": number_banana,
                    "manager_id": manager_id,
                    "transfer_id": ID}, ID])

                # montando the list to display the popup
                banana = "Envelope# {}".format(number_banana)

                info = filter(lambda x: 'Valor Informado=' in x, gla_ccount.split(';'))
                if info:
                    info = info[0].split("=")[1] if info[0] else ""

                esper = filter(lambda x: 'Valor Esperado=' in x, gla_ccount.split(';'))
                if esper:
                    esper = esper[0].split("=")[1] if esper[0] else ""

                just = filter(lambda x: 'Justificativa= ' in x, gla_ccount.split(';'))
                if just:
                    just = just[0].split("=")[1] if just[0] else ""


                # banana, period, timestanp, user
                print_banana = "%-13s: %s" % ("Envelope", number_banana)
                print_period = "%-13s: %s/%s/%s" % ("Periodo", date_fiscal[6:], date_fiscal[4:6], date_fiscal[:4])
                print_timestamp = "%-13s: %s/%s/%s %s:%s:%s" % ("Timestamp", date_sangria[8:10], date_sangria[5:7], date_sangria[:4], date_sangria[11:13], date_sangria[14:16], date_sangria[17:19])
                print_user = "%-13s: %s" % ("Usuario", user)
                formated_msg = "{}\n\n{}\n{}\n{}\n{}\n{}\n{}\n{}\n\n{}".format(header, print_banana, print_period, print_timestamp, info, esper, print_user, just, footer)

                # dict with all the sangrias
                print_list.append([number_banana, formated_msg])

                # list to popup
                data.append([number_banana, banana, formated_msg])

        if len(data) == 0:
            show_info_message(posid, "Não existem sangrias {}para essa data".format("" if show_all_transfer else "pendentes "), msgtype="error")
            return
    finally:
        if conn:
            conn.close()

    index = show_text_preview(posid, data, title='Selecione uma Sangria:', buttons='$PRINT|$CANCEL', defvalue='', onthefly=False, timeout=120000)
    if index is None:
        return


    if int(index[0]) == 0:
        try:
            message = None

            for msg in print_list:
                try:
                    if msg[0] == index[1]:
                        message = str(msg[1])
                except:
                    continue

            if message is not None:
                try:
                    msg = mbcontext.MB_EasySendMessage("printer%s" % posid, TK_PRN_PRINT, FM_PARAM, message)
                except MBException:
                    time.sleep(0.5)
                    msg = mbcontext.MB_EasySendMessage("printer%s" % posid, TK_PRN_PRINT, FM_PARAM, message)
                finally:
                    if msg.token == TK_SYS_ACK:
                        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
                    else:
                        show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        except Exception as _:
            show_info_message(posid, "Erro ao imprimir relatório", msgtype="error")


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
    initial_date = show_keyboard(pos_id, "Digite a Data Inicial ou pressione 'Ok' para Data Atual", title="", mask="DATE", numpad=True)
    if initial_date is None:
        return
    if not is_valid_date(initial_date):
        show_info_message(pos_id, "$INVALID_DATE", msgtype="error")
        return None

    final_date = show_keyboard(pos_id, "Digite a Data Inicial ou pressione 'Ok' para Data Atual", title="", mask="DATE", numpad=True)
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

    period = show_keyboard(pos_id, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)
    if period is None:
        return
    if not is_valid_date(period):
        show_info_message(pos_id, "$INVALID_DATE", msgtype="error")
        return

    date_bkOffice = '-'.join(i for i in [period[:4], period[4:6], period[6:8]])
    query_transfer = "SELECT PosId, OrderId, datetime(DataNota, 'unixepoch') as date, OrderPicture  FROM fiscal.FiscalData WHERE date(datetime(datanota, 'unixepoch')) == '{0}' AND SentToBKOffice <> 1 AND SentToNfce = 1".format(date_bkOffice)

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

        order_pict = etree.XML(base64.b64decode(order_picture))

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
        wait_dlg_id = show_messagebox(pos_id, "$SENDING_ORDER_TO_BKOFFICE", "$WAIT_MESSAGE", buttons="", asynch=True)
        try:
            obj = {}
            for data in json_data:
                try:
                    if data[0] == index[1]:
                        obj = data[1]
                except:
                    continue

            msg = mbcontext.MB_EasySendMessage("BKOfficeUploader", TK_BKOFFICEUPLOADER_SEND_BKOFFICE_ORDER, data=str(obj), format=FM_PARAM, timeout=-1)
            msg = eval(msg.data)

            if msg.get('status'):
                show_info_message(pos_id, msg.get('msg').encode('utf-8'), msgtype="success")
            else:
                show_info_message(pos_id, msg.get('msg').encode('utf-8'), msgtype="error")

        except Exception as _:
            show_info_message(pos_id, "Falha de comunicação com o servidor", msgtype="error")
        finally:
            close_asynch_dialog(pos_id, wait_dlg_id)

    if int(index[0]) == 1:
        try:
            message = None

            for msg in print_list:
                try:
                    if msg[0] == index[1]:
                        message = str(msg[1])
                except:
                    continue

            if message is not None:
                try:
                    msg = mbcontext.MB_EasySendMessage("printer%s" % pos_id, TK_PRN_PRINT, FM_PARAM, message)
                except MBException:
                    time.sleep(0.5)
                    msg = mbcontext.MB_EasySendMessage("printer%s" % pos_id, TK_PRN_PRINT, FM_PARAM, message)
                finally:
                    if msg.token == TK_SYS_ACK:
                        show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")
                    else:
                        show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
        except Exception as _:
            show_info_message(pos_id, "Erro ao imprimir relatório", msgtype="error")


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
        logger.exception("Erro consultando componente Blacklist")
        return True
    return True


@action
def changeRemoteOrderStoreStatus(posid):
    model = get_model(posid)
    user_id = get_custom(model, 'Last Manager ID')
    msg = send_message("RemoteOrder", TK_REMOTE_ORDER_GET_STORE, FM_PARAM)
    if msg.token == TK_SYS_NAK:
        show_info_message(posid, "Erro obtendo status da loja para o app/delivery.", msgtype="error")
        return
    result = json.loads(msg.data)
    is_store_open = result["status"] == "Open"
    status_from = "aberta" if is_store_open else "fechada"
    status_to = "aberta" if not is_store_open else "fechada"
    if show_confirmation(posid, message="Atualmente a loja está {}.\Mudar para {}?".format(status_from, status_to), buttons="Sim|Não"):
        msg = send_message(
            "RemoteOrder",
            TK_REMOTE_ORDER_CLOSE_STORE if is_store_open else TK_REMOTE_ORDER_OPEN_STORE,
            FM_PARAM,
            user_id
        )
        if msg.token == TK_SYS_NAK:
            show_info_message(posid, "Erro alterando status da loja para o app/delivery.", msgtype="error")
        else:
            show_info_message(posid, "Loja {} para o app/delivery.".format(status_to), msgtype="success")


def handle_order_taker_exception(pos_id, pos_ot, ex, mbcontext, dlgid=None):
    # type: (int, OrderTaker, OrderTakerException, MBEasyContext, int) -> bool
    if ex.getErrorCode() == 4005:
        order_xml = etree.XML(pos_ot.orderPicture(pos_id))
        logger.exception("OrderTakerException: synchronization error.\n Order XML:\n {}"
                         .format(etree.tostring(order_xml)))

        error_description_is_json = True
        try:
            json.loads(ex.getErrorDescr())
        except Exception as _:
            error_description_is_json = False

        if not error_description_is_json:
            # show_info_message(pos_id, "$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(),
            #                                                      ex.getErrorDescr().replace("{}", "")),
            #                  msgtype="critical")
            show_messagebox(pos_id, message="$ERROR_CODE_INFO|%d|%s" % (ex.getErrorCode(), ex.getErrorDescr()),
                            icon="error")
        handle_synchronization_error(pos_id, pos_ot, dlgid)
        return True
    elif ex.getErrorCode() == 100036:
        handle_printer_validation_error(pos_id, "$SERIAL_PRINTER_VALIDATION_ERROR")
        return True
    elif ex.getErrorCode() == 100037:
        try:
            prn = FpRetry(pos_id, mbcontext)
            gt_encrypted = prn.readEncrypted("RW_GT")
            if gt_encrypted == "ERROR":
                gt_printer = prn.readOut(fpreadout.FR_GT).strip()
                prn.writeEncrypted("RW_GT", gt_printer)
                show_info_message(pos_id, "Validando GT. Tente novamente.", msgtype="warning")
                return True
        except FPException as _:
            logger.exception("Error reading/writing gt")
            return True
        except Exception as _:
            logger.exception("Error reading/writing gt")
            return True

        handle_printer_validation_error(pos_id, "$GT_PRINTER_VALIDATION_ERROR")
        return True

    return False


class FpRetry(fp):
    def readOut(self, readout_option, params = []):
        """ fp.readOut(readout_option, params=[]) -> readout value
        Performs a fiscal printer readout
        @return: the readout data
        @raise FPException on fiscal-printer error
        """
        error = None
        for i in xrange(0, 3, 1):
            try:
                data = '\x00'.join(map(str, [fpcmds.FPRN_READOUT, readout_option] + params))
                msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
                self._checkErr(msg)
                return msg.data
            except FPException as ex:
                error = ex
                logger.exception("Erro lendo da impressora. readout_option=%d, Tentativa=%d" % (readout_option, i))
                time.sleep(1)
            except:
                logger.exception("Erro lendo da impressora. readout_option=%d, Tentativa=%d" % (readout_option, i))
                time.sleep(1)
        if error:
            sysactions.show_info_message(self._posid, str(error), msgtype="error")
            raise error

def _get_custom_property_value_by_key(property_key, custom_properties):
    filtered_custom_properties = filter(lambda x: x[0] == property_key, custom_properties.items())
    if len(filtered_custom_properties) == 1:
        return filtered_custom_properties[0][1]
    else:
        return None


@action
def doClearOptionItem(posid, linenumber="", itemid="", *args):
    model = get_model(int(posid))
    check_current_order(posid, model=model, need_order=True)
    if not linenumber or not itemid:
        show_info_message(posid, "Select the line to clear", msgtype="error")
        return False  # Nothing to clear
    # Clear the option
    posot = get_posot(model)
    try:
        posot.clearOption(posid, linenumber, "", itemid)
        return True
    except ClearOptionException, e:
        sys_log_exception("Could not clear option")
        show_info_message(posid, "Error %s" % e, msgtype="error")
    except OrderTakerException, e:
        # show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
        show_messagebox(posid, message="$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()),
                        icon="error")
    return False


@action
def doModifier(posid, itemid, level, pcode, qty, linenumber, modtype):
    """
    @param itemid  parent item id
    @param level  parent level
    @param pcode  modifier code to add/remove
    @param qty  quantity to add (0 to remove)
    @param linenumber  current line selected
    @param modtype  type of modification:
        'TOGGLE' add or remove modifier
        'EXTRA' set modifier as extra
        'LIGHT' set modifier as light
        'ON_SIDE' set modifier as on-side
    """
    model = get_model(posid)
    posot = get_posot(model)
    nextlevel = int(level) + 1
    removing = int(qty) == 0

    posot.blkopnotify = True
    posot.changeModifier(posid, linenumber, itemid, nextlevel, pcode, qty)

    commentmap = {
        "ON_SIDE": "[On Side]",
        "LIGHT": "[Light]"
    }
    commentkeys = commentmap.keys()

    if modtype in commentkeys or removing:
        # find current sale line
        order = model.find("CurrentOrder/Order")
        currline = filter(
            lambda sl:
                sl.get("itemId") == itemid and
                sl.get("partCode") == pcode and
                sl.get("lineNumber") == linenumber,
            order.findall("SaleLine")
        )
        lineexists = currline and len(currline) > 0
        # make a dictionary of existing comments, where the key is the comment description
        # and the value the comment id
        comments = {}
        if lineexists:
            for comment in currline[0].findall("Comment"):
                comments[comment.get("comment")] = comment.get("commentId")
        if removing:
            # check if comments needs to be removed
            for commentkey in commentkeys:
                commenttext = commentmap[commentkey]
                if commenttext in comments.keys():
                    posot.delComment(comments[commenttext])
        else:
            # add comment if necessary
            # workaround: we cannot add a comment on a line that is default ingredient, we need to
            # remove the ingredient and re-add it in order to ensure that the line exist
            if not lineexists:
                posot.changeModifier(posid, linenumber, itemid, nextlevel, pcode, 0)
                posot.changeModifier(posid, linenumber, itemid, nextlevel, pcode, qty)
            posot.addComment(linenumber, itemid, nextlevel, pcode, commentmap[modtype])

    posot.blkopnotify = False
    posot.updateOrderProperties(posid)


@action
def importEmployees(pos_id):
    try:
        params = '\0'.join(['', 'MwBOH', 'ImportUser'])
        reply = send_message("MwBOH", TK_EVT_EVENT, FM_PARAM, params)
        if reply.token == TK_SYS_NAK:
            show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
            return False
        show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")
    except:
        show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
    return True


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


def _get_products(pos_id="1"):
    global _products_cache, _product_by_barcode

    if _products_cache is None:
        model = get_model(pos_id)
        query = """SELECT P.ProductCode, P.ProductName, Price.DefaultUnitPrice AS UnitPrice, PCP.CustomParamValue AS BarCode, NULLIF(Production.JITLines,'None') AS ProductionLine
                   FROM ProductClassification PC
				   Left Join Product P on PC.ProductCode = P.ProductCode and PC.ClassCode = 1
                   Left JOIN Production ON Production.ProductCode=P.ProductCode
                   JOIN Price ON Price.ProductCode=P.ProductCode AND Context IS NULL AND CURRENT_DATE BETWEEN Price.ValidFrom AND Price.ValidThru AND PriceListId='EI' AND UnitPrice >0
                   Left JOIN ProductCustomParams PCP ON PCP.ProductCode=P.ProductCode AND PCP.CustomParamId='BarCode'
                   WHERE PC.ProductCode not in (select ProductCode from ProductClassification where ClassCode <> 1 ) and PC.ProductCode not in (select ClassCode from ProductClassification where ClassCode <> 1 ) ORDER BY P.ProductName"""
        prodlist = []
        try:
            conn = persistence.Driver().open(mbcontext, pos_id)
            cursor = conn.select(query)
            for row in cursor:
                plu, name, price, barcode, prodline = map(row.get_entry, ("ProductCode", "ProductName", "UnitPrice", "BarCode", "ProductionLine"))
                product = {
                    "plu": plu,
                    "name": name,
                    "price": format_amount(model, price),
                    "barcode": barcode,
                    "prodline": prodline
                }
                prodlist.append(product)
                _product_by_barcode[barcode] = product
        except:
            sys_log_exception("Error getting product list")
        finally:
            if conn:
                conn.close()
        _products_cache = prodlist

    return _products_cache


@action
def getProducts(pos_id, *args):
    return json.dumps(_get_products(pos_id))


@action
def doPriceLookup(pos_id, timeout=45, *args):
    global _scanner_sale_paused
    model = get_model(pos_id)
    services = get_used_service(model, "scanner", get_all=True)
    scanner = None
    for svc in services:
        if "scanner" in svc:
            scanner = svc
            break
    if scanner is None:
        show_info_message(pos_id, "$NO_SCANNER_CONFIGURED", msgtype="critical")

        return
    timeout = timeout * 1000
    try:
        _scanner_sale_paused[int(pos_id)] = True
        dlg_id = show_messagebox(pos_id, message="$PLEASE_SCAN_FOR_PRICE_LOOKUP", title="$PRICE_LOOKUP", buttons="$CANCEL", asynch=True, timeout=timeout, focus=False)
        try:
            barcode = read_scanner(scanner, timeout, dlg_id)
        finally:
            close_asynch_dialog(pos_id, dlg_id)
        if barcode is not None:
            barcode = base64.b64decode(barcode).strip()
            if barcode and barcode in _product_by_barcode:
                show_messagebox(pos_id, message="{0}: {1}".format(_product_by_barcode[barcode]['name'], _product_by_barcode[barcode]['price']), title="$PRICE_LOOKUP")
    finally:
        _scanner_sale_paused[int(pos_id)] = False


@action
def doUpdateMediaData(posid, *args):
    try:
        mbcontext.MB_EasySendMessage('MediaManager', TK_EVT_EVENT, data='\0MediaManager\0UpdateMedia\0true\01\01\0', timeout=5000000)
        show_messagebox(posid, "Atualizando imagens em segundo plano")
    except:
        sys_log_exception("Exception updating media data")
        show_info_message(posid, "Erro atualizando imagens, tente novamente.", msgtype="error")


@action
def doScanTab(pos_id, timeout=45, store_order=True, message="Por favor, pegue sua ficha de consumo e posicione o código de barras da ficha no leitor abaixo.", title="Envie seu pedido", *args):
    global _scanner_sale_paused
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
            _scanner_sale_paused[int(pos_id)] = True
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
            _scanner_sale_paused[int(pos_id)] = False
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