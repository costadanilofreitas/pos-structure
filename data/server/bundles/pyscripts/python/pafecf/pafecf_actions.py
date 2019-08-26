# -*- coding: utf-8 -*-
# Python module responsible to implement mandatory PAF-ECF actions.
# This module should be loaded by the "pyscripts" component
#
# Copyright (C) 2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

# Python standard modules
import os
import sys
import datetime
from xml.etree import cElementTree as etree
# Our modules
import pyscripts
import persistence
import fiscalprinter

import pafecf
from sysactions import action, get_model, translate_message, is_valid_date, \
    check_operator_logged, check_current_order, show_keyboard, get_business_period, \
    show_info_message, show_listbox, get_posot, get_pricelist, change_screen, \
    close_asynch_dialog, show_messagebox, show_confirmation, generate_report, \
    show_ppview, get_podtype, get_operator_session, show_order_preview, \
    show_print_preview, get_posfunction
from systools import sys_log_debug, sys_log_exception
from fiscalprinter import fpcmds, fpreadout
from posot import OrderTakerException
from cpf_functions import CPF
from sysact_bk import validar_cpf, validar_cnpj
from msgbus import TK_SYS_ACK, FM_PARAM, MBException
from bustoken import TK_SAPIENS_GENERATE_ALL_FILES_PER_PERIOD
# Try to import the posactions module, but ignore it if not found
try:
    import posactions
except:
    posactions = {}

# Message-bus context
mbcontext = pyscripts.mbcontext

# Tender types
TENDER_CASH = "0"


msg_data_or_z = "Relatório Parcial por Intervalo de Data ou Redução Z ?"
btns_data_or_z = "Data|Redução Z"
msg_data_or_coo = "Relatório Parcial por Intervalo de Data ou COO ?"
btns_data_or_coo = "Data|COO"


def request_begin_end_periods(posid, model):
    dtFormatInput = translate_message(model, "L10N_DATE_FORMAT_INPUT")
    begin = show_keyboard(posid, "Entre com a data de Início\n[%s]" % (dtFormatInput), mask="DATE", numpad=True)
    if begin is None:
        return None  # Cancelled
    if not is_valid_date(begin):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return None
    end = show_keyboard(posid, "Entre com a data final\n[%s]" % (dtFormatInput), mask="DATE", numpad=True)
    if end is None:
        return  # Cancelled
    if not is_valid_date(end):
        show_info_message(posid, "$INVALID_DATE", msgtype="error")
        return None
    return begin, end


def request_z_interval(posid):
    begin = show_keyboard(posid, "Entre com a primeira redução Z:", mask="INTEGER", numpad=True)
    if begin is None:
        return  # Cancelled
    end = show_keyboard(posid, "Entre com a última redução Z:", mask="INTEGER", numpad=True)
    if end is None:
        return  # Cancelled

    return begin, end

def request_coo_interval(posid):
    begin = show_keyboard(posid, "Entre com o COO inicial:", mask="INTEGER", numpad=True)
    if begin is None:
        return  # Cancelled
    end = show_keyboard(posid, "Entre com o COO final:", mask="INTEGER", numpad=True)
    if end is None:
        return  # Cancelled

    return begin, end


