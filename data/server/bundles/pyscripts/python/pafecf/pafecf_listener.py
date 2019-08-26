# -*- coding: utf-8 -*-
# Python module responsible to listen to POS events and perform fiscal-related functions.
# This module should be loaded by the "pyscripts" component
#
# Copyright (C) 2011 MWneo Corporation
#
# $Id$
# $Revision$
# $Date$
# $Author$

# Python standard modules
import sys
import os
import base64
import threading
import decimal
import hashlib
import datetime
import time
import calendar
from xml.etree import cElementTree as etree
from decimal import Decimal as D
# Our modules
import pyscripts
import sysactions
import persistence
import logging
import pafecf_actions
from systools import sys_log_info, sys_log_warning, sys_log_debug, sys_log_exception
from msgbus import TK_POS_GETSTATE, TK_SYS_ACK, TK_SYS_NAK, FM_PARAM, TK_EVT_EVENT, TK_FISCAL_CMD
from syserrors import SE_FPERROR
from sysactions import get_storewide_config, get_model, get_podtype, get_posfunction, has_operator_opened
from fiscalprinter import fpcmds, fpreadout, fp, FPException, fpstatus
from posot import OrderTaker, OrderTakerException
from pafecf import PAF_ECF
from helper import config_logger, PosUtil

from bustoken import TK_FISCALWRAPPER_GET_NF_TYPE, TK_FISCALWRAPPER_GET_IBPT_TAX

# Try to import the posactions module, but ignore it if not found
try:
    import posactions
except:
    posactions = {}

# Message-bus context
mbcontext = pyscripts.mbcontext
# Global set of "already-verified" fiscal printers
verified_printers = set()
# We keep this as a global variable since it is read BEFORE the day-close, but only used AFTER it
global_DGT = {}
# Unidade da federacao
UF = "SP"

verify_gt = True
verify_time = True
verify_printer_id = True

d = None

#
# Constants
#
TENDER_CASH = "0"

# Transaction statements - used to disable/enable the "manual modification detection" triggers
# before we change anything in the fiscalinfo database
BEGIN_TRANSACTION = ["BEGIN TRANSACTION", "UPDATE fiscalinfo.FiscalDEnabled SET Enabled=0"]
COMMIT_TRANSACTION = ["UPDATE fiscalinfo.FiscalDEnabled SET Enabled=1", "COMMIT TRANSACTION"]

config_logger(os.environ["LOADERCFG"], 'PAFListener')
logger = logging.getLogger("PAFListener")


def _get_additional_info(order, info, additional_info=""):
    info += "="
    if order:
        additional_info = order.findtext("AdditionalInfo")
    l = (additional_info or "").split('|')
    for item in l:
        if item.startswith(info):
            return item[len(info):].encode("UTF-8")
    return ""


def update_inventory(order, posid):
    """Removes sold items from the inventory"""
    state = order.get("state")
    if state != "PAID":
        return
    conn = None
    for i in xrange(0, 3, 1):
        try:
            conn = persistence.Driver().open(mbcontext, dbname=str(posid))
            queries = []
            insumos = []
            for row in conn.select("SELECT SKU,ProductCode,Qty FROM fiscalinfo.Insumos"):
                sku, pcode, qty = map(row.get_entry, ("SKU", "ProductCode", "Qty"))
                insumos.append([sku, pcode, qty])
            lines = order.findall("SaleLine")
            for line in lines:
                pcode = line.get("partCode")
                qty = line.get("qty")
                if not float(qty):
                    continue
                queries.append("UPDATE fiscalinfo.Estoque SET Qty=tdsub(Qty,tdmul('%s','%s')) WHERE SKU=%s" % (qty, 1, pcode))
                for insumo in insumos:
                    if insumo[1] == pcode:
                        sql = "UPDATE fiscalinfo.Estoque SET Qty=tdsub(Qty,tdmul('%s','%s')) WHERE SKU=%s" % (qty, insumo[2], insumo[0])
                        queries.append(sql)
            if not queries:
                return
            queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
            conn.query("\0".join(queries))
            break
        except:
            logger.exception("Erro atualizando estoque. Tentativa=%d" % (i))
            sys_log_exception("Erro atualizando estoque. Tentativa=%d" % (i))
            if conn:
                conn.query('''ROLLBACK TRANSACTION;''')
        finally:
            if conn:
                conn.close()


