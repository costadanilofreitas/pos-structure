# -*- coding: utf-8 -*-
# Module name: sysactions.py
# Module Description: Contains action helper functions and "kernel" actions which do not depend on a specific environment
#
# Copyright (C) 2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

"""
Module sysactions
Contains action helper functions and "kernel" actions which do not depend on a specific environment

Please note that this module depends on the "pyscripts" module, so it can only be imported on a script run by that component.
"""

# Python standard modules
import os
import datetime
import time
import threading
import base64
import json
from xml.etree import cElementTree as etree
from cStringIO import StringIO
from xml.sax import saxutils
# Our modules
import pyscripts  # IMPORTANT - THIS CAN ONLY BE IMPORTED BY A SCRIPT RUNNING IN THE PYSCRIPTS COMPONENT !!!
import cfgtools
import persistence
from systools import sys_log_info, sys_log_debug, sys_log_exception, sys_log_warning
# from syserrors import *
from msgbus import TK_SYS_NAK, TK_POS_SETDEFSERVICE, TK_SYS_ACK, TK_POS_GETCONFIG, TK_POS_GETPOSLIST, TK_MSR_REQUESTSWIPE, TK_POS_SETMAINSCREEN, \
    TK_POS_SETSCREEN, TK_POS_GETMODEL, TK_LDISP_WRITE, TK_POS_SETINFOMSG, TK_POS_SHOWDIALOG, TK_POS_DIALOGRESP, TK_REPORT_GENERATE, TK_POS_UPDATEDIALOG, \
    TK_PRN_PRINT, TK_STORECFG_GETFULL, TK_POS_MODELSETCUSTOM, TK_STORECFG_GET, TK_I18N_TRANSLATE, TK_L10N_TOCURRENCY, TK_USERCTRL_GETINFO, \
    TK_USERCTRL_GETINFO_BADGE, TK_USERCTRL_AUTHENTICATE, TK_PERSIST_QUERYEXEC, TK_EVT_EVENT, TK_HV_LISTHVS, FM_STRING, FM_PARAM, FM_XML, MBTimeout, MBException
from posot import OrderTaker


__all__ = (
    "StopAction", "AuthenticationFailed",
    "action", "send_message", "change_mainscreen", "change_screen", "get_model", "get_podtype", "get_posfunction", "get_business_period",
    "check_genesis_error", "get_operator_session", "get_posot", "get_used_service", "write_ldisplay", "is_day_opened", "is_day_blocked",
    "is_drawer_opened", "is_operator_logged", "has_operator_opened", "get_current_operator", "has_current_order", "has_open_options", "get_current_order",
    "check_drawer", "check_business_day", "check_operator_logged", "check_current_order", "show_info_message", "show_any_dialog", "show_messagebox",
    "show_confirmation", "show_listbox", "show_keyboard", "show_form", "show_print_preview", "show_ppview", "remove_xml_prolog", "show_order_preview",
    "show_text_preview", "close_asynch_dialog", "generate_report", "print_text", "print_report", "set_custom", "get_custom", "clear_custom",
    "translate_message", "format_date", "format_amount", "get_last_order", "get_line_product_name", "get_clearOptionsInfo", "can_void_line",
    "get_user_information", "authenticate_user", "is_valid_date", "calculate_giftcards_amount", "get_custom_params", "get_dimension",
    "get_pricelist", "check_main_screen", "get_storewide_config", "on_before_total", "assert_order_discounts", "get_authorization", "read_msr",
    "get_poslist", "get_cfg", "get_tender_types", "get_tender_type", "show_custom_dialog", "is_valid_datetime", "encode_string", "decode_string", "read_scanner",
    "list_hv_nodes", "ha_get_context", "ha_switch_servers", "update_any_dialog", "update_messagebox", "update_confirmation", "order_has_items", "show_rupture"
)

# Message-bus context
mbcontext = pyscripts.mbcontext
# Dictionary that holds action handlers
_actions = {}
# List of pending msr events
_msr_events = []
# List of pending scanner events
_scanner_events = []
# Parsed configuration for each POS (posid -> cfgtools.Group)
_posconfig = {}

# Date format
DATE_FMT = "%m/%d/%Y"
# Datetime format
DATETIME_FMT = '%m/%d/%Y %H:%M'

# Generic data key
GENERIC_DATA_KEY = "L#i*&<i43=dD91)yek(++moDnAR"


class StopAction(BaseException):
    """Exception class used to stop an action execution"""
    pass


class AuthenticationFailed(Exception):
    """ Exception raised by the *authenticate_user* function """


def initialize():
    """Initialize the sysactions module, subscribing to required events"""
    # Subscribes event callbacks
    pyscripts.subscribe_event_listener("POS_ACTION", _action_received)
    pyscripts.subscribe_event_listener("MSR_DATA", _msr_data_received)
    pyscripts.subscribe_event_listener("DIALOG_RESP", _dialog_resp_received)
    pyscripts.subscribe_event_listener("DEVICE_DATA", _scanner_data_received)


def _action_received(params):
    """Callback called by pyscripts module"""
    xml, subject, type = params[:3]
    # Find the action handler
    fn = _actions.get(type)
    if fn:
        # Parse the action parameters from the XML
        args = [el.findtext(".").encode("UTF-8") for el in etree.XML(xml).findall("Param")]
        # Call the action handler with the parameters
        return fn(*args)
    return None


def _msr_data_received(params):
    """Callback called by pyscripts module"""
    xml, subject, type = params[:3]
    msrtag = etree.XML(xml).find("MSR")
    tracks = [el.findtext(".") for el in msrtag.findall("Track")]
    logicalname = msrtag.get("name")
    msr_evt = None
    for msr_evt in _msr_events:
        if msr_evt[1] == logicalname:
            msr_evt[2] = tracks
            msr_evt[0].set()
            _msr_events.remove(msr_evt)
            break
    return None


def _scanner_data_received(params):
    """Callback called by pyscripts module"""
    xml, subject, type = params[:3]
    devicetag = etree.XML(xml).find("Device")
    data = devicetag.text
    logicalname = devicetag.get("name")
    scanner_evt = None
    for scanner_evt in _scanner_events:
        if scanner_evt[1] == logicalname:
            scanner_evt[2] = data
            scanner_evt[0].set()
            _scanner_events.remove(scanner_evt)
            break
    return None


def _dialog_resp_received(params):
    """Callback called by pyscripts module"""
    xml, subject, type = params[:3]
    parsed = etree.XML(xml)
    dialog = parsed.find("Dialog")
    response = parsed.find(".//Response")
    dlgid = str(dialog.get("id"))
    for msr_evt in _msr_events:
        if str(msr_evt[3]) == dlgid:
            msr_evt[0].set()
            if response is not None:
                # now the response contains the dialog return code
                res = 0
                try:
                    res = int(response.findtext("."))
                except:
                    sys_log_exception("Response field not found in dialog XML")
                msr_evt[2] = res
            _msr_events.remove(msr_evt)
            break
    for scanner_evt in _scanner_events:
        if str(scanner_evt[3]) == dlgid:
            scanner_evt[0].set()
            _scanner_events.remove(scanner_evt)
            break
    return None


#
# Helper functions
#


def action(fn):
    """Decorator used to indicate that a function is an action handler
    Functions with this decorator will be automatically called when
    a POS action with the same name is requested.
    """
    # Creates a wrapper function to handle fatal exceptions
    def wrapper(*args):
        res = ""
        try:
            res = fn(*args)
            # None becomes "", tuple is not modified so must be (format, str(data)) - any other value is converted to string
            res = "" if res is None else res if isinstance(res, tuple) else str(res)
        except StopAction:
            pass  # Ignore StopAction
        except:
            sys_log_exception("Exception trapped on action '%s.%s' [posid: %s]" % (fn.__module__, fn.func_name, args[0] if args else "unknown"))
            try:
                show_messagebox(args[0], "$FATAL_ERROR_CALL_SUPPORT", icon="critical")
            except:
                sys_log_exception("Could not show 'fatal error' message")
        return res
    # Save the wrapper as an action handler
    _actions[fn.func_name] = wrapper
    return fn


# Shortcut function for "mbcontext.MB_EasySendMessage"
def send_message(dest_name, token, format=FM_STRING, data=None, timeout=30000000):
    """ send_message(dest_name, token, format=FM_STRING, data=None, timeout=30000000) -> MBMessage
    Sends a message using the message-bus layer.
    Please refer to MBEasyContext.MB_EasySendMessage for the parameters documentation.
    The only difference of this function is that it defines a default timeout of 30 seconds for all messages.
    @note: This function will raise an exception if the message cannot be sent (see MB_EasySendMessage)
    """
    try:
        return mbcontext.MB_EasySendMessage(dest_name, token, format, data, timeout)
    except MBTimeout:
        sys_log_debug("Message-bus timeout sending message to [%s] token [%d]" % (dest_name, token))
        raise


def get_cfg(posid):
    """ get_cfg(posid) -> cfgtools.Group
    Retrieve the configuration group of a POS
    """
    posid = int(posid)
    if posid not in _posconfig:
        # Reads and stores the POS configuration
        msg = send_message("POS%d" % posid, TK_POS_GETCONFIG)
        cfg = cfgtools.read_string(msg.data)
        for grp in cfg.group("POS").groups:
            grpid = int(grp.name[3:] if grp.name.lower().startswith("pos") else grp.name)
            if grpid not in _posconfig:
                # Store this cfg group
                _posconfig[grpid] = grp
    return _posconfig[posid]


