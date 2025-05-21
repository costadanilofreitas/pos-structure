# -*- coding: utf-8 -*-

import sysactions
from actions.util import get_opened_pos_user
from common_close_user import common_close_user
from mw_helper import show_message_options_dialog
from sysactions import get_model, action, get_business_period

from .. import logger


@action
def sign_out_user(pos_id, user_id=None):
    logger.debug("Logoff POS %d - Iniciando logoff." % int(pos_id))
    model = get_model(pos_id)

    if user_id is None:
        operator = model.find("Operator")
        if operator is None:
            sysactions.show_messagebox(pos_id, "$INVALID_USER_OR_PASSWORD", "$INFORMATION")
            return False
        user_id = model.find("Operator").get('id')

    if user_id is None:
        sysactions.show_messagebox(pos_id, "$INVALID_USER_OR_PASSWORD", "$INFORMATION")
        return False

    pos_user = get_opened_pos_user(pos_id, user_id)

    if pos_user is None:
        sysactions.show_messagebox(pos_id, "$USER_NOT_OPENED", "$INFORMATION")
        return False

    resp = show_message_options_dialog(pos_id, "$OK|$CANCEL", "$INFORMATION", "$CONFIRM_CLOSE_USER|{}"
                                       .format(pos_user.get("name")))
    if resp is None or resp == 1:
        return False

    if not continue_with_opened_tables(pos_id, model, user_id):
        return False

    return common_close_user(pos_id, model, user_id)


def continue_with_opened_tables(pos_id, model, user_id):
    from table_actions import can_close_operator_with_opened_table

    is_valid_pod_type = model.find("WorkingMode").get("podType") in ["TS", "FL"]
    is_order_taker = model.find("WorkingMode").get("podFunction") == "OT"
    period = get_business_period(model)

    if is_valid_pod_type and not is_order_taker:
        from tablemgrapi import get_posts
        pos_ts = get_posts(model)
        operator_table = pos_ts.listTables(user_id)
        for table in operator_table:
            if table['statusDescr'] == "InProgress":
                if table["businessPeriod"].replace("-", "") == period:
                    if can_close_operator_with_opened_table:
                        ret = sysactions.show_messagebox(pos_id, "$HAS_OPENED_TABLES_CONTINUE", buttons="$YES|$NO")
                        return ret == 0
                    else:
                        sysactions.show_messagebox(pos_id, "$HAS_OPENED_TABLES")
                        return False

    return True
