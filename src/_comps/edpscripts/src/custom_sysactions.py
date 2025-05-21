# -*- coding: utf-8 -*-
import inspect
from functools import wraps
from sysactions import get_model, StopAction, show_messagebox, get_podtype
from systools import sys_log_exception
from actions.config import get_function_authorization_level_from_config
from actions.util import get_user_level, get_authorization
from actions.pos import pos_must_be_blocked

configurations = None


def initialize_manager_authorizations(config):
    global configurations
    configurations = config


def user_authorized_to_execute_action(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_data = None

        pos_id = args[0]
        try:
            function_level = get_function_authorization_level_from_config(configurations, f.func_name)
            model = get_model(pos_id)
            operator = model.find("./Operator")
            if operator is not None:
                user_id = operator.get("id")
                if get_user_level(user_id) <= function_level:
                    status, user_data = get_authorization(pos_id, min_level=function_level, model=model)
                    if not status:
                        return StopAction()
        except BaseException as ex:
            error_message = "$GET_USER_AUTHORIZATION_ERROR_" + str(type(ex).__name__).upper()
            sys_log_exception("Error validating user authorization")
            show_messagebox(pos_id, message=error_message, icon="error")
            return False

        if 'auth_data' in inspect.getargspec(f).args:
            kwargs['auth_data'] = user_data

        return f(*args, **kwargs)

    return decorated_function


def block_action_if_pos_is_blocked(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            pos_id = args[0]
            model = get_model(pos_id)
            pod_type = get_podtype(model)
            if pod_type != 'TT' and pos_must_be_blocked(pos_id):
                from msgbusboundary import MsgBusTableService as tableService
                from table_actions import deselect_table
                selected_table = tableService().get_selected_table(pos_id)
                if selected_table is None:
                    deselect_table(pos_id)

                show_messagebox(pos_id, message="$POS_BLOCKED", icon="error")
                return StopAction()
        except BaseException as _:
            return False

        return f(*args, **kwargs)

    return decorated_function
