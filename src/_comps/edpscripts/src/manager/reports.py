# -*- coding: utf-8 -*-
import json
import datetime
import logging
import os
import time

import persistence
import sysactions
from functools import wraps
from actions.models import TransferType
from old_helper import config_logger, convert_from_utf_to_localtime
from msgbus import TK_EVT_EVENT, TK_SYS_ACK, FM_STRING, TK_PRN_PRINT, FM_PARAM, MBException
from sysactions import get_model, show_keyboard, is_valid_date, show_info_message, action, \
    get_user_information, generate_report, show_listbox, show_messagebox, get_storewide_config, send_message, \
    print_text, sys_log_info
from actions.util.get_menu_user_logged import get_menu_manager_authenticated_user
from systools import sys_log_exception

mbcontext = None
poslist = []
store_id = None
config_logger(os.environ["LOADERCFG"], 'ManagerReports')
report_logger = logging.getLogger("ManagerReports")
config_logger(os.environ["LOADERCFG"], 'ManagerReportsData')
report_data_logger = logging.getLogger("ManagerReportsData")

invalid_date_i18n = "$INVALID_DATE"
type_report_i18n = "$TYPE_REPORT_POS"
type_operator_id_i18n = "$TYPE_OPERATOR_ID"
invalid_user_id_i18n = "$INVALID_USER_ID"