def handle_nota_manual(posid, order, orderxml):
    try:
        state = order.get("state")
        if state != "PAID":
            return

        date = _get_additional_info(order, "NOTA_MANUAL_DATA")
        number = _get_additional_info(order, "NOTA_MANUAL_NUMERO")
        serie = _get_additional_info(order, "NOTA_MANUAL_SERIE")
        subserie = _get_additional_info(order, "NOTA_MANUAL_SUBSERIE")
        CPF = _get_additional_info(order, "CPF")
        period = order.get("businessPeriod")

        conn = None
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))

                queries = []
                # Store information on fiscal database
                queries.append("INSERT INTO fiscalinfo.NotasManuais(PosId,Period,OrderId,Data,Numero,Serie,Subserie,Cpf) VALUES(%d,%d,%d,%d,%d,'%s','%s','%s')" % (
                    int(posid), int(period), int(order.get("orderId")), int(date), int(number), conn.escape(serie), conn.escape(subserie), conn.escape(CPF)
                ))
                queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                conn.query("\0".join(queries))
                break
            except:
                logger.exception("Erro inserindo nota manual. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro inserindo nota manual. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                if conn:
                    conn.close()
    except:
        logger.exception("Error on [handle_nota_manual]")
        sysactions.show_messagebox(posid, "Erro armazenando dados fiscais.\\\\Por favor chame o suporte.", icon="error")


def handle_nfe(posid, order, orderxml):
    try:
        state = order.get("state")
        if state != "PAID":
            return

        conn = None
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))

                def quote(s):
                    if not s:
                        return "NULL"
                    return "'%s'" % (conn.escape(s))
                nfe = {}
                nfe["posid"] = int(posid)
                nfe["period"] = int(order.get("businessPeriod"))
                nfe["order_id"] = int(order.get("orderId"))
                orderinfo = order.findtext("AdditionalInfo")
                nfe["nfe_id"] = quote(_get_additional_info(None, "NFE_ID", orderinfo))
                nfe["nfe_number"] = int(_get_additional_info(None, "NFE_NUMBER", orderinfo))
                nfe["nfe_code"] = int(_get_additional_info(None, "NFE_CODE", orderinfo))
                nfe["nfe_ambiente"] = quote(_get_additional_info(None, "NFE_AMBIENTE", orderinfo))
                nfe["dest_CNPJ"] = quote(_get_additional_info(None, "NFE_CNPJ", orderinfo))
                nfe["dest_CPF"] = quote(_get_additional_info(None, "NFE_CPF", orderinfo))
                nfe["dest_nome"] = quote(_get_additional_info(None, "NFE_NOME", orderinfo))
                nfe["dest_logradouro"] = quote(_get_additional_info(None, "NFE_LOGRADOURO", orderinfo))
                nfe["dest_numeroendereco"] = quote(_get_additional_info(None, "NFE_NUMERO_END", orderinfo))
                nfe["dest_complemento"] = quote(_get_additional_info(None, "NFE_COMPLEMENTO", orderinfo))
                nfe["dest_bairro"] = quote(_get_additional_info(None, "NFE_BAIRRO", orderinfo))
                nfe["dest_municipio"] = quote(_get_additional_info(None, "NFE_MUNICIPIO", orderinfo))
                nfe["dest_munibge"] = int(_get_additional_info(None, "NFE_MUNICIPIO_IBGE", orderinfo))
                nfe["dest_uf"] = quote(_get_additional_info(None, "NFE_UF", orderinfo))

                queries = []
                # Store information on fiscal database
                queries.append("""
                INSERT INTO
                    fiscalinfo.NFe(PosId,Period,OrderId,NfeId,Number,Code,Ambiente,DestCPF,DestCNPJ,DestNome,DesfUF,DestMunicipio,DestMunIBGE,DestLogradouro,DestNumeroEnd,DestComplemento,DestBairro)
                VALUES(
                    %(posid)d,%(period)d,%(order_id)d,%(nfe_id)s,%(nfe_number)d,%(nfe_code)d,%(nfe_ambiente)s,
                    %(dest_CPF)s,%(dest_CNPJ)s,%(dest_nome)s,%(dest_uf)s,%(dest_municipio)s,%(dest_munibge)d,
                    %(dest_logradouro)s,%(dest_numeroendereco)s,%(dest_complemento)s,%(dest_bairro)s
                )""" % nfe)
                queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                conn.query("\0".join(queries))
                break
            except:
                logger.exception("Erro inserindo dados da NFe. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro inserindo dados da NFe. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                if conn:
                    conn.close()
    except:
        logger.exception("Error on [handle_nfe]")
        sysactions.show_messagebox(posid, "Erro armazenando dados fiscais.\\\\Por favor chame o suporte.", icon="error")


def check_auto_memory_dump(prn, serial):
    conn = None
    for i in xrange(0, 3, 1):
        try:
            conn = persistence.Driver().open(mbcontext)
            cur = conn.select("SELECT Period FROM fiscalinfo.ZTapes WHERE FPSerialNo='%s' ORDER BY Period LIMIT 2" % conn.escape(serial))
            if cur.rows() <= 0:
                sys_log_info("[PAF] No known Z-Tapes - bypassing auto memory dump")
                return
            elif cur.rows() == 1:
                this_z = cur.get_row(0).get_entry(0)
                this_z_day = int(this_z[:2])
                this_z_month = int(this_z[4:6])
                if this_z_day != 1:
                    sys_log_info("[PAF] First known Z-Tape and not day 01 - bypassing auto memory dump")
                    return
            elif cur.rows() == 2:
                previous_z = str(cur.get_row(0).get_entry(0))
                previous_z_month = int(previous_z[4:6])
                this_z = str(cur.get_row(1).get_entry(0))
                this_z_month = int(this_z[4:6])
                if this_z_month == previous_z_month:
                    return  # Nothing to do
            # Generate the auto memory dump (first Z-Tape of the month)
            printer_month = int(this_z[4:6])
            printer_year = int(this_z[2:4])
            # Check for which month/year we need to generate the automatic memory dump
            if printer_month == 1:
                dump_month = 12
                dump_year = (printer_year - 1)
            else:
                dump_month = (printer_month - 1)
                dump_year = printer_year

            dump_year = dump_year + 2000
            dump_lastday = calendar.monthrange(dump_year, dump_month)[1]
            period_begin = datetime.datetime(dump_year, dump_month, 1).strftime("%Y%m%d")
            period_end = datetime.datetime(dump_year, dump_month, dump_lastday).strftime("%Y%m%d")
            sys_log_info("[PAF] Generating auto memory dump for the given dates: [%s] to [%s]" % (period_begin, period_end))
            prn.printMFD(period_begin, period_end)
            break
        except:
            logger.exception("Erro obtendo informacoes da reducao Z. Tentativa=%d" % i)
        finally:
            if conn:
                conn.close()


def handle_neworder(posid, xml):
    """Stores FP data after an order has been created on the fiscal printer """
    logger.debug("handle_neworder - START")

    try:
        xml = etree.XML(xml)
        cmdbuf = base64.b64decode(xml.find("FiscalPrinter").get("cmdbuf"))
        cmdparams = cmdbuf.split("\0")
        orderid = cmdparams[0]
        additional_info = cmdparams[1].decode("UTF-8")
        CPF = _get_additional_info(None, "CPF", additional_info).replace(".", "").replace("-", "")
        NAME = _get_additional_info(None, "NAME", additional_info)
        ADDRESS = _get_additional_info(None, "ADDRESS", additional_info)
        sysactions.show_info_message(posid, "Aguardando impressora fiscal...", timeout=-1)
        # read FP data
        prn = FpRetry(posid, mbcontext)
        d = _get_common_fiscal_data(posid, extra=["tslastdoc", "ignoremfadded"])
        serial = d.ecf_serial[posid]
        model = d.ecf_model[posid]
        CCF = int(xml.find("FiscalInfo").get("CCF"))
        COO = int(xml.find("FiscalInfo").get("COO"))
        fp_date = d.dateLastDoc[posid]
        period = get_pos_period(posid)
        stateid = 1  # IN_PROGRESS
        # insert the [fiscalinfo.FiscalOrders] data
        conn = None
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))
                queries = []
                queries.append("""INSERT OR REPLACE INTO fiscalinfo.FiscalOrders(PosId,OrderId,StateId,Period,FPDate,FPSerialNo,ECFModel,ECFUser,CCF,COO,AdditionalMem,CustomerName,CustomerCPF,CustomerAddress)
                    VALUES (%d,%d,%d,%d,%d,'%s','%s',%d,%d,%d,'%s','%s','%s','%s')""" % (
                        int(posid), int(orderid), int(stateid), int(period), int(fp_date), conn.escape(serial), conn.escape(model),
                        int(d.ecf_usernumber[posid]), int(CCF), int(COO),
                        conn.escape(d.ecf_addedmem[posid]), conn.escape(NAME), conn.escape(CPF), conn.escape(ADDRESS))
                )
                queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                conn.query("\0".join(queries))
                break
            except:
                logger.exception("Erro inserindo dados fiscais da nova Order. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro inserindo dados fiscais da nova Order. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                if conn:
                    conn.close()
    except FPException:
        logger.exception("Error on [handle_neworder]")
    except:
        logger.exception("Error on [handle_neworder]")
        sysactions.show_messagebox(posid, "Erro armazenando dados fiscais.\\\\Por favor chame o suporte.", icon="error")
    finally:
        sysactions.show_info_message(posid, "")
        logger.debug("handle_neworder - END")


def handle_nonfiscal_doc(posid, xml, cmd):
    """Stores FP data after non-fiscal document has been printed """
    xml = etree.XML(xml)
    cmdbuf = base64.b64decode(xml.find("FiscalPrinter").get("cmdbuf"))
    cmdparams = cmdbuf.split("\0")
    if cmd == fpcmds.FPRN_CASHIN:
        amount = cmdparams[2]
        if (float(amount) == 0.0):
            # fpcmds.FPRN_CASHIN command only prints something if there is an initial float amount
            # if the amount is zero, nothing is printed, so we can ignore this command
            return
    """
    Tabela de simbolos dos demais documentos emitidos pelo ECF:
    +-------------------------------------+---------+
    | Documento                           | Simbolo |
    +-------------------------------------+---------+
    | Conferencia de Mesa                 |   CM    |
    +-------------------------------------+---------+
    | Registro de Venda                   |   RV    |
    +-------------------------------------+---------+
    | Comprovante de Credito ou Debito    |   CC    |
    +-------------------------------------+---------+
    | Comprovante Nao-Fiscal              |   CN    |
    +-------------------------------------+---------+
    | Comprovante Nao-Fiscal Cancelamento |   NC    |
    +-------------------------------------+---------+
    | Relatorio Gerencial                 |   RG    |
    +-------------------------------------+---------+
    """
    doc_type = "??"
    if cmd in (fpcmds.FPRN_CASHIN, fpcmds.FPRN_CASHOUT):
        doc_type = "CN"  # Comprovante Nao-Fiscal
    elif cmd == fpcmds.FPRN_NFEND:
        doc_type = "RG"  # Relatorio Gerencial
    elif cmd == fpcmds.FPRN_EFTSLIP:
        doc_type = "CC"  # Comprovante de Credito ou Debito
    sysactions.show_info_message(posid, "Aguardando impressora fiscal...", timeout=-1)
    try:
        # read FP data
        prn = FpRetry(posid, mbcontext)
        d = _get_common_fiscal_data(posid, extra=["tslastdoc", "ignoremfadded"])
        serial = d.ecf_serial[posid]
        model = d.ecf_model[posid]
        fp_date = d.dateLastDoc[posid]
        fp_time = d.timeLastDoc[posid]
        COO = int(prn.readOut(fpreadout.FR_RECPNUMBER))
        GNF = int(prn.readOut(fpreadout.FR_NONFISCALQTY))
        GRG = int(prn.readOut(fpreadout.FR_NONFISCALREPQTY)) if (doc_type == "RG") else 0
        CDC = int(prn.readOut(fpreadout.FR_EFTSLIPQTY)) if (doc_type == "CC") else 0
        period = get_pos_period(posid)
        # insert the [fiscalinfo.NonFiscalDocuments] data
        conn = None
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))
                queries = []
                queries.append("""INSERT OR REPLACE INTO fiscalinfo.NonFiscalDocuments(PosId,Period,FPSerialNo,COO,FPDate,FPTime,ECFModel,ECFUser,GNF,GRG,CDC,AdditionalMem,DocType,FiscalCMD)
                    VALUES (%d,%d,'%s',%d,%d,'%s','%s',%d,%d,%d,%d,'%s','%s',%d)""" % (
                    int(posid), int(period), conn.escape(serial), int(COO), int(fp_date), conn.escape(fp_time), conn.escape(model), int(d.ecf_usernumber[posid]), int(GNF), int(GRG), int(CDC),
                    conn.escape(d.ecf_addedmem[posid]), conn.escape(doc_type), int(cmd))
                )
                if cmd in (fpcmds.FPRN_CASHIN, fpcmds.FPRN_CASHOUT):
                    # Those operations just allows cash
                    # tender_id = 0
                    amount = cmdparams[2]
                    # REMOVED DURING PAF-ECF CERTIFICATION
                    # insert the [fiscalinfo.NonFiscalDocumentTenders] data
                    # queries.append("""INSERT OR REPLACE INTO fiscalinfo.NonFiscalDocumentTenders(PosId,FPSerialNo,COO,TenderId,TenderDescr,Amount,VoidedAmount)
                    #    VALUES (%d,'%s',%d,%d,%s,'%s','%s')"""%(
                    #    int(posid), conn.escape(serial), int(COO), tender_id,
                    #    "\n(SELECT TenderDescr FROM productdb.TenderType WHERE TenderId=%d)\n"%(tender_id),
                    #    conn.escape(amount), '0.00')
                    # )
                queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                conn.query("\0".join(queries))
                break
            except:
                logger.exception("Erro inserindo dados nao fiscais. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro inserindo dados nao fiscais. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                if conn:
                    conn.close()
    except FPException:
        logger.exception("Error on [handle_nonfiscal_doc]")
    except:
        logger.exception("Error on [handle_nonfiscal_doc]")
        sysactions.show_messagebox(posid, "Erro armazenando dados fiscais.\\\\Por favor chame o suporte.", icon="error")
    finally:
        sysactions.show_info_message(posid, "")


def get_pos_period(pos_id):
    # Retrieve the business period
    msg = mbcontext.MB_EasySendMessage("POS{}".format(pos_id), TK_POS_GETSTATE, FM_PARAM, str(pos_id))
    if msg.token != TK_SYS_ACK:
        logger.error("Error retrieving current business period for POS id: {}".format(pos_id))
        return
    period = int(msg.data.split('\0')[0])
    return period


def get_last_z_saved(ecf_serial, pos_id):
    # type: (unicode, unicode) -> tuple[unicode, unicode]
    logger.debug("Start Getting Last Z Saved...")
    conn = None
    try:
        conn = persistence.Driver().open(mbcontext)
        query = "SELECT MAX(CRZ), GT FROM fiscalinfo.ZTapes WHERE PosId={} AND FPSerialNo='{}'"
        query = query.format((int(pos_id)), ecf_serial)
        cursor = conn.select(query)

        last_gt_saved = "0"
        last_crz_saved = "0"
        for row in cursor:
            last_crz_saved = (row.get_entry(0) or "0")
            last_gt_saved = (row.get_entry(1) or "0")
    finally:
        if conn:
            conn.close()

    logger.debug("End Getting Last Z Saved...")
    return last_gt_saved, last_crz_saved


def check_z_reports():
    logger.debug("Start Checking Z Reports on Database...")

    pos_list = PosUtil(mbcontext).get_pos_list()

    for pos in pos_list:
        pos_id = pos

        model = get_model(pos_id)
        if has_operator_opened(model):
            continue

        check_pos_z_report(pos_id)
    logger.debug("End Checking Z Reports on Database...")


def check_pos_z_report(pos_id):
    try:
        sysactions.show_info_message(pos_id, "Aguardando Impressora Fiscal...", timeout=-1)
        return handle_z_report(pos_id)
    finally:
        sysactions.show_info_message(pos_id, "")


def handle_z_report(pos_id):
    logger.debug("Start Handle Z Report for POS: {}".format(pos_id))

    for i in xrange(0, 4, 1):
        try:
            prn = FpRetry(pos_id, mbcontext)
            fiscal_data = _get_common_fiscal_data(pos_id, ["aInfoZ", "coosLastZ", "allTax"])

            if "EMULADOR" in d.ecf_serial[pos_id]:
                return True

            md5_serial = prn.readEncrypted("ECF_Serial")
            ecf_serial = fiscal_data.ecf_serial[pos_id]

            if str(md5_serial).strip() != str(ecf_serial).strip():
                sysactions.show_info_message(pos_id, "$SERIAL_PRINTER_VALIDATION_ERROR", timeout=-1, msgtype="error")
                time.sleep(3)
                return False

            ecf_gt = prn.readOut(fpreadout.FR_GT)
            ecf_flags = prn.printerRead(extra=True)
            ecf_sw_version = prn.readOut(fpreadout.FR_FIRMWAREVERSION)
            sefaz_sw_id = prn.readEncrypted("User_FederalRegister")
            break
        except Exception:
            logger.exception("Error Reading Fiscal Info fro Printer - PosId: {}".format(pos_id))
            pass
    else:
        # Failed to read Printer
        return False

    try:
        last_gt, last_crz = get_last_z_saved(ecf_serial, pos_id)

        new_printer = False
        if last_gt == "0":
            new_printer = True
            logger.error("Last Saved GT is Zero - NEW PRINTER - PosId: {} / Serial: {}".format(pos_id, ecf_serial))

        ecf_crz = int(fiscal_data.aInfoZ[pos_id][2])
        if last_crz is not None and int(last_crz.strip()) == ecf_crz:
            logger.debug("Z Already Saved into Database...")
            return True
    except Exception as _:
        # Failed to read Last Z
        return False

    try:
        period = get_pos_period(pos_id)
        if period == 0:
            period = int(time.strftime("%Y%m%d"))
            logger.error("POS Period is ZERO - PosID: {} / Using: {}".format(pos_id, period))

        fp_date = int(fiscal_data.dateLastZ[pos_id])
        fp_business_day = int(fiscal_data.aInfoZ[pos_id][36])
        if fp_business_day == 0:
            fp_business_day = fp_date
            logger.error("ECF Business Day is ZERO - PosID: {} / Printer: {}".format(pos_id, ecf_serial))

        z_gt = fiscal_data.lastZGT[pos_id]
        if round(float(z_gt), 2) != round(float(ecf_gt), 2):
            logger.error("Current Z GT differs from GT - PosId: {} / ZGT: {} / GT: {}".format(pos_id, z_gt, ecf_gt))
            z_gt = ecf_gt

        daily_gt = str(round(float(z_gt) - float(last_gt), 2)) if new_printer is False else "0.00"
        if round(float(daily_gt), 2) < 0:
            logger.error("DGT less than Zero - PosId: {} / DGT: {} / LGT: {}".format(pos_id, daily_gt, last_gt))
            daily_gt = '0.00'

        ecf_model = fiscal_data.ecf_model[pos_id]
        fp_date = int(fiscal_data.dateLastZ[pos_id])
        fp_time = str(fiscal_data.timeLastZ[pos_id])
        first_coo = int(fiscal_data.coosLastZ[pos_id][0])
        last_coo = int(fiscal_data.coosLastZ[pos_id][1])
        cro = int(fiscal_data.aInfoZ[pos_id][1])

        issqn = "S" if (ecf_flags & fpstatus.FP_ISSQN) else "N"
        fp_user = int(fiscal_data.ecf_usernumber[pos_id])
        opnf = _calculate_OPNF(pos_id, fp_business_day)
        fiscal_data.allTax[pos_id]["OPNF"] = _decimal_to_fixed_int(opnf)

        # ECF Information
        ecf_type = fiscal_data.ecf_type[pos_id]
        ecf_brand = fiscal_data.ecf_brand[pos_id]
        ecf_sw_date = fiscal_data.ecf_swdate[pos_id]
        ecf_sw_time = fiscal_data.ecf_swtime[pos_id]
        ecf_pos_id = fiscal_data.ecf_posid[pos_id]

        conn = None
        queries = []
        try:
            query_tape = """INSERT OR REPLACE INTO FiscalInfo.ZTapes (PosId, FPSerialNo, CRZ, FirstCOO, LastCOO, CRO, 
            Period, FPBusinessDate, FPDate, FPTime, ECFModel, ECFUser, DGT, GT, ISSQN, AdditionalMem, ECFType, ECFBrand,
            ECFSwDate, ECFSwTime, ECFSwVersion, ECFPosId, UserCNPJ) VALUES (%d,'%s',%d,%d,%d,%d,%d,%d,%d,'%s','%s',%d,
            '%s','%s','%s','%s','%s','%s','%s','%s','%s',%d,'%s')"""

            conn = persistence.Driver().open(mbcontext, dbname=str(pos_id))
            queries.append(query_tape % (int(pos_id), conn.escape(ecf_serial), ecf_crz, first_coo, last_coo, cro,
                                         period, fp_business_day, fp_date, conn.escape(fp_time),
                                         conn.escape(ecf_model), fp_user, conn.escape(daily_gt), conn.escape(z_gt),
                                         conn.escape(issqn), conn.escape(d.ecf_addedmem[pos_id]), conn.escape(ecf_type),
                                         conn.escape(ecf_brand), conn.escape(ecf_sw_date), conn.escape(ecf_sw_time),
                                         conn.escape(ecf_sw_version), int(ecf_pos_id), conn.escape(sefaz_sw_id)))

            query = """INSERT OR REPLACE INTO FiscalInfo.ZTapeTotalizers(PosId, FPSerialNo, CRZ, Totalizer, 
            AdditionalMem, ECFModel, ECFUser, Period, Amount) VALUES (%d,'%s',%d,'%s','%s','%s',%d,%d,%d)"""

            for name, amount in d.allTax[pos_id].items():
                if new_printer is True:
                    continue

                queries.append(query % (int(pos_id), conn.escape(ecf_serial), ecf_crz, conn.escape(name),
                                        conn.escape(d.ecf_addedmem[pos_id]), conn.escape(ecf_model), fp_user,
                                        fp_business_day, int(amount)))

            queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
            conn.query("\0".join(queries))
        finally:
            if conn:
                conn.close()

    except Exception as _:
        pass

    logger.debug("End Handle Z Report for POS: {}".format(pos_id))
    return True


def update_fiscal_order_totals(posid, order):
    sysactions.show_info_message(posid, "Aguardando impressora fiscal...", timeout=-1)
    try:
        # Read FP data
        d = _get_common_fiscal_data(posid, extra=["taxByIndex", "ignoremfadded"])
        orderid = order.get("orderId")
        lines = [line for line in order.findall("SaleLine") if line.get("taxIndex") is not None and int(line.get("qty") or 0)]
        pcodelist = '|'.join(set([line.get("partCode") for line in lines]))
        params = sysactions.get_custom_params(posid, pcodelist, cacheable=False).findall("Product")

        def get_param(pcode, paramid, default=None):
            paramid = paramid.lower()
            for p in params:
                if p.get("productCode") == pcode:
                    for param in p.findall("CustomParameter"):
                        if (param.get("id") or "").lower() == paramid:
                            return param.get("value")
            return default
        queries = []
        for item in lines:
            lnbr = item.get("lineNumber")
            itemid = item.get("itemId")
            level = item.get("level")
            pcode = item.get("partCode")
            unit = item.get("measureUnit")
            taxindex = item.get("taxIndex") or "0"
            try:
                taxindex = str(int(taxindex, 10)).zfill(4)
            except ValueError:
                pass
            taxcode = d.taxByIndex[posid].get(taxindex, taxindex)  # Ex: para ICMS (TaxFiscalIndex=1) 3.4% esse campo deve ser: "01T0340"
            IAT = get_param(pcode, "IAT", "T")
            IPPT = get_param(pcode, "IPPT", "P")
            qty = D(item.get("qty"))
            decqty = D(item.get("decQty") or 0)
            totalqty = qty + decqty
            productName = item.get("productName")
            unitPrice = item.get("unitPrice") or "0.00"
            discountAmount = item.get("discountAmount") or "0.00"
            void_indicator = "S" if decqty == totalqty else "P" if decqty > 0 else "N"
            queries.append("""INSERT INTO fiscalinfo.FiscalOrderItems
            (PosId,OrderId,LineNumber,ItemId,Level,PartCode,MeasureUnit,TaxCode,IAT,IPPT,VoidIndicator,ProductName,OrderedQty,DecQty,UnitPrice,DiscountAmount)
            VALUES (%(posid)s,%(orderid)s,%(lnbr)s,'%(itemid)s',%(level)s,%(pcode)s,'%(unit)s','%(taxcode)s',
            '%(IAT)s','%(IPPT)s','%(void_indicator)s','%(productName)s','%(qty)s','%(decqty)s','%(unitPrice)s','%(discountAmount)s')""" % locals())
        # Also update the [fiscalinfo.FiscalOrders] total amounts
        totalGross = order.get("totalGross") or "0.00"
        discountAmount = order.get("discountAmount") or "0.00"
        stateId = order.get("stateId")
        queries.append("""UPDATE fiscalinfo.FiscalOrders SET
        TotalGross='%(totalGross)s', DiscountAmount='%(discountAmount)s', StateId=%(stateId)s WHERE OrderId=%(orderid)s""" % locals())
        # Also update the [fiscalinfo.FiscalOrderTender]
        change = order.get("change")
        tenders = list(order.findall("TenderHistory/Tender"))
        last_index = (len(tenders) - 1)
        for i, tender in enumerate(tenders):
            tenderId = tender.get("tenderId")
            tenderType = tender.get("tenderType")
            tenderDescr = tender.get("tenderDescr")
            tenderAmount = tender.get("tenderAmount")
            is_last = (i == last_index)
            if is_last and change and D(change) > 0 and D(change) <= D(tenderAmount):
                # Remove the change from the last tender in the list
                tenderAmount = str(D(tenderAmount) - D(change))
                change = None
            queries.append("""INSERT OR REPLACE INTO fiscalinfo.FiscalOrderTender(OrderTenderId,OrderId,TenderId,TenderDescr,TenderAmount)
            VALUES('%(tenderId)s','%(orderid)s','%(tenderType)s','%(tenderDescr)s','%(tenderAmount)s')""" % locals())
        conn = None
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))
                queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                conn.query("\0".join(queries))
                break
            except:
                logger.exception("Erro inserindo dados fiscais da venda. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro inserindo dados fiscais da venda. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                if conn:
                    conn.close()
    except:
        logger.exception("Error on [update_fiscal_order_totals]")
        sysactions.show_messagebox(posid, "Erro armazenando dados fiscais.\\\\Por favor chame o suporte.", icon="error")
    finally:
        sysactions.show_info_message(posid, "")


def event_fiscal_order_state(params):
    """
    Handles the synchronous "FISCAL_ORDER_STATE" event
    Please note that this function will hold the kernel flow during its execution
    """
    logger.debug("event_fiscal_order_state - START")

    xml, subject, type, sync, posid = params[:5]

    if type not in ("PAID", "VOIDED"):
        logger.debug("event_fiscal_order_state - not PAID or VOIDED - END")
        return

    conn = None
    order = etree.XML(xml).find("Order")
    prn = FpRetry(posid, mbcontext)
    orderid = order.get("orderId")

    try:
        logger.debug("event_fiscal_order_state before update_inventory")
        update_inventory(order, posid)
        logger.debug("event_fiscal_order_state after update_inventory")
    except:
        logger.exception("Error updating inventory")

    if type == "VOIDED":
        # Check if this is a "void last" operation
        is_void_last = False

        for state in order.findall("StateHistory/State"):
            if state.get("state") == "PAID":
                is_void_last = True
                break
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))
                if is_void_last:
                    # On this case, we need to store the COO of the void in the [FiscalOrders] table
                    sysactions.show_info_message(posid, "Aguardando impressora fiscal...", timeout=-1)
                    # Read FP data
                    COO = int(prn.readOut(fpreadout.FR_RECPNUMBER))
                    stateId = order.get("stateId")
                    queries = []
                    queries.append("UPDATE fiscalinfo.FiscalOrders SET COOVoid=%s,StateId=%s WHERE OrderId=%s" % (COO, stateId, orderid))
                    queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                    conn.query("\0".join(queries))
                else:
                    # For void current, just update the state
                    stateId = order.get("stateId")
                    queries = []
                    queries.append("UPDATE fiscalinfo.FiscalOrders SET StateId=%s WHERE OrderId=%s" % (stateId, orderid))
                    queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                    conn.query("\0".join(queries))
                break
            except FPException:
                logger.exception("Error on [event_fiscal_order_state]")
            except:
                logger.exception("Erro armazenando dados fiscais de cancelamento. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro armazenando dados fiscais de cancelamento. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                sysactions.show_info_message(posid, "")
                if conn:
                    conn.close()

        if not is_void_last:
            # We don't need to update this on "void last", since it has been done already
            update_fiscal_order_totals(posid, order)

    if type == "PAID":
        conn = None
        for i in xrange(0, 3, 1):
            try:
                n = 0
                conn = persistence.Driver().open(mbcontext)
                cur = conn.select("SELECT * FROM fiscalinfo.ElectronicTransactions WHERE PosId=%d AND OrderId=%d" % (int(posid), int(orderid)))
                for row in cur:
                    sys_log_info("Printing EFT slip on fiscal printer...")
                    amount = row.get_entry("Amount")
                    tendername = row.get_entry("TenderDescr")
                    xml_data = row.get_entry("XmlData")
                    try:
                        report = sysactions.generate_report("fiscal_eft_customer_slip", posid, xml_data)
                        report +='\r\n\n\n\n\n'+ sysactions.generate_report("fiscal_eft_merchant_slip", posid, xml_data)
                        prn.printEftSlip(tendername, (report or ""), twocopies=False, amount=amount, tenderid=n)
                    except FPException, ex:
                        logger.exception("Error printing EFT slip")
                        sysactions.show_info_message(posid, str(ex), msgtype="error")
                    except:
                        logger.exception("Error printing EFT slip")
                        sysactions.show_messagebox(posid, "Erro imprimindo comprovante de crédito ou débito", icon="error")
                    n += 1
                break
            except:
                logger.exception("Erro obtendo cupom de pagamento com cartao. Posid=%d, Tentativa=%d" % (int(posid), i))
            finally:
                if conn:
                    conn.close()

    logger.debug("event_fiscal_order_state - END")


def event_cashless(params):
    xml, subject, type, sync, posid = params[:5]
    if not int(posid):
        return
    if type != "PROCESS_FINISHED":
        return
    cashless = etree.XML(xml).find("Cashless")
    if cashless.get("command") not in ("CREDITSALE", "DEBITSALE"):
        return
    resp = cashless.find("CashlessResponse")
    if resp is None:
        return
    if resp.get("TerminationStatus") != "SUCCESS":
        return
    if resp.get("Result") != "CAPTURED":
        return
    if not cashless.get("orderId"):
        sys_log_warning("Received a CASHLESS response without an order id")
        return
    try:
        orderid = cashless.get("orderId")
        eftcmd = cashless.get("command")
        tender_id = cashless.get("tenderId")
        amount = cashless.find("CashlessResponse").get("ApprovedAmount")
        if not tender_id:
            # Only for compatibility purposes...
            TENDER_CREDIT_CARD = "2"
            TENDER_DEBIT_CARD = "3"
            tender_id = (TENDER_CREDIT_CARD if eftcmd == "CREDITSALE" else TENDER_DEBIT_CARD)
        # insert the [fiscalinfo.ElectronicTransactions] data
        conn = None
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))
                queries = []
                queries.append("""INSERT OR REPLACE INTO fiscalinfo.ElectronicTransactions(PosId,OrderId,Sequence,TenderId,TenderDescr,Amount,XmlData)
                    VALUES (%d,%d,%s,%d,%s,'%s','%s')""" % (
                    int(posid), int(orderid),
                    "\n(SELECT count() FROM fiscalinfo.ElectronicTransactions WHERE PosId=%d AND OrderId=%d)\n" % (int(posid), int(orderid)),
                    int(tender_id),
                    "\n(SELECT TenderDescr FROM productdb.TenderType WHERE TenderId=%d)\n" % int(tender_id),
                    conn.escape(amount), conn.escape(xml))
                )
                queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                conn.query("\0".join(queries))
                break
            except:
                logger.exception("Erro inserindo dados fiscais de pagamento. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro inserindo dados fiscais de pagamento. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                if conn:
                    conn.close()
    except:
        logger.exception("Error on [event_cashless]")
        sysactions.show_messagebox(posid, "Erro armazenando dados fiscais.\\\\Por favor chame o suporte.", icon="error")


def event_account_transfer(params):
    xml, subject, type, sync, posid = params[:5]
    if type not in ("TRANSFER_SKIM", "TRANSFER_INITIAL_FLOAT", "TRANSFER_CASH_IN"):
        return
    transfer = etree.XML(xml).find("POSTransfer")
    if float(transfer.get("amount")) <= 0:
        return
    amount = "%.2f" % float(transfer.get("amount"))
    tenderId = "1"
    f = FpRetry(posid, mbcontext)
    try:
        if type == "TRANSFER_SKIM":
            f.cashOut(tenderId, '', amount)
        elif type in ("TRANSFER_INITIAL_FLOAT", "TRANSFER_CASH_IN"):
            # We need to force the tender name to be empty string, otherwise the cashin fails with "FORMA DE PAGAMENTO NAO PROGRAMADA" error
            f.cashIn(tenderId, '', amount)
    except FPException, ex:
        logger.exception("Error executing fiscal-printer [%s] for pos id: %s" % (type, posid))
        return [FM_PARAM, "%s\0%s" % (ex.errcode, ex.errmsg)]


def event_fiscal_promotional_msg(params):
    logger.debug("event_fiscal_promotional_msg - START")

    try:
        xml, subject, type, sync, posid = params[:5]
        order = etree.XML(xml).find("Order")
        if order.find("State") is not None and order.find("State").attrib["toState"] == "VOIDED":
            logger.debug("event_fiscal_promotional_msg - State Voided - END")
            return
        # orderid = order.get("orderId")
        order_ts = datetime.datetime.strptime(order.get("createdAt")[:19], "%Y-%m-%dT%H:%M:%S")
        infos = (order.findtext("AdditionalInfo") or "").split('|')
        pre_venda = ""
        for info in infos:
            if info.lower().startswith("prevenda="):
                pre_venda = info[len("prevenda="):]
        prn = FpRetry(posid, mbcontext)
        MD5_file = prn.readFile(PAF_ECF.SW_MD5_FILE)
        md5 = hashlib.md5(MD5_file).hexdigest().upper()

        # MD5
        promo_message = "MD-5: %s" % (md5)
        # Pre-venda
        if pre_venda:
            promo_message += "\nPV%010d" % (int(pre_venda))
        # Minas legal - Requisito VIII-A, item 2 REVOGADO
        # Cupom Mania - Requisito VIII-A, item 3 REVOGADO
        # Paraiba Legal
        if UF in "PB":
            cnpj, ie = prn.readEncrypted("SW_MD5", "User_StateRegister")
            COO = int(prn.readOut(fpreadout.FR_RECPNUMBER))
            total_gross = order.get("totalGross")
            promo_message += "\nPARAIBA LEGAL - RECEITA CIDADA\nTORPEDO PREMIADO:\n%s %s %06d %d" % (ie[:8], order_ts.strftime("%d%m%Y"), COO, int(total_gross.replace('.', '')))
        federal, estadual = get_pis_cofins(posid, order)
        piscofins = federal.get("value")
        piscofins_percent = federal.get("percent")
        icms = estadual.get("value")
        icms_percent = estadual.get("percent")
        promo_message += "\nLei 12.741, Valor Aprox., Imposto F=%.2f (%.2f%%), E=%.2f (%.2f%%)" % (piscofins, piscofins_percent, icms, icms_percent)
        if hasattr(posactions, 'get_promotional_msg'):
            try:
                extra = posactions.get_promotional_msg(order)
                if extra:
                    promo_message = "%s\n%s" % (promo_message, extra)
            except:
                logger.exception("Error getting extra promotional message")
        return promo_message
    except FPException:
        logger.exception("Error on [event_fiscal_promotional_msg]")
    except:
        logger.exception("Error on event_fiscal_promotional_msg")

    logger.debug("event_fiscal_promotional_msg - END")


def get_pis_cofins(posid, order):
    ret = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_GET_IBPT_TAX, format=FM_PARAM, data=etree.tostring(order))
    # Processamento Finalizado com Sucesso
    if ret.token == TK_SYS_ACK:
        taxes_dict = eval(ret.data)
        return taxes_dict.get("nacionalfederal"), taxes_dict.get("estadual")
    return None


