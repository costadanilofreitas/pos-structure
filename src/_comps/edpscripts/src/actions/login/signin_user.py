# -*- coding: utf-8 -*-
import actions.util
import sysactions
import utils
from actions.goals import update_daily_goals
from actions.models import UserLevels


@sysactions.action
def sign_in_table_user(pos_id, user_id=None):
    if not actions.util.check_valid_user(pos_id, user_id):
        return False

    if actions.util.is_user_already_logged(pos_id, user_id, block_by_working_mode=True):
        return False

    ret, user_data = actions.util.get_authorization(pos_id, UserLevels.OPERATOR.value, user_id=user_id)
    if not ret:
        return False
    user_id = user_data[0]
    password = user_data[1]

    return sign_in_user(pos_id, user_id, password)


def sign_in_user(pos_id, user_id, password):
    if not utils.check_current_day(pos_id):
        return False

    pos_user = actions.util.get_opened_pos_user(pos_id, user_id)
    try:
        sysactions.authenticate_user(user_id, password)
    except sysactions.AuthenticationFailed:
        sysactions.show_messagebox(pos_id, "$INVALID_USERNAME_OR_PASSWORD", "$INFORMATION")
        return False

    user_opened = False
    if pos_user is None:
        long_name, _, user_id = utils.get_user_info(user_id)
        confirmation_message = "$CONFIRM_OPEN_USER|{}".format(long_name)
        resp = sysactions.show_messagebox(pos_id, confirmation_message, buttons="$OK|$CANCEL", asynch=False)
        if resp is None or resp == 1:
            return False

        user_opened = utils.open_user(pos_id, user_id)

    pod_type, pos_function = utils.get_pod_type_and_pos_function(pos_id)
    if pod_type is None or pos_function is None:
        return False

    initial_float = None
    model = sysactions.get_model(pos_id)

    _, _, session = actions.util.get_operator_info(model, user_id)
    if pos_function != "OT" and not utils.user_inserted_initial_amount(pos_id, session):
        initial_float = utils.get_initial_float(pos_id, pod_type, pos_function)

    if not utils.login_user(pos_id, user_id):
        return False

    utils.change_pod_type_and_pos_function(pos_id, pod_type, pos_function)

    if initial_float is not None:
        utils.save_initial_float(initial_float, pos_id, user_id)

    update_daily_goals(pos_id)

    if user_opened:
        model = sysactions.get_model(pos_id)
        utils.print_open_day_report(model, pos_id, initial_float)

    return True