@action
def generateElectronicFiscalFile(posid, serial="", request_date="false", preview="false", show_result="false", *args):
    model = get_model(posid)
    period = get_business_period(model)
    if request_date.lower() == "true":
        periods = request_begin_end_periods(posid, model)
        if not periods:
            return
        period_begin, period_end = periods
    else:
        period_begin = period
        period_end = period
    """ Requisito XXV item 6
    o arquivo gerado deverá ser denominado no formato CCCCCCNNNNNNNNNNNNNNDDMMAAAA.txt, sendo:
    a) “CCCCCC” o Código Nacional de Identificação de ECF relativo ao ECF a que se refere o movimento informado;
    b) “NNNNNNNNNNNNNN” os 14 (quatorze) últimos dígitos do número de fabricação do ECF;
    c) “DDMMAAAA” a data (dia/mês/ano) do movimento informado no caso de arquivo gerado automaticamente após a emissão da Redução Z, ou a data (dia/mês/ano) da geração do arquivo no caso de execução por meio do comando previsto no item 9 do requisito VII.
    """
    try:
        pod_type = get_podtype(model)
        if pod_type == "OT":
            fp = fiscalprinter.fp(1, mbcontext)
            pos_id = 1
        else:
            fp = fiscalprinter.fp(posid, mbcontext)
            pos_id = posid
        # Get the printer serial number if necessary
        if not serial:
            conn = None
            try:
                conn = persistence.Driver().open(mbcontext)
                cursor = conn.select("""
                SELECT DISTINCT FPSerialNo
                FROM (
                    SELECT DISTINCT FPSerialNo FROM fiscalinfo.FiscalPrinters
                    UNION ALL
                    SELECT DISTINCT FPSerialNo FROM fiscalinfo.FiscalOrders WHERE PosId=%(pos_id)s AND Period BETWEEN %(period_begin)s AND %(period_end)s
                    UNION ALL
                    SELECT DISTINCT FPSerialNo FROM fiscalinfo.NonFiscalDocuments WHERE PosId=%(pos_id)s AND Period BETWEEN %(period_begin)s AND %(period_end)s
                    UNION ALL
                    SELECT DISTINCT FPSerialNo FROM fiscalinfo.ZTapes WHERE PosId=%(pos_id)s AND Period BETWEEN %(period_begin)s AND %(period_end)s
                    UNION ALL
                    SELECT DISTINCT FPSerialNo FROM fiscalinfo.ZTapeTotalizers WHERE PosId=%(pos_id)s AND Period BETWEEN %(period_begin)s AND %(period_end)s
                )
                """ % locals())
                if not cursor.rows():
                    show_messagebox(posid, message="Nenhum dado encontrado para este período!", icon="warning")
                    return
            finally:
                if conn:
                    conn.close()
            serials = [row.get_entry(0) for row in cursor]
            serial = serials[0]
        # get encrypted information
        try:
            values = fp.readEncrypted("FiscalOutputPath", "ECF_CodigoNacional")
        except:
            values = "./", "030803"
        if not values:
            show_messagebox(posid, message="Erro consultando dados da impressora", icon="error")
            return
        path, CNIE = values
        if not path.endswith("/") and not path.endswith("\\"):
            path += "/"
        ddmmaaaa = (period[6:8] + period[4:6] + period[:4])
        filename = path + "%06d%14.14s%s.txt" % (int(CNIE), serial[-14:], ddmmaaaa)
        # Format the signed fiscal file data
        fiscal_data = generate_report("fiscalReport", "electronicFiscalFile", pos_id, period_begin, period_end, serial)
        product_data = generate_report("fiscalReport", "pafEcfTableReport", pos_id, period_begin, period_end, *args)

        filters = []
        if request_date.lower() == "true":
            index = show_messagebox(posid, message="Escolha um tipo de relatório:", title="Relatório Gerencial", icon="question", buttons="ESTOQUE TOTAL|ESTOQUE PARCIAL|Cancelar")
            if index in (None, 2):
                return
            parcial = (index == 1)

            if parcial:
                while True:
                    data = show_keyboard(posid, "Digite o código (SKU) ou descrição:", title="ESTOQUE PARCIAL", numpad=False)
                    if not data:
                        break
                    filters.append(data)
        filters = '|'.join(filters)
        inventory_data = generate_report("fiscalReport", "inventoryReport", pos_id, period, filters, serial)
        signed_complete_data = generate_report("signFiscalReport",(product_data or "") + (inventory_data or "") + (fiscal_data or ""))

        try:
            savedpath = fp.saveFile(filename, signed_complete_data)
        except:
            savedpath = os.path.abspath(filename)
            savedfile = file(filename, "w+")
            savedfile.write(signed_complete_data.replace('\r\n', '\n'))
            savedfile.close()
        #if show_result.lower() == "true":
        if sys.platform == "win32":
            savedpath = savedpath.replace("/", "\\")
        show_messagebox(posid, "Arquivo salvo em:\n%s" % savedpath, icon="success", linefeed="\n")
        # if preview.lower() == "true":
        #     is_print = show_print_preview(posid, signed_complete_data, buttons="$PRINT|$CLOSE")
        #     if is_print == 0:
        #         fp.printNonFiscal(signed_complete_data)
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")

@action
def generateEstoqueReport(posid):
    model = get_model(posid)
    period = get_business_period(model)
    if not period:
        return
    data = generate_report("estoque", posid, period)
    show_ppview(posid, data, buttons="$CLOSE")


@action
def pafLeituraX(posid):
    sys_log_debug("Leitura X posid=%s" % posid)
    dlgid = None
    model = get_model(posid)
    pod_function = get_posfunction(model) if get_podtype(model) == "DT" else get_podtype(model)
    if pod_function == "OT":
        show_messagebox(posid, "Função não disponível")
        return

    fp = fiscalprinter.fp(posid, mbcontext)
    try:
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
        fp.printXReport()
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)


@action
def pafLeituraMF(posid):
    sys_log_debug("Leitura MF posid=%s" % posid)
    dlgid = None
    model = get_model(posid)
    pod_function = get_posfunction(model) if get_podtype(model) == "DT" else get_podtype(model)
    if pod_function == "OT":
        show_messagebox(posid, "Função não disponível")
        return

    fp = fiscalprinter.fp(posid, mbcontext)
    try:
        model = get_model(posid)
        index = show_messagebox(posid, "Escolha o tipo:", buttons="Completa|Simplificada|Cancelar", title="Tipo LMF", icon="question")
        if index in (None, 2):
            return
        if index == 0:
            cmd = "LMFC"
        else:
            cmd = "LMFS"
        kind = show_messagebox(posid, msg_data_or_z, buttons=btns_data_or_z, title="", icon="question")
        if kind == 0:  # report by date
            mode = "D"
            period = request_begin_end_periods(posid, model)
            if not period:
                return
            else:
                begin, end = period
        else:  # report by reduction numbers
            mode = "Z"  # by Reduction Z
            interval = request_z_interval(posid)
            if not interval:
                return
            else:
                begin, end = interval

        output_kind = show_messagebox(posid, "Saída do relatório:", buttons="Arquivo|ECF", title="", icon="question")
        if output_kind == 0:  # to file
            # get path to save file
            path = fp.readEncrypted("FiscalOutputPath")
            if not path:
                path = "./"
            file = "%s%s%s.txt" % (path, cmd, "_por_data" if kind == 0 else "_por_z")
        else:
            file = ""
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
        response = fp.genericFiscalCMD(fpcmds.FPRN_MEMORYDUMP, mode, begin, end, "0" if cmd == "LMFC" else "1", file, "00001", "")
        if response and file:
            # Sign the file
            file = response
            report = fp.readFile(file)
            EAD = pafecf.PAF_ECF.get_EAD_signature(report)
            report = "%s%s" % (report, EAD)
            file = fp.saveFile(file, report)
            if sys.platform == "win32":
                file = file.replace("/", "\\")
        if file:
            show_messagebox(posid, "Salvo em: %s" % file, icon="info", linefeed="\n")
        else:
            show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
        return response
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)


