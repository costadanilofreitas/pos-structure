# -*- coding: utf-8 -*-

from datetime import datetime

import msgbus
import sysactions
from actions.kiosk import do_void_kiosk_order
from actions.login.utils import login_user, open_user, close_user
from systools import sys_log_exception, sys_log_error


@sysactions.action
def do_start_kiosk_order(pos_id, sale_type):
    try:
        model = sysactions.get_model(pos_id)

        if sysactions.has_current_order(model):
            do_void_kiosk_order(pos_id)

        user_id = authenticate_kiosk_operator()

        check_kiosk_pos_state(pos_id, user_id)
        check_kiosk_operator_state(pos_id, user_id)
        create_kiosk_order(pos_id, sale_type)

        return True
    except Exception as _:
        sys_log_exception("Error starting kiosk order")


def create_kiosk_order(pos_id, sale_type):
    model = sysactions.get_model(pos_id)
    pos_ot = sysactions.get_posot(model)
    price_list = sysactions.get_pricelist(model)
    pos_ot.createOrder(pos_id, price_list, saletype=sale_type)


def check_kiosk_operator_state(pos_id, user_id):
    model = sysactions.get_model(pos_id)
    operator = model.find("Operator")
    operator_state = operator.get("state") if operator is not None else None
    if not sysactions.has_operator_opened(model):
        open_kiosk_operator_automatically(pos_id, user_id, operator_state)


def check_kiosk_pos_state(pos_id, user_id):
    model = sysactions.get_model(pos_id)
    model_pos_state = model.find("PosState")
    pos_state = model_pos_state.get("state") if model_pos_state is not None else None
    pos_business_period = sysactions.get_business_period(model)
    actual_business_period = datetime.now().strftime("%Y%m%d")
    if pos_business_period != actual_business_period:
        pos_state = "BLOCKED"
    if pos_state in ["BLOCKED", "CLOSED", "UNDEFINED"]:
        open_kiosk_business_day_automatically(model, pos_id, user_id, pos_state, actual_business_period)


def open_kiosk_operator_automatically(pos_id, user_id, operator_state):
    try:
        if operator_state != "PAUSED" and not open_user(pos_id, user_id):
            raise sysactions.StopAction()
        if not login_user(pos_id, user_id):
            raise sysactions.StopAction()
    except Exception as _:
        sys_log_exception("Error on kiosk auto operator logging")
        raise


def get_kiosk_user_information():
    # todo: get totem user info from another place
    user_id = "2718"
    user_password = "2818"
    return user_id, user_password


def authenticate_kiosk_operator():
    user_id, user_password = get_kiosk_user_information()
    try:
        sysactions.authenticate_user(user_id, user_password)
    except sysactions.AuthenticationFailed as _:
        sys_log_error("Error authenticating kiosk operator")
        raise sysactions.StopAction()
    return user_id


def open_kiosk_business_day_automatically(model, pos_id, user_id, pos_state, actual_business_period):
    try:
        msg_dest_name = "POS{}".format(pos_id)

        if pos_state == "BLOCKED":
            if _need_to_close_user(model) and not close_user(pos_id, user_id):
                raise sysactions.StopAction()

            if sysactions.is_day_opened(model):
                msg = sysactions.send_message(msg_dest_name, msgbus.TK_POS_BUSINESSEND, msgbus.FM_PARAM, pos_id, 90 * 1000000)
                if msg.token == msgbus.TK_SYS_NAK:
                    raise sysactions.StopAction()

        msg_data = "\0".join([pos_id, actual_business_period])
        msg = sysactions.send_message(msg_dest_name, msgbus.TK_POS_BUSINESSBEGIN, msgbus.FM_PARAM, msg_data, 90 * 1000000)
        if msg.token == msgbus.TK_SYS_NAK:
            raise sysactions.StopAction()
    except Exception as _:
        sys_log_exception("Error opening business day on POS#{}".format(pos_id))
        raise


def _need_to_close_user(model):
    for operator in model.findall("Operators/Operator"):
        if operator.get("state") in ["LOGGEDIN", "OPENED", "PAUSED"]:
            return True
    return False