def verify_printer(posid, force=False, showmsg=True, save_pre_gt=False, xml=None):
    posid = int(posid)
    MAX_TIME_VARIATION = 3600      # max variation between printer and system
    if force:
        verified_printers.discard(posid)
    if posid in verified_printers:
        return True

    logger.debug("verify_printer - START")

    if xml is not None:
        xml = etree.XML(xml)

    # Read data from fiscal-printer
    try:
        global verify_printer_id
        global verify_gt

        prn = FpRetry(posid, mbcontext)

        serial = None
        gt = None
        if verify_printer_id or verify_gt:
            serial, gt = prn.readEncrypted("ECF_Serial", "RW_GT")

        fiscal_info = None
        if xml is not None:
            fiscal_info = xml.find("FiscalInfo")

        global verify_time
        if verify_time:
            prn_ts = fiscal_info.get("Date") if fiscal_info is not None else None

            if not prn_ts:
                prn_ts = prn.getPrinterTimestamp()

            prn_tsSec = time.mktime(datetime.datetime.strptime(prn_ts, "%Y-%m-%dT%H:%M:%S").timetuple())

            now_ts = datetime.datetime.now()
            now_tsSec = time.mktime(now_ts.timetuple())
            now_ts = now_ts.isoformat()[:19]
            dif = prn_tsSec - now_tsSec
            if prn_tsSec < now_tsSec:
                dif = now_tsSec - prn_tsSec
            if dif > (MAX_TIME_VARIATION * 24):
                logger.error("FISCAL PRINTER VERIFICATION ERROR! POS ID: [%d]\n"
                              "Printer Date: %s\nSystem  Date: %s \n"
                              "Variation exceeds one day \n" % (posid, prn_ts, now_ts))
                if showmsg:
                    sysactions.show_messagebox(posid, "Diferença de data superior ao permitido.\\\\Por favor chame o suporte", title="Impressora Fiscal", icon="error", asynch=True, timeout=120000)
                return False
            if dif > MAX_TIME_VARIATION:
                logger.error("FISCAL PRINTER VERIFICATION ERROR! POS ID: [%d]\n"
                              "Printer Date: %s\nSystem  Date: %s \n"
                              "Variation exceeds one hour \n" % (posid, prn_ts, now_ts))
                if showmsg:
                    sysactions.show_messagebox(posid, "Diferença de horário superior ao permitido.\\\\Por favor chame o suporte", title="Impressora Fiscal", icon="error", asynch=True, timeout=120000)
                return False

        # Read expected values
        if verify_printer_id:
            prn_serial = fiscal_info.get("Serial") if fiscal_info is not None else None

            if not prn_serial:
                prn_serial = prn.readOut(fpreadout.FR_FPSERIALNUMBER).strip()

            if prn_serial != serial:
                logger.error("FISCAL PRINTER ERROR! POS: [%d] - Allowed ECF: %s - Current ECF: %s" % (posid, serial, prn_serial))
                if showmsg:
                    sysactions.show_messagebox(posid, "Impressora Fiscal não permitida:\\Número de série diferente.\\\\Por favor chame o suporte", title="Impressora Fiscal", icon="error", asynch=True, timeout=120000)
                return False

        if verify_gt:
            prn_gt = fiscal_info.get("GT") if fiscal_info is not None else None

            if not prn_gt:
                prn_gt = prn.readOut(fpreadout.FR_GT).strip()

            prn_gt = float(prn_gt)
            gt_pre = float(readPreGt(posid) or 0)
            gt = float(gt.replace(",", ".")) if gt is not None else 0.0
            if prn_gt != gt:
                if gt <= prn_gt <= gt_pre:
                    prn.writeEncrypted("RW_GT", prn_gt)
                    return True
                logger.error("FISCAL PRINTER VERIFICATION ERROR! POS ID: [%d] - Printer GT: %s - Stored GT: %s - Stored GT PRE: %s" % (posid, prn_gt, gt, gt_pre))
                if showmsg:
                    sysactions.show_messagebox(posid, "Impressora Fiscal não permitida:\\GT Inválido.\\\\Por favor chame o suporte", title="Impressora Fiscal", icon="error", asynch=True, timeout=120000)
                return False
            else:
                logger.info("FISCAL PRINTER GT INFO POS ID: [%d] - Printer GT: %s - Stored GT: %s - Stored GT PRE: %s" % (posid, prn_gt, gt, gt_pre))

            if save_pre_gt:
                writePreGt(posid, prn_gt)

    except FPException:
        logger.exception("Error on [verify_printer]")
        return False
    except:
        logger.exception("FISCAL PRINTER VERIFICATION ERROR! POS ID: [%d]\n" % (posid))
        return False

    # Success
    verified_printers.add(posid)
    logger.debug("verify_printer - END")

    return True


