# -*- coding: utf-8 -*-
import datetime
import logging
import os
import time

import persistence
import json
from helper import config_logger
from msgbus import TK_EVT_EVENT, TK_SYS_ACK, TK_SYS_NAK, FM_STRING, FM_PARAM
from bustoken import TK_RUPTURA_GET_ENABLED, TK_RUPTURA_GET_DISABLED, \
    TK_RUPTURA_ENABLE_ITEM, TK_RUPTURA_DISABLE_ITEM, TK_RUPTURA_IS_PROCESSED
from sysactions import get_model, show_keyboard, is_valid_date, show_info_message, print_report, action, get_user_information, \
    generate_report, show_listbox, show_messagebox, get_storewide_config, send_message, get_operator_session, close_asynch_dialog


mbcontext = None
poslist = []
store_id = None
config_logger(os.environ["LOADERCFG"], 'ManagerReports')
logger = logging.getLogger("ManagerReports")


@action
def speedOfServiceReport(posid, store_wide="false", *args):
    model = get_model(posid)

    period = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)
    if period is None:
        return

    if not is_valid_date(period):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return

    if is_date_old(period):
        show_info_message(posid, "Não é possivel consultar datas com mais de 30 dias", msgtype="error")
        return

    pos = show_keyboard(posid, "Digite o número do POS ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
    if pos in (None, "", "."):
        return

    print_report(posid, model, True, "speedOfService", posid, period, pos, store_id)


@action
def hourlySalesReport(posid, store_wide="true", *args):
    model = get_model(posid)
    period = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)
    if period is None:
        return
    if not is_valid_date(period):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return

    if is_date_old(period):
        show_info_message(posid, "Não é possivel consultar datas com mais de 30 dias", msgtype="error")
        return

    pos = show_keyboard(posid, "Digite o número do POS ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
    if pos in (None, "", "."):
        return

    print_report(posid, model, True, "hourlySales", posid, period, pos, store_id)


@action
def productMixReportByPeriod(posid, date_type="BusinessPeriod", *args):
    model = get_model(posid)

    start = show_keyboard(posid, "Digite a data de início", title="", mask="DATE", numpad=True)

    if start is None:
        return
    if not is_valid_date(start):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return

    if is_date_old(start):
        show_info_message(posid, "Não é possivel consultar datas com mais de 30 dias", msgtype="error")
        return

    end = show_keyboard(posid, "Digite a data de fim", title="", mask="DATE", numpad=True)

    if end is None:
        return

    if not is_valid_date(end):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return

    selected_pos_id = show_keyboard(posid, "Digite o número do POS ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)

    if selected_pos_id in (None, "", "."):
        return

    if int(selected_pos_id) not in [0] + list(poslist):
        show_info_message(posid, "Número de POS inválido", msgtype="error")
        return

    dlg_id = None
    try:
        dlg_id = show_messagebox(posid, message="$PLEASE_WAIT", title="$PROCESSING", icon="info", buttons="", asynch=True, timeout=180000)
        time.sleep(0.5)
        print_report(posid, model, True, "new_pmix_report", date_type, posid, selected_pos_id, start, end, store_id)
    finally:
        if dlg_id:
            close_asynch_dialog(posid, dlg_id)


@action
def cashReport(pos_id, ask_operator="ask", date_type="BusinessPeriod", ask_pos="ask", *args):
    model = get_model(pos_id)
    if date_type == "SessionId":
        operator = model.find("Operator")
        if operator is None or operator.get("state") != "LOGGEDIN":
            show_info_message(pos_id, "Não há operador logado", msgtype="error")
            return

        session_id = model.find("Operator").get("sessionId")
        initial_date = None
        end_date = None
        operatorid = None
        report_pos = None

    else:
        session_id = None
        initial_date = get_report_date(pos_id, "Digite a Data Inicial ou pressione 'Ok' para Data Atual")
        if initial_date is None:
            return

        end_date = get_report_date(pos_id, "Digite a Data Final ou pressione 'Ok' para Data Atual")
        if end_date is None:
            return

        if ask_pos == "ask":
            report_pos = show_keyboard(pos_id, "Digite o número do POS ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
            if report_pos in (None, "", "."):
                return

            report_pos = int(0 if report_pos in (None, 'None') else report_pos)
            if report_pos not in poslist and report_pos not in (0,):
                show_info_message(pos_id, "POS digitado não Existe", msgtype="warning")
                return
            report_pos = str(report_pos)
        else:
            report_pos = None

        if ask_operator == "ask":
            operatorid = show_keyboard(pos_id, "Digite o número do Operador ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
            if operatorid in (None, "", "."):
                return
            if not get_user_information(operatorid):
                show_info_message(pos_id, "$INVALID_USER_ID", msgtype="warning")
                return
        elif ask_operator == "current":
            try:
                current_operator_id = model.find('Operator').get('id')
                operatorid = current_operator_id
            except:
                show_info_message(pos_id, "Não há último operador", msgtype="error")
                return
        else:
            operatorid = "0"

    print_report(pos_id, model, True, "new_cash_report", date_type, pos_id, report_pos, initial_date, end_date, operatorid, session_id, store_id)


@action
def salesByBrandReport(pos_id, ask_operator="ask", date_type="BusinessPeriod", ask_pos="ask"):
    model = get_model(pos_id)
    if date_type == "SessionId":
        operator = model.find("Operator")
        if operator is None or operator.get("state") != "LOGGEDIN":
            show_info_message(pos_id, "Não há operador logado", msgtype="error")
            return

        session_id = model.find("Operator").get("sessionId")
        initial_date = None
        end_date = None
        operator_id = None
        report_pos = None

    else:
        session_id = None
        initial_date = get_report_date(pos_id, "Digite a Data Inicial ou pressione 'Ok' para Data Atual")
        if initial_date is None:
            return

        end_date = get_report_date(pos_id, "Digite a Data Final ou pressione 'Ok' para Data Atual")
        if end_date is None:
            return

        if ask_pos == "ask":
            report_pos = show_keyboard(pos_id, "Digite o número do POS ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
            if report_pos in (None, "", "."):
                return

            report_pos = int(0 if report_pos in (None, 'None') else report_pos)
            if report_pos not in poslist and report_pos not in (0,):
                show_info_message(pos_id, "POS digitado não Existe", msgtype="warning")
                return
            report_pos = str(report_pos)
        else:
            report_pos = None

        if ask_operator == "ask":
            operator_id = show_keyboard(pos_id, "Digite o número do Operador ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
            if operator_id in (None, "", "."):
                return
            if not get_user_information(operator_id):
                show_info_message(pos_id, "$INVALID_USER_ID", msgtype="warning")
                return
        elif ask_operator == "current":
            try:
                current_operator_id = model.find('Operator').get('id')
                operator_id = current_operator_id
            except Exception as _:
                show_info_message(pos_id, "Não há último operador", msgtype="error")
                return
        else:
            operator_id = "0"

    print_report(pos_id, model, True, "sales_by_brand", date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, store_id)


@action
def voidedOrdersReport(pos_id, ask_operator="ask", date_type="BusinessPeriod", ask_pos="ask"):
    model = get_model(pos_id)
    if date_type == "SessionId":
        operator = model.find("Operator")
        if operator is None or operator.get("state") != "LOGGEDIN":
            show_info_message(pos_id, "Não há operador logado", msgtype="error")
            return

        session_id = model.find("Operator").get("sessionId")
        initial_date = None
        end_date = None
        operator_id = None
        report_pos = None

    else:
        session_id = None
        initial_date = get_report_date(pos_id, "Digite a Data Inicial ou pressione 'Ok' para Data Atual")
        if initial_date is None:
            return

        end_date = get_report_date(pos_id, "Digite a Data Final ou pressione 'Ok' para Data Atual")
        if end_date is None:
            return

        if ask_pos == "ask":
            report_pos = show_keyboard(pos_id, "Digite o número do POS ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
            if report_pos in (None, "", "."):
                return

            report_pos = int(0 if report_pos in (None, 'None') else report_pos)
            if report_pos not in poslist and report_pos not in (0,):
                show_info_message(pos_id, "POS digitado não Existe", msgtype="warning")
                return
            report_pos = str(report_pos)
        else:
            report_pos = None

        if ask_operator == "ask":
            operator_id = show_keyboard(pos_id, "Digite o número do Operador ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
            if operator_id in (None, "", "."):
                return
            if not get_user_information(operator_id):
                show_info_message(pos_id, "$INVALID_USER_ID", msgtype="warning")
                return
        elif ask_operator == "current":
            try:
                current_operator_id = model.find('Operator').get('id')
                operator_id = current_operator_id
            except Exception as _:
                show_info_message(pos_id, "Não há último operador", msgtype="error")
                return
        else:
            operator_id = "0"

    print_report(pos_id, model, True, "voided_orders_report", date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id, store_id)


def get_report_date(pos_id, message):
    date = show_keyboard(pos_id, message, title="", mask="DATE", numpad=True)

    if date is None:
        return None
    if not is_valid_date(date):
        show_info_message(pos_id, "$INVALID_DATE", msgtype="error")
        return None

    return date


@action
def extendedReport(posid, report_type="sales_report", store_wide="false", keyboard="false", *args):
    period = time.strftime("%Y%m%d")

    if keyboard != "false":
        period = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)

    if not is_valid_date(period):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return
    posnumbers = "|".join(map(str, poslist))
    return generate_report("pos_extended_report", posid, period, 0, store_wide, posnumbers, report_type)


@action
def checkoutReport(posid, *args):
    def get_option(session):
        close_time = datetime.datetime.strptime(session['closeTime'], "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
        return "%s - %s" % (close_time, session['operatorName'])

    def get_operator_sessions(operatorid, period, posid):
        sessions = []
        options = []
        session_cols = ('openTime', 'closeTime', 'sessionId', 'operatorName')

        conn = None
        try:
            conn = persistence.Driver().open(mbcontext, dbname=str(posid))
            conn.transaction_start()
            cursor = conn.pselect("drawerChangeReport", startPeriod=period, endPeriod=period, instance=posid)
            for row in cursor:
                if row.get_entry("closeTime") and (int(row.get_entry("operatorId")) == int(operatorid) or int(operatorid) == 0):
                    sessions.append(dict([(col, row.get_entry(col)) for col in session_cols]))
                    options.append(get_option(sessions[-1]))

            conn.transaction_end()
        finally:
            if conn:
                conn.close()
        return sessions, options

    model = get_model(posid)
    period = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)
    if period is None:
        return
    if not is_valid_date(period):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return

    operatorid = show_keyboard(posid, "Digite o número do Operador ou pressione 'Ok' para todos", title="", defvalue="0", mask="INTEGER", numpad=True)
    if operatorid in (None, "", "."):
        return
    if not get_user_information(operatorid):
        show_info_message(posid, "$INVALID_USER_ID", msgtype="warning")
        return

    sessions, options = get_operator_sessions(operatorid, period, posid)
    if sessions:
        index = show_listbox(posid, options)
        if index is None:
            return  # The user cancelled - or timed-out

        session_id = sessions[index]['sessionId']
        print_report(posid, model, True, "cash", posid, period, operatorid, "False", "0", "Check Out Report", session_id)
    else:
        show_messagebox(posid, message="Não existe nenhum turno para o operador selecionado")


@action
def employeesClockedInReport(posid, *args):
    model = get_model(posid)

    business_day = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE", numpad=True)
    if business_day is None:
        return
    if not is_valid_date(business_day):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return

    store_id = get_storewide_config("Store.Id")
    business_day = datetime.datetime.strptime(business_day, '%Y%m%d').strftime('%Y-%m-%d')
    params = '["GET_TIMESHEET", "%s", "%s"]' % (str(business_day), str(store_id))
    msg = send_message("MwCentral", TK_EVT_EVENT, FM_STRING, params)

    if msg.token == TK_SYS_ACK:
        print_report(posid, model, True, "employeesClockedInReport", posid, business_day, msg.data)


def is_date_old(period, *args):
    consult_days = abs((datetime.datetime.strptime(period, "%Y%m%d") - datetime.datetime.now()).days)

    return consult_days > 30


def is_current_date(period, *args):
    return datetime.datetime.strptime(period, "%Y%m%d").date() == datetime.date.today()