def get_poslist():
    """get_poslist() -> tuple
    Retrieves the list of configured POS IDs (tuple of ints)
    """
    # Gets the list of registered POS
    msg = send_message("PosController", TK_POS_GETPOSLIST)
    if msg.token == TK_SYS_NAK or not msg.data:
        # Try again
        time.sleep(2)
        msg = send_message("PosController", TK_POS_GETPOSLIST)
    poslist = tuple(int(posid) for posid in msg.data.split('\0'))
    return poslist


def check_genesis_error():
    """Check for any genesis error and notify the users"""
    flag = ".generrorflag"
    try:
        if not os.path.exists(flag):
            return
        mtime = os.stat(flag).st_mtime
        if abs(time.time() - mtime) > (60 * 60):
            # This flag file is older than one hour... just remove it and continue
            os.remove(flag)
            return
        # There was a recent genesis error... notify all POS
        sys_log_warning("Genesis error detected, notifying all POS to call the support")
        for posid in get_poslist():
            show_info_message(posid, "$GENESIS_ERROR_CALL_SUPPORT", timeout=10000, msgtype="error")
        os.remove(flag)
    except:
        sys_log_exception("Could not check for genesis error flag")


def read_msr(logicalname, timeout=60000, dialogid=-1, params=[]):
    evt = threading.Event()
    evt.clear()
    evtdata = [evt, logicalname, None, dialogid]
    _msr_events.append(evtdata)
    try:
        send_message(logicalname, TK_MSR_REQUESTSWIPE, FM_STRING, "\0".join([str(timeout)] + params))
    except:
        sys_log_exception("Error communicating with MSR: %s" % logicalname)
    # This timeout is in seconds
    evt.wait(float(timeout) / 1000)
    # Note that the response can be a list with the tracks, or the button
    # index from the dialog
    return evtdata[2]


def read_scanner(logicalname, timeout=60000, dialogid=-1, params=[]):
    evt = threading.Event()
    evt.clear()
    evtdata = [evt, logicalname, None, dialogid]
    _scanner_events.append(evtdata)
    # This timeout is in seconds
    evt_state = evt.wait(float(timeout) / 1000)
    res = evtdata[2]
    if not evt_state:
        # remove event from list on timeout
        _scanner_events.remove(evtdata)
    return res


def get_authorization(posid, min_level=None, model=None, timeout=60000, numpad=True, nopad=False, hide_user_id=False):
    """ get_authorization(posid, min_level=None, model=None, timeout=60000) -> True or False
    Requests authorization for an operation.
    The "authorizationType" parameter on PosController defines how the authorization will be requested.
    Possible values are: ("login", "card")
    @param posid - POS id
    @param min_level - optional minimum user level required for this operation
    @param model - optional POS model (will be retrieved if necessary)
    @param timeout - operation timeout (in millis)
    @return True if authorization succeeded, False otherwise
    """
    auth_type = get_cfg(posid).key_value("authorizationType", "card").lower()
    #
    # CARD authorization
    #
    if auth_type in ('card', 'badge_number'):
        # Check wich card reader (MSR) we should use
        model = model or get_model(posid)
        msr_name = get_used_service(model, "msr")
        if not msr_name:
            # No card reader configured - on DEMO mode we can just show a confirmation
            demo_mode = (get_cfg(posid).key_value("demoMode", "false").lower() == "true")
            if demo_mode:
                return show_confirmation(posid, message="$CONFIRM_DEMO_MODE")
            show_info_message(posid, "$CARDREADER_NOT_CONFIGURED", msgtype="error")
            return False

        try:
            user_number = int(show_keyboard(posid, "$SWIPE_CARD_TO_AUTHORIZE", title="$MAGNETIC_STRIPE_READER", mask="INTEGER", is_password=True, nopad=True, noinput=True))
        except:
            return  # User cancelled, or timeout

        if auth_type == 'badge_number':
            key = 'badge_number'
        else:
            key = 'user_id'
        user_str = get_user_information(str(user_number), key)
        if user_str:
            user = etree.XML(user_str).find('user')
        else:
            user = None

        try:
            level = None
            if user is not None:
                level = int(user.get('Level') or -1)
                if level >= min_level:
                    # Success
                    sys_log_info("Authentication succeeded for POS id: %s, user id: %s" % (posid, user_number))
                    return True
            else:
                show_info_message(posid, "$INVALID_USER_OR_PASSWORD", msgtype="error")
                sys_log_info("Authentication failed for POS id: %s, user id: %s" % (posid, user_number))
                return False
        except:
            show_info_message(posid, "$INVALID_USER_OR_PASSWORD", msgtype="error")
            return False
    #
    # LOGIN authorization
    #
    if auth_type == "login":
        # Request user ID and password to GUI
        userid = show_keyboard(posid, "$AUTH_ENTER_USER_ID", title="", mask="INTEGER", numpad=numpad, nopad=nopad, is_password=hide_user_id)
        if userid is None:
            return  # User cancelled, or timeout
        message = "$ENTER_PASSWORD_NOID" if hide_user_id is True else "$ENTER_PASSWORD|%s" % (userid)
        passwd = show_keyboard(posid, message=message, title="$OPERATOR_LOGIN", is_password=True, numpad=numpad, nopad=nopad)
        if passwd is None:
            return  # User cancelled, or timeout
        # Verify the user id/password/level
        try:
            authenticate_user(userid, passwd, min_level=min_level)
            # Success
            sys_log_info("Authentication succeeded for POS id: %s, user id: %s" % (posid, userid))
            return True
        except AuthenticationFailed, ex:
            show_info_message(posid, "$%s" % ex.message, msgtype="error")
        return False
    return False


def change_mainscreen(posid, screenid, persist=False):
    """ change_mainscreen(posid, screenid, persist=False)
    Changes the main screen of a POS.
    @param posid - {str or int} - POS id
    @param screenid - {str or int} - screen id
    @param persist - {bool} - Flag indicating if the operation should be persisted
    """
    send_message("POS%d" % int(posid), TK_POS_SETMAINSCREEN, FM_PARAM, "%s\0%s\0%s" % (posid, screenid, "true" if persist else "false"))


def change_screen(posid, screenid, previousid=""):
    """ change_screen(posid, screenid)
    Changes the current screen of a POS.
    @param posid - {str or int} - POS id
    @param screenid - {str or int} - screen id
    @param previousid - {str or int} - optional "previous screen id" to push in the screens stack INSTEAD of the current screen id
    """
    send_message("POS%d" % int(posid), TK_POS_SETSCREEN, FM_PARAM, "%s\0%s\0%s" % (posid, screenid, previousid))


def get_model(posid):
    """ get_model(posid) -> etree.XML
    Retrieves the model of a POS, in the form of an ElementTree instance (parsed XML).
    @param posid - {str or int} - POS id
    @return {etree.XML} - parsed model XML
    """
    resp = send_message("POS%d" % int(posid), TK_POS_GETMODEL, FM_STRING, str(posid))
    if resp.token != TK_SYS_ACK:
        raise Exception("Could not retrieve state of pos '%s'" % posid)
    return etree.XML(resp.data)


def get_podtype(model):
    """ get_podtype(model) -> str
    Retrieves the POD type of a POS model
    """
    return model.find("WorkingMode").get("podType")


def get_posfunction(model):
    """ get_podtype(model) -> str
    Retrieves the POS function of a POS model
    """
    return model.find("WorkingMode").get("posFunction")


def get_business_period(model):
    """ get_business_period(model) -> str
    Retrieves the business period of a POS model
    """
    return model.find("PosState").get("period")


def get_operator_session(model):
    """ get_operator_session(model)
    Gets the operator's session
    @param model - {etree.XML} - parsed model XML
    @return {str} - The session or None in case of error
    """
    for op in model.findall("Operator"):
        if op.get("state") == "LOGGEDIN":
            return op.get("sessionId")
    return None


def get_posot(model):
    """ get_posot(model) -> OrderTaker
    Retrieves an OrderTaker API instance for the given POS model.
    This API can be used to perform order operations (sale, void, etc)
    @param model - {etree.XML} - parsed model XML
    @return {OrderTaker} - instance
    """
    posot = OrderTaker(model.get("posId"), mbcontext)
    posot.podType = get_podtype(model)
    posot.businessPeriod = get_business_period(model)
    posot.sessionId = get_operator_session(model)
    operator = model.find("Operator")
    if operator is not None:
        posot.operatorId = operator.get("id")
    return posot


def get_used_service(model, service_type, get_all=False):
    """ get_used_service(model, service_type, get_all=False) -> str or list
    Retrieves an "used service" of a POS model, for a given service type.
    If get_all is False (default), then only the DEFAULT used service of that type will be returned (or None).
    If get_all is True, then ALL used services of that type will be returned (as a list).
    @param model - {etree.XML} - parsed model XML
    @param service_type - {str} - service type (E.g.: "printer", "cashdrawer", etc)
    @param get_all - {bool} - Indicates if all services should be returned, or just the default one
    @return {str or list} - used service(s)
    """
    services = [node for node in model.findall("UsedServices/Service") if node.get("type") == service_type]
    # Return all services
    if get_all:
        return [str(service.get("name")) for service in services]
    # only the default one
    for service in services:
        if service.get("default") == "true":
            return str(service.get("name"))
    return None