def verify_system_md5(posid):
    try:
        logger.debug("verify_system_md5 - START")

        report = sysactions.generate_report("signedFiscalReport", "paf_system_md5", posid)
        if not report:
            logger.error("Error generating PAF-ECF system MD5 file")
            return
        prn = FpRetry(posid, mbcontext)
        # Calculate the SW_MD5
        SW_MD5 = hashlib.md5(report).hexdigest().upper()
        prn.writeEncrypted("SW_MD5", SW_MD5)
        MD5_file = PAF_ECF.SW_MD5_FILE
        current = ""
        try:
            current = prn.readFile(MD5_file)
        except:
            pass
        # Save the new MD5 file list
        fpath = prn.saveFile(MD5_file, report)
        if sys.platform == "win32":
            fpath = fpath.replace("/", "\\")
        if current != report:
            # Save the new MD5 file list
            sysactions.show_messagebox(posid, "Sistema atualizado!\n\nLista de arquivos salva em:\n%s" % fpath, title="PAF-ECF", icon="info", asynch=True, linefeed="\n")
        else:
            # TODO - Check if we REALLY need to show this message on this case
            sysactions.show_info_message(posid, "<html>Lista de arquivos salva em: %s</html>" % fpath, timeout=5000)
    except:
        logger.exception("Error on [verify_system_md5]! POS ID: [%d]\n" % (posid))
        sysactions.show_messagebox(posid, "Erro gravando lista de arquivos\\\\Por favor chame o suporte", title="PAF-ECF", icon="error", asynch=True, timeout=120000)
    finally:
        logger.debug("verify_system_md5 - END")


