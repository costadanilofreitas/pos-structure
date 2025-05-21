# -*- coding: utf-8 -*-
import datetime
import json
from xml.etree import cElementTree as eTree

import actions
import bustoken
import msgbus
import sysactions
from systools import sys_log_info, sys_log_exception

from actions.goals import update_daily_goals
from actions.util import get_authorization, get_operator_info, get_user_level
from utils import open_user, login_user, print_open_day_report, get_pod_type_and_pos_function, \
                  change_pod_type_and_pos_function, close_user, get_initial_float, save_initial_float, \
                  user_inserted_initial_amount

from .. import mb_context, logger
from ..drawer.do_open_drawer import doOpenDrawer
from ..fiscal.get_nf_type import get_nf_type
from ..models import UserLevels
from actions.pos import pos_must_be_blocked

SIGNED_IN_USER = "SIGNED_IN_USER"
USECS_PER_SEC = 1000000


@sysactions.action
def loginuser(pos_id, user_id=None, password=None):
    if pos_must_be_blocked(pos_id):
        return False

    model = sysactions.get_model(pos_id)
    if sysactions.has_operator_opened(model) and not is_multi_operator_allowed(pos_id):
        sysactions.show_messagebox(pos_id, "$NEED_TO_LOGOFF_FIRST", "$INFORMATION")
        return False

    if actions.util.is_user_already_logged(pos_id, user_id, block_by_working_mode=True):
        return False

    try:
        user_info = get_user_info(pos_id, user_id, password, model)
    except sysactions.AuthenticationFailed as _:
        sysactions.show_messagebox(pos_id, "$INVALID_USERNAME_OR_PASSWORD", "$INFORMATION")
        return False

    if get_authorization_if_necessary(model, pos_id, user_info) is False:
        return False

    model = sysactions.get_model(pos_id)
    last_manager_id = 'Last Manager ID'
    last_manager_id = sysactions.get_custom(model, last_manager_id) or ""
    last_authorization_level = sysactions.get_custom(model, last_manager_id) or ""

    pod_type, pos_function = get_pod_type_and_pos_function(pos_id)
    if pod_type is None or pos_function is None:
        return False

    initial_float = 0
    _, _, session = get_operator_info(model, user_id)
    if not user_inserted_initial_amount(pos_id, session):
        initial_float = get_initial_float(pos_id, pod_type, pos_function)

    if open_user(pos_id, user_id) is False:
        return False

    if login_user(pos_id, user_id) is False:
        close_user(pos_id, user_id)
        return False

    change_pod_type_and_pos_function(pos_id, pod_type, pos_function)
    save_initial_float(initial_float, pos_id, user_id)
    update_daily_goals(pos_id)
    check_z_reduction(pod_type, pos_function, pos_id)

    if int(initial_float) > 0:
        doOpenDrawer(pos_id)

    sysactions.set_custom(pos_id, last_manager_id, last_manager_id)
    sysactions.set_custom(pos_id, 'Authorization Level', last_authorization_level)
    model = sysactions.get_model(pos_id)
    print_open_day_report(model, pos_id, initial_float, last_manager_id)

    sysactions.set_custom(pos_id, "VOIDAUTH_SESSION_DISABLED", "false", persist=True)
    save_signed_in_user(pos_id, user_id, user_info)
    return True


def must_change_business_period(model):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    return model.find("PosState").get("period") != current_date or model.find("PosState").get("state") != "OPENED"


def must_close_business_period(model):
    return model.find("PosState").get("state") == "OPENED" or model.find("PosState").get("state") == "BLOCKED"


def open_business_period(pos_id):
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    business_begin_msg = mb_context.MB_EasySendMessage("POS{}".format(pos_id),
                                                       msgbus.TK_POS_BUSINESSBEGIN,
                                                       msgbus.FM_PARAM,
                                                       "{}\0{}".format(pos_id, current_date),
                                                       timeout=90000000)
    if business_begin_msg.token != msgbus.TK_SYS_ACK:
        if business_begin_msg.data:
            raise Exception("Error opening day: {}".format(business_begin_msg.data))
        raise Exception("Error opening day")


def get_pos_service(pos_id):
    return "POS%d" % int(pos_id)


def get_authorization_if_necessary(model, pos_id, user_info):
    if int(user_info["Level"] or 0) < UserLevels.MANAGER.value:
        if not get_authorization(pos_id, min_level=UserLevels.MANAGER.value, model=model)[0]:
            return False
    else:
        sysactions.set_custom(pos_id, 'Last Manager ID', user_info["UserName"])
        sysactions.set_custom(pos_id, 'Authorization Level', get_user_level(user_info["UserName"]))

    return True


def is_multi_operator_allowed(pos_id):
    return sysactions.get_cfg(pos_id).key_value("multipleOperators", "false").lower() == "true"