@action
def pafArquivo(posid, cmd):
    sys_log_debug("Arquivo %s posid=%s cmd=%s" % (type, posid, cmd))
    model = get_model(posid)
    pod_function = get_posfunction(model) if get_podtype(model) == "DT" else get_podtype(model)
    if pod_function == "OT":
        show_messagebox(posid, "Função não disponível")
        return

    dlgid = None
    fp = fiscalprinter.fp(posid, mbcontext)
    try:
        # get path to save file
        path = fp.readEncrypted("FiscalOutputPath")
        if not path:
            path = "./"
        mode = "D"
        begin = "20010101"
        ecf_serial = fp.readEncrypted("ECF_Serial")
        today = datetime.datetime.now()
        date = today.strftime("%Y%m%d")
        time = today.strftime("%H%M%S")
        file = "%s%s_%s_%s.%s" % (path, ecf_serial, date, time, cmd)
        file_ead = "%s%s_%s_%s.%s.txt" % (path, ecf_serial, date, time, cmd)
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
        response = fp.genericFiscalCMD(fpcmds.FPRN_MEMORYDUMP, mode, begin, date, "1", file, "00001", "4" if cmd == "MF" else "5")
        if response:
            report = fp.readFile("dump.mf" if cmd == "MF" else "dump.mfd")
            file = fp.saveFile(file, report)
            EAD = pafecf.PAF_ECF.get_EAD_signature(report)
            report = "%s" % (EAD)
            fp.saveFile(file_ead, report)
            if sys.platform == "win32":
                file = file.replace("/", "\\")
            show_messagebox(posid, "Salvo em: %s" % file, icon="info", linefeed="\n")
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)


@action
def pafArq1704(posid):
    sys_log_debug("Arquivo %s posid=%s" % (type, posid))
    model = get_model(posid)
    pod_function = get_posfunction(model) if get_podtype(model) == "DT" else get_podtype(model)
    if pod_function == "OT":
        show_messagebox(posid, "Função não disponível")
        return

    dlgid = None
    model = get_model(posid)
    fp = fiscalprinter.fp(posid, mbcontext)
    try:
        index = show_messagebox(posid, "Escolha o tipo:", buttons="MF|MFD|Cancelar", title="Tipo", icon="question")
        if index in (None, 2):
            return
        if index == 0:
            read_type = "MF"
        else:
            read_type = "MFD"
        kind = show_messagebox(posid, msg_data_or_coo, buttons=btns_data_or_coo, title="", icon="question")
        if kind == 0:  # report by date
            mode = "D"
            period = request_begin_end_periods(posid, model)
            if not period:
                return
            else:
                begin, end = period
        else:  # report by reduction numbers
            by_coo_suported = "TRUE"
            val = fp.readOut(fpreadout.FR_PRINTERTYPE).split('\0')
            if len(val) > 3:
                by_coo_suported = val[3].strip()
            if by_coo_suported == "FALSE":
                show_messagebox(posid, "Função não suportada pelo modelo de ECF utilizado", icon="warning", linefeed="\n")
                return
            else:
                mode = "C"  # by COO
                interval = request_coo_interval(posid)
                if not interval:
                    return
                else:
                    begin, end = interval
        # get path to save file
        path = fp.readEncrypted("FiscalOutputPath")
        if not path:
            path = "./"
        ecf_serial = fp.readEncrypted("ECF_Serial")
        today = datetime.datetime.now()
        date = today.strftime("%Y%m%d")
        hour = today.strftime("%H%M%S")
        file = "%s%s%s_%s_%s.txt" % (path, read_type, ecf_serial, date, hour)
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
        response = fp.genericFiscalCMD(fpcmds.FPRN_MEMORYDUMP, mode, begin, end, "1", file, "00001", "6" if read_type == "MF" else "7")
        if response:
            # Sign the file
            file = response
            report = fp.readFile(file)[:-259]
            EAD = pafecf.PAF_ECF.get_EAD_signature(report)
            report = "%s%s" % (report, EAD)
            file = fp.saveFile(file, report)
            if sys.platform == "win32":
                file = file.replace("/", "\\")
            show_messagebox(posid, "Salvo em: %s" % str(file), icon="info", linefeed="\n")
        else:
            show_messagebox(posid, "$FATAL_ERROR", icon="error", linefeed="\n")
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)


@action
def pafEspelhoMFD(posid):
    sys_log_debug("EspelhoMFD posid=%s" % posid)
    model = get_model(posid)
    pod_function = get_posfunction(model) if get_podtype(model) == "DT" else get_podtype(model)
    if pod_function == "OT":
        show_messagebox(posid, "Função não disponível")
        return

    dlgid = None
    model = get_model(posid)
    fp = fiscalprinter.fp(posid, mbcontext)
    try:
        kind = show_messagebox(posid, msg_data_or_coo, buttons=btns_data_or_coo, title="", icon="question")
        if kind == 0:  # report by date
            mode = "D"
            period = request_begin_end_periods(posid, model)
            if not period:
                return
            else:
                begin, end = period
        else:  # report by reduction numbers
            mode = "Z"  # by COO, uses the same mode as Z
            interval = request_coo_interval(posid)
            if not interval:
                return
            else:
                begin, end = interval

        # get path to save file
        path = fp.readEncrypted("FiscalOutputPath")
        if not path:
            path = "./"
        file = "%sEspelhoMFD_%s.txt" % (path, "por_data" if kind == 0 else "por_coo")
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
        response = fp.genericFiscalCMD(fpcmds.FPRN_MEMORYDUMP, mode, begin, end, "1", file, "00001", "1")
        if response and file:
            # Sign the file
            file = response
            report = fp.readFile(file)
            EAD = pafecf.PAF_ECF.get_EAD_signature(report)
            report = "%s%s" % (report, EAD)
            file = fp.saveFile(file, report)
            if sys.platform == "win32":
                file = file.replace("/", "\\")
            show_messagebox(posid, "Salvo em: %s" % file, icon="info", linefeed="\n")
        return response
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)