def event_fiscal_startup(params):
    xml, subject, type, sync, posid = params[:5]
    posid = int(posid)

    logger.debug("event_fiscal_startup - START")

    verify_system_md5(posid)

    logger.debug("event_fiscal_startup - END")


def writePreGt(pos_id, gt_pre):
    try:
        gtpre = open("gtpre_%s.txt" % pos_id, "w+")
        gtpre.write(str(gt_pre))
        gtpre.close()
    except Exception as _:
        logger.exception("Error Writing Pre-GT")


def readPreGt(pos_id):
    fname = "gtpre_%s.txt" % pos_id
    if os.path.isfile(fname):
        gtpre = open(fname, "r")
        pre_gt = gtpre.readline()
        gtpre.close()
        return pre_gt
    else:
        return 0.0


def check_electronic_fiscal_file(xml, subject, type, cmd, posid):
    sysactions.show_info_message(posid, "Aguardando impressora fiscal...", timeout=-1)
    try:
        d = _get_common_fiscal_data(posid)
        pafecf_actions.generateElectronicFiscalFile(posid, d.ecf_serial[posid])
        pafecf_actions.pafEnvioFiscoZ(posid, True)
    except:
        logger.exception("Error on [check_electronic_fiscal_file]! POS ID: [%s]\n" % (posid))
    finally:
        sysactions.show_info_message(posid, "")