def get_user_info(pos_id, user_id, password, model):
    user_got_from_finger_print = False
    if user_id is None:
        user_id = get_username_from_finger_print_reader(pos_id)
        if user_id is not None:
            user_got_from_finger_print = True

    if user_id is None:
        user_id = get_username_from_ui(pos_id, model)

    if not user_got_from_finger_print:
        if password is None:
            password = get_password_from_ui(pos_id, user_id, model)

        return sysactions.authenticate_user(user_id, password)
    else:
        user_xml_str = get_user_xml(pos_id, user_id)
        return build_user_info_from_user_xml(user_xml_str)


def build_user_info_from_user_xml(user_xml_str):
    user_xml = eTree.XML(user_xml_str)
    user_element = user_xml.find("user")
    return {
        'Level': user_element.attrib["Level"],
        'UserName': user_element.attrib["UserName"],
        'LongName': user_element.attrib["LongName"]
    }


def get_user_xml(pos_id, user_id):
    error_text = "$ERROR"
    try:
        user_xml_str = sysactions.get_user_information(user_id)
    except Exception as ex:
        sysactions.show_messagebox(pos_id, "$ASSOCIATED_FINGERPRINT_ERROR", error_text)
        sys_log_exception("Erro get_user_information - %s" % str(ex))
        raise sysactions.StopAction()
    # Se identificamos o usuario pela digital, pegamos a informacao dele e constuimos o objeto igual a autenticacao por usuario e senha faz
    if user_xml_str is None:
        sysactions.show_messagebox(pos_id, "$ASSOCIATED_FINGERPRINT_ERROR", error_text)
        raise sysactions.StopAction()
    return user_xml_str


def get_username_from_finger_print_reader(pos_id):
    try:
        if is_finger_print_device_available(pos_id):
            finger_print_data = get_finger_print_data(pos_id)
            if was_finger_print_successfully_acquired(finger_print_data) or not was_user_acquired(finger_print_data):
                sysactions.show_messagebox(pos_id, "$ERROR_READING_FINGERPRINT", "$ERROR")
                raise sysactions.StopAction()
            else:
                return finger_print_data.user_id

    except msgbus.MBException as ex:
        if ex.errorcode == 2:  # NOT_FOUND,FingerPrint not Available
            sys_log_info("Servico de FingerPrint Não Disponível")
        else:
            sysactions.sys_log_warning("Erro get_user_information - %s" % str(ex))
    return None


def is_finger_print_device_available(pos_id):
    ret = mb_context.MB_EasySendMessage("FingerPrintReader{0}".format(pos_id), bustoken.TK_FPR_OK)
    return ret.token == msgbus.TK_SYS_ACK


def get_finger_print_data(pos_id):
    return mb_context.MB_EasySendMessage(
        "FingerPrintReader{0}".format(pos_id),
        bustoken.TK_FPR_IDENTIFY_USER,
        format=msgbus.FM_PARAM,
        data=pos_id)


def was_finger_print_successfully_acquired(finger_print_data):
    return finger_print_data.token != msgbus.TK_SYS_ACK


def was_user_acquired(finger_print_data):
    return finger_print_data.data != ""


def get_username_from_ui(pos_id, model):
    level_name = sysactions.translate_message(model, UserLevels.OPERATOR.name)
    display_title = "$USER_AUTHENTICATION_WITH_PARAMETER|{}".format(level_name)
    username = sysactions.show_keyboard(pos_id,
                                        "$ENTER_USER_ID",
                                        title=display_title,
                                        mask="INTEGER",
                                        numpad=True)
    if username in (None, ""):
        raise sysactions.StopAction()
    return int(username, 10)


def get_password_from_ui(pos_id, username, model):
    level_name = sysactions.translate_message(model, UserLevels.OPERATOR.name)
    display_title = "$USER_AUTHENTICATION_WITH_PARAMETER|{}".format(level_name)
    password = sysactions.show_keyboard(pos_id,
                                        message="$ENTER_PASSWORD|{}".format(username),
                                        title=display_title,
                                        is_password=True,
                                        numpad=True)
    if password is None:
        raise sysactions.StopAction()

    return password


def check_z_reduction(pod_type, pos_function, pos_id):
    try:
        if get_nf_type() == "PAF" and not (pod_type == "OT" or pos_function == "OT"):
            mb_context.MB_EasyEvtSend("pafVerifyLastZReduction", xml='', type="", synchronous=True, sourceid=int(pos_id))
    except:
        logger.exception("posid: {}, Error on [pafVerifyLastZReduction]".format(pos_id))


def save_signed_in_user(pos_id, user_id, user):
    user["Id"] = str(user_id)
    sysactions.set_custom(pos_id, SIGNED_IN_USER, json.dumps(user), True)
