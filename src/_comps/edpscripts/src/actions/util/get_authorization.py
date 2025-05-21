# -*- coding: utf-8 -*-

from xml.etree import cElementTree as eTree

import bustoken
import sysactions
from msgbus import TK_SYS_ACK, FM_PARAM
from mw_helper import show_message_dialog, show_numpad_dialog

from .get_operator_level import get_user_level
from ..models import UserLevels


def get_authorization(pos_id,
                      min_level=None,
                      model=None,
                      timeout=60000,
                      can_bypass_reader=False,
                      insert_auth=False,
                      order_id=None,
                      display_title="$USER_AUTHENTICATION_WITH_PARAMETER",
                      user_id=None):

    # Fingerprint
    try:
        ret = sysactions.mbcontext.MB_EasySendMessage("FingerPrintReader{0}".format(pos_id), bustoken.TK_FPR_OK)
        if ret.token == TK_SYS_ACK:
            ret = sysactions.mbcontext.MB_EasySendMessage(
                "FingerPrintReader{0}".format(pos_id),
                bustoken.TK_FPR_AUTHORIZE_USER,
                format=FM_PARAM,
                data=pos_id)

            if ret.token == bustoken.TK_FPR_TIMEOUT and can_bypass_reader and not user_id:
                return get_authorization_original(pos_id, UserLevels.MANAGER.value, model, timeout, display_title)
            if ret.token != TK_SYS_ACK:
                sysactions.show_messagebox(pos_id, "$ERROR_READING_FINGERPRINT", "$ERROR")
            elif ret.data == "":
                sysactions.show_messagebox(pos_id, "$NOT_VERIFIED_USER_FINGERPRINT", "$ERROR")
            else:
                user_xml_str = None
                user_id = user_id or ret.data
                try:
                    user_xml_str = sysactions.get_user_information(user_id)
                except Exception as _:
                    sysactions.show_messagebox(pos_id, "$ASSOCIATED_FINGERPRINT_ERROR", "$ERROR")

                if user_xml_str is None:
                    sysactions.show_messagebox(pos_id, "$ASSOCIATED_FINGERPRINT_ERROR", "$ERROR")

                user_xml = eTree.XML(user_xml_str)
                user_element = user_xml.find("user")
                user_level = int(user_element.attrib["Level"])
                if user_level < min_level:
                    sysactions.show_messagebox(pos_id, "$ACCESS_DENIED", "$INFORMATION")
    except Exception as _:
        pass

    # Se chegamos aqui, nao temos leitor de impressao digital ativo, fallback para a forma tradicional
    response = get_authorization_original(pos_id, min_level, model, timeout, display_title, user_id)
    if response[0] and insert_auth:
        if not model:
            model = sysactions.get_model(pos_id)
        pos_ot = sysactions.get_posot(model)
        user_id = sysactions.get_custom(model, 'Last Manager ID')
        if not order_id:
            order = model.find("CurrentOrder/Order")
            order_id = order.get("orderId")
        pos_ot.setOrderCustomProperty("AUTHENTICATION_USER", user_id, order_id)

    return response


def get_authorization_original(pos_id, min_level=None, model=None, timeout=60000, display_title="", user_id=None):
    auth_type = sysactions.get_cfg(pos_id).key_value("authorizationType", "card").lower()

    if auth_type == "card":
        model = model or sysactions.get_model(pos_id)
        msr_name = sysactions.get_used_service(model, "msr")
        if not msr_name:
            show_message_dialog(pos_id, message="$CARDREADER_NOT_CONFIGURED")
            return False, None

        dlgid = sysactions.show_any_dialog(pos_id, "messageDialog", "$SWIPE_CARD_TO_AUTHORIZE",
                                           "$MAGNETIC_STRIPE_READER", "", "$CANCEL", "swipecard", timeout, "", "", "",
                                           "", None, True)

        try:
            # Read tracks from the card reader
            tracks = sysactions.read_msr(msr_name, timeout, dlgid)
        finally:
            sysactions.close_asynch_dialog(pos_id, dlgid)

        if tracks:
            # TODO: parse tracks and validate level if necessary
            return True, None

        return False, None

    elif auth_type == "login":
        if display_title == "$USER_AUTHENTICATION_WITH_PARAMETER":
            model = model or sysactions.get_model(pos_id)
            user_level_name = UserLevels.get_name(min_level)
            if user_level_name is None:
                user_levels = UserLevels.list_values()
                for level in user_levels:
                    if min_level <= level:
                        user_level_name = UserLevels.get_name(level)
                        break

            display_title = "$USER_AUTHENTICATION"
            if user_level_name is not None:
                level_name = sysactions.translate_message(model, user_level_name)
                display_title = "$USER_AUTHENTICATION_WITH_PARAMETER|{}".format(level_name)

        if not user_id:
            user_id = show_numpad_dialog(pos_id, display_title, "$ENTER_USER_ID")
            if user_id is None:
                return False, None
            if user_id == '':
                show_message_dialog(pos_id, message="$INVALID_USER")
                return False, None

        password = show_numpad_dialog(pos_id, display_title, "$ENTER_PASSWORD|{}".format(user_id), "password")
        if password is None:
            return False, None

        try:
            sysactions.authenticate_user(user_id, password, min_level=min_level)
            sysactions.set_custom(pos_id, 'Last Manager ID', user_id)
            sysactions.set_custom(pos_id, 'Authorization Level', get_user_level(user_id))
            sysactions.sys_log_info("Authentication succeeded for POS id: {}, user id: {}".format(pos_id, user_id))
            user_data = (str(user_id), str(password))
            return True, user_data
        except sysactions.AuthenticationFailed:
            show_message_dialog(pos_id, message="$INVALID_USERNAME_OR_PASSWORD")

        return False, None

    return False, None