def write_ldisplay(model, text, marquee=None):
    """ write_ldisplay(model, text)
    Writes some text in the default line dispay of a POS.
    @param model - {etree.XML} - parsed model XML
    @param text - {str} - text to write
    @param marquee - {bool} - optional - if True, the marquee is started.
                     If False, the marquee is stopped.
                     If None (default), the marquee is not changed.
    @return {bool} - True if the text was successfuly written
    """
    service = get_used_service(model, "linedisplay")
    if service:
        try:
            if marquee is None:
                msg = send_message(service, TK_LDISP_WRITE, FM_STRING, text)
            else:
                reqbuf = "%s\0%s" % (text, "start" if marquee else "stop")
                msg = send_message(service, TK_LDISP_WRITE, FM_PARAM, reqbuf)
            return msg.token != TK_SYS_NAK
        except:
            sys_log_warning("Could not write to line-display")
    return False


def is_day_opened(model):
    """ is_day_opened(model)
    Checks if the given POS model has an open business period
    @param model - {etree.XML} - parsed model XML
    @return {bool} - True if there is an open business period
    """
    return model.find("PosState").get("state") in ("OPENED", "BLOCKED")


def is_day_blocked(model):
    """ is_day_blocked(model)
    Checks if the given POS model has a "blocked-by-time" business period
    @param model - {etree.XML} - parsed model XML
    @return {bool} - True if there is a blocked business period
    """
    return model.find("PosState").get("state") == "BLOCKED"


def is_drawer_opened(model):
    """ is_drawer_opened(model)
    Checks if the given POS model has an opened drawer
    @param model - {etree.XML} - parsed model XML
    @return {bool} - True if there is an drawer is opend
    """
    return model.findtext("CashDrawerStatus") == "OPENED"


def is_operator_logged(model):
    """ is_operator_logged(model)
    Checks if the given POS model has an operator logged
    @param model - {etree.XML} - parsed model XML
    @return {bool} - True if there is an operator logged
    """
    for op in model.findall("Operator"):
        if op.get("state") == "LOGGEDIN":
            return True
    return False


def has_operator_opened(model):
    """ has_operator_opened(model)
    Checks if the given POS model has any operator opened
    @param model - {etree.XML} - parsed model XML
    @return {bool} - True if there is any operator opened
    """
    for op in model.findall("Operators/Operator"):
        if op.get("state") in ("LOGGEDIN", "OPENED"):
            return True
    return False


def get_current_operator(model):
    """ get_current_operator(model)
    Retrieves the current operator logged
    @param model - {etree.XML} - parsed model XML
    @return - Operator tag or None
    """
    for op in model.findall("Operator"):
        if op.get("state") == "LOGGEDIN":
            return op
    return None


def has_current_order(model):
    """ has_current_order(model)
    Checks if the given POS model has an open order
    @param model - {etree.XML} - parsed model XML
    @return {bool} - True if there is an open order
    """
    order = model.find("CurrentOrder/Order")
    if order:
        state = order.get("state")
        if state in ("IN_PROGRESS", "TOTALED"):
            return True
    return False


def has_open_options(posid, model, show_message=False):
    """ has_current_order(model)
    Checks if the given POS model has an order with open options
    @param model - {etree.XML} - parsed model XML
    @param show_info_message - {bool} - if open option found should it show an info message?
    @return {bool} - True if there is an order with open options
    """
    posot = get_posot(model)
    open_options = posot.listOptions(posid, posot.ONLY_OPENOPTIONS, '')
    if open_options:
        if show_message:
            product_name = get_line_product_name(
                model, int(open_options[0]['lineNumber']))
            show_info_message(posid, '$NEED_TO_RESOLVE_OPTION|%s' % (product_name))
    return bool(open_options)


def get_current_order(model):
    """ get_current_order(model)
    Retrieves current order. The retrieved order may be in any state including closed.
    @param model - {etree.XML} - parsed model XML
    @return {etree.Element} - The order XML element
    """
    return model.find("CurrentOrder/Order")


def order_has_items(model):
    """ order_has_items(model)
    Check if current order is not empty.
    @param model - {etree.XML} - parsed model XML
    @return {bool} - True if there is at least an item in the order
    """
    has_items = False
    order = get_current_order(model)

    for sale_line in order.findall("SaleLine"):
        line_level = int(sale_line.attrib["level"])
        if line_level == 0:
            qty = int(sale_line.attrib["qty"])
            if qty > 0:
                has_items = True
                break

    return has_items


def check_drawer(posid, model=None):
    """ check_drawer(posid, model=None)
    Check if the cash drawer is opened. This will raise
    a StopAction exception if a drawer is opened (and an
    information message will be displayed)
    @param posid - {str or int} - POS id
    @param model - {etree.XML or None} - parsed model XML. If None, it will be
           retrieved from the PosController
    """
    opened = is_drawer_opened(model or get_model(posid))
    if opened:
        show_info_message(posid, "$NEED_TO_CLOSE_DRAWER_FIRST", msgtype="error")
        raise StopAction()


def check_business_day(posid, model=None, need_opened=True, can_be_blocked=True):
    """ check_business_day(posid, model=None, need_opened=True, can_be_blocked=True)
    Default business-period verification routine. This will raise
    a StopAction exception if a wrong state is detected (and an
    information message will be displayed)
    @param posid - {str or int} - POS id
    @param model - {etree.XML or None} - parsed model XML. If None, it will be
           retrieved from the PosController
    @param need_opened {bool} - If True (default), the business-period MUST be
           opened. If False, the business-period MUST be closed.
    @param can_be_blocked {bool} - If True (default), the business-period can be
           blocked by time. If False, the business-period MUST NOT be blocked.
    """
    if model is None:
        model = get_model(posid)
    opened = is_day_opened(model)
    if opened and not need_opened:
        show_info_message(posid, "$NEED_TO_CLOSE_BDAY_FIRST", msgtype="error")
        raise StopAction()
    if need_opened and not opened:
        show_info_message(posid, "$NEED_TO_OPEN_BDAY_FIRST", msgtype="error")
        raise StopAction()
    if (not can_be_blocked) and is_day_blocked(model):
        show_info_message(posid, "$POS_IS_BLOCKED_BY_TIME", msgtype="error")
        raise StopAction()


def check_operator_logged(posid, model=None, need_logged=True, can_be_blocked=True):
    """ check_operator_logged(posid, model=None, need_logged=True)
    Default operator verification routine. This will raise
    a StopAction exception if a wrong state is detected (and an
    information message will be displayed)
    @param posid - {str or int} - POS id
    @param model - {etree.XML or None} - parsed model XML. If None, it will be
           retrieved from the PosController
    @param need_logged {bool} - If True (default), there MUST be an operator
           logged in. If False, there MUST NOT be an operator logged in.
    @param can_be_blocked {bool} - If True (default), the business-period can be
           blocked by time. If False, the business-period MUST NOT be blocked.
    """
    if model is None:
        model = get_model(posid)
    if need_logged:
        check_business_day(posid, model)
    is_logged = is_operator_logged(model)
    if need_logged and not is_logged:
        show_info_message(posid, "$NEED_TO_LOGIN_FIRST", msgtype="warning")
        raise StopAction()
    elif is_logged and not need_logged:
        show_info_message(posid, "$NEED_TO_LOGOFF_FIRST", msgtype="warning")
        raise StopAction()
    if (not can_be_blocked) and is_day_blocked(model):
        show_info_message(posid, "$POS_IS_BLOCKED_BY_TIME", msgtype="error")
        raise StopAction()


def check_current_order(posid, model=None, need_order=True):
    """ check_current_order(posid, model=None, need_order=True)
    Default order verification routine. This will raise
    a StopAction exception if a wrong state is detected (and an
    information message will be displayed)
    @param posid - {str or int} - POS id
    @param model - {etree.XML or None} - parsed model XML. If None, it will be
           retrieved from the PosController
    @param need_order {bool} - If True (default), there MUST be an open order.
           If False, there MUST NOT be an open order.
    """
    has_order = has_current_order(model or get_model(posid))
    if has_order and not need_order:
        show_info_message(posid, "$NEED_TO_FINISH_ORDER", msgtype="error")
        raise StopAction()
    if need_order and not has_order:
        show_info_message(posid, "$NEED_TO_HAVE_ORDER", msgtype="error")
        raise StopAction()


def show_info_message(posid, message, timeout=5000, msgtype="info"):
    """ show_info_message(posid, message, timeout=5000, msgtype="info")
    Displays an information message for a POS
    @param posid - {str or int} - POS id
    @param message - {str} - Message to be displayed (may be an I18N message key)
    @param timeout - {int} - Message timeout in milliseconds (default: 5 seconds)
    @param msgtype - {str} - Message type (info, warning, etc) - known by UI implementation
    """
    send_message("POS%d" % int(posid), TK_POS_SETINFOMSG, FM_PARAM, "%s\0%s\0%d\0%s" % (posid, message, timeout, msgtype))


