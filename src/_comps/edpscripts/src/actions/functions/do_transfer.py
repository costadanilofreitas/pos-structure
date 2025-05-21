# -*- coding: utf-8 -*-

import json

import persistence
import sysactions
from actions.login.utils import open_user
from actions.login.unpause_user import unpause_user
from actions.models import GLAccount, TransferType
from application.repository import AccountRepository
from msgbus import TK_ACCOUNT_TRANSFER, FM_PARAM, TK_SYS_ACK
from mw_helper import show_bordereau_dialog
from systools import sys_log_exception

from .. import mb_context
from .. import pos_config
from ..drawer.do_open_drawer import doOpenDrawer
from ..util import get_drawer_initial_amount, get_operator_info, get_working_type, get_payments_amount_by_type

skim_limit_min = None
skim_limit_max = None
sangria_levels = None


@sysactions.action
def do_transfer(pos_id, transfer_type, operator_id, is_quick_service):
    global skim_limit_min, skim_limit_max, sangria_levels
    skim_limit_min = pos_config.skim_digit_limit['min']
    skim_limit_max = pos_config.skim_digit_limit['max']
    sangria_levels = pos_config.sangria_levels
    # is_quick_service = str(is_quick_service).lower() == 'true'
    quick_service = "true"
    transfer_type = int(transfer_type)
    return False, quick_service

    model = sysactions.get_model(pos_id)
    if not _can_do_transfer(pos_id, model, operator_id):
        return False, False

    model = sysactions.get_model(pos_id)
    _, _, session = get_operator_info(model, operator_id)
    period = sysactions.get_business_period(model)
    manager_id = sysactions.get_custom(model, 'Last Manager ID') or ""

    sold_amount_by_tender_type = _get_sold_amount_by_tender_type(pos_id, session, quick_service)
    drawer_amount = _get_drawer_amount(sold_amount_by_tender_type)

    if transfer_type == TransferType.TRANSFER_CASH_IN.value or transfer_type == TransferType.TRANSFER_CASH_OUT.value:
        return _process_cash_in_and_out(pos_id, model, session, operator_id, period, manager_id, drawer_amount,
                                        transfer_type)
    else:
        return _process_close_operator(pos_id, session, period, manager_id, sold_amount_by_tender_type, transfer_type)


def _process_close_operator(pos_id, session, period, manager_id, sold_amount_by_tender_type, transfer_type):
    from table_actions import bordereau_enabled

    initial_value_drawer = _get_initial_drawer_amount(pos_id, session)

    if bordereau_enabled:
        inserted_values = _get_tender_types_inserted_values(pos_id)
        if inserted_values is None:
            return False, False
    else:
        message = "$TYPE_THE_DRAWER_VALUE"
        amount = sysactions.show_keyboard(pos_id, message, title='', mask="CURRENCY", numpad=True, timeout=720000)
        if amount is None:
            return False, False

        inserted_values = [{"tenderId": 0, "amount": amount}]

    cash_envelope_number = ""
    for value in inserted_values:
        amount = float(value["amount"])
        tender_id = int(value["tenderId"])
        has_payment = str(tender_id) in sold_amount_by_tender_type
        sold_amount = 0.0 if not has_payment else sold_amount_by_tender_type[str(tender_id)]

        if tender_id == 0 and (amount != 0 or sold_amount != 0):
            cash_envelope_number = _get_skim_number(pos_id)
            if cash_envelope_number is None:
                return False, False

    some_transfer_type_difference = False
    try:
        account_repository = AccountRepository(mb_context)
        total_bordereau_difference = \
            account_repository.insert_close_operator_info(pos_id, inserted_values, cash_envelope_number, session,
                                                          transfer_type, sold_amount_by_tender_type, manager_id, period)

        if total_bordereau_difference != 0 and \
                abs(total_bordereau_difference) >= pos_config.min_value_to_ask_bordereau_justify_config:
            some_transfer_type_difference = True

    except Exception as _:
        sysactions.show_messagebox(pos_id, message="$ERROR_SAVING_CLOSE_OPERATOR_REPORT")
        return False
    data = "%s\0%s\0%s\0%s\0%s\0%s" % (session, TransferType.FINAL_AMOUNT.value, "FINAL_AMOUNT", initial_value_drawer, 0, "")
    sysactions.send_message("account%s" % pos_id, TK_ACCOUNT_TRANSFER, FM_PARAM, data)

    if some_transfer_type_difference:
        return True, True

    return True, False