def report_action(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            report_logger.info('Requested report: {}'.format(f.func_name))
        except BaseException as _:
            return False

        report = f(*args, **kwargs)
        if report:
            report_data_logger.info(
                "\n".join((
                    '---',
                    'Requested report: {}'.format(f.func_name),
                    'Args: {} | Kwargs: {}'.format(str(args), str(kwargs)),
                    report,
                    '---'
                ))
            )
        return report

    return action(decorated_function)


def print_report(posid, model, preview, report_name, *report_params):
    report = generate_report(report_name, *report_params)
    if report:
        print_text(posid, model, report, preview)
        return report
    else:
        sys_log_info("Could not generate report: %s" % report_name)
    return None


@report_action
def speedOfServiceReport(posid, store_wide="false", *args):
    model = get_model(posid)

    period = show_keyboard(posid, "$TYPE_DATE", title="", mask="DATE", numpad=True)
    if period is None:
        return

    if not is_valid_date(period):
        show_messagebox(posid, invalid_date_i18n)
        return

    if is_date_old(period):
        show_messagebox(posid, "Não é possivel consultar datas com mais de 30 dias")
        return

    pos = show_keyboard(posid, type_report_i18n, title="", defvalue="0", mask="INTEGER", numpad=True)
    if pos in (None, "", "."):
        return

    return print_report(posid, model, True, "speedOfService", posid, period, pos, store_id)


@report_action
def hourlySalesReport(pos_id, ask_pos="ask", ask_operator="ask", get_logged_user=False):
    from msgbusboundary import MsgBusTableService as tableService

    get_logged_user = get_logged_user.lower() == 'true'
    model = get_model(pos_id)
    period = show_keyboard(pos_id, "$TYPE_DATE", title="", mask="DATE", numpad=True)
    if period is None:
        return
    if not is_valid_date(period):
        show_messagebox(pos_id, invalid_date_i18n)
        return

    if is_date_old(period):
        show_messagebox(pos_id, "Não é possivel consultar datas com mais de 30 dias")
        return

    pos_list = []
    if ask_pos == "ask":
        pos_list = show_keyboard(pos_id, type_report_i18n, title="", defvalue="0", mask="INTEGER", numpad=True)
        if pos_list in (None, "", "."):
            return

    pos_list = tableService().get_exclusive_pos_list() if int(pos_list) == 0 else [int(pos_list)]
    operator_id = ""
    if ask_operator == "ask":
        operator_id = show_keyboard(pos_id, type_operator_id_i18n, title="", defvalue="0", mask="INTEGER", numpad=True)
        if operator_id in (None, "", "."):
            return
        if not get_user_information(operator_id):
            show_info_message(pos_id, invalid_user_id_i18n, msgtype="warning")
            return
        if operator_id == "0":
            operator_id = ""
        else:
            operator_id = int(operator_id)

    if bool(get_logged_user):
        operator = model.find("Operator")
        operator_id = operator.get("id")

    return print_report(pos_id, model, True, "hourlySales", pos_id, json.dumps(pos_list), str(operator_id), period)


def _get_report_parameters(pos_id, model, ask_operator, date_type, ask_pos, user=None, get_logged_user=False):
    if date_type == "SessionId":
        operator = model.find("Operator")
        if operator is None or operator.get("state") != "LOGGEDIN":
            show_messagebox(pos_id, "$USER_NOT_OPENED")
            raise sysactions.StopAction()

        session_id = model.find("Operator").get("sessionId")
        initial_date = None
        end_date = None
        operator_id = None
        report_pos = 0

    else:
        session_id = None
        initial_date = get_report_date(pos_id, "$TYPE_INITIAL_DATE")
        if initial_date is None:
            raise sysactions.StopAction()

        end_date = get_report_date(pos_id, "$TYPE_FINAL_DATE")
        if end_date is None:
            raise sysactions.StopAction()

        if ask_pos == "ask" or type(ask_pos) == int:
            if type(ask_pos) == int:
                report_pos = str(ask_pos)
            else:
                report_pos = show_keyboard(pos_id, type_report_i18n, title="", defvalue="0", mask="INTEGER",
                                           numpad=True)
                if report_pos in (None, "", "."):
                    raise sysactions.StopAction()
            report_pos = int(0 if report_pos in (None, 'None') else report_pos)
            if report_pos not in poslist and report_pos not in (0,):
                show_messagebox(pos_id, "POS digitado não existe")
                raise sysactions.StopAction()
            report_pos = str(report_pos)
        elif ask_pos == "current":
            report_pos = str(pos_id)
        else:
            report_pos = 0

        if ask_operator == "ask":
            operator_id = show_keyboard(pos_id, type_operator_id_i18n, title="", defvalue="0", mask="INTEGER",
                                        numpad=True)
            if operator_id in (None, "", "."):
                raise sysactions.StopAction()
            if not get_user_information(operator_id):
                show_messagebox(pos_id, message=invalid_user_id_i18n)
                raise sysactions.StopAction()
        elif ask_operator == "current":
            try:
                current_operator_id = model.find('Operator').get('id')
                operator_id = current_operator_id
            except Exception as _:
                show_messagebox(pos_id, message="$USER_NOT_OPENED")
                raise sysactions.StopAction()
        else:
            operator_id = "0"

            if user not in [None, "None", ""]:
                operator_id = user

        if get_logged_user.lower() == "true" if type(get_logged_user) == str else get_logged_user:
            operator = model.find("Operator")
            operator_id = operator.get("id")

    return [date_type, pos_id, report_pos, initial_date, end_date, operator_id, session_id]


@report_action
def productMixReportByPeriod(pos_id, date_type="BusinessPeriod", ask_pos="ask", ask_operator="ask",
                             get_logged_user=False):
    model = get_model(pos_id)

    parameters = _get_report_parameters(pos_id, model, ask_operator, date_type, ask_pos, None, get_logged_user)
    parameters.extend([store_id, get_pmix_report_model(pos_id)])

    return print_report(pos_id, model, True, "new_pmix_report", *parameters)


@report_action
def tipReport(pos_id, ask_operator="ask", get_logged_user=False):
    model = get_model(pos_id)

    parameters = _get_report_parameters(pos_id, model, ask_operator, "BusinessPeriod", "notAsk", None, get_logged_user)
    parameters.extend([store_id])

    return print_report(pos_id, model, True, "tip_report", *parameters)


@report_action
def cashReport(pos_id, ask_operator="ask", date_type="BusinessPeriod", ask_pos="ask", is_table_service=False, user=None,
               get_logged_user=False, only_body=False, only_payments=False):
    model = get_model(pos_id)

    parameters = _get_report_parameters(pos_id, model, ask_operator, date_type, ask_pos, user, get_logged_user)
    parameters.extend([store_id, None, None, None, bool(is_table_service), only_body, only_payments])

    return print_report(pos_id, model, True, "new_cash_report", *parameters)


@report_action
def discountReport(pos_id, ask_operator="ask", date_type="BusinessPeriod", ask_pos="ask", is_table_service=False,
                   user=None, get_logged_user=False):
    model = get_model(pos_id)

    parameters = _get_report_parameters(pos_id, model, ask_operator, date_type, ask_pos, user, get_logged_user)
    parameters.extend([store_id, None, None, None, bool(is_table_service)])

    return print_report(pos_id, model, True, "discount_report", *parameters)


@report_action
def voidedOrdersReport(pos_id, ask_operator="ask", date_type="BusinessPeriod", ask_pos="ask"):
    model = get_model(pos_id)

    parameters = _get_report_parameters(pos_id, model, ask_operator, date_type, ask_pos)
    parameters.extend([store_id])

    return print_report(pos_id, model, True, "voided_orders_report", *parameters)


def get_report_date(pos_id, message):
    date = show_keyboard(pos_id, message, title="", mask="DATE", numpad=True)

    if date is None:
        return None
    if not is_valid_date(date):
        show_messagebox(pos_id, invalid_date_i18n)
        return None

    return date


def get_pmix_report_model(pos_id):
    ret = show_messagebox(pos_id, "$CHOOSE_PMIX_PRODUCT_TYPE", title="", buttons="$ALL_PRODUCTS|$PRICED|$UNPRICED")

    if ret == 1:
        return "PRICED"
    elif ret == 2:
        return "UNPRICED"
    else:
        return "ALL_PRODUCTS"


@report_action
def extendedReport(posid, report_type="sales_report", store_wide="false", keyboard="false", *args):
    period = time.strftime("%Y%m%d")

    if keyboard != "false":
        period = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE",
                               numpad=True)

    if not is_valid_date(period):
        show_info_message(posid, invalid_date_i18n, msgtype="error")
        return
    posnumbers = "|".join(map(str, poslist))
    return generate_report("pos_extended_report", posid, period, 0, store_wide, posnumbers, report_type)