def show_any_dialog(posid, dlgtype, message, title, infotext, buttons, icon, timeout, mask, defvalue, minvalue, maxvalue, contents, asynch, linefeed="\\", focus=True, custom_dlg_id="", custom_dlg_timeout="0"):
    """private - used by other dialog helpers"""
    asynch = str(asynch).lower()
    focus = "true" if focus else "false"
    dlgtype, message, title, infotext, buttons, icon, mask, defvalue, minvalue, maxvalue, linefeed, focus, custom_dlg_id, custom_dlg_timeout = map(saxutils.quoteattr, map(str, (dlgtype, message, title, infotext, buttons, icon, mask, defvalue, minvalue, maxvalue, linefeed, focus, custom_dlg_id, custom_dlg_timeout)))
    contents_tag = "" if not contents else ("<Contents>%s</Contents>" % contents)
    xml = """<?xml version=\"1.0\" encoding="UTF-8"?>
    <DialogBox type=%(dlgtype)s title=%(title)s message=%(message)s info=%(infotext)s
    btn=%(buttons)s icon=%(icon)s mask=%(mask)s default=%(defvalue)s
    min=%(minvalue)s max=%(maxvalue)s lineFeed=%(linefeed)s focus=%(focus)s custom_dlg_id=%(custom_dlg_id)s custom_dlg_timeout=%(custom_dlg_timeout)s>
        %(contents_tag)s
    </DialogBox>
    """ % locals()
    etree.XML(xml)  # Ensure that the XML is well-formed
    params = "%(posid)s\0%(xml)s\0%(timeout)s\0%(asynch)s" % locals()
    res = send_message("POS%d" % int(posid), TK_POS_SHOWDIALOG, FM_PARAM, params, timeout=-1)
    if res.token == TK_SYS_ACK and res.data and res.data != "-1":
        return res.data
    return None  # Timeout


def update_any_dialog(posid, dlgid, dlgtype, message, title, infotext, buttons, icon, timeout, mask, defvalue, minvalue, maxvalue, contents, linefeed="\\", focus=True, custom_dlg_id="", custom_dlg_timeout="0"):
    """Update dialog, notice that this only works on asynch dialogs"""
    focus = "true" if focus else "false"
    dlgtype, message, title, infotext, buttons, icon, mask, defvalue, minvalue, maxvalue, linefeed, focus, custom_dlg_id, custom_dlg_timeout = map(saxutils.quoteattr, map(str, (dlgtype, message, title, infotext, buttons, icon, mask, defvalue, minvalue, maxvalue, linefeed, focus, custom_dlg_id, custom_dlg_timeout)))
    contents_tag = "" if not contents else ("<Contents>%s</Contents>" % contents)
    xml = """<?xml version=\"1.0\" encoding="UTF-8"?>
    <DialogBox type=%(dlgtype)s title=%(title)s message=%(message)s info=%(infotext)s
    btn=%(buttons)s icon=%(icon)s mask=%(mask)s default=%(defvalue)s
    min=%(minvalue)s max=%(maxvalue)s lineFeed=%(linefeed)s focus=%(focus)s custom_dlg_id=%(custom_dlg_id)s custom_dlg_timeout=%(custom_dlg_timeout)s>
        %(contents_tag)s
    </DialogBox>
    """ % locals()
    etree.XML(xml)  # Ensure that the XML is well-formed
    params = "%(posid)s\0%(dlgid)s\0%(xml)s\0%(timeout)s\0true" % locals()
    res = send_message("POS%d" % int(posid), TK_POS_UPDATEDIALOG, FM_PARAM, params, timeout=-1)
    if res.token == TK_SYS_ACK:
        return True
    return False  # error


def show_messagebox(posid, message, title="$INFORMATION", icon="info", buttons="$OK", timeout=60000, asynch=False, linefeed="\\", focus=True):
    infotext, mask, defvalue, minvalue, maxvalue, contents = ("", "", "", "", "", None)
    data = show_any_dialog(posid, "messagebox", message, title, infotext, buttons, icon, timeout, mask, defvalue, minvalue, maxvalue, contents, asynch, linefeed, focus)
    if data is None:
        return None  # Timeout
    return int(data)  # Index of the button clicked, or the dialog id for asynch dialogs


def update_messagebox(posid, dlgid, message, title="$INFORMATION", icon="info", buttons="$OK", timeout=60000, linefeed="\\", focus=True):
    infotext, mask, defvalue, minvalue, maxvalue, contents = ("", "", "", "", "", None)
    return update_any_dialog(posid, dlgid, "messagebox", message, title, infotext, buttons, icon, timeout, mask, defvalue, minvalue, maxvalue, contents, linefeed, focus)


def show_confirmation(posid, message="$ARE_YOU_SURE", title="$CONFIRMATION", icon="question", buttons="$YES|$NO", timeout=60000, asynch=False):
    index = show_messagebox(posid, message, title, icon, buttons, timeout, asynch)
    if asynch:
        return index  # the dialog id
    if index is None:
        return None
    return (index == 0)


def update_confirmation(posid, dlgid, message="$ARE_YOU_SURE", title="$CONFIRMATION", icon="question", buttons="$YES|$NO", timeout=60000):
    return update_messagebox(posid, dlgid, message, title, icon, buttons, timeout)


def show_custom_dialog(posid, custom_dlg_id, custom_dlg_timeout="0"):
    timeout = int(custom_dlg_timeout)
    if timeout == 0:
        timeout = 60000  # default timeout 1 minute
    else:
        timeout += 30000  # adds extra 30 seconds before msgbus timeout
    message, title, infotext, buttons, icon, mask, defvalue, minvalue, maxvalue, contents, asynch, linefeed, focus = ("", "", "", "", "", "", "", "", "", None, False, "\\", True)
    return show_any_dialog(posid, "custom", message, title, infotext, buttons, icon, timeout, mask, defvalue, minvalue, maxvalue, contents, asynch, linefeed, focus, custom_dlg_id=custom_dlg_id, custom_dlg_timeout=custom_dlg_timeout)


def show_listbox(posid, options, message="$SELECT_AN_OPTION", title="", defvalue="", buttons="$OK|$CANCEL", icon="", timeout=60000, asynch=False):

    mask, minvalue, maxvalue, contents = ("", "", "", None)
    # If "options" is a list, join it
    infotext = "|".join(options) if hasattr(options, '__iter__') else str(options)
    data = show_any_dialog(posid, "listbox", message, title, infotext, buttons, icon, timeout, mask, defvalue, minvalue, maxvalue, contents, asynch)
    if asynch:
        return int(data)  # Dialog id
    if data is None:
        return None  # Timeout
    split = data.split(",")
    if split[0] == "0":  # Index of the button pressed
        return int(split[1])  # Selected option index
    return None  # User canceled


def show_rupture(posid, asynch=False):

    data = show_any_dialog(posid, "rupture", "", "$RUPTURE", "", "$OK|$CANCEL", "", 60000, "", "", "", "", None, asynch)

    if asynch:
        return int(data)  # Dialog id
    if data is None:
        return None

    return data


def show_keyboard(posid, message, title="$INPUT_DATA", infotext="$PRESS_OK_TO_CONTINUE",
                  buttons="$OK|$CANCEL", icon="info", timeout=60000, mask="", is_password=False,
                  defvalue="", minvalue="", maxvalue="", numpad=False, nopad=False, noinput=False, asynch=False):
    """show_keyboard(posid, message, title="$INPUT_DATA", infotext="$PRESS_OK_TO_CONTINUE", buttons="$OK|$CANCEL", icon="info", timeout=60000, mask="", is_password=False, defvalue="", minvalue="", maxvalue="", numpad=False, asynch=False) -> str
    Show a keyboard input dialog
    @param posid: POS id
    @param message: Dialog message
    @param title: Dialog title
    @param infotext: Dialog informational text
    @param buttons: Dialog buttons (pipe-separated)
    @param icon: Dialog icon
    @param timeout: Dialog timeout in millis. Default: 1 minute (60000ms)
    @param mask: Optional validation/formatting mask to apply
    @param is_password: If True, this will be a password dialog
    @param defvalue: Initial value to display
    @param minvalue: Minimum value
    @param maxvalue: Maximum value
    @param numpad: If True, this will be a numpad dialog (numbers-only)
    @param nopad: If True, this will be a nopad dialog (no buttons)
    @param asynch: If True, this will be an asynchronous dialog (the response will be the dialog id)
    @return: The data inputed by the user OR None if the dialog timed-out/was cancelled OR a dialog id if "asynch" is True
    """

    dlgtype = "numpad" if numpad else "nopad" if nopad else "password" if is_password else "keyboard"
    if nopad and is_password:
        dlgtype = "nopad_password"
    if nopad and noinput:
        dlgtype = "nopad_noinput"
    if numpad and is_password:
        dlgtype = "numpad_password"
    contents = None
    data = show_any_dialog(posid, dlgtype, message, title, infotext, buttons, icon, timeout, mask, defvalue, minvalue, maxvalue, contents, asynch)
    if asynch:
        return int(data)  # Dialog id
    if data is None:
        return None  # Timeout
    # RZR - 2010/Nov/22 - do not use "data.split()" here, since the response message may contain a ',' character
    if ',' in data:
        idx = data.index(',')
        split = [data[:idx], data[idx + 1:]]
    else:
        split = [data, ""]
    if split[0] == "0":  # Index of the button pressed
        return split[1]  # Entered data
    return None  # User canceled