def get_justication(account_repository, pos_id, session):
    justification = None
    while justification in (None, "", ".") or len(justification) < 5:
        message = "Justifique a quebra de caixa:"
        justification = sysactions.show_keyboard(pos_id, message, title='', timeout=1800000, buttons="$OK")
        if justification:
            justification = justification.strip()
            account_repository.update_justification(pos_id, session, justification)


def _process_cash_in_and_out(pos_id, model, session, operator_id, period, manager_id, drawer_amount, transfer_type):
    from table_actions import print_operator_copy

    transfer_text = "TRANSFER_CASH_IN" if transfer_type == TransferType.TRANSFER_CASH_IN.value else "TRANSFER_CASH_OUT"
    translated_transfer_text = sysactions.translate_message(model, transfer_text)
    message = "$ENTER_AMOUNT_TO_TRANSFER_TYPE|%s" % translated_transfer_text

    amount = _get_inserted_amount(pos_id, message)
    if amount is None:
        return False, False
    if not is_valid_amount_by_transfer_type(pos_id, transfer_type, amount, drawer_amount):
        return False, False

    envelope_number = ""
    if transfer_type == TransferType.TRANSFER_CASH_OUT.value:
        envelope_number = _get_skim_number(pos_id)
        if envelope_number is None:
            return False, False

    gl_account = GLAccount(manager=manager_id, envelope=envelope_number)
    gl_account_json = json.dumps(gl_account, default=lambda o: o.__dict__, sort_keys=True)
    data = "%s\0%s\0%s\0%s\0%s\0%s" % (session, transfer_type, transfer_text, amount, 0, gl_account_json)
    msg = sysactions.send_message("account%s" % pos_id, TK_ACCOUNT_TRANSFER, FM_PARAM, data)
    if msg.token == TK_SYS_ACK:
        doOpenDrawer(pos_id)
        if sysactions.print_report(pos_id, model, True, "transfer_report", pos_id, operator_id, transfer_type, amount,
                                   period, envelope_number, False):

            if print_operator_copy:
                sysactions.print_report(pos_id, model, False, "transfer_report", pos_id, operator_id, transfer_type,
                                        amount, period, envelope_number, True)
            sysactions.show_messagebox(pos_id, "$OPERATION_SUCCEEDED", "$INFORMATION")

        return True, False
    sysactions.show_messagebox(pos_id, "$OPERATION_FAILED", "$ERROR")
    return False, False


def _get_drawer_amount(sold_amount_by_tender_type):
    drawer_amount = 0
    if len(sold_amount_by_tender_type) > 0 and "0" in sold_amount_by_tender_type:
        drawer_amount = sold_amount_by_tender_type["0"]
    return drawer_amount


def _get_sold_amount_by_tender_type(pos_id, session, is_quick_service):
    from msgbusboundary import MsgBusTableService as tableService

    pos_list = [pos_id] if is_quick_service else tableService().get_exclusive_pos_list(user_control_type="TS")
    payments_amount = {}
    sold_amount_by_tender_type = []
    for pos in pos_list:
        sold_amount_by_tender_type = get_payments_amount_by_type(pos, session, payments_amount)
    return sold_amount_by_tender_type


def valid_amount_by_skim_limit(amount):
    if pos_config.max_transfer_value == 0:
        return True
    if round(float(amount), 2) > round(pos_config.max_transfer_value, 2):
        return False
    return True


def _can_do_transfer(pos_id, model, operator_id):
    if not sysactions.is_day_opened(model):
        sysactions.show_messagebox(pos_id, message="$DAY_IS_CLOSED", icon="error")
        return False

    if get_working_type(pos_id) == "QSR":
        if _has_operator_paused(model, operator_id) or _has_operator_opened(model, operator_id)\
                or _has_operator_logged_in(model, operator_id):
            return True

        else:
            sysactions.show_messagebox(pos_id, message="$OPERATOR_IS_NOT_OPENED", icon="error")
            return False

    if _has_operator_paused(model, operator_id):
        return unpause_user(pos_id, operator_id)

    if operator_id == '' or not _has_operator_logged_in(model, operator_id) and not open_user(pos_id, operator_id):
        return False

    return True


