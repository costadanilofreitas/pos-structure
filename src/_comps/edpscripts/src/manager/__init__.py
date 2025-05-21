# -*- coding: utf-8 -*-
import datetime

from msgbus import TK_POS_BUSINESSBEGIN, FM_PARAM, TK_SYS_ACK, TK_PERSIST_SEQUENCER_RESET
from sysactions import get_model, format_date, get_business_period,  translate_message, \
    show_info_message, sys_log_info, send_message, sys_log_exception, print_report, action,  show_confirmation, \
    get_podtype, get_posfunction, is_day_opened, StopAction, is_day_blocked, show_messagebox
from actions.util.get_menu_user_logged import get_menu_manager_authenticated_user

USECS_PER_SEC = 1000000

poslist = []

is24HoursStore = False
nf_type = None
mbcontext = None


@action
def openday(pos_id, store_wide="false", force_open="false", *args):
    model = get_model(pos_id)
    if store_wide == "false":
        check_business_day(pos_id, model=model, need_opened=False)

    today = datetime.date.today().strftime("%Y%m%d")
    confirm = show_confirmation(pos_id, message="Você tem certeza que deseja abrir o dia de negócio %s?" % format_date(today), title="Alerta", icon="warning", buttons="$OK|$CANCEL")
    if not confirm:
        return

    posnumbers = tuple(poslist) if (store_wide.lower() == "true") else (pos_id,)

    cannot_open = []
    poslist_new = []

    for x in posnumbers:
        model_x = get_model(x)
        x_period = get_business_period(model_x)
        if nf_type == "PAF" and today <= x_period != "0" and force_open == "false":
            cannot_open.append(translate_message(model_x, "DAY_OPEN_ALREADY_OPENED", "%02d" % int(x), format_date(x_period)))
            continue
        if model_x.find("PosState").get("state") not in ("CLOSED", "UNDEFINED"):
            cannot_open.append(translate_message(model_x, "DAY_OPEN_NOT_CLOSED", "%02d" % int(x), format_date(x_period)))
            continue

        poslist_new.append(x)

    if len(cannot_open) > 0:
        pos_nok = ""
        for opt in sorted(cannot_open):
            pos_nok += "%s\\" % opt

        if not is24HoursStore:
            # For non-24hours stores, does not allow partial open
            poslist_new = []

        message = ("$REGISTERS_NOT_OPENED_CONFIRM|%s" % pos_nok) if poslist_new else ("$REGISTERS_NOT_OPENED|%s" % pos_nok)
        options = ("$CANCEL", "$OPEN_OTHER_REGISTERS") if poslist_new else ("$CANCEL",)
        icon = "question" if poslist_new else "error"
        question = show_messagebox(pos_id, message=message, title="$DAY_OPEN", icon=icon, buttons="|".join(options))
        if (question is None) or (question == 0):
            return  # User cancelled, or timeout

        posnumbers = poslist_new

    posnumbers = sorted(posnumbers)
    sys_log_info("Opening business day. [Store-wide: %s] posnumbers: %s" % (store_wide, posnumbers))
    pos_ok = []

    for posno in posnumbers:
        try:
            model = get_model(posno)
            pod_type = str(get_podtype(model))
            pos_function = get_posfunction(model)
            if nf_type == "PAF" and not (pod_type == "OT" or pos_function == "OT"):
                ret = mbcontext.MB_EasyEvtSend("pafVerifyLastZReduction",
                                               xml='',
                                               type='',
                                               synchronous=True,
                                               sourceid=int(posno))
                if ret.token != TK_SYS_ACK:
                    error_message = "Erro obtendo informações da Redução Z. Verifique a impressora."
                    show_info_message(posno, error_message, msgtype="error")
                    continue

            sys_log_info("Opening business day on POS id: [%s]" % posno)
            msg = send_message("POS%d" % int(posno), TK_POS_BUSINESSBEGIN, FM_PARAM, "%s\0%s" % (posno, today), timeout=3600 * USECS_PER_SEC)
            if msg.token == TK_SYS_ACK:
                pos_ok.append(posno)
                show_info_message(posno, "$OPERATION_SUCCEEDED", msgtype="success")
                continue
            else:
                sys_log_exception("Error opening business day on pos id: %s" % posno)
                errors = msg.data.split('\0')
                errormsg = errors[1] if len(errors) > 1 else errors[0] if len(errors) > 0 else errors
                show_messagebox(pos_id, "$ERROR_OPENING_BUSINESS_PERIOD|%02d|%s" % (int(posno), errormsg))

        except Exception as ex:
            sys_log_exception("Error opening business day on pos id: %s" % posno)
            show_messagebox(pos_id, "$ERROR_OPENING_BUSINESS_PERIOD|%02d|%s" % (int(posno), str(ex)))

    posnumbers = "|".join(map(str, pos_ok))
    if len(pos_ok):
        menu_manager_user = get_menu_manager_authenticated_user()
        print_report(pos_id, model, True, "dayOpen_report", pos_id, today, posnumbers, store_wide, menu_manager_user)
    # Reset daily counters
    send_message("Persistence", TK_PERSIST_SEQUENCER_RESET, format=FM_PARAM, data="TraySetNameGen")


def check_business_day(posid, model=None, need_opened=True, can_be_blocked=True):
    if model is None:
        model = get_model(posid)
    opened = is_day_opened(model)
    if opened and not need_opened:
        show_messagebox(posid, "$NEED_TO_CLOSE_BDAY_FIRST")
        raise StopAction()
    if need_opened and not opened:
        show_messagebox(posid, "$NEED_TO_OPEN_BDAY_FIRST")
        raise StopAction()
    if (not can_be_blocked) and is_day_blocked(model):
        show_messagebox(posid, "$POS_IS_BLOCKED_BY_TIME")
        raise StopAction()