def show_print_preview(posid, text_data, title="$PRINT_PREVIEW", buttons="$PRINT|$CLOSE", timeout=180000):
    """show_print_preview(posid, text_data, title="$PRINT_PREVIEW", buttons="$PRINT|$CLOSE", timeout=180000) -> int
    Show the "print preview" dialog
    @param posid: POS id
    @param text_data: Text to preview
    @param title: Dialog title
    @param buttons: Dialog buttons (pipe-separated)
    @param timeout: Dialog timeout in millis. Default: 3 minutes (180000ms)
    @return: Index of the button that has been pressed, or None if the dialog timed-out
    """
    contents = saxutils.escape(text_data)
    infotext, icon = ("", "")
    data = show_any_dialog(posid, "printpreview", "", title, infotext, buttons, icon, timeout, "", "", "", "", contents, False)
    if not data:
        return None
    ret = data.split(",")[0]
    return int(ret)


show_ppview = show_print_preview  # ALIAS


def show_form(posid, fields, title="$INPUT_DATA", message="", buttons="$OK|$CANCEL", icon="info", timeout=60000, minvalue="", maxvalue="", asynch=False):
    """show_keyboard(posid, fields, title="$INPUT_DATA", message="", buttons="$OK|$CANCEL", icon="info", timeout=60000, minvalue="", maxvalue="", asynch=False) -> str
    Show a keyboard form dialog
    @param posid: POS id
    @param fields: List of tuples containing the form fields info e.g. (("Field 1", "Default"), ...)
                   For each field you must provide the label and default value
    @param title: Dialog title
    @param message: Dialog message
    @param buttons: Dialog buttons (pipe-separated)
    @param icon: Dialog icon
    @param timeout: Dialog timeout in millis. Default: 1 minute (60000ms)
    @param minvalue: Minimum value
    @param maxvalue: Maximum value
    @param asynch: If True, this will be an asynchronous dialog (the response will be the dialog id)
    @return: The data inputed by the user OR None if the dialog timed-out/was cancelled OR a dialog id if "asynch" is True
    """
    contents = None
    infotext, defvalue = ("", "")
    l = len(fields)
    for i in range(l):
        sep = "" if i == l - 1 else "&#001e;"
        f = fields[i]
        infotext += f[0] + sep
        defvalue += f[1] + sep
    data = show_any_dialog(posid, "form", message, title, infotext, buttons, icon, timeout, "", defvalue, minvalue, maxvalue, contents, asynch)
    if asynch:
        return int(data)  # Dialog id
    if data is None:
        return None  # Timeout
    # RZR - 2010/Nov/22 - do not use "data.split()" here, since the response message may contain a ',' character
    if ',' in data:
        idx = data.index(',')
        split = [data[:idx], data[idx + 1:]]
    else:
        split = [data, ""]
    if split[0] == "0":  # Index of the button pressed
        return split[1].split("\x1e")  # Entered data
    return None  # User canceled


def remove_xml_prolog(xml):
    """remove_xml_prolog(xml) -> str
    Removes the processing instructions from an XML (<?xml ... ?>)
    @param xml: XML to remove prolog
    @return: XML without prolog
    """
    idx1 = xml.find("<?xml")
    if idx1 != -1:
        idx2 = xml.find("?>", idx1)
        if idx2 != -1:
            return xml[idx2 + 2:].lstrip()
    return xml


def show_order_preview(posid, orders, title="$SELECT_ORDER", buttons="$OK|$CANCEL", defvalue="", onthefly=False, timeout=120000, show_recipe=True):
    """ show_order_preview(posid, orders, title="$SELECT_ORDER", buttons="$OK|$CANCEL", defvalue="", timeout=120000)
    Displays a "select order by preview" dialog.
    @param posid: POS id
    @param orders: A list of orders data to be displayed. Each element in the list must be a 3-elements tuple where:
                   orders[n][0] - The order identification key (this will be the value returned to identify the order)
                                  You may use simply the index of the order in the list for example, or any other convenient value.
                   orders[n][1] - The order description. This will be the description displayed to the user to select
                                  the order on the list. This field may also be an I18N key with optional parameters separated by pipe.
                   orders[n][2] - If the "onthefly" parameter is False, this must be the order XML (an order picture) - this may be the
                                  raw XML string, or an etree.Element instance.
                                  If the "onthefly" parameter is True, then this must be an URL to retrieve the order picture.
                                  The GUI is responsible to dinamically load the order pictures as necessary from this URL.
    @param title: Dialog title.
    @param buttons: List of buttons for the user to press.
    @param defvalue: Default value to select - must equal to the "key" of the order (the first element in the tuple).
    @param onthefly: If this is true, the caller must send an URL instead of an order picture XML. The GUI
                     will load the order picture on-the-fly from the given URLs, instead of receiving all of
                     them at once.
    @param timeout: Dialog timeout (in milliseconds)
    @return None if the dialog timed-out, or a 2-elements list ["button-index", "selected-key"] if the UI replied.
    """
    buf = StringIO()
    buf.write("""<Orders onTheFly="%s" showRecipe="%s">\n""" % (("true" if onthefly else "false"), ("true" if show_recipe else "false")))
    for key, descr, order in orders:
        if onthefly:
            order = saxutils.escape(order)
        else:
            order = etree.tostring(order) if etree.iselement(order) else remove_xml_prolog(order)
        buf.write("""<PreviewOrder key=%s descr=%s>\n%s\n</PreviewOrder>\n""" % (saxutils.quoteattr(str(key)), saxutils.quoteattr(str(descr)), order))
    buf.write("</Orders>")
    contents = buf.getvalue()
    del buf
    data = show_any_dialog(posid, "orderpreview", "", title, "", buttons, "", timeout, "", defvalue, "", "", contents, False)
    if data is not None:
        data = data.split(",")
    return data


def show_text_preview(posid, texts, title="$SELECT_AN_OPTION", buttons="$OK|$CANCEL", defvalue="", onthefly=False, timeout=120000):
    """ show_text_preview(posid, texts, title="$SELECT_AN_OPTION", buttons="$OK|$CANCEL", defvalue="", timeout=120000)
    Displays a "select text by preview" dialog.
    This is often used to display pre-formatted receipts, slips or reports for the user to select an option.
    @param posid: POS id
    @param texts: A list of text data to be displayed. Each element in the list must be a 3-elements tuple where:
                   texts[n][0] - The text identification key (this will be the value returned to identify the selection)
                                 You may use simply the index of the text in the list for example, or any other convenient value.
                   texts[n][1] - The text description. This will be the description displayed to the user to select
                                 the text on the list. This field may also be an I18N key with optional parameters separated by pipe.
                   texts[n][2] - If the "onthefly" parameter is False, this must be the text to be displayed in the preview area.
                                 If the "onthefly" parameter is True, then this must be an URL to retrieve the text.
                                 The GUI is responsible to dinamically load the texts as necessary from this URL.
    @param title: Dialog title.
    @param buttons: List of buttons for the user to press.
    @param defvalue: Default value to select - must equal to the "key" of the text (the first element in the tuple).
    @param onthefly: If this is true, the caller must send an URL instead of a text. The GUI
                     will load the text from the given URLs, instead of receiving all of
                     them at once.
    @param timeout: Dialog timeout (in milliseconds)
    @return None if the dialog timed-out, or a 2-elements list ["button-index", "selected-key"] if the UI replied.
    """
    buf = StringIO()
    buf.write("""<Texts onTheFly="%s">\n""" % ("true" if onthefly else "false"))
    for key, descr, text in texts:
        text = saxutils.escape(text)
        buf.write("""<PreviewText key=%s descr=%s>%s</PreviewText>\n""" % (saxutils.quoteattr(str(key)), saxutils.quoteattr(str(descr)), text))
    buf.write("</Texts>")
    contents = buf.getvalue()
    del buf
    data = show_any_dialog(posid, "textpreview", "", title, "", buttons, "", timeout, "", defvalue, "", "", contents, False)
    if data is not None:
        data = data.split(",")
    return data


def close_asynch_dialog(posid, dlgid):
    """close_asynch_dialog(posid, dlgid) -> bool
    Closes an asynchronous dialog
    @param posid: POS id
    @param dlgid: Dialog id
    @return: True if the dialog was closed
    """
    reqbuf = ("%s\0%s" % (posid, dlgid))
    try:
        send_message("POS%d" % int(posid), TK_POS_DIALOGRESP, FM_PARAM, reqbuf)
        return True
    except:
        sys_log_exception("Error closing asynchronous dialog")
        return False


def generate_report(name, *params):
    """generate_report(name, *params) -> str
    Generate a report
    @param name: Report name
    @param *params: Optional report parameters
    @return: The formatted report, or None if it fails to generate
    """
    msgparams = (name, ) + params
    msgparams = "\0".join(map(str, msgparams))
    msg = send_message("ReportsGenerator", TK_REPORT_GENERATE, FM_PARAM, msgparams, timeout=60000000)
    if msg.token == TK_SYS_ACK:
        return msg.data
    return None