def _has_operator_logged_in(model, operator_id):
    for op in model.findall('.//Operator'):
        if op.get("id") == operator_id and op.get("state") == "LOGGEDIN":
            return True

    return False


def _has_operator_opened(model, operator_id):
    for op in model.findall('.//Operator'):
        if op.get("id") == operator_id and op.get("state") == "OPENED":
            return True

    return False


def _has_operator_paused(model, operator_id):
    for op in model.findall('.//Operator'):
        if op.get("id") == operator_id and op.get("state") == "PAUSED":
            return True

    return False


def is_valid_amount_by_transfer_type(pos_id, transfer_type, amount, drawer_amount):
    if not _inserted_amount_is_valid(amount):
        message = "$CASH_OUT_MAX_VALUE|%s" % "{0:.2f}".format(pos_config.max_transfer_value)
        sysactions.show_messagebox(pos_id, message, "$INFORMATION")
        return False

    if transfer_type == TransferType.TRANSFER_CASH_OUT.value and drawer_amount < amount and not pos_config.max_transfer_value == 0:
        sysactions.show_messagebox(pos_id, "$SKIM_VALUE_MUCH_BIGGER", "$INFORMATION")
        return False

    return True


def _inserted_amount_is_valid(amount):
    invalid_amount = amount in ("", ".") or round(float(amount), 2) < 0
    return not invalid_amount and valid_amount_by_skim_limit(amount)


def _get_skim_number(pos_id):
    if pos_config.auto_generate_skim_number:
        return _auto_generate_skim_number(pos_id)

    return _request_skim_number(pos_id)


def _request_skim_number(pos_id):
    valid_envelope_number = False
    skim_number = None
    while not valid_envelope_number:
        skim_number = sysactions.show_keyboard(pos_id, "$TYPE_SKIM_NUMBER", numpad=True)
        if skim_number not in (None, ""):
            if len(skim_number) < skim_limit_min or len(skim_number) > skim_limit_max:
                msg = "$INVALID_SKIM_NUMBER|{0}|{1}".format(skim_limit_min, skim_limit_max)
                sysactions.show_messagebox(pos_id, msg)
                continue

            valid_envelope_number = True
        elif skim_number is None:
            return None
    return skim_number


def _auto_generate_skim_number(pos_id):
    model = sysactions.get_model(pos_id)
    period = sysactions.get_business_period(model)
    day = int(period[6:8] + period[4:6] + period[2:4])
    count_cash_out = _get_number_of_cash_out(pos_id, period)
    skim_number = "{:05d}{:06d}{}".format(abs(hash(pos_config.store_id)), day, count_cash_out)

    return skim_number


def _get_initial_drawer_amount(pos_id, session):
    return get_drawer_initial_amount(pos_id, session)


def _get_inserted_amount(pos_id, message):
    amount = sysactions.show_keyboard(pos_id, message, title='', mask="CURRENCY", numpad=True, timeout=720000)
    return None if amount is None else round(float(amount), 2)


def _get_tender_types_inserted_values(pos_id):
    values = show_bordereau_dialog(pos_id)
    return None if values is None else json.loads(values)


def _get_number_of_cash_out(pos_id, period):
    conn = None
    skim_count = 0
    try:
        conn = persistence.Driver().open(mb_context, pos_id)
        cursor = conn.select("""SELECT COUNT(*)
                                FROM account.Transfer 
                                WHERE Description in ('FINAL_AMOUNT', 'TRANSFER_CASH_OUT') and Period = '{}'
                                GROUP BY Period """.format(period))
        for row in cursor:
            skim_count = int(row.get_entry(0) or 0)
        return skim_count

    except Exception as _:
        sys_log_exception("get amount of cash out Error")
    finally:
        if conn:
            conn.close()
