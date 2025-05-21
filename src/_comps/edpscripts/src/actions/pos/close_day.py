from datetime import date

from msgbus import TK_POS_BUSINESSEND, FM_PARAM, TK_SYS_ACK
from mw_helper import show_message_dialog, show_message_options_dialog
from sysactions import action, get_model, get_business_period, get_podtype, set_custom, print_report, \
    translate_message, send_message
from systools import sys_log_info, sys_log_error, sys_log_exception

from actions.util import list_opened_users
from actions.pos.check_table_status import has_tab_or_tables_opened
from actions.util.get_menu_user_logged import get_menu_manager_authenticated_user
from actions.models.mw_sys_errors import MwSysErrors


@action
def close_day(pos_id):
    from msgbusboundary import MsgBusTableService as tableService
    
    error_dict = {}
    model = get_model(pos_id)
    period = get_business_period(model)
    is_table_service = model.find("WorkingMode").get("usrCtrlType") == "TS"

    pos_list = tableService().get_exclusive_pos_list(user_control_type="TS")
    if not is_table_service:
        pos_list = [pos_id]
    
    if is_table_service and has_tab_or_tables_opened(period, pos_id):
        return False
    
    opened_users = list_opened_users(pos_id)
    _fill_pos_list_with_can_close_day_pos(error_dict, period, pos_list, opened_users)
    error_messages = _parse_error_messages(model, error_dict)
    
    if len(error_messages) > 0:
        show_message_dialog(pos_id, message="$CANNOT_CLOSE_DAYS|{}".format("\\".join(error_messages)))
        return False
    
    if len(pos_list) == 0:
        show_message_dialog(pos_id, message="$HAS_NO_POS_TO_CLOSE")
        return False
    
    confirmation_message = "$CONFIRM_CLOSE_DAY|{}".format("POS {}".format(pos_list))
    resp = show_message_options_dialog(pos_id, "$OK|$CANCEL", "$INFORMATION", confirmation_message)
    if resp is None or resp == 1:
        return False
    
    try:
        sys_log_info("Closing business day for POS's: {}".format(pos_list))
        error_dict = {}
        succeed_pos_id = []
        
        for pos_no in pos_list:
            _perform_close_day(pos_no, succeed_pos_id, error_dict)
        
        if len(error_dict) > 0:
            error_messages = _parse_error_messages(model, error_dict)
            show_message_dialog(pos_id, "$INFORMATION", "$ERROR_CLOSING_DAYS|{}".format("\\".join(error_messages)))
        
        set_custom(pos_id, 'POS_MUST_BE_BLOCKED', False)
        
        if len(succeed_pos_id) > 0:
            today = date.today().strftime("%Y%m%d")
            report_pos_id = "|".join(map(str, succeed_pos_id))
            menu_manager_user = get_menu_manager_authenticated_user()
            print_report(pos_id, model, True, "cash", pos_id, today, "0", "true", report_pos_id, "end_of_day", "",
                         menu_manager_user)
    except Exception as ex:
        show_message_dialog(pos_id, "$ERROR", "$ERROR_CLOSING_DAY|{}".format(ex.message))
        

def _fill_pos_list_with_can_close_day_pos(error_dict, period, pos_list, opened_users):
    for pos_no in sorted(pos_list):
        model = get_model(pos_no)
        if not _verify_if_can_close_day(pos_no, model, period, error_dict, opened_users):
            pos_list.remove(pos_no)
            
            
def _parse_error_messages(model, error_dict):
    error_messages = []
    if len(error_dict) > 0:
        for key in error_dict:
            if key in MwSysErrors.list_values():
                msg = translate_message(model, MwSysErrors.get_name(key))
            else:
                msg = str(key)

            error_messages.append("POS {}".format(error_dict[key]) + (" - {}".format(msg)))
    return error_messages


def _perform_close_day(pos_id, succeed_pos, error_dict):
    try:
        sys_log_info("Closing business day on POS id: [{}]".format(pos_id))

        pos_model = get_model(pos_id)
        if pos_model.find("PosState").get("state") == "CLOSED":
            return

        msg = send_message("POS%d" % int(pos_id), TK_POS_BUSINESSEND, FM_PARAM, str(pos_id), timeout=60 * 1000000)
        if msg.token == TK_SYS_ACK:
            succeed_pos.append(pos_id)
            return
        else:
            sys_log_error("Error closing business day on pos id: {}. Error: {}".format(pos_id, msg.data))
            _fill_error_dict(error_dict, pos_id, msg.data)

    except Exception as ex:
        sys_log_exception("Error closing business day on pos id: {}".format(pos_id))
        _fill_error_dict(error_dict, pos_id, ex.message)
        

def _verify_if_can_close_day(pos_id, model, period, error_dict, opened_users):
    try:
        if model.find("PosState").get("state") == "CLOSED":
            error_msg = translate_message(model, "DAY_IS_ALREADY_CLOSED")
            _fill_error_dict(error_dict, pos_id, error_msg)
            return False

        operator = model.find("Operator")
        if operator is not None and operator.get('id') in [x.get('id') for x in opened_users]:
            error_msg = translate_message(model, "THERE_ARE_OPEN_OPERATORS")
            _fill_error_dict(error_dict, pos_id, error_msg)
            return False

        if period == '0':
            error_msg = translate_message(model, "NEED_TO_OPEN_DAY_FIRST")
            _fill_error_dict(error_dict, pos_id, error_msg)
            return False
    except Exception as ex:
        _fill_error_dict(error_dict, pos_id, ex.message)

    return True


def _fill_error_dict(error_dict, pos_id, error_message):
    error_message = error_message.split("\0")[0]
    
    if error_message not in error_dict:
        error_dict[error_message] = [pos_id]
    else:
        error_dict[error_message].append(pos_id)
        
    return error_dict