def print_text(posid, model, text, preview=False, force_printer=None):
    """print_text(posid, model, text, preview=False, force_printer=None) -> bool
    Prints some text
    @param posid: POS id
    @param model: POS model
    @param text: Text to print
    @param preview: If True, the print-preview will be shown
    @param force_printer: Optional printer service to use instead of the default configured printer "used service"
    @return: True if the text was printed with success
    """
    model = model or get_model(posid)
    if preview and (show_print_preview(posid, text) in (1, None)):
        return False
    # Retrieve the printer service to use
    printer_service = force_printer or get_used_service(model, "printer")
    default_printer = printer_service
    if not printer_service:
        sys_log_warning("There are no printers configured for POS %s" % posid)
    while printer_service:
        # Print
        msg = None
        try:
            msg = send_message(printer_service, TK_PRN_PRINT, FM_STRING, text)
        except MBException:
            sys_log_exception("Error printing text")
        if not msg or msg.token == TK_SYS_NAK:
            # Could not print, so show the list of available printers to retry
            options = get_used_service(model, "printer", get_all=True)
            default_idx = options.index(default_printer) if (default_printer in options) else 0
            index = show_listbox(posid, options, message="$PRINTER_ERROR_SELECT_ANOTHER", defvalue=default_idx)
            if index is None:
                return False  # User canceled
            printername = options[index]
            # Change the default printer if we are not forcing one
            if not force_printer:
                msg = send_message("POS%d" % int(posid), TK_POS_SETDEFSERVICE, FM_PARAM, "%s\0printer\0%s" % (posid, printername))
                if msg.token == TK_SYS_NAK:
                    show_info_message("$OPERATION_FAILED")
                    return False
            printer_service = printername
            continue  # Try again!
        return True
    return False


def print_report(posid, model, preview, report_name, *report_params):
    """print_report(posid, model, preview, report_name, *report_params) -> bool
    Generates and prints a report
    @param posid: POS id
    @param model: POS model
    @param preview: If True, the print-preview will be displayed
    @param report_name: The report name
    @param *report_params: Optional report parameters
    @return: True if the report was printed with success
    """
    report = generate_report(report_name, *report_params)
    if report:
        return print_text(posid, model, report, preview)
    else:
        sys_log_info("Could not generate report: %s" % report_name)
    return False


def set_custom(posid, key, value, persist=False):
    """set_custom(posid, key, value, persist=False)
    Sets a custom model property.
    @param posid: POS id
    @param key: Custom model property
    @param value: Custom model property value
    @param persist: If True, the property will be persisted in the database
    """
    persist = "true" if persist else "false"
    res = send_message("POS%d" % int(posid), TK_POS_MODELSETCUSTOM, FM_PARAM, "%s\0%s\0%s\0%s" % (posid, key, value, persist))
    return res.token == TK_SYS_ACK


def get_custom(model, key, default=None):
    """get_custom(model, key, default=None) -> str
    Retrieves a custom model property.
    @param posid: POS id
    @param key: Custom model property
    @param default: Default value to return if the property is not set
    @return: The property value
    """
    for node in model.findall("Custom"):
        if node.get("name") == key:
            return node.get("value")
    return default


def clear_custom(posid, key, persist=False):
    """clear_custom(posid, key)
    Clears a custom model property.
    @param posid: POS id
    @param key: Custom model property to clear
    @param persist: If True, the property will be persisted in the database
    """
    res = send_message("POS%d" % int(posid), TK_POS_MODELSETCUSTOM, FM_PARAM, "%s\0%s\0%s\0%s" % (posid, key, "", "true" if persist else "false"))
    return res.token == TK_SYS_ACK


def translate_message(model, message_key, *params):
    """translate_message(model, message_key, *params) -> str
    Translates a message with the I18N database
    @param model: POS model
    @param message_key: The I18N message key
    @param *params: Optional I18N parameters
    @return: The translated message
    """
    lang_name = str(model.find("Language").get("name"))
    data = "%s\0%s\0%s" % (lang_name, message_key, '\0'.join(params))
    msg = send_message("I18N", TK_I18N_TRANSLATE, FM_PARAM, data)
    if msg.token == TK_SYS_ACK:
        return msg.data
    return message_key


def format_date(yyyymmdd=None, date=None, format=None):
    """format_date(yyyymmdd=None, date=None, format=None) -> str
    Formats a date to any format
    @param yyyymmdd: Input date in the "YYYYMMDD" format
    @param param: date object, if yyyymmdd was not passed
    @param format: the output format. If None, the DATE_FMT will be used
    @return: The formatted date
    @note:You can "configure" which date format to use by default changing the DATE_FMT variable
    """
    format = format or DATE_FMT
    return time.strftime(format, (date or time.strptime(yyyymmdd, "%Y%m%d")))


def format_amount(model, amount, addsymbol=True):
    """format_amount(model, amount, addsymbol=True) -> str
    Formats an amount using L10N rules
    @param model: POS model
    @param amount: the amount to format (will be converted to string, so any object is accepted)
    @param addsymbol: If True, the currency symbol will be added in the response
    @return: The formated amount string
    """
    lang_name = str(model.find("Language").get("name"))
    data = "%s\0%s\0%s" % (lang_name, amount, "true" if addsymbol else "false")
    msg = send_message("I18N", TK_L10N_TOCURRENCY, FM_PARAM, data)
    if msg.token == TK_SYS_ACK:
        return msg.data
    return amount


def get_last_order(model):
    """get_last_order(model) -> dict
    Retrieves information from the last order (if there is one).
    @param model: POS model
    @return: A dictionary containing order information, or None if there is no last order
    """
    orders = get_posot(model).listOrders(sessionid=get_operator_session(model), limit=2, decrescent=True, orderby='LastStateAt')
    if not orders:
        return None
    if len(orders) == 1 or (orders[0]["state"] in ("PAID", "VOIDED", "ABANDONED", "STORED")):
        return orders[0]
    return orders[1]


def get_line_product_name(model, line_number):
    """get_line_product_name(model, line_number) -> str
    Gets the product name from a line number in the current order
    @param model: POS model
    @param line_number: Line number
    @return: Product name
    """
    line_number = str(line_number).split("|")[0]
    for line in model.findall("CurrentOrder/Order/SaleLine"):
        if line.get("lineNumber") == line_number and int(line.get("level")) == 0:
            return line.get("productName")
    return "(unknown)"


def get_clearOptionsInfo(model, line_number):
    line_number = str(line_number).split("|")[0]
    ret = []
    level = 0
    for line in model.findall("CurrentOrder/Order/SaleLine"):
        if line.get("lineNumber") != line_number:
            continue
        if line.get("itemType") == "OPTION":
            level = int(line.get("level"))  # Record the option level
            continue
        if level and line.get("itemType") == "PRODUCT" and int(line.get("level")) == level + 1:
            # Found an option solution
            try:
                if int(line.get("qty")) > 0:
                    ret.append(line)
            except:
                # quantity can be a fraction
                if float(line.get("qty")) > 0:
                    ret.append(line)
        elif level:
            level = 0  # Finished this option
    return ret


def can_void_line(model, line_number):
    """can_void_line(model, line_number) -> bool
    Checks if a line can be voided (has quantity > 0) or not
    @param model: POS model
    @param line_number: Line number
    @return: True or False
    """
    line_numbers = line_number.split("|")
    for line in model.findall("CurrentOrder/Order/SaleLine"):
        if line.get("lineNumber") in line_numbers and int(line.get("level")) == 0:
            try:
                if int(line.get("qty")) > 0:
                    return True
            except:
                # quantity can be a fraction
                if float(line.get("qty")) > 0:
                    return True
    return False


def get_user_information(user_number='', key='user_id'):
    """ get_user_information(user_number="", key='userid') -> xml string
    Get the user informations and check if it's valid
    @param user_number - User number to be validated or blank to retrieve information from ALL users.
    @param key - Field that will be used to retrieve the user: user_id or badge_number
    @return - xml with the user(s) information (if userid is valid or blank).
              If the userId was passed but was invalid, then *None* is returned.
    """
    if key == 'user_id':
        msg = send_message("UserControl", TK_USERCTRL_GETINFO, FM_PARAM, (str(user_number) if user_number else ''))
    elif key == 'badge_number':
        msg = send_message("UserControl", TK_USERCTRL_GETINFO_BADGE, FM_PARAM, str(user_number))
    else:
        raise Exception('Invalid key for get_user_information:{}'.format(key))
    if msg.token == TK_SYS_ACK:
        if user_number:
            # If the userId parameter was passed, validate that this user exists
            xml_response = etree.XML(msg.data)
            if not xml_response.findall("user"):
                return None
    else:
        raise Exception("Could not retrieve info from the UserControl service")
    return msg.data