@action
def pafEnvioFiscoZ(posid, endofday=False):
    if not endofday:
        show_messagebox(posid, "Função ainda não disponível", icon="info", buttons="$OK", linefeed="\n", asynch=False, timeout=1200000)
    else:
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
        try:
            model = get_model(posid)
            date_time = get_business_period(model)
            fiscal_data = generate_report("paf_envio_fisco_reducao_z", posid, date_time)
            if not fiscal_data:
                show_messagebox(posid, message="Erro gerando relatório", icon="error")
                return
            fp = fiscalprinter.fp(posid, mbcontext)
            path = fp.readEncrypted("FiscalOutputPath")
            if not path:
                path = "./"

            filename = "%spafEnvioFiscoZ_%s.xml" % (path, date_time)
            savedpath = fp.saveFile(filename, fiscal_data)
            if sys.platform == "win32":
                savedpath = savedpath.replace("/", "\\")
            show_messagebox(posid, "Salvo em: %s" % savedpath, icon="success", linefeed="\n")
            show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
        except fiscalprinter.FPException, ex:
            show_info_message(posid, str(ex), msgtype="error")
        finally:
            if dlgid:
                close_asynch_dialog(posid, dlgid)


@action
def pafEnvioFiscoEstoque(posid):
    show_messagebox(posid, "Função ainda não disponível", icon="info", buttons="$OK", linefeed="\n", asynch=False, timeout=1200000)
    return
    # dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
    # try:
    #     today = datetime.date.today()
    #     first = today.replace(day=1)
    #     last_month_last_day = first - datetime.timedelta(days=1)
    #     last_month_first_day = last_month_last_day.replace(day=1)
    #    #fiscal_data = generate_report("paf_envio_fisco_estoque", posid, last_month_first_day, last_month_last_day)
    #     fiscal_data = generate_report("paf_envio_fisco_estoque", posid, first, today)
    #     if not fiscal_data:
    #         show_messagebox(posid, message="Erro gerando relatório", icon="error")
    #         return
    #     fp = fiscalprinter.fp(posid, mbcontext)
    #     path = fp.readEncrypted("FiscalOutputPath")
    #     if not path:
    #         path = "./"
    #
    #     filename = "%spafEnvioFiscoEstoque_%s_%s.xml" % (path, str(first).replace('-', ''), str(today).replace('-', ''))
    #     savedpath = fp.saveFile(filename, fiscal_data)
    #     if sys.platform == "win32":
    #         savedpath = savedpath.replace("/", "\\")
    #     show_messagebox(posid, "Salvo em: %s" % savedpath, icon="success", linefeed="\n")
    #     show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
    # except fiscalprinter.FPException, ex:
    #     show_info_message(posid, str(ex), msgtype="error")
    # finally:
    #     if dlgid:
    #         close_asynch_dialog(posid, dlgid)


@action
def pafRegistrosPafEcf(posid):
    sys_log_debug("Registros PAF-ECF posid=%s" % posid)
    generateElectronicFiscalFile(posid, request_date="true", show_result="true", preview="true")


@action
def pafParametrosConfig(posid):
    dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
    try:
        date_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        fiscal_data = generate_report("paf_parametros_de_config", posid, date_time)
        if not fiscal_data:
            show_messagebox(posid, message="Erro gerando relatório", icon="error")
            return
        fp = fiscalprinter.fp(posid, mbcontext)
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
        is_print = show_print_preview(posid, fiscal_data, buttons="$PRINT|$CLOSE")
        if is_print == 0:
            fp.printNonFiscal(fiscal_data)
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)

@action
def pafVendasIdentCpfCnpj(posid, *args):
    cpf_cnpj = ''

    month = show_keyboard(posid, "Digite o mês: [mm]", mask="INTEGER", numpad=True)
    if month is None or len(month) < 2:
        show_messagebox(posid, "Erro mês inválido:", icon="question")
        return

    year = show_keyboard(posid, "Digite o ano: [yyyy]", mask="INTEGER", numpad=True)
    if year is None or len(year) < 4:
        show_messagebox(posid, "Erro ano inválido:", icon="question")
        return

    if show_messagebox(posid, "Deseja especificar um CPF/CNPJ?", title="Escolha uma opção", buttons="Sim|Não", icon="question") == 0:

        if show_messagebox(posid, "", buttons="CPF|CNPJ", icon="question") == 0:
            cpf_cnpj = show_keyboard(posid, "Digite o CPF (somente números)", mask="###########", numpad=True)
            if not validar_cpf(cpf_cnpj):
                show_messagebox(posid, "Erro CPF inválido:", icon="question")
                return
        else:
            cpf_cnpj = show_keyboard(posid, "Digite o CNPJ (somente números)", mask="##############", numpad=True)
            if not validar_cnpj(cpf_cnpj):
                show_messagebox(posid, "Erro CNPJ inválido:", icon="question")
                return

    model = get_model(posid)
    pod_type = get_podtype(model)
    if pod_type == "OT":
        fp = fiscalprinter.fp(1, mbcontext)
        pos_id = 1
    else:
        fp = fiscalprinter.fp(posid, mbcontext)
        pos_id = posid

    try:
        # get path to save file
        try:
            path = fp.readEncrypted("FiscalOutputPath")
        except:
            path = "./"
        if not path:
            path = "./"

        period = '%s-%s' % (month, year)
        report = generate_report("signedFiscalReport", "ordersCpfCnpjReport", pos_id, period, cpf_cnpj)
        filename = "%svendIdentCPF_CNPJ.txt" % path
        try:
            savedpath = fp.saveFile(filename, report)
        except:
            file = open(filename, "w+")
            file.write(report.replace('\r\n', '\n'))
            file.close()
            savedpath = os.path.abspath(filename)
        if sys.platform == "win32":
            savedpath = savedpath.replace("/", "\\")
        show_messagebox(posid, "Salvo em: %s" % savedpath, icon="success", linefeed="\n")
        # is_print = show_print_preview(posid, report, buttons="$PRINT|$CLOSE")
        # if is_print == 0:
        #     fp.printNonFiscal(report)
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")


