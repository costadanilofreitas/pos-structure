# -*- coding: utf-8 -*-
import logging

from sysactions import StopAction, show_messagebox, set_custom, get_business_period, get_operator_session
from actions.util import get_drawer_amount

logger = logging.getLogger("PosActions")


def do_set_drawer_status(pos_id, amount, state=None, alert_level_1='0'):
    from posactions import sangria_levels

    try:
        sangria_levels_list = [float(level) for level in sangria_levels.split(";")] if sangria_levels else []
        if len(sangria_levels_list) == 3:
            amount = float(amount)
            if amount >= sangria_levels_list[2]:
                show_messagebox(pos_id, "Caixa travado, necessario fazer a Sangria", title="$SKIM_ALERT", buttons="$OK")
                return True
            elif state in ["TOTALED", "PAID"] and sangria_levels_list[0] <= amount < sangria_levels_list[2]:
                if amount < sangria_levels_list[1]:
                    if int(alert_level_1 or 0) == 0:
                        set_custom(pos_id, "sangria_level_1_alert", "1")
                    else:
                        return False
                show_messagebox(pos_id, "Necessario fazer a Sangria", title="$SKIM_ALERT", icon="error", buttons="$OK")
    except (BaseException,):
        logger.exception("Error in Skim Level configuration")

    return False


def check_sangria(model, pos_id):
    if is_sangria_enable():
        period = get_business_period(model)
        session = get_operator_session(model)
        drawer_amount = get_drawer_amount(pos_id, period, session)

        logger.debug("--- doSale doSetDrawerStatus ---")
        if do_set_drawer_status(pos_id, drawer_amount):
            raise StopAction()


def is_sangria_enable():
    from posactions import is_sangria_enabled_config, sangria_levels
    return is_sangria_enabled_config and sangria_levels is not None