def authenticate_user(userid, password, min_level=None):
    """ check_user(userid, password, min_level=None) -> {"Level":Level, "UserName":UserName, "LongName":LongName}
    Authenticates the given user ID, checking if the password match and optionally checking a minimum required level.
    If the user authentication fails, an *AuthenticationFailed* exception will be raised, with one of
    the following I18N message keys:
      - INVALID_USER_OR_PASSWORD
      - ACCESS_DENIED
    @param userid - User ID number to be validated.
    @param password - User password.
    @param min_level - If not none, the user will only be authorized if its level is >= min_level.
    @return - A dictionary with the user info, if it has been authorized:
              {"Level":Level, "UserName":UserName, "LongName":LongName}
    @raise AuthenticationFailed when the user authentication fails
    """
    # Verify if the user password is correct
    msg = send_message("UserControl", TK_USERCTRL_AUTHENTICATE, FM_PARAM, "%s\0%s\0" % (userid, password))
    if msg.token == TK_SYS_NAK:
        raise AuthenticationFailed("INVALID_USER_OR_PASSWORD")
    # Retrieve the user info
    level, username, longusername = msg.data.split('\0')[:3]
    # Verify the minimum required level
    if (min_level is not None) and (int(level) < int(min_level)):
        raise AuthenticationFailed("ACCESS_DENIED")
    # Return the user info as a dictionary
    return {"Level": level, "UserName": username, "LongName": longusername}


def is_valid_date(date_string):
    """ is_valid_date(date_string) -> True or False
    Checks if a date is valid
    @param date_string - {str} date string (YYYYMMDD)
    @return True if this date is valid
    """
    try:
        date_string = str(date_string)
        if len(date_string) != 8:
            return False
        datetime.date(int(date_string[:4]), int(date_string[4:6]), int(date_string[6:8]))
        return True
    except:
        return False


def is_valid_datetime(datetime_string):
    """ is_valid_datetime(date_string) -> True or False
    Checks if a datetime is valid
    @param datetime_string - {str} datetime string ('%m/%d/%Y %H:%M')
    @return True if this datetime is valid
    """
    try:
        datetime.datetime.strptime(datetime_string, DATETIME_FMT)
    except ValueError:
        return False
    return True


def calculate_giftcards_amount(model):
    """calculate_giftcards_amount(model) -> float
    Calculates the amount of gift-card items in the current order.
    This is done by looking for a "FamilyGroup"="GiftCard" custom parameter.
    @return: {float} the gift-cards amount
    """
    posot = get_posot(model)
    # Find all level 0 lines
    lines = [line for line in get_current_order(model).findall("SaleLine") if str(line.get("level")) == "0"]
    # Find all level 0 product codes
    pcodes = set(line.get("partCode") for line in lines)
    # Retrieve all family groups
    xml = etree.XML(posot.productCustomParameters(pcodelist="|".join(pcodes), paramid="FamilyGroup"))
    # Find all sold product codes which represents a gift-card
    gc_codes = [product.get("productCode") for product in xml.findall("Product") if product.find("CustomParameter").get("value").lower() == "giftcard"]
    if not gc_codes:
        return 0  # No GC sales
    # Calculate the total amount of sold gift-cards
    amt_giftcard = sum([float(line.get("itemPrice")) for line in lines if line.get("partCode") in gc_codes])
    return amt_giftcard


def get_custom_params(posid, pcodelist, cacheable=True):
    """
    Retrieves the custom parameters for one or more products
    @param posid {int or str} - pos ID
    @param pcodelist {list or str} - list of product codes (or a single one)
    @param cacheable {bool} - Indicates if the result should be cached (default: True)
    @return {etree.XML} parsed custom parameters
    """
    if not hasattr(get_custom_params, 'cache'):
        get_custom_params.cache = {}
    cache = get_custom_params.cache if cacheable else {}
    if pcodelist not in cache:
        posot = OrderTaker(posid, mbcontext)
        cache[pcodelist] = etree.XML(posot.productCustomParameters(pcodelist=pcodelist))
    return cache[pcodelist]


def get_dimension(posid, pcodelist, cacheable=True):
    """
    Retrieves the dimension information for one or more products
    @param posid {int or str} - pos ID
    @param pcodelist {list or str} - list of product codes (or a single one)
    @param cacheable {bool} - Indicates if the result should be cached (default: True)
    @return {etree.XML} parsed list of product dimensions
    """
    if not hasattr(get_dimension, 'cache'):
        get_dimension.cache = {}
    cache = get_dimension.cache if cacheable else {}
    if pcodelist not in cache:
        posot = OrderTaker(posid, mbcontext)
        cache[pcodelist] = etree.XML(posot.productDimension(pcodelist=pcodelist))
    return cache[pcodelist]


def get_pricelist(model):
    """
    Retrieves the price list that should be used for the current time
    @param model {etree.XML} - POS model
    @return {str} price list ID
    """
    DEFAULT = get_pricelist.DEFAULT if hasattr(get_pricelist, 'DEFAULT') else "EI"
    if not hasattr(get_pricelist, 'rules'):
        # Parse the rules (only once)
        rules = []
        cfg = cfgtools.read_string(send_message("StoreWideConfig", TK_STORECFG_GETFULL).data)
        cfg = cfg.find_group("PublishedConfiguration.PriceList") or cfgtools.Group()
        default = cfg.find_value("Default") or DEFAULT
        rulescfg = cfg.group("Rules")
        if rulescfg:
            rulescfg = rulescfg.groups
        else:
            rulescfg = []

        def matcher_aftertime(rule_cond, rule_res):
            hhmm = datetime.datetime.strptime(rule_cond, "%H:%M").time()

            def matcher(now, model):
                return str(rule_res) if now.time() >= hhmm else None
            return matcher

        def matcher_beforetime(rule_cond, rule_res):
            hhmm = datetime.datetime.strptime(rule_cond, "%H:%M").time()

            def matcher(now, model):
                return str(rule_res) if now.time() < hhmm else None
            return matcher

        def matcher_timerange(rule_cond, rule_res):
            fromto = rule_cond.split("-")
            hhmmfrom = datetime.datetime.strptime(fromto[0], "%H:%M").time()
            hhmmto = datetime.datetime.strptime(fromto[1], "%H:%M").time()

            def matcher(now, model):
                return str(rule_res) if hhmmfrom <= now.time() < hhmmto else None
            return matcher
        for rule in rulescfg:
            try:
                rule_type, rule_cond, rule_res = map(rule.find_value, ("RuleType", "Rule", "PriceListId"))
                if not all((rule_type, rule_cond, rule_res)):
                    continue
                if rule_type == "AFTER_TIME":
                    rules.append(matcher_aftertime(rule_cond, rule_res))
                elif rule_type == "BEFORE_TIME":
                    rules.append(matcher_beforetime(rule_cond, rule_res))
                elif rule_type == "TIME_RANGE":
                    rules.append(matcher_timerange(rule_cond, rule_res))
            except:
                sys_log_exception("Error parsing Price List rule - ignored")
        # Default rule (applied after all others)
        rules.append(lambda now, model: default)
        get_pricelist.rules = rules
    # Determine the current price list
    rules = get_pricelist.rules
    price_list = None
    now = datetime.datetime.now()
    for rule in rules:
        price_list = rule(now, model)
        if price_list:
            return price_list
    return DEFAULT


def check_main_screen(posid, change_now=True):
    """
    Checks if the main screen should be changed for the current POD type and POS function
    @param posid {int or str} - pos ID
    @param change_now {bool} - Indicates if we should change to the (new) main screen now (default: True)
    """
    model = get_model(posid)
    podtype = get_podtype(model)
    posfunction = get_posfunction(model) if podtype == "DT" else ""
    # Check the main screen for this POD and POS Function
    keyname = str(("mainScreen_%s" % podtype) + ("_%s" % posfunction.replace('/', '') if posfunction else ""))
    mainscreen = str(get_cfg(posid).key_value(keyname, "0"))
    change_mainscreen(posid, mainscreen, persist=True)
    if change_now:
        change_screen(posid, "main")


def get_storewide_config(parameter, defval=None, array=False):
    """
    Retrieves a store-wide configuration parameter from the "StoreWideConfig" service
    @param parameter: Path to the published parameter (E.g.: "MySection.MySubSection.MyParameter")
    @param defval: Value to return if the parameter is not found (default=None)
    @param array: Indicates if the values should be returned as a list (default=False)
    @return: The parameter value, list of values or "defval"
    """
    msg = send_message("StoreWideConfig", token=TK_STORECFG_GET, format=FM_PARAM, data=str(parameter))
    if msg.token == TK_SYS_ACK:
        if array:
            return (msg.data.split('\0') if msg.size else defval)
        else:
            return (msg.data.split('\0')[0] or defval)
    return defval


def get_tender_types(cache={}):
    """get_tender_types(cache={}) -> dict
    Retrieve the configured tender types table.
    The key in the returned dictionary is the tender type id, and the value is
    the tender information in the following format:
    {"id": id, "descr": x, "currency": x, "idForChange": x, "keepExcess": 0, "skimLimit": x,
    "changeLimit": x, "openDrawer": 0, "electronicType": x, "electronicTypeId": 0}
    @param cache: Optional dictionary to keep cached information
    @return: The tender types
    """
    if 'tenders' not in cache:
        conn = persistence.Driver().open(mbcontext)
        tenders = {}

        def intnull(x):
            return int(x) if x else None
        # Execute the "getTenderTypes" procedure to retrieve tender types
        for row in conn.pselect("getTenderTypes"):
            id = int(row.get_entry("TenderId"))
            tenders[id] = {
                "id": id,
                "descr": row.get_entry("TenderDescr"),
                "currency": row.get_entry("TenderCurrency"),
                "idForChange": intnull(row.get_entry("TenderIdForChange")),
                "keepExcess": int(row.get_entry("KeepExcess")),
                "skimLimit": row.get_entry("SkimLimit"),
                "changeLimit": row.get_entry("ChangeLimit"),
                "openDrawer": int(row.get_entry("OpenDrawer")),
                "needAuth": int(row.get_entry("NeedAuth")),
                "electronicType": row.get_entry("ElectronicTypeDescr"),
                "electronicTypeId": int(row.get_entry("ElectronicTypeId")),
                "parentId": intnull(row.get_entry("ParentTenderId")),
            }
        cache['tenders'] = tenders
    return cache['tenders']