@action
def fiscalCMD(posid, cmd, *args):
    model = get_model(posid)
    period = get_business_period(model)
    sys_log_debug("fiscalCMD posid=%s cmd=%s" % (posid, cmd))

    model = get_model(posid)
    pod_type = get_podtype(model)
    if pod_type == "OT":
        fp = fiscalprinter.fp(1, mbcontext)
        pos_id = 1
    else:
        fp = fiscalprinter.fp(posid, mbcontext)
        pos_id = posid

    try:
        # get path to save file
        try:
            path = fp.readEncrypted("FiscalOutputPath")
        except:
            path = "./"
        if not path:
            path = "./"
        # Asks the type of LMF, LMFC or LMFS
        if cmd == "LMF":
            index = show_messagebox(posid, "Escolha o tipo:", buttons="Completo|Simplificado|Cancelar", title="Tipo LMF", icon="question")
            if index in (None, 2):
                return
            if index == 0:
                cmd = "LMFC"
            else:
                cmd = "LMFS"

        if cmd == "LMFC":
            # When the LMFC button is pressed, there must be an option to generate a "COTEPE/ICMS 17/04" (from MF) file
            # This file is actually the same as the "Arq.MF" button
            index = show_messagebox(posid, "Escolha o formato:", buttons="LMFC|COTEPE/ICMS 17/04|Cancelar", title="Formato LMFC", icon="question")
            if index in (None, 2):
                return
            if index == 1:
                cmd = "Arq.MF"

        if cmd == "LX":
            return fp.printXReport()
        elif cmd in ("LMFC", "LMFS", "ESPELHOMFD", "Arq.MFD", "Arq.MF"):
            file = ""
            # choose period
            mode = "D"  # default mode: by Date
            msg_tipo_intervalo = "Relatório Parcial por Intervalo de Data ou Redução Z ?"
            msg_first_z = "Entre com a primeira redução Z:"
            msg_last_z = "Entre com a última redução Z:"
            btns_tipo_intervalo = "Data|Redução Z"
            if cmd in ("ESPELHOMFD", "Arq.MFD"):
                msg_tipo_intervalo = "Relatório Parcial por Intervalo de Data ou COO ?"
                btns_tipo_intervalo = "Data|COO"
                msg_first_z = "Entre com o COO inicial:"
                msg_last_z = "Entre com o COO final:"
            kind = show_messagebox(posid, msg_tipo_intervalo, buttons=btns_tipo_intervalo, title="", icon="question")
            dtFormatInput = translate_message(model, "L10N_DATE_FORMAT_INPUT")
            if kind == 0:  # report by date
                begin = show_keyboard(posid, "Entre com a data de Início\n[%s]" % (dtFormatInput), mask="DATE", numpad=True)
                if begin is None:
                    return  # Cancelled
                if not is_valid_date(begin):
                    show_info_message(posid, "$INVALID_DATE", msgtype="error")
                    return
                end = show_keyboard(posid, "Entre com a data final\n[%s]" % (dtFormatInput), mask="DATE", numpad=True)
                if end is None:
                    return  # Cancelled
                if not is_valid_date(end):
                    show_info_message(posid, "$INVALID_DATE", msgtype="error")
                    return
            else:    # report by reduction numbers
                mode = "Z"  # by Reduction Z
                begin = show_keyboard(posid, msg_first_z, mask="INTEGER", numpad=True)
                if begin is None:
                    return  # Cancelled
                end = show_keyboard(posid, msg_last_z, mask="INTEGER", numpad=True)
                if end is None:
                    return  # Cancelled
            if cmd == "LMFC" or cmd == "LMFS":
                kind = show_messagebox(posid, "Saída do relatório:", buttons="Arquivo|ECF", title="", icon="question")
                if kind == 0:  # to file
                    file = "%s%s.txt" % (path, cmd)
                type = ""
            elif cmd == "ESPELHOMFD":
                type = "1"
                file = "%s%s.txt" % (path, "EspelhoMFD")
            elif cmd == "Arq.MFD":
                # Ato COTEPE/ICMS 17/04 (from MFD)
                type = "2"
                file = "%s%s.txt" % (path, "ArqMFD")
            elif cmd == "Arq.MF":
                # Ato COTEPE/ICMS 17/04 (from MF)
                type = "3"
                file = "%s%s.txt" % (path, "ArqMF")
            else:
                return
            response = fp.genericFiscalCMD(fpcmds.FPRN_MEMORYDUMP, mode, begin, end, "0" if cmd == "LMFC" else "1", file, "00001", type)
            if response and file:
                # Sign the file
                file = response
                report = fp.readFile(file)
                EAD = pafecf.PAF_ECF.get_EAD_signature(report)
                report = "%s%s" % (report, EAD)
                file = fp.saveFile(file, report)
                if sys.platform == "win32":
                    file = file.replace("/", "\\")
                show_messagebox(posid, "Salvo em: %s" % file, icon="info", linefeed="\n")
            return response

        elif cmd == "Tab.Prod":
            # Generate the signed report
            report = generate_report("signedFiscalReport", "merchandiseReport", pos_id, period, *args)
            filename = "%stabprod.txt" % path
            try:
                savedpath = fp.saveFile(filename, report)
            except:
                file = open(filename, "w+")
                file.write(report.replace('\r\n', '\n'))
                file.close()
                savedpath = os.path.abspath(filename)
            if sys.platform == "win32":
                savedpath = savedpath.replace("/", "\\")
            show_messagebox(posid, "Salvo em: %s" % savedpath, icon="success", linefeed="\n")
            # try:
            #     is_print = show_print_preview(posid, report, buttons="$PRINT|$CLOSE")
            #     if is_print == 0:
            #         fp.printNonFiscal(report)
            # except fiscalprinter.FPException, ex:
            #     show_info_message(posid, str(ex), msgtype="error")
        else:
            sys_log_debug("Comando [%s] Não Implementado " % (cmd))
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")