def void_stored_order(posid, model, order, pre_venda):
    try:
        posot = sysactions.get_posot(model)
        session = sysactions.get_operator_session(model)
        order_id = order.get("orderId")
        posot.updateOrderProperties(orderid=order_id, orderSubType=" ")
        posot.recallOrder(posid, order_id, session)
        posot.doTotal(posid)
        posot.doTender(int(posid), TENDER_CASH, "")
        posot.voidOrder(posid, lastpaidorder=1)
        return True
    except OrderTakerException, e:
        sysactions.show_info_message(posid, "$ERROR_CODE_INFO|%d|%s" % (e.getErrorCode(), e.getErrorDescr()), msgtype="error")
        sysactions.show_messagebox(posid, "Ocorreu um erro ao tentar cancelar a pré-venda número %s\\\\Por favor chame o suporte" % pre_venda, title="Intervenção requerida", icon="error")
        return False


def void_stored_orders(posid, posot, orders_to_void):
    try:
        sys_log_info("Voiding stored orders: [%s]" % ",".join([order["orderId"] for order in orders_to_void]))
        model = sysactions.get_model(posid)
        dlgid = sysactions.show_messagebox(posid, "Por favor aguarde\\\\Cancelando pré-vendas armazenadas", buttons="", asynch=True, timeout=120000)
        try:
            for order in orders_to_void:
                orderid = order["orderId"]
                order = etree.XML(posot.orderPicture(orderid=orderid)).find("Order")
                pre_venda = _get_additional_info(order, "PreVenda")
                if not pre_venda:
                    sys_log_warning("Found a stored order (%s) without the [PreVenda] additional info (%s) - voiding it anyway" % (orderid, (order.findtext("AdditionalInfo") or "")))
                    pre_venda = orderid
                try:
                    sysactions.show_info_message(posid, "Emitindo cancelamento da pré-venda: %s" % pre_venda, msgtype="warning", timeout=-1)
                    void_stored_order(posid, model, order, pre_venda)
                finally:
                    sysactions.show_info_message(posid, "")
        finally:
            sysactions.close_asynch_dialog(posid, dlgid)
    except:
        logger.exception("Error on [void_stored_orders]")


