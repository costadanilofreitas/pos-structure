# -*- coding: utf-8 -*-
import datetime
from sysactions import show_messagebox, get_model, check_business_day, format_date, get_business_period, \
    translate_message, show_info_message, sys_log_info, send_message, sys_log_exception, print_report, action, \
    show_confirmation

from msgbus import TK_POS_BUSINESSBEGIN, FM_PARAM, TK_SYS_ACK, TK_PERSIST_SEQUENCER_RESET

# usecs per second
USECS_PER_SEC = 1000000

poslist = []

is24HoursStore = False
nf_type = None

@action
def openday(posid, store_wide="false", force_open="false", *args):
    """
    Opens a business day
    @param store_wide: "true" for store-wide operations
    @param force_open: "true" for LEVEL_SYSTEM operations
    """
    model = get_model(posid)

    # verify updates
    # doCheckUpdates(posid, show_msg="no")

    # verify all POS
    if store_wide == "false":
        check_business_day(posid, model=model, need_opened=False)

    today = datetime.date.today().strftime("%Y%m%d")
    confirm = show_confirmation(posid, message="Você tem certeza que deseja abrir o dia de negócio %s?" % format_date(today), title="Alerta", icon="warning", buttons="$OK|$CANCEL")
    if not confirm:
        return

    posnumbers = tuple(poslist) if (store_wide.lower() == "true") else (posid,)

    # Check if all registers can be opened
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
        question = show_messagebox(posid, message=message, title="$DAY_OPEN", icon=icon, buttons="|".join(options))
        if (question is None) or (question == 0):
            return  # User cancelled, or timeout

        posnumbers = poslist_new

    posnumbers = sorted(posnumbers)
    sys_log_info("Opening business day. [Store-wide: %s] posnumbers: %s" % (store_wide, posnumbers))
    pos_ok = []

    for posno in posnumbers:
        try:
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
                show_info_message(posid, "$ERROR_OPENING_BUSINESS_PERIOD|%02d|%s" % (int(posno), errormsg), msgtype="error")
        except Exception as ex:
            sys_log_exception("Error opening business day on pos id: %s" % posno)
            show_info_message(posid, "$ERROR_OPENING_BUSINESS_PERIOD|%02d|%s" % (int(posno), str(ex)), msgtype="error")

    posnumbers = "|".join(map(str, pos_ok))
    if len(pos_ok):
        print_report(posid, model, True, "dayOpen_report", posid, today, posnumbers, store_wide)
    # Reset daily counters
    send_message("Persistence", TK_PERSIST_SEQUENCER_RESET, format=FM_PARAM, data="TraySetNameGen")