@action
def pafIdentificacaoPafEcf(posid):
    model = get_model(posid)
    pod_function = get_posfunction(model) if get_podtype(model) == "DT" else get_podtype(model)
    if pod_function == "OT":
        show_messagebox(posid, "Função não disponível")
        return
    dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
    try:
        fiscal_data = generate_report("identificacaoDoPAF_ECF", posid)
        if not fiscal_data:
            show_messagebox(posid, message="Erro gerando relatório", icon="error")
            return
        fp = fiscalprinter.fp(posid, mbcontext)
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
        is_print = show_print_preview(posid, fiscal_data, buttons="$PRINT|$CLOSE")
        if is_print == 0:
            fp.printNonFiscal(fiscal_data)
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)


@action
def generatePafParametersReport(posid):
    dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
    fiscal_data = generate_report("paf_parametros_de_configuracao", posid)
    if not fiscal_data:
        show_messagebox(posid, message="Erro gerando relatório", icon="error")
        return
    fp = fiscalprinter.fp(posid, mbcontext)
    try:
        fp.printNonFiscal(fiscal_data)
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)


@action
def generatePafInventoryReport(posid, show_result="true", preview="false"):
    model = get_model(posid)
    period = get_business_period(model)
    fp = fiscalprinter.fp(posid, mbcontext)
    index = show_messagebox(posid, message="Escolha um tipo de relatório:", title="Relatório Gerencial", icon="question", buttons="ESTOQUE TOTAL|ESTOQUE PARCIAL|Cancelar")
    if index in (None, 2):
        return
    parcial = (index == 1)
    try:
        output = fp.readEncrypted("FiscalOutputPath")
        # conn = persistence.Driver().open(mbcontext)
        filters = []
        if parcial:
            while True:
                data = show_keyboard(posid, "Digite o código (SKU) ou descrição:", title="ESTOQUE PARCIAL", numpad=False)
                if not data:
                    break
                filters.append(data)
        filters = '|'.join(filters)
        fiscal_data = generate_report("signedFiscalReport", "inventoryReport", posid, period, filters)
        filename = "estoque.txt"
        savedpath = fp.saveFile(output + "/" + filename, fiscal_data)
        if show_result.lower() == "true":
            if sys.platform == "win32":
                savedpath = savedpath.replace("/", "\\")
            show_messagebox(posid, "Arquivo salvo em: %s" % savedpath, icon="success", linefeed="\n")
        if preview.lower() == "true":
            show_ppview(posid, fiscal_data, buttons="$CLOSE")
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")


@action
def pafTabIndiceTecnicoProducao(posid):
    model = get_model(posid)
    pod_type = get_podtype(model)
    if pod_type == "OT":
        fp = fiscalprinter.fp(1, mbcontext)
    else:
        fp = fiscalprinter.fp(posid, mbcontext)
    try:
        output = fp.readEncrypted("FiscalOutputPath")
    except:
        output = "./"
    fiscal_data = generate_report("signedFiscalReport", "paf_indice_tecnico")
    filename = "producao.txt"
    try:
        savedpath = fp.saveFile(os.path.join(output, filename), fiscal_data)
    except:
        savedfile = open(output+filename, "w+")
        savedpath = os.path.abspath(output+filename)
        savedfile.write(fiscal_data.replace('\r\n', '\n'))
        savedfile.close()
    if sys.platform == "win32":
        savedpath = savedpath.replace("/", "\\")
    show_messagebox(posid, "Arquivo salvo em: %s" % savedpath, icon="success", linefeed="\n")
    # is_print = show_print_preview(posid, fiscal_data, buttons="$PRINT|$CLOSE")
    # if is_print == 0:
    #     fp.printNonFiscal(fiscal_data)


@action
def generatePafVendasDoPeriodo(posid, show_result="true", preview="false"):
    model = get_model(posid)
    index = show_messagebox(posid, message="Selecione uma opção:", icon="question", buttons="Sintegra|Convênio 57/95|COTEPE/ICMS 09/08|Cancelar")
    if index in (3, None):
        return
    periods = request_begin_end_periods(posid, model)
    if not periods:
        return
    period_begin, period_end = periods
    fp = fiscalprinter.fp(posid, mbcontext)
    try:
        if index == 0:
            # Sintegra
            fiscal_data = generate_report("paf_sintegra", posid, period_begin, period_end)
            filename = "sintegra.txt"
        elif index == 1:
            # Convênio 57/95
            laudo = fp.readEncrypted("PAF_CertNumber")
            ddmmaahhmmss = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
            fiscal_data = generate_report("signedFiscalReport", "paf_sintegra", posid, period_begin, period_end)
            filename = "%s%s.txt" % (laudo, ddmmaahhmmss)
        elif index == 2:
            # COTEPE/ICMS 09/08
            laudo = fp.readEncrypted("PAF_CertNumber")
            ddmmaahhmmss = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
            fiscal_data = generate_report("signedFiscalReport", "paf_sped", posid, period_begin, period_end)
            filename = "%s%s.txt" % (laudo, ddmmaahhmmss)
        output = fp.readEncrypted("FiscalOutputPath")
        savedpath = fp.saveFile(output + "/" + filename, fiscal_data)
        if show_result.lower() == "true":
            if sys.platform == "win32":
                savedpath = savedpath.replace("/", "\\")
            show_messagebox(posid, "Arquivo salvo em: %s" % savedpath, icon="success", linefeed="\n")
        if preview.lower() == "true":
            show_ppview(posid, fiscal_data, buttons="$CLOSE")
    except fiscalprinter.FPException, ex:
        show_info_message(posid, str(ex), msgtype="error")