def store_printer_information(xml, posid):
    try:
        sysactions.show_info_message(posid, "Aguardando impressora fiscal...", timeout=-1)
        xml = etree.XML(xml)
        # cmdbuf = base64.b64decode(xml.find("FiscalPrinter").get("cmdbuf"))
        # cmdparams = cmdbuf.split("\0")
        # period = int(cmdparams[0])
        # Read FP data
        prn = FpRetry(posid, mbcontext)
        d = _get_common_fiscal_data(posid, extra=["tslastdoc"])
        serial = d.ecf_serial[posid]
        model = d.ecf_model[posid]
        flags = prn.printerRead(extra=True)
        ISSQN = "S" if (flags & fpstatus.FP_ISSQN) else "N"
        fp_user = int(d.ecf_usernumber[posid])
        User_FederalRegister = prn.readEncrypted("User_FederalRegister")
        ECFType = d.ecf_type[posid]
        ECFBrand = d.ecf_brand[posid]
        ECFSwVersion = prn.readOut(fpreadout.FR_FIRMWAREVERSION)
        ECFSwDate = d.ecf_swdate[posid]
        ECFSwTime = d.ecf_swtime[posid]
        ECFPosId = d.ecf_posid[posid]
        printer_date_time = datetime.datetime.strptime(d.dateLastDoc[posid] + d.timeLastDoc[posid], "%Y%m%d%H%M%S")
        # Insert the [fiscalinfo.FiscalPrinters] data
        conn = None
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))
                queries = []
                queries.append("""INSERT OR REPLACE INTO fiscalinfo.FiscalPrinters(PosId,FPSerialNo,ECFModel,ECFUser,ISSQN,AdditionalMem,ECFType,ECFBrand,ECFSwDate,ECFSwTime,ECFSwVersion,ECFPosId,UserCNPJ, CreatedAt)
                    VALUES (%d,'%s','%s',%d,'%s','%s','%s','%s','%s','%s','%s',%d,'%s', '%s')""" % (
                    int(posid), conn.escape(serial), conn.escape(model), int(fp_user), conn.escape(ISSQN), conn.escape(d.ecf_addedmem[posid]),
                    conn.escape(ECFType), conn.escape(ECFBrand), conn.escape(ECFSwDate), conn.escape(ECFSwTime), conn.escape(ECFSwVersion),
                    int(ECFPosId), conn.escape(User_FederalRegister), printer_date_time
                )
                )
                queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                conn.query("\0".join(queries))
                break
            except:
                logger.exception("Erro inserindo dados fiscais da impressora. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro inserindo dados fiscais da impressora. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                if conn:
                    conn.close()
    except FPException:
        logger.exception("Error on [store_printer_information]")
    except:
        logger.exception("Error on [store_printer_information]")
        sysactions.show_messagebox(posid, "Erro armazenando dados fiscais.\\\\Por favor chame o suporte.", icon="error")
    finally:
        sysactions.show_info_message(posid, "")


def store_daily_inventory(xml, posid):
    try:
        conn = None
        for i in xrange(0, 3, 1):
            try:
                conn = persistence.Driver().open(mbcontext, dbname=str(posid))
                queries = []
                d = _get_common_fiscal_data(posid, extra=["tslastdoc"])
                printer_date_time = datetime.datetime.strptime(d.dateLastDoc[posid] + d.timeLastDoc[posid], "%Y%m%d%H%M%S")
                queries.append("""DELETE FROM fiscalinfo.EstoqueHistorico""")
                queries.append("""
                INSERT OR REPLACE INTO fiscalinfo.EstoqueHistorico(DataHora, SKU, Descr, Unidade, ValorUnitario, Qty)
                SELECT
                    '%s' AS DataHora,
                    SKU, Descr, Unidade, ValorUnitario, Qty
                FROM fiscalinfo.Estoque
                """ % printer_date_time)
                queries = BEGIN_TRANSACTION + queries + COMMIT_TRANSACTION
                conn.query("\0".join(queries))
                break
            except:
                logger.exception("Erro inserindo historico do estoque. Posid=%d, Tentativa=%d" % (int(posid), i))
                sys_log_exception("Erro inserindo historico do estoque. Posid=%d, Tentativa=%d" % (int(posid), i))
                if conn:
                    conn.query('''ROLLBACK TRANSACTION;''')
            finally:
                if conn:
                    conn.close()
    except:
        logger.exception("Error on [store_daily_inventory]")


def check_stored_orders(xml, posid):
    # today = datetime.datetime.strftime(datetime.date.today(), "%Y%m%d")
    # if sysactions.get_business_period(sysactions.get_model(posid)) == today:
    #     return
    posot = OrderTaker(posid, mbcontext)
    orders = posot.listOrders(state="STORED")
    if not orders:
        return
    bdays = set()  # List of all opened business days
    STATE_OPENED = "2"
    for pos in sysactions.get_poslist():
        if str(pos) == posid:
            continue
        msg = mbcontext.MB_EasySendMessage("POS%d" % pos, TK_POS_GETSTATE, FM_PARAM, str(pos))
        if msg.token == TK_SYS_ACK:
            period, state = msg.data.split('\0')[:2]
            if state == STATE_OPENED:
                bdays.add(int(period))
    orders_to_void = [order for order in orders if int(order["businessPeriod"]) not in bdays]
    if not orders_to_void:
        return
    # Create a thread to void the orders
    # we cannot hold this event since we will need to communicate with the fiscal component
    # (this would cause a dead lock)
    threading.Thread(target=void_stored_orders, name="void_stored_orders", args=(posid, posot, orders_to_void)).start()


def event_fiscal_cmd_executed(params):
    xml, subject, type, sync, posid = params[:5]
    cmd = int(type, 0)

    logger.debug(str(cmd) + ": event_fiscal_cmd_executed - START")

    posid = int(posid)
    if cmd in (fpcmds.FPRN_ENDOFDAY, fpcmds.FPRN_ZREPORT):
        check_pos_z_report(posid)
        check_electronic_fiscal_file(xml, subject, type, cmd, posid)

    if cmd in (fpcmds.FPRN_NFEND, fpcmds.FPRN_CASHIN, fpcmds.FPRN_CASHOUT, fpcmds.FPRN_EFTSLIP):
        handle_nonfiscal_doc(posid, xml, cmd)

    if cmd == fpcmds.FPRN_BEGINOFDAY:
        store_printer_information(xml, posid)
        store_daily_inventory(xml, posid)
        check_stored_orders(xml, posid)

    logger.debug(str(cmd) + ": event_fiscal_cmd_executed - END")


def event_querychagestate(params):
    xml, subject, type, sync, posid = params[:5]
    model = get_model(posid)
    if get_podtype(model) == "OT" or get_posfunction(model) == "OT":
        return
    if not verify_printer(posid, force=True):
        sys_log_info("Blocking POS %s state change (%s)" % (posid, type))
        data = "%s\0%s" % (SE_FPERROR, "Erro verificando a Impressora Fiscal")
        return [FM_PARAM, data]


def event_fiscal_queue_error(params):
    xml, subject, type, sync, posid = params[:5]
    xml = etree.XML(xml)
    errmsg = xml.find("Fiscal").get("errmsg").encode("UTF-8")
    sysactions.show_messagebox(posid, "Erro na impressora fiscal:\\%s\\\\A venda atual será cancelada devido a este erro." % errmsg, title="Impressora Fiscal", icon="error", asynch=True, timeout=120000)


def event_verify_last_z_reduction(params):
    logger.debug("[event_verify_last_z_reduction] Begin")
    pos_id = params[4]
    if pos_id == 0:
        check_z_reports()
    else:
        if check_pos_z_report(pos_id) is False:
            return None
        else:
            return "\0"

    logger.debug("[event_verify_last_z_reduction] End")

#
# Printer information
#


class CommonFiscalData:
    # cached
    ecf_brand = {}
    ecf_model = {}
    ecf_type = {}
    ecf_usernumber = {}
    ecf_serial = {}
    ecf_userdate = {}
    ecf_usertime = {}
    ecf_swdate = {}
    ecf_swtime = {}
    ecf_addedmem = {}
    ecf_posid = {}
    ecf_printer_taxes = {}

    # non-cached
    tslastdoc = {}
    dateLastDoc = {}
    timeLastDoc = {}
    coosLastZ = {}
    aInfoZ = {}
    dateLastZ = {}
    timeLastZ = {}
    vTax = {}
    allTax = {}
    taxByIndex = {}
    lastZGT = {}


class FpRetry(fp):
    def readOut(self, readout_option, params = []):
        """ fp.readOut(readout_option, params=[]) -> readout value
        Performs a fiscal printer readout
        @return: the readout data
        @raise FPException on fiscal-printer error
        """
        error = None
        for i in xrange(0, 3, 1):
            try:
                data = '\x00'.join(map(str, [fpcmds.FPRN_READOUT, readout_option] + params))
                msg = self._mbctxt.MB_EasySendMessage(self.fpservice, TK_FISCAL_CMD, FM_PARAM, data)
                self._checkErr(msg)
                return msg.data
            except FPException as ex:
                error = ex
                logger.exception("Erro lendo da impressora. readout_option=%d, Tentativa=%d" % (readout_option, i))
                time.sleep(1)
            except:
                logger.exception("Erro lendo da impressora. readout_option=%d, Tentativa=%d" % (readout_option, i))
                time.sleep(1)
        if error:
            sysactions.show_info_message(self._posid, str(error), msgtype="error")
            raise error


def _get_common_fiscal_data(posid, extra=[]):
    global d
    if not d:
        d = CommonFiscalData()
    prn = FpRetry(posid, mbcontext)
    # Fully cached values (those are retrieved only once)
    if posid not in d.ecf_serial:
        d.ecf_serial[posid] = prn.readOut(fpreadout.FR_FPSERIALNUMBER).strip()
    if (posid not in d.ecf_addedmem or d.ecf_addedmem[posid] == '') and "ignoremfadded" not in extra:
        try:
            if "EMULADOR" in d.ecf_serial[posid]:
                # For BEMATECH emulator only
                val = ["2000-01-01T00:00:00", "2000-01-01T00:00:00", ""]
                return
            else:
                # Read from printer
                val = prn.readOut(fpreadout.FR_MFADDED).split('\0')
        except:
            logger.exception("Erro obtendo FR_MFADDED da impressora fiscal")
            val = ["1981-01-01T01:11:10", "1982-02-02T02:22:20", "0"]
        # TS USER
        ts = val[0].replace("-", "").replace(":", "").split('T')
        d.ecf_userdate[posid] = ts[0]
        d.ecf_usertime[posid] = ts[1]
        # TS SOFTWARE
        ts = val[1].replace("-", "").replace(":", "").split('T')
        d.ecf_swdate[posid] = ts[0]
        d.ecf_swtime[posid] = ts[1]
        # Added memory
        d.ecf_addedmem[posid] = val[2].strip()
    else:
        d.ecf_addedmem[posid] = ""
    if posid not in d.ecf_type:
        val = prn.readOut(fpreadout.FR_PRINTERTYPE).split('\0')
        d.ecf_brand[posid] = val[0].strip()
        d.ecf_model[posid] = val[1].strip()
        d.ecf_type[posid] = val[2].strip()
    if posid not in d.ecf_usernumber:
        d.ecf_usernumber[posid] = int(prn.readOut(fpreadout.FR_USERNUMBER))
    if posid not in d.ecf_posid:
        d.ecf_posid[posid] = int(prn.readOut(fpreadout.FR_POSSTATION))

    # Non-cached values
    if "tslastdoc" in extra:
        d.tslastdoc[posid] = prn.readOut(fpreadout.FR_DTLASTDOC).replace("-", "").replace(":", "").split("T")
        d.dateLastDoc[posid] = d.tslastdoc[posid][0]
        d.timeLastDoc[posid] = d.tslastdoc[posid][1]
    if "coosLastZ" in extra:
        d.coosLastZ[posid] = prn.readOut(fpreadout.FR_COOSLASTZ).split(',')
    if "taxByIndex" in extra:
        _build_tax_by_index(prn, posid, d)
    if ("aInfoZ" in extra) or ("allTax" in extra):
        # Read information from the last Z
        val = prn.readOut(fpreadout.FR_ZREPORTDATE).replace("-", "").replace(":", "").split("T")
        d.dateLastZ[posid] = val[0]
        d.timeLastZ[posid] = val[1]
        try:
            d.aInfoZ[posid] = prn.readOut(fpreadout.FR_INFOLASTZ).split(',')
            d.lastZGT[posid] = d.aInfoZ[posid][15]
            d.lastZGT[posid] = d.lastZGT[posid][:-2] + '.' + d.lastZGT[posid][-2:]
        except:
            logger.exception("Could not perform fiscal-printer readout FR_INFOLASTZ - this is expected in the emulator only!")
            d.aInfoZ[posid] = ["0" for _ in range(40)]
        if int(d.aInfoZ[posid][2]) == 0:
            # Using the emulator the fiscal memory is always zeroed - so make a readout to get the real CRZ
            d.aInfoZ[posid][2] = int(prn.readOut(fpreadout.FR_ZNUMBER))
        if "allTax" in extra:
            # Build the "allTax" and "taxByIndex" information
            _build_all_taxes(prn, posid, d)
    return d


def _build_all_taxes(prn, pos_id, d):
    # type: (fp, int, CommonFiscalData) -> None

    d.ecf_printer_taxes = prn.genericFiscalCMD(fpcmds.FPRN_GETTAXLIST).split(',,') \
        if (d.ecf_printer_taxes is None or len(d.ecf_printer_taxes) == 0) else d.ecf_printer_taxes
    all_tax = {}
    for taxType in range(0, 2):
        type = "S" if taxType else "T"
        for tax in d.ecf_printer_taxes[taxType].split(','):
            if tax:
                idx = int(tax[0:2])
                taxRate = int(tax[3:])
                initial = (idx - 1) * 14
                final = (idx - 1) * 14 + 14
                taxAcc = 0
                try:
                    taxAcc = int(d.aInfoZ[pos_id][16][initial:final])
                except Exception:
                    logger.exception("Erro acessando index %d:%d de %s" % (initial, final, d.aInfoZ[pos_id][16]))
                key = "%02d%s%04d" % (idx, type, taxRate)
                all_tax[key] = taxAcc

    all_tax["F1"] = d.aInfoZ[pos_id][19]      # Substituição tributária - ICMS
    all_tax["I1"] = d.aInfoZ[pos_id][17]      # Isento - ICMS
    all_tax["N1"] = d.aInfoZ[pos_id][18]      # Não incidência de ICMS
    all_tax["FS1"] = d.aInfoZ[pos_id][22]     # Substituição tributária ISSQN
    all_tax["IS1"] = d.aInfoZ[pos_id][20]     # Isento - ISSQN
    all_tax["NS1"] = d.aInfoZ[pos_id][21]     # Não incidência - ISSQN

    all_tax["OPNF"] = 0               # Operações não fiscais
    for i in range(0, 28):
        initial = i * 14
        final = i * 14 + 14
        try:
            all_tax["OPNF"] += int(d.aInfoZ[pos_id][29][initial:final])    # Soma os 28 totalizadores
        except Exception:
            logger.exception("Erro acessando index %d:%d de %s" % (initial, final, d.aInfoZ[pos_id][29]))
    all_tax["OPNF"] = "%014d" % all_tax["OPNF"]

    all_tax["DT"] = d.aInfoZ[pos_id][23]      # descontos - ICMS
    all_tax["DS"] = d.aInfoZ[pos_id][24]      # descontos - ISSQN
    all_tax["AT"] = d.aInfoZ[pos_id][25]      # acréscimos - ICMS
    all_tax["AS"] = d.aInfoZ[pos_id][26]      # acréscimos - ISSQN
    all_tax["Can-T"] = d.aInfoZ[pos_id][27]   # cancelamento - ICMS
    all_tax["Can-S"] = d.aInfoZ[pos_id][28]   # cancelamento - ISSQN
    d.allTax[pos_id] = all_tax


def _build_tax_by_index(prn, pos_id, d):
    # type: (fp, int, CommonFiscalData) -> None
    if pos_id not in d.taxByIndex:
        d.ecf_printer_taxes = prn.genericFiscalCMD(fpcmds.FPRN_GETTAXLIST).split(',,') \
            if d.ecf_printer_taxes is not None else d.ecf_printer_taxes
        tax_by_index = {"SI": "IS1", "SF": "FS1", "SN": "NS1"}
        for taxType in range(0, 2):
            type = "S" if taxType else "T"
            for tax in d.ecf_printer_taxes[taxType].split(','):
                if tax:
                    idx = int(tax[0:2])
                    tax_rate = int(tax[3:])
                    key = "%02d%s%04d" % (idx, type, tax_rate)
                    tax_by_index["%d" % idx] = key
                    tax_by_index["%02d" % idx] = key
                    tax_by_index["%04d" % tax_rate] = key

        d.taxByIndex[pos_id] = tax_by_index


def _decimal_to_fixed_int(v):
    return int((D(v) * 100).quantize(D("1"), decimal.ROUND_DOWN))


def _calculate_OPNF(posid, period):
    conn = None
    OPNF = None
    for i in xrange(0, 3, 1):
        try:
            conn = persistence.Driver().open(mbcontext, dbname=str(posid))
            if not period:
                cursor = conn.select("""SELECT BusinessPeriod FROM posctrl.PosState WHERE PosId=%d""" % int(posid))
                period = cursor.get_row(0).get_entry(0)
            cursor = conn.select("""
            SELECT
                COALESCE(tdsum(Amount,2),'0.00') AS OPNF
            FROM account.Transfer
                WHERE PosId=%d
                AND Period=%d
                AND Type IN (1,2,3)
            """ % (int(posid), int(period)))
            OPNF = cursor.get_row(0).get_entry(0)
            break
        except:
            logger.exception("Erro calculando OPNF. Posid=%d, Tentativa=%d" % (int(posid), i))
        finally:
            if conn:
                conn.close()
    return OPNF


#
# Main function (called by pyscripts)
#
def main():
    ret = mbcontext.MB_EasySendMessage("FiscalWrapper", TK_FISCALWRAPPER_GET_NF_TYPE, format=FM_PARAM, data=None)
    # Processamento Finalizado com Sucesso
    if ret.token == TK_SYS_ACK:
        nf_type = ret.data.upper()
        if nf_type == "PAF":
            global verify_gt
            verify_gt = str(get_storewide_config("Store.VerifyGT", True)).lower() != "false"
            global verify_time
            verify_time = str(get_storewide_config("Store.VerifyTime", True)).lower() != "false"
            global verify_printer_id
            verify_printer_id = str(get_storewide_config("Store.VerifyPrinterId", True)).lower() != "false"
            pyscripts.subscribe_event_listener("FISCAL_STARTUP", event_fiscal_startup)
            pyscripts.subscribe_event_listener("FISCAL_ORDER_STATE", event_fiscal_order_state)
            pyscripts.subscribe_event_listener("FISCAL_CMD_EXECUTED", event_fiscal_cmd_executed)
            pyscripts.subscribe_event_listener("CASHLESS", event_cashless)
            pyscripts.subscribe_event_listener("FISCAL_PROMOTIONAL_MSG", event_fiscal_promotional_msg)
            pyscripts.subscribe_event_listener("POS_ACCOUNT_TRANSFER_SYNC", event_account_transfer)
            pyscripts.subscribe_event_listener("POS_QUERYCHANGESTATE", event_querychagestate)
            pyscripts.subscribe_event_listener("FISCAL_QUEUE_ERROR", event_fiscal_queue_error)
            pyscripts.subscribe_event_listener("pafVerifyLastZReduction", event_verify_last_z_reduction)
    else:
        raise Exception("Waiting for FiscalWrapper component")