@report_action
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
                if row.get_entry("closeTime") and (
                        int(row.get_entry("operatorId")) == int(operatorid) or int(operatorid) == 0):
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
        show_info_message(posid, invalid_date_i18n, msgtype="error")
        return

    operatorid = show_keyboard(posid, type_operator_id_i18n, title="", defvalue="0", mask="INTEGER", numpad=True)
    if operatorid in (None, "", "."):
        return
    if not get_user_information(operatorid):
        show_info_message(posid, invalid_user_id_i18n, msgtype="warning")
        return

    sessions, options = get_operator_sessions(operatorid, period, posid)
    if sessions:
        index = show_listbox(posid, options)
        if index is None:
            return  # The user cancelled - or timed-out

        session_id = sessions[index]['sessionId']
        menu_manager_user = get_menu_manager_authenticated_user()
        return print_report(posid, model, True, "cash", posid, period, operatorid, "False", "0", "Check Out Report",
                            session_id, menu_manager_user)
    else:
        show_messagebox(posid, message="Não existe nenhum turno para o operador selecionado")


@report_action
def employeesClockedInReport(posid, *args):
    model = get_model(posid)

    business_day = show_keyboard(posid, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE",
                                 numpad=True)
    if business_day is None:
        return
    if not is_valid_date(business_day):
        show_info_message(posid, invalid_date_i18n, msgtype="error")
        return

    store_id = get_storewide_config("Store.Id")
    business_day = datetime.datetime.strptime(business_day, '%Y%m%d').strftime('%Y-%m-%d')
    params = '["GET_TIMESHEET", "%s", "%s"]' % (str(business_day), str(store_id))
    msg = send_message("MwCentral", TK_EVT_EVENT, FM_STRING, params)

    if msg.token == TK_SYS_ACK:
        return print_report(posid, model, True, "employeesClockedInReport", posid, business_day, msg.data)


def is_date_old(period, *args):
    consult_days = abs((datetime.datetime.strptime(period, "%Y%m%d") - datetime.datetime.now()).days)

    return consult_days > 30


def is_current_date(period, *args):
    return datetime.datetime.strptime(period, "%Y%m%d").date() == datetime.date.today()


@report_action
def transfers_report(pos_id, *args):
    model = get_model(pos_id)
    options = [sysactions.translate_message(model, "CASH_IN"), sysactions.translate_message(model, "CASH_OUT")]
    transfer_type = show_listbox(pos_id, options, message="$SELECT_OPTION")
    if transfer_type is None:
        return
    transfer_type = TransferType.TRANSFER_CASH_IN.value if transfer_type == 0 \
        else TransferType.TRANSFER_CASH_OUT.value

    period = show_keyboard(pos_id, "Digite a data ou pressione 'Ok' para data atual", title="", mask="DATE",
                           numpad=True)
    if period is None:
        return
    if not is_valid_date(period):
        show_messagebox(pos_id, message=invalid_date_i18n, icon="error")
        return

    report = generate_report("transfer_report_by_period", pos_id, "", transfer_type, period)
    reports = json.loads(report)
    data = []
    index = 0
    for report in reports:
        report_id = index
        index += 1
        for key, value in report.items():
            data.append((report_id, key, value))

    if not data:
        show_messagebox(pos_id, message="$HAS_NO_ITEMS_TO_SHOW", icon="error")
        return

    if transfer_type == 3:
        transfer_title = 'Selecione um Suprimento :'

    elif transfer_type == 4:
        transfer_title = 'Selecione uma Sangria :'

    else:
        transfer_title = 'Selecione :'

    selected_transfer = sysactions.show_text_preview(pos_id, data, title=transfer_title, buttons='$PRINT|$CANCEL',
                                                     defvalue='', onthefly=False, timeout=120000)

    if selected_transfer is None:
        return

    if int(selected_transfer[0]) == 0:
        try:
            message = None
            index = 0
            for msg in data:
                try:
                    if index == int(selected_transfer[1]):
                        message = str(msg[2])
                    index += 1
                except:
                    continue

            if message is not None:
                try:
                    msg = mbcontext.MB_EasySendMessage("printer%s" % pos_id, TK_PRN_PRINT, FM_PARAM, message)
                except MBException as _:
                    time.sleep(0.5)
                    msg = mbcontext.MB_EasySendMessage("printer%s" % pos_id, TK_PRN_PRINT, FM_PARAM, message)
                finally:
                    if msg.token == TK_SYS_ACK:
                        show_info_message(pos_id, "$OPERATION_SUCCEEDED", msgtype="success")
                    else:
                        show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
        except Exception as _:
            show_info_message(pos_id, "Erro ao imprimir relatório", msgtype="error")