def get_tender_type(tender_id, cache={}):
    """get_tender_type(tender_id, cache={}) -> dict or None
    Retrieve information about a tender type.
    The returned information is in the following format:
    {"id": id, "descr": x, "currency": x, "idForChange": x, "keepExcess": 0, "skimLimit": x,
    "changeLimit": x, "openDrawer": 0, "electronicType": x, "electronicTypeId": 0}
    @param tender_id: Tender type ID
    @param cache: Optional dictionary to keep cached information
    @return: The tender type information, or None if the ID is invalid
    """
    tender_id = int(tender_id)
    tenders = get_tender_types(cache)
    return tenders.get(tender_id, None)


def on_before_total(posid, model=None, *args, **kwargs):
    """
    Function called before totalizing an order, to acti like an script event.
    Other scripts may wish to add a callback function in the [on_before_total.callbacks] list to be notified of a "total" operation.
    @param posid: POS id
    @param model: POS model
    """
    for callback in on_before_total.callbacks:
        if not callback(posid, model, *args, **kwargs):
            return False
    return True


on_before_total.callbacks = []


def assert_order_discounts(posid, model=None):
    """assert_order_discounts(posid, model=None)
    Asserts that an order contains no "order-total" discounts (discounts applied to the order total rather than to an item).
    If the order contains any discount of that type, this function displays a confirmation message indicating which discounts
    will be removed (cleared) from the order.
    If the user confirm the message, the indicated discounts are cleared.
    If the user does not confirm, the operation is aborted (by raising StopAction).
    """
    posot = get_posot(model or get_model(posid))
    order_discounts = {}
    for discount in etree.XML(posot.getOrderDiscounts(applied=True)).findall("OrderDiscount"):
        if discount.get("lineNumber") == "0" and float(discount.get("discountAmount")) > 0:
            discountId = str(discount.get("discountId"))
            discountDescription = discount.get("discountDescription").encode("UTF-8")
            order_discounts[discountId] = discountDescription
    if order_discounts:
        descrs = "\\".join("* %s" % s for s in order_discounts.values())
        message = "$CONFIRM_DISCOUNT_EXCLUSIONS|%s" % descrs
        if not show_confirmation(posid, message=message):
            raise StopAction()
        for discountid in order_discounts.keys():
            posot.clearDiscount(discountid)


#
# Generic data by order id functions
#


def encode_string(key, string):
    encoded_chars = []
    for i in xrange(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(string[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return base64.urlsafe_b64encode(encoded_string)


def decode_string(key, string):
    decoded_chars = []
    string = base64.urlsafe_b64decode(string)
    for i in xrange(len(string)):
        key_c = key[i % len(key)]
        encoded_c = chr(abs(ord(string[i]) - ord(key_c) % 256))
        decoded_chars.append(encoded_c)
    decoded_string = "".join(decoded_chars)
    return decoded_string


def _generic_data_db_path():
    datadir = os.environ.get("HVDATADIR", "../data")
    return os.path.join(datadir, "databases", "generic.db")


def clear_generic_data(posid, orderid, mbctxt=None):
    if mbctxt is None:
        mbctxt = mbcontext
    try:
        posot = OrderTaker(posid, mbctxt)
        posot.setOrderCustomProperty("Generic_Data", value="clear", orderid=str(orderid))
    except:
        sys_log_exception("Error clearing generic data for order=%r." % (orderid, ))


def set_generic_data(posid, orderid, data, mbctxt=None):
    if mbctxt is None:
        mbctxt = mbcontext
    encoded_data = encode_string(GENERIC_DATA_KEY, json.dumps(data))
    try:
        posot = OrderTaker(posid, mbctxt)
        posot.setOrderCustomProperty("Generic_Data", value=encoded_data, orderid=str(orderid))
    except:
        sys_log_exception("Error setting generic data for posid=%r order=%r." % (posid, orderid))
        return False
    return True


def get_generic_data(posid, orderid, mbctxt=None):
    if mbctxt is None:
        mbctxt = mbcontext
    try:
        posot = OrderTaker(posid, mbctxt)
        r = etree.XML(posot.getOrderCustomProperties("Generic_Data", orderid=str(orderid)))
        r = r.find("OrderProperty").get("value")
        if r:
            data = json.loads(decode_string(GENERIC_DATA_KEY, str(r)))
        else:
            data = None
    except:
        sys_log_exception("Error getting generic data for posid=%r order=%r." % (posid, orderid))
        return None
    return data


def _safe_sqlite_xml(s):
    """
    Return a string safe for SQLite (character ' escaped) and XML escaped.
    Also, ensure ASCII for use in persist component
    """
    return saxutils.escape(str(s).replace("'", "''"))


def storage_set(key, value, mbctx=None):
    if mbctx is None:
        mbctx = mbcontext
    # parameters are converted to ASCII
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <Request>
        <STMT>INSERT OR REPLACE INTO cache.GenericStorage (DataKey, DataValue) VALUES ('%s', '%s');</STMT>
        <INSTANCE>1</INSTANCE>
    </Request>
    """ % (_safe_sqlite_xml(key), _safe_sqlite_xml(value))
    return mbctx.MB_EasySendMessage("Persistence", TK_PERSIST_QUERYEXEC, FM_XML, xml, 30000000)


def storage_increment(key, incr_val=0, mbctx=None):
    if mbctx is None:
        mbctx = mbcontext

    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <Request>
        <STMT>INSERT OR REPLACE INTO cache.GenericStorage (DataKey, DataValue)
              VALUES ('{0}', COALESCE((SELECT DataValue FROM cache.GenericStorage
                WHERE DataKey='{0}'), 0) + {1});</STMT>
        <INSTANCE>1</INSTANCE>
    </Request>""".format(key, incr_val)
    return mbctx.MB_EasySendMessage("Persistence", TK_PERSIST_QUERYEXEC, FM_XML, xml, 30000000)


def storage_get(key, mbctx=None):
    if mbctx is None:
        mbctx = mbcontext
    # parameters are converted to ASCII
    xml = """<?xml version="1.0" encoding="UTF-8"?>
    <Request>
        <STMT>SELECT DataValue FROM cache.GenericStorage WHERE DataKey = '%s'</STMT>
        <INSTANCE>1</INSTANCE>
    </Request>
    """ % _safe_sqlite_xml(key)
    msg = mbctx.MB_EasySendMessage("Persistence", TK_PERSIST_QUERYEXEC, FM_XML, xml, 30000000)
    res = etree.XML(msg.data)
    cols = res.findall("R/C")
    text = None
    if len(cols) > 0:
        text = cols[0].text
    return text


def list_hv_nodes():
    msg = mbcontext.MB_EasySendMessage('Hypervisor', TK_HV_LISTHVS)
    return [h.attrib for h in etree.XML(msg.data).findall("hypervisor")] if msg and msg.token == TK_SYS_ACK else []


def ha_get_context(posid):
    nodes = [n.get("name", "") for n in list_hv_nodes()]
    pos_nodes = [n for n in nodes if "POS" in n.upper()]
    for pos_node in pos_nodes:
        if int(pos_node.upper().replace("POS", "")) == int(posid):
            msg = mbcontext.MB_EasySendMessage("HA_{0}".format(pos_node), TK_EVT_EVENT, data="\0".join([pos_node, "GET_CONTEXT", "HAMANAGER"]))
            if msg.token == TK_SYS_ACK and msg and msg.data:
                return json.loads(msg.data) if msg and msg.data else None
            break
    return None


def ha_switch_servers(posid):
    msg = None
    context = ha_get_context(posid)
    if context and context["slave"] and "secs_since_last_update" in context["slave"]:
        if context["slave"]["secs_since_last_update"] <= 5:
            msg = mbcontext.MB_EasyEvtSend("SWITCH_SERVERS_REQUEST", "HAMANAGER", json.dumps({"source": context["node_name"], "slave": context["slave"]}))
        else:
            sys_log_warning("Slave server is updated. Can't proceed with the server switch request.")
    if msg and msg.token == TK_SYS_ACK:
        return True
    return False


#
# System actions
#


@action
def doShowConfirmation(posid, message, title="$CONFIRMATION", icon="question", buttons="$YES|$NO", timeout="60000", asynch="false", *args):
    asynch = asynch.lower() == "true"
    res = show_confirmation(posid, message=message, title=title, icon=icon, buttons=buttons, timeout=int(timeout), asynch=asynch)
    if asynch:
        return str(res)
    else:
        return "true" if res else "false"


@action
def doCloseAsynchDialog(posid, dlgid, *args):
    if close_asynch_dialog(posid, dlgid):
        return "true"
    return "false"
