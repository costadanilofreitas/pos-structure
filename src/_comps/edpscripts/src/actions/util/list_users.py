# -*- coding: utf-8 -*-
from msgbus import TK_POS_LISTUSERS, FM_PARAM, TK_SYS_NAK
from mw_helper import show_filtered_list_box_dialog, show_message_dialog
from sysactions import send_message, get_model, get_user_information, show_messagebox, StopAction
from xml.etree import cElementTree as eTree

from .. import USECS_PER_SEC, logger


def list_opened_users(pos_id):
    msg = send_message("POS%d" % int(pos_id), TK_POS_LISTUSERS, FM_PARAM, "%s" % pos_id, timeout=600 * USECS_PER_SEC)
    if msg.token == TK_SYS_NAK:
        logger.error("Logoff POS %d - Error listing logged operators" % int(pos_id))
        raise Exception("Error listing logged operators")

    model = get_model(pos_id)
    working_mode = model.find("WorkingMode").get("usrCtrlType")

    xml = eTree.XML(msg.data)
    opened_users = [tag for tag in xml.findall("User") if not tag.get("closeTime")]
    working_users = [tag for tag in opened_users if tag.get("userControlType") == working_mode]

    if working_mode == 'QSR':
        working_users = [tag for tag in working_users if tag.get("posId") == pos_id]

    return working_users


def list_all_opened_users(pos_id):
    msg = send_message("POS%d" % int(pos_id), TK_POS_LISTUSERS, FM_PARAM, "%s" % pos_id, timeout=600 * USECS_PER_SEC)

    if msg.token == TK_SYS_NAK:
        logger.error("Logoff POS %d - Error listing logged operators" % int(pos_id))
        raise Exception("Error listing logged operators")

    xml = eTree.XML(msg.data)
    opened_users = [tag for tag in xml.findall("User") if not tag.get("closeTime")]
    working_users = [tag for tag in opened_users]

    return working_users


def check_valid_user(pos_id, user_id):
    user_xml = get_user_information(user_id)
    if user_xml is None:
        show_message_dialog(pos_id, "$INFORMATION", "$INVALID_USER_OR_PASSWORD")
        return False

    user_list = eTree.XML(user_xml).findall("user")
    user_filter = filter(lambda x: x.get("UserId") == str(user_id), user_list)
    if user_filter in [None, [], ""]:
        show_message_dialog(pos_id, "$INFORMATION", "$INVALID_USER_OR_PASSWORD")
        return False

    return True


def get_selected_opened_user(pos_id):
    opened_users = list_opened_users(pos_id)
    if not opened_users:
        show_message_dialog(pos_id, "$INFORMATION", "$THERE_ARE_NO_OPENED_USERS")
        return None, None

    index = 0
    if len(opened_users) > 1:
        opened_users.sort(key=lambda x: x.get("id"))

        parsed_users_options = []
        for user in opened_users:
            parsed_users_options.append("{} - {}".format(user.get('id'), user.get('name')))

        index = show_filtered_list_box_dialog(pos_id, "|".join(parsed_users_options), "$LOGOUT", "", "NOFILTER")
        if index is None:
            return None, None

    model = get_model(pos_id)
    operator = [op for op in model.findall("Operators/Operator") if op.get("id") == opened_users[index].get('id')]
    return opened_users[index], operator[0]


def get_opened_users_from_pos(pos_id):
    opened_users = list_opened_users(pos_id)

    for opened_user in opened_users:
        if opened_user.get("posId") != pos_id:
            opened_users.remove(opened_user)

    if not opened_users:
        show_message_dialog(pos_id, "$INFORMATION", "$THERE_ARE_NO_OPENED_USERS")
        return None, None

    index = 0
    if len(opened_users) > 1:
        opened_users.sort(key=lambda x: x.get("id"))

        parsed_users_options = []
        for user in opened_users:
            parsed_users_options.append("{} - {}".format(user.get('id'), user.get('name')))

        index = show_filtered_list_box_dialog(pos_id, "|".join(parsed_users_options), "$LOGOUT", "", "NOFILTER")
        if index is None:
            return None, None

    model = get_model(pos_id)
    operator = [op for op in model.findall("Operators/Operator") if op.get("id") == opened_users[index].get('id')]
    return opened_users[index], operator[0]


def is_user_already_logged(pos_id, user_id, block_by_working_mode=False):
    msg = send_message("POS%d" % int(pos_id), TK_POS_LISTUSERS, FM_PARAM, "%s" % pos_id, timeout=600 * USECS_PER_SEC)
    if msg.token == TK_SYS_NAK:
        logger.error("Logoff POS %d - Erro obtendo lista de operadores logados." % int(pos_id))
        return True

    xml = eTree.XML(msg.data)
    opened_users = [tag for tag in xml.findall("User") if not tag.get("closeTime")]
    working_users = [tag for tag in opened_users if tag.get("id") == user_id]

    if len(working_users) > 0:
        model = get_model(pos_id)

        if block_by_working_mode:
            user_info = [x for x in opened_users if x.get("id") == user_id]
            if user_info:
                pos_working_mode = model.find("WorkingMode").get("usrCtrlType")
                operator_working_mode = "QSR" if "pos" in user_info[0].get("sessionId") else "TS"
                if pos_working_mode != operator_working_mode:
                    show_messagebox(pos_id, "$USER_LOGGED_IN_ANOTHER_POS_TYPE", "$INFORMATION")
                    raise StopAction()

        operator = [op for op in model.findall("Operators/Operator") if op.get("id") == user_id]

        if len(operator) > 0 and operator[0].get('state') != 'LOGGEDIN':
            return False

        show_message_dialog(pos_id, "$INFORMATION", "$OPERATOR_ALREADY_LOGGED")
        return True

    return False