@report_action
def opened_tables_report(pos_id):
    model = get_model(pos_id)
    return print_report(pos_id, model, True, "openedtablesreport", pos_id)


@report_action
def doPrintLogoffReport(pos_id):
    model = get_model(pos_id)
    sessions = []

    period = show_keyboard(pos_id, "$TYPE_DATE", title="", mask="DATE", numpad=True)

    if period in (None, ''):
        return

    conn = None
    try:
        date_input_format = "%Y-%m-%d %H:%M:%S"
        date_output_format = "%d/%m/%Y %H:%M:%S"

        conn = persistence.Driver().open(mbcontext, dbname=str(pos_id))
        conn.transaction_start()

        sql = """SELECT * FROM posctrl.UserSession
                  WHERE BusinessPeriod = '%s'
                  ORDER BY CloseTime DESC
                  """ % period
        cursor = conn.select(sql)

        for row in cursor:
            session_id = row.get_entry("SessionId")
            pos = session_id.split(",")[0].split("=")[1]
            close_time = row.get_entry("CloseTime")
            if close_time is not None:
                open_time = convert_from_utf_to_localtime(
                    datetime.strptime(row.get_entry("OpenTime"), date_input_format)).strftime(date_output_format)
                close_time = convert_from_utf_to_localtime(datetime.strptime(close_time, date_input_format)).strftime(
                    date_output_format)
                operator_name = row.get_entry("OperatorName")
                descr = operator_name + "  " + open_time
                msg = "Loja: %s" \
                      "\nPOS: %s" \
                      "\nNome do operador: %s" \
                      "\nHora de entrada: %s" \
                      "\nHora de saída: %s" % (store_id.zfill(5), pos, operator_name, open_time, close_time)
                sessions.append((session_id, descr, msg))

    except Exception as e:
        sys_log_exception('Exception printing logoff report: {}'.format(e))
        show_info_message(pos_id, "$OPERATION_FAILED", msgtype="error")
        return
    finally:
        if conn:
            conn.close()

    if not sessions:
        show_messagebox(pos_id, "Não há sessões encerradas", title="$ERROR", icon="error", buttons="$OK")
        return

    selected = sysactions.show_text_preview(
        pos_id,
        sessions,
        title='$SELECT_AN_OPTION',
        buttons='$PRINT|$CANCEL',
        defvalue='',
        onthefly=False,
        timeout=120000
    )

    if selected is not None and selected[0] == '0':
        try:
            period = selected[4][7:15]
            userid = selected[2][5:]
            session_id = selected[1] + "," + selected[2] + "," + selected[3] + "," + selected[4]
            session_pos_id = selected[1][4:]
            return print_report(
                pos_id, model, True, "close_operator_report", session_pos_id, period, userid, "False", "0", "logoffuser"
            )
        except Exception as e:
            show_info_message(pos_id, "Erro ao tentar reimprimir Relatório de Fechamento de Operador", msgtype="error")


@report_action
def get_voided_lines_report(pos_id):
    start_date = get_report_date(pos_id, "$TYPE_INITIAL_DATE")
    if start_date is None:
        return

    end_date = get_report_date(pos_id, "$TYPE_FINAL_DATE")
    if end_date is None:
        return

    report_pos = sysactions.show_keyboard(pos_id,
                                          "$TYPE_REPORT_POS",
                                          title="",
                                          defvalue="0",
                                          mask="INTEGER",
                                          numpad=True)
    if report_pos is None:
        return

    operator_id = sysactions.show_keyboard(pos_id,
                                           "$TYPE_OPERATOR_ID",
                                           title="",
                                           defvalue="0",
                                           mask="INTEGER",
                                           numpad=True)
    if operator_id is None:
        return

    model = sysactions.get_model(pos_id)
    return sysactions.print_report(pos_id,
                                   model,
                                   True,
                                   "generate_voided_lines_report",
                                   report_pos,
                                   start_date,
                                   end_date,
                                   False,
                                   operator_id)
