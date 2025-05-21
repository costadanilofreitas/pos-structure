# -*- coding: utf-8 -*-
import datetime

from xml.etree import cElementTree as eTree

import msgbus
import sysactions
import persistence
from actions.models.mw_sys_errors import MwSysErrors

from .. import get_pos_service, mb_context, logger

from actions.util import get_operator_info


def login_user(pos_id, user_id):
    try:
        long_name, level, user_id = get_user_info(user_id)

        msg = sysactions.send_message(
            get_pos_service(pos_id),
            msgbus.TK_POS_USERLOGIN,
            msgbus.FM_PARAM, "{}\0{}\0{}".format(pos_id, user_id, long_name),
            timeout=60 * 1000000
        )
        if msg.token != msgbus.TK_SYS_ACK:
            model = sysactions.get_model(pos_id)
            message = sysactions.translate_message(model, "ERROR") + ": "
            message += sysactions.translate_message(model, MwSysErrors.get_name(msg.data.replace("\0", "")))
            sysactions.show_messagebox(pos_id, message, "$INFORMATION")
            logger.error("Invalid response from PosCtrl while login user: {} - {}".format(msg.token, msg.data))
            return False
    except (Exception, BaseException):
        logger.error("Exception while login user")
        sysactions.show_messagebox(pos_id, "$CANNOT_LOGIN_OPERATOR")
        return False
    return True


def open_user(pos_id, user_id):
    msg = None
    try:
        long_name, level, user_id = get_user_info(user_id)

        msg = sysactions.send_message(
            get_pos_service(pos_id),
            msgbus.TK_POS_USEROPEN,
            msgbus.FM_PARAM,
            "%s\0%s\0%s\0%s\0%s" % (pos_id, user_id, 0.0, long_name, level),
            timeout=60 * 1000000
        )
        if msg.token != msgbus.TK_SYS_ACK:
            raise Exception()

    except (Exception, BaseException):
        logger.exception("Error opening user {} on POS {}".format(user_id, pos_id))
        message = "$CANNOT_OPEN_OPERATOR"
        if msg is not None and \
                msg.data and \
                len(msg.data.split("\0")) > 1 and \
                msg.data.split("\0")[0] in MwSysErrors.list_values():
            model = sysactions.get_model(pos_id)
            message = sysactions.translate_message(model, MwSysErrors.get_name(msg.data.split("\0")[0]))
        sysactions.show_messagebox(pos_id, message)
        return False
    return True


def close_user(pos_id, user_id):
    try:
        msg = sysactions.send_message(
            get_pos_service(pos_id),
            msgbus.TK_POS_USERLOGOUT,
            msgbus.FM_PARAM,
            "%s\0%s" % (pos_id, user_id),
            timeout=60 * 1000000
        )
        if msg.token != msgbus.TK_SYS_ACK:
            if msg.data.startswith("5007"):
                return True
            logger.exception("Error closing user: Token: {} / Data: {}".format(msg.token, msg.data))
            sysactions.show_messagebox(pos_id, "$CANNOT_CLOSE_OPERATOR")
            return False
    except (Exception, BaseException):
        logger.exception("Error closing user {} on POS {}".format(user_id, pos_id))
        sysactions.show_messagebox(pos_id, "$CANNOT_CLOSE_OPERATOR")
        return False

    return True


def check_current_day(pos_id):
    model = sysactions.get_model(pos_id)
    if sysactions.is_day_blocked(model):
        sysactions.show_messagebox(pos_id, "$POS_IS_BLOCKED_BY_TIME", "$INFORMATION")
        return False

    if not sysactions.is_day_opened(model):
        sysactions.show_messagebox(pos_id, "$NEED_TO_OPEN_BDAY_FIRST", "$INFORMATION")
        return False

    return True


def get_user_info(user_id):
    msg = sysactions.send_message("UserControl", msgbus.TK_USERCTRL_GETINFO, msgbus.FM_PARAM, user_id)
    if msg.token != msgbus.TK_SYS_ACK:
        raise Exception("Error getting user information {}-{}".format(msg.token, msg.data))

    user_info = eTree.XML(msg.data)
    long_name = user_info.find("user").get("LongName")
    level = user_info.find("user").get("Level")
    user_id = user_info.find("user").get("UserId")

    return long_name, level, user_id