@action
def notaManual(posid, *args):
    model = get_model(posid)
    check_operator_logged(posid, model=model)
    check_current_order(posid, model=model, need_order=False)
    posot = get_posot(model)
    # podtype = str(get_podtype(model))
    # session = get_operator_session(model)
    try:
        dtFormatInput = translate_message(model, "L10N_DATE_FORMAT_INPUT")
        data = show_keyboard(posid, "Data de emissão da nota\n[%s]" % (dtFormatInput), title="NOTA FISCAL", mask="DATE", numpad=True)
        if data is None:
            return None  # Cancelled
        if not is_valid_date(data):
            show_info_message(posid, "$INVALID_DATE", msgtype="error")
            return None
        numero = show_keyboard(posid, "Digite o número da nota:", title="NOTA FISCAL", mask="INTEGER", numpad=True)
        if numero is None:
            return None  # Cancelled
        serie = show_keyboard(posid, "Digite a série (1 a 3 dígitos):", title="NOTA FISCAL", mask="/^.{1,3}$/", numpad=False)
        if serie is None:
            return None  # Cancelled
        subserie = show_keyboard(posid, "Digite a sub-série (1 ou 2 dígitos):", title="NOTA FISCAL", mask="/^.{1,2}$/", numpad=False)
        if subserie is None:
            return None  # Cancelled
        serie = serie.replace("|", "")
        subserie = subserie.replace("|", "")
        # CPF
        cpf_formatted = None
        # cpf_message = "Digite o CPF do cliente (somente números)"
        while True:
            cpfno = show_keyboard(posid, "Digite o CPF do cliente (somente números)", title="NOTA FISCAL", mask="###########", numpad=True)
            if cpfno is None:
                cpf_formatted = ""
                break
            cpf_formatted = CPF(cpfno)
            if cpf_formatted.isValid():
                break
            # cpf_message = "CPF inválido. Digite novamente:"
            continue
        posot.additionalInfo = "NOTA_MANUAL_DATA=%s|NOTA_MANUAL_NUMERO=%s|NOTA_MANUAL_SERIE=%s|NOTA_MANUAL_SUBSERIE=%s|CPF=%s" % (data, numero, serie, subserie, cpf_formatted)
        posot.createOrder(posid, pricelist=get_pricelist(model), orderSubType="NONFISCAL")
        show_info_message(posid, "Entre com os items da nota", msgtype="success", timeout=-1)
        change_screen(posid, "main")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")


@action
def doMergeOrders(posid, screenNumber="", *args):
    model = get_model(posid)
    check_operator_logged(posid, model=model)
    check_current_order(posid, model=model, need_order=False)
    posot = get_posot(model)
    podtype = str(get_podtype(model))
    session = get_operator_session(model)
    dlgid = 0
    try:
        # Lists all stored orders for our POD type
        orders = posot.listOrders(state="STORED", podtype=podtype)
        if not orders:
            show_info_message(posid, "$THERE_ARE_NO_STORED_ORDERS", msgtype="warning")
            return
        if len(orders) < 2:
            show_info_message(posid, "$TWO_STORED_ORDERS_REQUIRED", msgtype="warning")
            return
        order_period = orders[0]["businessPeriod"]
        bus_period = get_business_period(model)
        order_period_fmt = "%02d/%02d/%04d" % (int(order_period[4:6]), int(order_period[6:8]), int(order_period[:4]))
        bus_period_fmt = "%02d/%02d/%04d" % (int(bus_period[4:6]), int(bus_period[6:8]), int(bus_period[:4]))
        if order_period != bus_period:
            if not show_confirmation(posid, message="$RECALL_DIFERENT_BUSINESS_DAY|%s|%s" % (order_period_fmt, bus_period_fmt)):
                return
        # Joins all order ids on a pipe-separated string (E.g.: "30|35|36")
        order_ids = "|".join([order["orderId"] for order in orders])
        xml = etree.XML(posot.orderPicture(orderid=order_ids))
        # Now we have the full order picture of each order
        orders = xml.findall("Order")
        orders.sort(lambda a, b: int(a.get("orderId", "-1")) - int(b.get("orderId", "-1")))

        def build_preview(orders):
            preview_data = []
            index = 0
            for order in orders:
                order_posid = int(order.get("originatorId")[3:])
                descr = "POS#%s ID: %s" % (order_posid, order.get("orderId"),)
                preview_data.append((index, descr, order))
                index += 1
            return preview_data
        preview_data = build_preview(orders)
        merge_orders = []
        while orders:
            selected = show_order_preview(posid, preview_data, title="$SELECT_THE_ORDER_TO_MERGE")
            if (selected is None) or (selected[0] == "1"):
                return  # Timeout, or the user cancelled
            index = int(selected[1])
            merge_orders.append(orders[index])
            del orders[index]
            preview_data = build_preview(orders)
            if not orders:
                break
            if (len(merge_orders) >= 2) and not show_confirmation(posid, message="$DO_YOU_WANT_TO_MERGE_ANOTHER"):
                break
        # We now have all the information required to merge the orders... lets begin
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", buttons="", asynch=True, timeout=120000)
        for order in merge_orders:
            orderid = order.get("orderId")
            posot.updateOrderProperties(orderid=orderid, orderSubType=" ")
            posot.recallOrder(posid, orderid, session)
            posot.doTotal(posid)
            posot.doTender(posid, TENDER_CASH, "")
            posot.voidOrder(posid, lastpaidorder=True)
        # Start a new, fresh order
        pricelist = get_pricelist(model)
        close_asynch_dialog(posid, dlgid)
        dlgid = None
        # TODO - Check how to do this right.. perhaps "check_new_order" should be moved to here
        posactions.check_new_order(posid, model, posot, checkmulti=False, forcefunction="OT")
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", buttons="", asynch=True, timeout=120000)
        posot.createOrder(posid, pricelist=pricelist)
        for order in merge_orders:
            lines = [line for line in order.findall("SaleLine") if line.get("level") == "0"]
            for line in lines:
                itemid = "%s.%s" % (line.get("itemId"), line.get("partCode"))
                qty = line.get("qty")
                posot.doSale(posid, itemid, pricelist, qty)
        if screenNumber:
            posot.doTotal(int(posid))
            change_screen(posid, screenNumber)  # Show tender screen
        show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
    except OrderTakerException, e:
        show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="critical")
    finally:
        close_asynch_dialog(posid, dlgid)