def print_open_day_report(model, pos_id, initial_float, autorized_by=""):
    operator = sysactions.get_current_operator(sysactions.get_model(pos_id))
    operator_name = (operator.get("name")).encode('utf-8')
    operator_id = operator.get("id")
    period = sysactions.get_business_period(model)
    if autorized_by == "":
        autorized_by = sysactions.get_custom(model, 'Last Manager ID', operator_id)
        
    sysactions.print_report(pos_id,
                            model,
                            True,
                            "login_operator_report",
                            pos_id,
                            operator_id,
                            operator_name,
                            initial_float,
                            period,
                            autorized_by)


def get_pod_type_and_pos_function(pos_id):
    pod_type = sysactions.get_cfg(pos_id).key_value("pod") or 'FL'
    pos_function_config = sysactions.get_cfg(pos_id).key_value("posFunction") or 'FL'
    pos_function_list = pos_function_config.split("|")
    pos_function = pos_function_list[0]
    if len(pos_function_list) > 1:
        pos_function_index = sysactions.show_listbox(pos_id, pos_function_list, message="$SELECT_A_POS_FUNCTION")

        if pos_function_index is None:
            return None, None

        pos_function = pos_function_list[pos_function_index]

    return pod_type, pos_function


def change_pod_type_and_pos_function(pos_id, pod_type, pos_function):
    if pos_function == "DS":
        sysactions.check_main_screen(pos_id)
    sysactions.send_message(
        get_pos_service(pos_id),
        msgbus.TK_POS_SETPOD,
        msgbus.FM_PARAM, "{}\0{}\0".format(pos_id, pod_type),
        timeout=60 * 1000000)
    sysactions.send_message(
        get_pos_service(pos_id),
        msgbus.TK_POS_SETFUNCTION,
        msgbus.FM_PARAM, "{}\0{}\0".format(pos_id, pos_function),
        timeout=60 * 1000000)


def get_initial_float(pos_id, pod_type, pos_function):
    if pod_type != "OT" and pos_function != "OT":
        list_min_values_drawer = sysactions.get_storewide_config("Store.MinValuesDrawer", defval=None)
        if list_min_values_drawer:
            list_limits = [("R$%.2f" % int(x)).replace(".", ",") for x in list_min_values_drawer.split(";")]
            if len(list_limits) > 1:
                index = sysactions.show_listbox(pos_id, list_limits, message="$ENTER_THE_INITIAL_FLOAT_AMOUNT",
                                                title="$OPERATOR_LOGIN", buttons="$OK|$CANCEL", icon="info",
                                                timeout=720000)
            elif len(list_limits) == 1:
                index = 0

            if index is None:
                raise sysactions.StopAction()

            initial_float = list_min_values_drawer.split(";")[index]
        else:
            initial_float = sysactions.show_keyboard(pos_id, message="$ENTER_THE_INITIAL_FLOAT_AMOUNT", title="$OPERATOR_OPENING",
                                                     mask="CURRENCY", numpad=True, timeout=720000)
            if initial_float is None:
                raise sysactions.StopAction()

        initial_float = round(float(initial_float or 0.0), 2)
        return float(initial_float)
    else:
        return 0.0


def save_initial_float(initial_float, pos_id, user_id):
    try:
        model = sysactions.get_model(pos_id)
        _, operator_id, session = get_operator_info(model, user_id)
        sql = "insert into Transfer (Period, PosId, SessionId, Type, Description, Amount, TenderId) " \
              "values ({}, {}, '{}', 1, 'INITIAL_AMOUNT', {}, 0);"\
            .format(datetime.datetime.now().strftime('%Y%m%d'), pos_id, session, initial_float)
        persistence.Driver().open(mb_context, pos_id).query(sql)
    except:
        pass


def user_inserted_initial_amount(pos_id, session):
    try:
        sql = "select count(*) from Transfer " \
              "where SessionId = '{}' and Description = 'INITIAL_AMOUNT'".\
            format(session)
        conn = persistence.Driver().open(mb_context, pos_id)
        row = conn.select(sql).get_row(0)
        return int(row.get_entry(0)) > 0
    except Exception as _:
        return False