@action
def changePrinterDST(posid, *args):
    # model = get_model(posid)
    try:
        fp = fiscalprinter.fp(posid, mbcontext)
        # Check the current printer DST status
        enabled = fp.isDSTenabled()
        current = "LIGADO" if enabled else "DESLIGADO"
        action = "DESLIGAR" if enabled else "LIGAR"
        buttons = "%s|Cancelar" % (action)
        msg = "O horário de verão está %s na impressora fiscal.\\\\Deseja %s o horário de verão?" % (current, action)
        if not show_confirmation(posid, message=msg, buttons=buttons):
            return
        # Change the status
        enabled = (not enabled)
        fp.setDST(enabled)
        action = "ligado" if enabled else "desligado"
        msg = "Horário de verão %s com sucesso!" % (action)
        show_info_message(posid, msg, msgtype="success")
    except fiscalprinter.FPException, ex:
        msg = " NÃO FOI POSSÍVEL ALTERAR O HORÁRIO DE VERÃO NA IMPRESSORA!\n"
        msg += "   Retorno da impressora: %s\n" % (str(ex))
        msg += "\n"
        msg += "   Para realizar esta operação, verifique que:\n"
        msg += "    1. O dia está fechado na impressora\n"
        msg += "    2. Não foi emitido nenhum documento na\n"
        msg += "       impressora após a redução Z\n"
        msg += "    3. Ao DESLIGAR o horário de verão, você\n"
        msg += "       aguardou pelo menos uma hora antes de\n"
        msg += "       executar esta operação\n"
        show_print_preview(posid, msg, title="Erro ao trocar o horário de verão", buttons="$CLOSE")


@action
def geraArquivosSapiens(posid):
    model = get_model(posid)
    period = request_begin_end_periods(posid, model)
    if not period:
        return
    else:
        begin, end = period

    sys_log_debug("[geraArquivosSapiens] Sending msg to Sapiens comp, params: {} {}".format(begin, end))
    msg = None
    dlgid = None
    try:
        dlgid = show_messagebox(posid, "$PLEASE_WAIT", icon="info", buttons="", linefeed="\n", asynch=True, timeout=1200000)
        msg = mbcontext.MB_EasySendMessage("SapiensUploader", TK_SAPIENS_GENERATE_ALL_FILES_PER_PERIOD, format=FM_PARAM, data='{}|{}'.format(begin, end))
    except Exception as ex:
        show_info_message(posid, str(ex), msgtype="error")
        sys_log_exception('[geraArquivosSapiens] Exception: {}'.format(ex))
    finally:
        if dlgid:
            close_asynch_dialog(posid, dlgid)

        if msg is not None:
            sys_log_debug("[geraArquivosSapiens] msg.token: {}, TK_SYS_ACK: {}".format(msg.token, TK_SYS_ACK))
            if msg.token == TK_SYS_ACK:
                show_info_message(posid, "$OPERATION_SUCCEEDED", msgtype="success")
            else:
                show_info_message(posid, "$OPERATION_FAILED", msgtype="error")
        else:
            show_info_message(posid, "$OPERATION_FAILED", msgtype="error")


@action
def doFixPaf(posid, full_synch="", *args):
    # model = get_model(posid)
    try:
        fp = fiscalprinter.fp(posid, mbcontext)
        # Check the current printer DST status
        printer_gt = fp.readOut(fpreadout.FR_GT).strip()
        fp.writeEncrypted("RW_GT", printer_gt)

        if full_synch.lower() == "true":
            prn_serial = fp.readOut(fpreadout.FR_FPSERIALNUMBER).strip()
            fp.writeEncrypted("ECF_Serial", prn_serial)

        msg = "PAF regerado com sucesso!"
        show_info_message(posid, msg, msgtype="success")
    except fiscalprinter.FPException, ex:
        msg = " NÃO FOI POSSÍVEL REGERAR PAF!\n"
        msg += "   Retorno da impressora: %s\n" % (str(ex))
        msg += "\n"
        show_messagebox(posid, msg, title="$ERROR")
    except MBException as _:
        show_messagebox(posid, " Não foi possível comunicar com a impressora!\n", title="$ERROR")
    except:
        show_messagebox(posid, " Não foi possível regerar PAF!\n", title="$ERROR")
