# -*- coding: utf-8 -*-

import base64
import bisect
import glob
import json
import logging
import os
import os.path
import re
import shutil
import zipfile
import zlib
from datetime import datetime, timedelta
from decimal import Decimal as D
from xml.etree import cElementTree as eTree

import fiscalpersistence
import printer
from bustoken import TK_FISCALWRAPPER_PROCESS_REQUEST, TK_FISCALWRAPPER_SEARCH_REQUEST, TK_FISCALWRAPPER_REPRINT, \
    TK_FISCALWRAPPER_SEFAZ_CONNECTIVITY, TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST, TK_SAT_STATUS_REQUEST, \
    TK_FISCALWRAPPER_EXPORT_FISCAL_FILES, TK_FISCALWRAPPER_GET_NF_TYPE, TK_SAT_OPERATIONAL_STATUS_REQUEST, \
    TK_FISCALWRAPPER_SAT_PROCESS_PAYMENT, TK_FISCALWRAPPER_SAT_PAYMENT_STATUS, TK_SAT_PROCESS_PAYMENT, \
    TK_SAT_PAYMENT_STATUS, TK_FISCALWRAPPER_CANCEL_ORDER, TK_SAT_CANCEL_ORDER, TK_FISCALWRAPPER_RE_SIGN_XML, \
    TK_FISCALWRAPPER_SITUATION, TK_FISCALWRAPPER_GET_CST, TK_FISCALWRAPPER_GET_BASE_REDUCTION, \
    TK_FISCALWRAPPER_GET_FISCAL_XML, TK_FISCALWRAPPER_GET_IBPT_TAX, TK_FISCALWRAPPER_GET_ORDERS_DATA, \
    TK_FISCALWRAPPER_GET_LAST_ORDER_ID, TK_FISCALWRAPPER_GET_CERTIFICATE_EXPIRATION_DAYS, \
    TK_FISCALWRAPPER_GET_CONTINGENCY_STATUS, TK_FISCALWRAPPER_CHANGE_CONTINGENCY_STATUS, TK_FISCALWRAPPER_PRINT_DONATION_COUPON
from common import FiscalParameterController
from comp_exceptions import EmptySearchException, VoidOrderException
from fiscalinterface import FiscalProcessor
from fiscalpaymentparser import convert_order_tenders_to_fiscal_tenders
from fiscalpersistence import FiscalDataRepository
from old_helper import OrderTaker, round_half_away_from_zero, remove_xml_namespace, convert_from_utf_to_localtime
from ibpttaxprocessor import IbptTaxProcessor
from messagehandler import EventHandler
from msgbus import TK_SYS_NAK, TK_SYS_ACK, MBEasyContext, MBException, FM_PARAM, MBMessage, FM_STRING
from nfce import NfceRequestBuilder, NfceConnectivityTester, NfceSituationChecker, NfceContingencia, NfceProcessor
from nfcecanceler import NfceCanceler
from nfcedisabler import OrderDisabler
from order_retriever import OrderRetrieverService
from persistence import Driver as DBDriver
from poslistener import get_updated_sale_line_defaults
from printer import DonationCouponPrinter
from sat import SatProcessor
from sysactions import get_model, get_posot, get_podtype
from systools import sys_log_exception
from typing import Optional, Union, Dict

logger = logging.getLogger("FiscalWrapper")
logger_coupons = logging.getLogger("FiscalWrapperCoupons")


class FiscalWrapperEventHandler(EventHandler):
    def __init__(self, mbcontext, fiscal_processor, printers, nfce_connectivity_tester, nfce_situation_checker, order_disabler, nfce_canceler, fiscal_parameter_controller, xml_enviados, xml_erros, export_xml_path, fiscal_sent_dir, nf_type, versao_ws, ibpt_tax_processor, order_retriever_service, xml_inconsistentes, donation_coupon_printer, nfce_contingencia, period_to_retry_orders_with_exception, synchronous_mode):
        # type: (MBEasyContext, Union[FiscalProcessor, NfceProcessor, SatProcessor], Dict[str, printer.FiscalPrinter], NfceConnectivityTester, NfceSituationChecker, OrderDisabler, NfceCanceler, FiscalParameterController, str, str, str, str, str, int, IbptTaxProcessor, OrderRetrieverService, str, DonationCouponPrinter, NfceContingencia, str, bool) -> None
        super(FiscalWrapperEventHandler, self).__init__(mbcontext)
        self.fiscal_processor = fiscal_processor
        self.printers = printers
        self.nf_type = nf_type  # type: str
        self.nfce_connectivity_tester = nfce_connectivity_tester
        self.nfce_situation_checker = nfce_situation_checker
        self.order_disabler = order_disabler
        self.order_retriever_service = order_retriever_service
        self.xml_enviados = xml_enviados
        self.xml_erros = xml_erros
        self.export_xml_path = export_xml_path
        self.fiscal_sent_dir = fiscal_sent_dir
        self.nfce_canceler = nfce_canceler
        self.versao_ws = versao_ws
        self.fiscal_parameter_controller = fiscal_parameter_controller
        self.ibpt_tax_processor = ibpt_tax_processor
        self.xml_inconsistentes = xml_inconsistentes
        self.donation_coupon_printer = donation_coupon_printer
        self.nfce_contingencia = nfce_contingencia
        self.period_to_retry_orders_with_exception = period_to_retry_orders_with_exception
        self.synchronous_mode = synchronous_mode

    def get_handled_tokens(self):
        return [TK_FISCALWRAPPER_PROCESS_REQUEST, TK_FISCALWRAPPER_SEARCH_REQUEST, TK_FISCALWRAPPER_REPRINT,
                TK_FISCALWRAPPER_SEFAZ_CONNECTIVITY, TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST, TK_FISCALWRAPPER_EXPORT_FISCAL_FILES, TK_FISCALWRAPPER_GET_NF_TYPE,
                TK_SAT_OPERATIONAL_STATUS_REQUEST, TK_FISCALWRAPPER_SAT_PROCESS_PAYMENT,
                TK_FISCALWRAPPER_SAT_PAYMENT_STATUS, TK_SAT_PROCESS_PAYMENT, TK_SAT_PAYMENT_STATUS, TK_FISCALWRAPPER_CANCEL_ORDER, TK_FISCALWRAPPER_RE_SIGN_XML,
                TK_FISCALWRAPPER_SITUATION, TK_FISCALWRAPPER_GET_CST, TK_FISCALWRAPPER_GET_BASE_REDUCTION, TK_FISCALWRAPPER_GET_FISCAL_XML, TK_FISCALWRAPPER_GET_IBPT_TAX,
                TK_FISCALWRAPPER_GET_LAST_ORDER_ID, TK_FISCALWRAPPER_GET_ORDERS_DATA, TK_FISCALWRAPPER_PRINT_DONATION_COUPON, TK_FISCALWRAPPER_GET_CERTIFICATE_EXPIRATION_DAYS,
                TK_FISCALWRAPPER_GET_CONTINGENCY_STATUS, TK_FISCALWRAPPER_CHANGE_CONTINGENCY_STATUS]

    def handle_message(self, msg):
        # type: (MBMessage) -> Union[None, bool]
        try:
            if msg.token == TK_FISCALWRAPPER_PROCESS_REQUEST:
                response = self._handle_process_request(msg)
            elif msg.token == TK_FISCALWRAPPER_GET_CERTIFICATE_EXPIRATION_DAYS:
                response = self._handle_get_certificate_expiration()
            elif msg.token == TK_FISCALWRAPPER_REPRINT:
                response = self._handle_process_request(msg, reprint=True)
            elif msg.token == TK_FISCALWRAPPER_SEARCH_REQUEST:
                response = self._handle_search_request()
            elif msg.token == TK_FISCALWRAPPER_SEFAZ_CONNECTIVITY:
                response = self._handle_sefaz_connectivity_request()
            elif msg.token == TK_FISCALWRAPPER_SAT_OPERATIONAL_STATUS_REQUEST:
                response = self._handle_sat_op_status_request(msg)
            elif msg.token == TK_FISCALWRAPPER_EXPORT_FISCAL_FILES:
                response = self._export_fiscal_files(msg)
            elif msg.token == TK_FISCALWRAPPER_GET_NF_TYPE:
                response = self._handle_get_nftype(msg)
            elif msg.token == TK_FISCALWRAPPER_SAT_PROCESS_PAYMENT:
                response = self._handle_sat_process_payment_request(msg)
            elif msg.token == TK_FISCALWRAPPER_SAT_PAYMENT_STATUS:
                response = self._handle_sat_payment_status_request(msg)
            elif msg.token == TK_FISCALWRAPPER_CANCEL_ORDER:
                response = self._handle_cancel_order(msg)
            elif msg.token == TK_FISCALWRAPPER_RE_SIGN_XML:
                response = self._handle_re_sign_xml()
            elif msg.token == TK_FISCALWRAPPER_SITUATION:
                response = self._handle_sefaz_situation(msg)
            elif msg.token == TK_FISCALWRAPPER_GET_FISCAL_XML:
                response = self._handle_fiscal_xml_request(msg.data, True)
            elif msg.token == TK_FISCALWRAPPER_GET_CST:
                response = self._handle_get_csts(msg)
            elif msg.token == TK_FISCALWRAPPER_GET_BASE_REDUCTION:
                response = self._handle_get_base_reductions(msg)
            elif msg.token == TK_FISCALWRAPPER_GET_IBPT_TAX:
                response = self._handle_get_ibpt_tax(msg)
            elif msg.token == TK_FISCALWRAPPER_PRINT_DONATION_COUPON:
                response = self._handle_print_donation_coupon(msg)
            elif msg.token == TK_FISCALWRAPPER_GET_CONTINGENCY_STATUS:
                response = self._handle_get_contingency_status(msg)
            elif msg.token == TK_FISCALWRAPPER_CHANGE_CONTINGENCY_STATUS:
                response = self._handle_change_contingency_status(msg)
            elif msg.token == TK_FISCALWRAPPER_GET_ORDERS_DATA:
                try:
                    orders_data_list_str = self.order_retriever_service.get_orders_data(msg.data)

                    msg.token = TK_SYS_ACK
                    self.mbcontext.MB_ReplyMessage(msg, data=orders_data_list_str)
                    return
                except Exception as ex:
                    logger.exception("Error handling TK_FISCALWRAPPER_GET_ORDERS_DATA")
                    msg.token = TK_SYS_NAK
                    self.mbcontext.MB_ReplyMessage(msg, data=ex.message)
                    return
            elif msg.token == TK_FISCALWRAPPER_GET_LAST_ORDER_ID:
                try:
                    last_order_id = self.order_retriever_service.get_last_order_id()

                    msg.token = TK_SYS_ACK
                    self.mbcontext.MB_ReplyMessage(msg, data=last_order_id)
                    return
                except Exception as ex:
                    logger.exception("Error handling TK_FISCALWRAPPER_GET_LAST_ORDER_ID")
                    msg.token = TK_SYS_NAK
                    self.mbcontext.MB_ReplyMessage(msg, data=ex.message)
                    return
            else:
                response = (False, "")

            msg.token = TK_SYS_ACK if response[0] else TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=response[1])

        except Exception as ex:
            sys_log_exception("Unexpected exception when handling event {0}. Error message: {1}".format(msg.token, ex.message))
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=str(ex))
        except:
            sys_log_exception("Unhandled BaseException Message")
            msg.token = TK_SYS_NAK
            self.mbcontext.MB_ReplyMessage(msg, data=str("Unhandled BaseException"))

        return False

    def terminate_event(self):
        self.fiscal_processor.terminate()

    def _handle_get_nftype(self, _):
        # type: (MBMessage) -> (str, str)
        return True, self.nf_type

    def _handle_get_certificate_expiration(self):
        if self.nf_type == "NFCE":
            ret = self.fiscal_processor.do_validation(get_days_to_expiration=True)
            if not ret[0]:
                return False, ret[1]
            return True, ret[1]

    def _handle_process_request(self, msg, reprint=False):
        # type: (MBMessage, Optional[bool]) -> (str, str)

        if self.nf_type != "PAF":
            ret = self.fiscal_processor.do_validation()
            if not ret[0]:
                return False, ret[1]

        if reprint:
            data = msg.data.split('\0')
            posid = data[0]
            orderid = data[1]
            danfe_type = data[2] if len(data) > 2 else ""
            model = get_model(posid)
            order = eTree.XML(get_posot(model).orderPicture(posid=posid, orderid=orderid))
            order = order.find("Order")

            # Add default quantity info to order pict
            dict_list = []
            for line in order.findall("SaleLine"):
                line_number = line.get('lineNumber')
                item_id = line.get('itemId')
                part_code = line.get('partCode')
                level = line.get('level')
                get_updated_sale_line_defaults(dict_list, orderid, int(line_number), item_id, part_code, line.get('qty'), int(level), get_podtype(model))
                for corrected_line in dict_list:
                    corrected_line_dict = json.loads(corrected_line)
                    if corrected_line_dict['line_number'] == line_number and \
                       corrected_line_dict['item_id'] == item_id and \
                       corrected_line_dict['part_code'] == part_code and \
                       corrected_line_dict['level'] == level:
                        line_orig_qty = line.get('qty')
                        line.set('addedQty', str(max(0.0, float(line_orig_qty) - float(corrected_line_dict['default_qty']))))
                        line.set('defaultQty', str(float(corrected_line_dict['default_qty'])))

        else:
            data = msg.data.split('\0')
            posid = data[0]
            orderid = data[1] if len(data) > 1 else ""
            danfe_type = data[2] if len(data) > 2 else ""
            model = get_model(posid)
            order = eTree.XML(get_posot(model).orderPicture(posid=posid, orderid=orderid))
            order = order.find("Order") if order.find("Order") else order
            if not orderid:
                orderid = order.get("orderId")

            fiscalization_date = order.find("CustomOrderProperties/OrderProperty[@key='FISCALIZATION_DATE']")
            if fiscalization_date is not None:
                return True, ""

        with FiscalDataRepository(self.mbcontext) as fiscal_repository:  # type: fiscalpersistence.FiscalDataRepository
            fiscal_ok = False
            try:
                tenders = convert_order_tenders_to_fiscal_tenders(order)

                customer_name = order.find("CustomOrderProperties/OrderProperty[@key='CUSTOMER_NAME']")
                if customer_name is not None:
                    customer_name = customer_name.get("value")

                total_taxes = self.ibpt_tax_processor.ibpt_tax_calculator(order)

                if reprint:
                    if self.nf_type not in ("SAT", "MFE"):
                        nfce_fiscal_processor = self.fiscal_processor  # type: NfceProcessor
                        params = {'tenders': tenders, 'order': order, 'customer_name': customer_name, 'url_sefaz': nfce_fiscal_processor.url_sefaz, 'posid': posid, 'total_taxes': total_taxes}
                    else:
                        params = {'tenders': tenders, 'order': order, 'customer_name': customer_name, 'posid': posid, 'total_taxes': total_taxes}
                    report = self._reprint_sat_or_nfce(fiscal_repository.get_xml_request(orderid), fiscal_repository.get_xml_response(orderid), params, danfe_type)
                    if report[0]:
                        return True, report[1]
                    else:
                        return False, report[1]

                logger.info("Nova order para processamento")
                fiscal_data = self.fiscal_processor.request_fiscal(posid, order, tenders, self.nf_type == "PAF")
                fiscal_ok = True

                if self.nf_type in ("SAT", "MFE"):
                    sat_fiscal_processor = self.fiscal_processor  # type: SatProcessor
                    sat_used = sat_fiscal_processor.last_sat_used[posid]
                    sat_used = sat_used[3:]
                    response_xml = eTree.tostring(fiscal_data.find("FiscalData"))
                    base64_response = base64.b64encode(response_xml)

                    fiscal_repository.start_save_fiscal_data_thread(posid, order, fiscal_data.find("XmlRequest").text.strip(), sat_used, 1, base64_response)
                    if danfe_type in self.printers:
                        selected_printer = self.printers[danfe_type]
                    else:
                        selected_printer = self.printers[""]

                    report = selected_printer.print_fiscal(posid, order, tenders, fiscal_data.find("XmlRequest"), fiscal_data.find("FiscalData"), total_taxes, customer_name)
                else:
                    request_xml = eTree.XML(fiscal_data[0])
                    response_xml = None
                    xml_response_base64 = None
                    if fiscal_data[1] is not None:
                        response_xml = eTree.XML(fiscal_data[1])
                        xml_response_base64 = base64.b64encode(fiscal_data[1])
                    idx_start = fiscal_data[0].find("<NFe")
                    idx_final = int(str(fiscal_data[0].find("</NFe"))) + 6
                    xml_string = fiscal_data[0][idx_start:idx_final]

                    contingencia = request_xml.find(
                        "{{{0}}}Body/{{{1}}}nfeDadosMsg/{{{2}}}enviNFe/{{{2}}}NFe/{{{2}}}infNFe/{{{2}}}ide/{{{2}}}tpEmis".format(
                            NfceRequestBuilder.NAMESPACE_SOAP,
                            NfceRequestBuilder.NAMESPACE_AUTORIZACAO if self.versao_ws in (1, 3) else NfceRequestBuilder.NAMESPACE_AUTORIZACAO_4,
                            NfceRequestBuilder.NAMESPACE_NFE)).text
                    if not contingencia == "9":
                        if self.nf_type == "PAF":
                            xml_string = "<nfeProc>" + xml_string + "<protNFe versao=\"%.2f\" xmlns=\"%s\"><infProt><cStat>100</cStat></infProt></protNFe></nfeProc>" % (3.1 if self.versao_ws in (1, 3) else 4, NfceRequestBuilder.NAMESPACE_NFE)
                        else:
                            xml_string = fiscal_data[2]
                    xml_base64 = base64.b64encode(xml_string)

                    if self.nf_type == "PAF":
                        originator_id = order.get("posId")
                    else:
                        originator_id = order.get("originatorId")[3:]

                    fiscal_repository.start_save_fiscal_data_thread(originator_id, order, xml_base64, "00", 0 if contingencia == "9" else 1, xml_response_base64)

                    if self.printers[""] and self.nf_type != "PAF":
                        report = self.printers[""].print_fiscal(posid, order, tenders, request_xml, response_xml, total_taxes, customer_name)
                    else:
                        report = ""

                self._print_coupon(report)

                return True, report

            except VoidOrderException as ex:
                fiscal_ok = False
                return False, '\0'.join(map(str, (fiscal_ok, str(ex))))

            except MBException:
                logger.exception("Erro de Impressão")
                return False, '\0'.join(map(str, (fiscal_ok, "Verifique a Impressora de Cupom Fiscal")))

            except Exception as ex:
                logger.exception("Nota Rejeitada pela SEFAZ")
                return False, '\0'.join(map(str, (fiscal_ok, str(ex))))

    def _print_coupon(self, report):
        try:
            logger_coupons.info("\n\n***************************************************************\n\n")
            logger_coupons.info(report)
        except Exception as _:
            logger_coupons.info("Error logging coupon")
        finally:
            logger_coupons.info("\n\n***************************************************************\n\n\n\n")

    def _handle_sefaz_connectivity_request(self):
        if self.nf_type == "NFCE":
            self.nfce_connectivity_tester.logger = logger
            if self.nfce_connectivity_tester.test_connectivity():
                return True, "Conexao com Sefaz OK!"
            else:
                return False, "Nao foi possivel se conectar com a Sefaz."
        else:
            return False, "Loja nao opera com NFCE"

    def _handle_sefaz_situation(self, msg):
        if self.nf_type == "NFCE":
            initial_date, final_date = msg.data.split('\0')
            initial_date = initial_date[:4] + '-' + initial_date[4:6] + '-' + initial_date[6:]
            final_date = final_date[:4] + '-' + final_date[4:6] + '-' + final_date[6:]

            if self.versao_ws == 1:
                namespace_consulta_situacao = NfceRequestBuilder.NAMESPACE_CONSULTA_SITUACAO
                tag_consulta_nf_result = "nfeConsultaNF2Result"
            elif self.versao_ws == 3:
                namespace_consulta_situacao = NfceRequestBuilder.NAMESPACE_CONSULTA_SITUACAO_3
                tag_consulta_nf_result = "nfeConsultaNFResult"
            else:
                namespace_consulta_situacao = NfceRequestBuilder.NAMESPACE_CONSULTA_SITUACAO_4
                tag_consulta_nf_result = "nfeResultMsg"

            with FiscalDataRepository(self.mbcontext) as fiscalrepository:
                logger.info("Tratando Evento Consultar Situacao XML")
                conn = None
                try:
                    conn = DBDriver().open(self.mbcontext, service_name="FiscalPersistence")
                    offset = 0
                    while True:
                        sql = """SELECT PosId, OrderId, XMLRequest, OrderPicture
                                  FROM fiscal.FiscalData
                                  WHERE date(DataNota, 'unixepoch', 'localtime') >= '%s'
                                  AND date(DataNota, 'unixepoch', 'localtime') <= '%s'
                                  ORDER BY OrderId ASC LIMIT 500 OFFSET %s""" % (initial_date, final_date, offset)
                        cursor = conn.select(sql)
                        if cursor.rows() == 0:
                            break
                        offset += cursor.rows()
                        eTree.register_namespace('', NfceRequestBuilder.NAMESPACE_NFE)
                        for row in cursor:
                            pos_id, order_id, request, order_picture = map(row.get_entry, ("PosId", "OrderId", "XMLRequest", "OrderPicture"))
                            logger.info("Order %s " % order_id)

                            request_str = base64.b64decode(request + "=" * ((4 - len(request) % 4) % 4))
                            req = eTree.XML(request_str)

                            c_stat = req.find("{{{0}}}protNFe/{{{0}}}infProt/{{{0}}}cStat".format(NfceRequestBuilder.NAMESPACE_NFE))
                            if c_stat is not None:
                                c_stat = c_stat.text

                            if c_stat in ("100", "150"):
                                logger.info("Order %s ja estava com status 100" % order_id)
                                continue
                            try:
                                logger.info("Buscando Protocolo. Order %s " % order_id)

                                nfe = req.find("{{{0}}}NFe/{{{0}}}infNFe".format(NfceRequestBuilder.NAMESPACE_NFE))
                                nfe_key = nfe.attrib["Id"]
                                nfe = nfe_key[3:]
                                data_emissao = req.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}dhEmi".format(
                                    NfceRequestBuilder.NAMESPACE_NFE)).text
                                serie_nota = req.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}serie".format(
                                    NfceRequestBuilder.NAMESPACE_NFE)).text
                                serie_nota = serie_nota.zfill(3)
                                numero_nota = req.find("{{{0}}}NFe/{{{0}}}infNFe/{{{0}}}ide/{{{0}}}nNF".format(
                                    NfceRequestBuilder.NAMESPACE_NFE)).text
                                numero_nota = numero_nota.zfill(9)

                                self.nfce_situation_checker.logger = logger
                                fiscal_data = self.nfce_situation_checker.check_situation_nfe(nfe)
                                if not fiscal_data:
                                    message = "Problemas ao tentar consultar a situação da nota na sefaz. Vamos tentar novamente depois."
                                    raise Exception(message)

                                logger.info("Protocolo recebido. Order %s " % order_id)
                                fiscal_data_xml = eTree.XML(fiscal_data)

                                c_stat = fiscal_data_xml.find(
                                    ("{{{0}}}Body/{{{1}}}" + tag_consulta_nf_result + "/{{{2}}}retConsSitNFe/{{{2}}}cStat").format(
                                        NfceRequestBuilder.NAMESPACE_SOAP,
                                        namespace_consulta_situacao,
                                        NfceRequestBuilder.NAMESPACE_NFE))
                                if c_stat is None:
                                    raise Exception("Campo cStat Nao Encontrado")
                                else:
                                    c_stat = c_stat.text
                                if c_stat in ("100", "150", "613"):  # 100 = ok; 613 = Chave de Acesso difere da existente em BD;
                                    if c_stat in ("613", ):
                                        try:
                                            logger.info("Regerando XML. Order %s " % order_id)
                                            order_picture = eTree.XML(base64.b64decode(order_picture + "=" * ((4 - len(order_picture) % 4) % 4)))
                                            envelopado, data_emissao, serie_nota, numero_nota = self.fiscal_processor.nfce_request_builder.build_request(order_picture, False, None, None)
                                            serie_nota = str(serie_nota).zfill(3)
                                            numero_nota = str(numero_nota).zfill(9)
                                            logger.info("XML Regerado. Order %s " % order_id)
                                            index1 = envelopado.index("<NFe")
                                            index2 = envelopado.index("</NFe>")
                                            new_req = envelopado[index1:index2 + 6]

                                            request_str = request_str[:request_str.index("<NFe ")] + new_req + request_str[request_str.index("</NFe>") + 6:]
                                            req = eTree.XML(request_str)
                                        except Exception:
                                            logger.exception("Erro ao gerar XML da order %s" % order_id)
                                            fiscalrepository.set_nfce_sent(order_id, -1)
                                            continue

                                    if c_stat in ("613", ):
                                        nfe_key = \
                                        req.find("{{{0}}}NFe/{{{0}}}infNFe".format(NfceRequestBuilder.NAMESPACE_NFE)).attrib['Id']
                                        chave_xml = nfe_key[3:]

                                        self.nfce_situation_checker.logger = logger
                                        fiscal_data = self.nfce_situation_checker.check_situation_nfe(chave_xml)
                                        if not fiscal_data:
                                            message = "Problemas ao tentar consultar a situação da nota na sefaz. Vamos tentar novamente depois."
                                            raise Exception(message)

                                        logger.info("Protocolo recebido. Order %s " % order_id)
                                        fiscal_data_xml = eTree.XML(fiscal_data)

                                        c_stat = fiscal_data_xml.find(
                                            ("{{{0}}}Body/{{{1}}}"+ tag_consulta_nf_result + "/{{{2}}}retConsSitNFe/{{{2}}}cStat").format(
                                                NfceRequestBuilder.NAMESPACE_SOAP,
                                                namespace_consulta_situacao,
                                                NfceRequestBuilder.NAMESPACE_NFE))
                                        if c_stat is None:
                                            raise Exception("Campo cStat Nao Encontrado")
                                        else:
                                            c_stat = c_stat.text
                                        if c_stat not in ("100",):
                                            raise Exception("Campo cStat diferente de 100")

                                    inf_prot = fiscal_data_xml.find(
                                        ("{{{0}}}Body/{{{1}}}" + tag_consulta_nf_result + "/{{{2}}}retConsSitNFe/{{{2}}}protNFe/{{{2}}}infProt").format(
                                            NfceRequestBuilder.NAMESPACE_SOAP,
                                            namespace_consulta_situacao,
                                            NfceRequestBuilder.NAMESPACE_NFE))
                                    inf_prot.attrib.pop("Id", None)
                                    new_req = request_str[:request_str.index("<infProt")] + eTree.tostring(inf_prot) + request_str[request_str.index("</protNFe"):]
                                    xml_base64 = base64.b64encode(new_req)
                                    fiscalrepository.set_nfce_sent_with_xml_bkoffice(order_id, xml_base64, 1, 0)

                                    dir_arquivo = os.path.join(data_emissao[0:4], data_emissao[5:7], data_emissao[8:10])
                                    dir_nota = os.path.join(self.fiscal_sent_dir, self.xml_enviados, dir_arquivo)
                                    self._create_directory_if_not_exists(dir_nota)
                                    nfce_file_name = "{0}_{1}_{2}_nfe_proc_pos{3}_{4}.xml".format(serie_nota, numero_nota, order_id.zfill(9), str(pos_id).zfill(2), nfe_key)

                                    for xml_file in glob.glob(dir_nota + '/*' + order_id.zfill(9) + '_nfe_proc_pos*'):
                                        os.remove(xml_file)

                                    with open(os.path.join(dir_nota, nfce_file_name), "w+") as nfe_proc_file:
                                        nfe_proc_file.write(new_req)
                                else:
                                    raise Exception("Status diferente de 100. %s" % c_stat)
                            except Exception:
                                logger.exception("Erro ao buscar protocolo da order %s" % order_id)
                                continue

                except Exception as _:
                    logger.exception("Erro ao Consultar Status dos XMLs")
                    return False, "Erro ao Consultar Status dos XMLs"
                finally:
                    if conn:
                        conn.close()

            return True, "Status Salvos com Sucesso"
        else:
            return False, "Loja nao opera com NFCE"

    def _handle_get_csts(self, _):
        return True, self.fiscal_parameter_controller.get_all_products_csts()

    def _handle_get_base_reductions(self, _):
        return True, self.fiscal_parameter_controller.get_all_products_base_reductions()

    def _handle_get_ibpt_tax(self, msg):
        order_xml = eTree.XML(msg.data)
        taxes_dict = self.ibpt_tax_processor.ibpt_tax_calculator(order_xml)
        return True, str(taxes_dict)

    def _handle_print_donation_coupon(self, msg):
        params = msg.data.split("\x00")
        report = self.donation_coupon_printer.print_coupon(*params)
        return True, report

    def _handle_get_contingency_status(self, _):
        return True, "Enabled" if self.nfce_contingencia.contingencia else "Disabled"

    def _handle_change_contingency_status(self, _):
        self.nfce_contingencia.force_contingency = not self.nfce_contingencia.force_contingency
        if self.nfce_contingencia.force_contingency:
            logger.info("Entrando em contingência forçada via menu suporte")
            self.nfce_contingencia.entra_contingencia("Contingencia forcada")
        else:
            self.nfce_contingencia.contingencia = False
            self.nfce_contingencia.process_now = True
            self.nfce_contingencia.start_contingencia()

        return True, "Contingency status successfully changed"

    def handle_event(self, subject, evt_type, data, msg):
        if subject == "ORDER_MODIFIED" and evt_type == "PAID":
            order = eTree.XML(data).find("Order")
            order_id = order.get("orderId")
            with FiscalDataRepository(self.mbcontext) as fiscal_repository:  # type: fiscalpersistence.FiscalDataRepository
                fiscal_repository.set_order_picture(order_id, base64.b64encode(eTree.tostring(order)))
        elif subject == "ORDER_MODIFIED" and evt_type == "VOID_ORDER":
            order = eTree.XML(data).find(".//Order")
            order_id = order.get("orderId")
            with FiscalDataRepository(self.mbcontext) as fiscal_repository:  # type: fiscalpersistence.FiscalDataRepository
                fiscal_repository.set_order_canceled(order_id)
        elif subject == "DisableNfceOrder":
            self._handle_disable_orders()
        elif subject == "ReSignXMLs":
            self._handle_re_sign_xml()
        elif subject == "OrderManagerFiscalXmlRequest":
            self._handle_fiscal_xml_request(data)
        elif subject == "CheckIfFiscalXmlIsCreatedInFolder":
            self._handle_check_if_fiscal_xml_is_created_in_folder()
        elif subject == "RetryFiscalOrdersWithException":
            self._handle_retry_fiscal_orders_with_exception()

    def _handle_search_request(self):
        if self.nf_type not in ("SAT", "MFE"):
            return False, "Loja não opera com SAT"

        sat_status_list = {}
        sat_processor = self.fiscal_processor  # type: SatProcessor
        for i in range(0, sat_processor.sat_service_finder.max_sat_number + 1):
            sat_service_name = "SAT%s" % str(i).zfill(2)
            try:
                ret = self.mbcontext.MB_EasySendMessage(sat_service_name, TK_SAT_STATUS_REQUEST, format=FM_PARAM, timeout=100 * 100000)

                if ret.token == TK_SYS_ACK:
                    sat_status_list[sat_service_name] = ret.data
                else:
                    sat_status_list[sat_service_name] = "ERROR"
            except Exception as ex:
                logger.error("Erro buscando SAT - Exception: %s", str(ex))
                sat_status_list[sat_service_name] = "Desabilitado"

        return True, str(sat_status_list)

    def _handle_disable_orders(self):
        if not self.nf_type == "NFCE":
            return
        try:
            self.order_disabler.disable_all_orders()
        except Exception as _:
            logger.exception("Erro inutilizando notas")

    def _handle_sat_op_status_request(self, msg):
        pos_id = msg.data

        if self.nf_type not in ("SAT", "MFE"):
            return False, "Loja não opera com SAT"

        sat_info_list = []
        sat_service_name = "SAT%s" % pos_id.zfill(2)
        try:
            ret = self.mbcontext.MB_EasySendMessage(sat_service_name, TK_SAT_OPERATIONAL_STATUS_REQUEST, format=FM_PARAM, timeout=100 * 100000)
            sat_info_list.append(ret.data)
        except MBException as ex:
            logger.info("Error searching SAT on POS#{}: {}".format(pos_id, str(ex)))
            sat_info_list.append("ERROR - Desabilitado")

        return True, str(sat_info_list)

    def _export_fiscal_files(self, msg):
        nok = False, 'Erro ao exportar arquivos fiscais'

        try:
            parse_ok, start_date, end_date = self._parse_date_from_fiscal_screen(msg.data)
            if not parse_ok:
                return nok

            try:
                folder_ok, folders = self._find_fiscal_folders(start_date, end_date, msg.data)
                if not folder_ok:
                    return nok
            except EmptySearchException as ex:
                return False, ex.message

            zip_ok, zip_path = self.zip_folders(folders)
            if not zip_ok:
                return nok

            return True, zip_path

        except Exception as ex:
            logger.error("Erro ao exportar arquivos fiscais %s", str(ex))

        return nok

    @staticmethod
    def _parse_date_from_fiscal_screen(dates):
        try:
            # parse das datas: yyyy/mm/dd;yyyy/mm/dd
            match = re.search(r'(\d+/\d+/\d+);(\d+/\d+/\d+)', dates)
            if match:
                dateSplit = dates.split(";")
                startDate = dateSplit[0]
                endDate = dateSplit[1]
                return True, startDate, endDate

        except Exception as ex:
            logger.error("Erro ao parsear datas (_parse_date_from_fiscal_screen) %s", str(ex))

        return False, '', ''

    def _find_fiscal_folders(self, start_date, end_date, msg):
        try:
            logger.info("start_date: " + start_date)
            logger.info("end_date: " + end_date)

            xml_type = self.xml_enviados if msg.split(";")[2] == '1' else self.xml_erros
            path = os.path.join(self.fiscal_sent_dir, xml_type)
            logger.info("path: " + path)

            export_folder = os.path.join(path, 'ExportTemp')
            logger.info("export_folder: " + export_folder)

            folders = filter(lambda f: os.path.isdir(f), glob.glob(path + '/*/*/*'))
            logger.info("lambda: " + str((lambda f: os.path.isdir(f), glob.glob(path + '/*/*/*'))))

            folders = [s.replace(path + "\\", '').replace(path + "/", '').replace('\\', '/') for s in folders]
            logger.info("folders after replace: " + str(folders))

            folders.sort()
            logger.info("folders after sort: " + str(folders))

            folders = folders[bisect.bisect_left(folders, start_date):bisect.bisect_right(folders, end_date)]
            logger.info("folders bisect_left: " + str(bisect.bisect_left(folders, start_date)))
            logger.info("folders bisect_right: " + str(bisect.bisect_right(folders, end_date)))
            logger.info("folders after bisect: " + str(folders))

            if folders:
                shutil.rmtree(export_folder, True)
                for item in folders:
                    shutil.copytree(os.path.join(path, item), os.path.join(export_folder, item))

                return True, export_folder
            else:
                raise EmptySearchException("Nenhum arquivo encontrado")

        except EmptySearchException as ex:
            raise ex

        except Exception as ex:
            logger.error("Erro ao buscar diretorios (_find_fiscal_folders) %s", str(ex))

        return False, ''

    def zip_folders(self, folder):
        try:
            zip_name = 'export'
            zip_complete_name = zip_name + '.zip'

            try:
                os.remove(os.path.join(self.export_xml_path, zip_complete_name))
            except OSError:
                pass

            self.zip(folder, zip_name)
            shutil.move(zip_complete_name, self.export_xml_path)
            shutil.rmtree(folder, True)
            return True, zip_complete_name
        except Exception as ex:
            logger.error("Erro ao zipar o diretorio temporario (zip_folders) %s", str(ex))
            shutil.rmtree(folder, True)

        return False, ''

    @staticmethod
    def zip(src, dst):
        zf = zipfile.ZipFile("%s.zip" % dst, "w", zipfile.ZIP_DEFLATED)
        abs_src = os.path.abspath(src)
        for dirname, subdirs, files in os.walk(src):
            for filename in files:
                absname = os.path.abspath(os.path.join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                zf.write(absname, arcname)
        zf.close()

    def _handle_sat_process_payment_request(self, msg):
        if self.nf_type not in ("MFE",):
            return True, ''
        sat_service_name = self.fiscal_processor.sat_service_finder.find_and_lock_sat_service(msg.data.split("\0")[1])
        msg = self.mbcontext.MB_EasySendMessage(sat_service_name, TK_SAT_PROCESS_PAYMENT, format=FM_PARAM, data=msg.data)
        self.fiscal_processor.sat_service_finder.unlock_sat_service(sat_service_name)
        return True, msg.data

    def _handle_sat_payment_status_request(self, msg):
        if self.nf_type not in ("MFE",):
            return True, ''

        sat_service_name = self.fiscal_processor.sat_service_finder.find_and_lock_sat_service(msg.data.split("\0")[1])
        msg = self.mbcontext.MB_EasySendMessage(sat_service_name, TK_SAT_PAYMENT_STATUS, format=FM_PARAM, data=msg.data)
        self.fiscal_processor.sat_service_finder.unlock_sat_service(sat_service_name)
        return True, msg.data

    def _handle_cancel_order(self, msg):
        pos_id, order_id = msg.data.split("|")
        model = get_model(pos_id)
        order = eTree.XML(get_posot(model).orderPicture(pos_id, order_id))
        if order.tag == "Orders":
            order = order.find("Order")

        order_id = order.get('orderId')
        fiscalization_date = order.find(".//CustomOrderProperties/OrderProperty[@key='FISCALIZATION_DATE']")
        if fiscalization_date is None:
            return False, "Pedido ainda não fiscalizado"
        formatted_fiscalization_date = datetime.strptime(fiscalization_date.get("value"), "%Y-%m-%dT%H:%M:%S")
        since_datetime = datetime.now() - timedelta(minutes=30)
        if convert_from_utf_to_localtime(formatted_fiscalization_date).replace(tzinfo=None) < since_datetime:
            return False, "Pedido excedeu o tempo limite para cancelamento fiscal (30 minutos)"

        justificativa = "Teste de cancelamento"

        if self.nf_type == 'NFCE':
            with FiscalDataRepository(self.mbcontext) as fiscal_repository:
                order_data = fiscal_repository.get_xml_response(order_id)
                if order_data is None:
                    return False, "Só é possível cancelar vendas já autorizadas"
                status, data = self.nfce_canceler.cancel_order(order_data, justificativa)
                if status:
                    self.order_disabler.order_repository.mark_order_canceled(pos_id, order_id)
                return status, data

        if self.nf_type == 'SAT':
            with FiscalDataRepository(self.mbcontext) as fiscal_repository:
                order_data = fiscal_repository.get_numero_sat_and_xml_request(order_id)
                status, data = self.fiscal_processor.cancel_sale(order_data)
                return status, data

        if self.nf_type == 'MFE':
            customer_doc = order.find(".//CustomOrderProperties/OrderProperty[@key='CUSTOMER_DOC']") or ""

            sat_service_name = self.fiscal_processor.sat_service_finder.find_and_lock_sat_service(order_id)
            cnpj_sw, sign_ac = self.fiscal_processor.get_sat_info()
            data = '\0'.join([pos_id, order_id, customer_doc, cnpj_sw, sign_ac])
            msg = self.mbcontext.MB_EasySendMessage(sat_service_name, TK_SAT_CANCEL_ORDER, format=FM_STRING, data=data.encode('utf-8'))
            self.fiscal_processor.sat_service_finder.unlock_sat_service(sat_service_name)

            self.printers[""].print_cancel(pos_id, msg.data)
            if msg.token == TK_SYS_ACK:
                return True, ''
            return False, 'SAT que realizou a venda nao encontrado'

    @staticmethod
    def _busca_parametros_sitef(order):
        # type: (eTree) -> (str, str, str)
        order_id = order.get("orderId")
        created_at = order.get("createdAt").replace("-", "").replace(":", "")
        data_fiscal = created_at[:8]
        hora_fiscal = created_at[9:15]

        return order_id, data_fiscal, hora_fiscal

    def _reprint_sat_or_nfce(self, xml_request, xml_response, params, danfe_type):
        if not xml_request:
            return False, "XML do pedido não encontrado"
        s = base64.b64decode(xml_request)
        contingencia = s[s.find("<tpEmis>")+8:s.find("</tpEmis>")]
        if contingencia == "9":
            return False, "Nota ainda não autorizada pela SEFAZ"
        if self.nf_type in ("SAT", "MFE"):
            ret_xml_request = self._get_xml_sat(xml_request)
            if None in [ret_xml_request['fiscal_data'], ret_xml_request['xml_request']]:
                return False, "Erro ao obter XML da venda!"
            if danfe_type in self.printers:
                selected_printer = self.printers[danfe_type]
            else:
                selected_printer = self.printers[""]
            return True, selected_printer.print_fiscal(params.get('posid'),
                                                       params.get('order'),
                                                       params.get('tenders'),
                                                       ret_xml_request.get("xml_request", ""),
                                                       eTree.XML(ret_xml_request.get("fiscal_data", "")),
                                                       params.get("total_taxes"),
                                                       params.get('customer_name'))
        else:
            try:
                ret_xml_request = self._get_xml_nfce(xml_request, xml_response)
            except StopIteration as ex:
                return False, ex.message
            if None in [ret_xml_request['request_xml'], ret_xml_request['response_xml']]:
                return False, "Erro ao obter XML da venda!"
            if danfe_type in self.printers:
                selected_printer = self.printers[danfe_type]
            else:
                selected_printer = self.printers[""]
            return True, selected_printer.print_fiscal(params.get('posid'),
                                                       params.get('order'),
                                                       params.get('tenders'),
                                                       ret_xml_request.get('request_xml'),
                                                       ret_xml_request.get('response_xml'),
                                                       params.get("total_taxes"),
                                                       params.get('customer_name'),
                                                       params.get('url_sefaz'))

    @staticmethod
    def _get_xml_sat(xml_request):
        try:
            xml = eTree.XML(base64.b64decode(xml_request))
            ide = xml.find('infCFe').find('ide')
            sat_key = xml.find('infCFe').attrib.get('Id')

            cpf_cnpj = xml.find('infCFe').find('dest') or ""
            if cpf_cnpj:
                if cpf_cnpj.find("CPF") is not None:
                    cpf_cnpj = cpf_cnpj.find("CPF").text
                elif cpf_cnpj.find("CNPJ") is not None:
                    cpf_cnpj = cpf_cnpj.find("CNPJ").text
                else:
                    cpf_cnpj = ""

            date_time = "{0}{1}".format(ide.find('dEmi').text, ide.find('hEmi').text)
            date_time_reprint = datetime.strptime(date_time, "%Y%m%d%H%M%S").strftime("%d/%m/%y %H:%M:%S")

            total = xml.find('infCFe').find('total')

            qr_code = sat_key[3:] + "|" + date_time + "|" + total.find('vCFe').text + "|" + cpf_cnpj + "|" + ide.find('assinaturaQRCODE').text

            list_tags_xml = ['vICMS', 'vPIS', 'vCOFINS', 'vPISST', 'vCOFINSST']
            total_taxes = 0
            icms_total = total.find('ICMSTot')
            for x in list_tags_xml:
                try:
                    total_taxes += D(icms_total.find(x).text)
                except (TypeError, AttributeError):
                    pass
            total_taxes = round_half_away_from_zero(total_taxes, 2)

            tag_xml_request = eTree.XML("<XmlRequest>{0}</XmlRequest>".format(xml_request))
            tag_fiscal_data = "<FiscalData>"
            tag_fiscal_data += "<datetime>{0}</datetime>".format(date_time_reprint)
            tag_fiscal_data += "<satno>{0}</satno>".format(ide.find('nserieSAT').text)
            tag_fiscal_data += "<satkey>{0}</satkey>".format(sat_key[3:])
            tag_fiscal_data += "<CustomerCPF>{0}</CustomerCPF>".format(cpf_cnpj)
            tag_fiscal_data += "<QRCode>{0}</QRCode>".format(qr_code)
            tag_fiscal_data += "</FiscalData>"

            return {"xml_request": tag_xml_request, "fiscal_data": tag_fiscal_data, "total_taxes": total_taxes}
        except Exception as ex:
            logger.error("Erro ao construir o xml - Exception %s", str(ex))
            return {"xml_request": None, "fiscal_data": None, "total_taxes": 0}

    def _get_xml_nfce(self, xml_request, xml_response):
        try:
            xml = remove_xml_namespace(base64.b64decode(xml_request))
            xml_resp = remove_xml_namespace(base64.b64decode(xml_response))

            response_tag = "retConsReciNFe"
            if self.synchronous_mode:
                response_tag = "retEnviNFe"
            xml_ws_version = int(float(xml_resp.find(".//{}".format(response_tag)).get('versao')))

            if xml_ws_version != self.versao_ws:
                raise StopIteration("Versão do XML diferente da versão fiscal atual. Versão XML: {}; Versão Fiscal: {}"
                                    .format(xml_ws_version, self.versao_ws))

            nprot = xml_resp.find(".//infProt/nProt").text
            data_resp = xml_resp.find(".//infProt/dhRecbto").text

            if xml.find('.//NFe'):
                body = eTree.tostring(xml.find('.//NFe'))
            else:
                body = eTree.tostring(xml)

            version = xml.find(".//infNFe").attrib['versao']
            total = xml.find('.//ICMSTot')

            list_tags_xml = ['vICMS', 'vPIS', 'vCOFINS', 'vPISST', 'vCOFINSST']
            total_taxes = 0

            for tag in list_tags_xml:
                try:
                    total_taxes += D(total.find('.//{}'.format(tag)).text)
                except (TypeError, AttributeError):
                    pass

            total_taxes = round_half_away_from_zero(total_taxes, 2)

            tag_request = '<ns0:Envelope xmlns = "http://www.portalfiscal.inf.br/nfe" ' \
                          'xmlns:ns0 = "http://www.w3.org/2003/05/soap-envelope" ' \
                          'xmlns:ns1 = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeAutorizacao" ' \
                          'xmlns:ns3 = "http://www.w3.org/2000/09/xmldsig#">'
            tag_request += '<ns0:Body><ns1:nfeDadosMsg>'
            tag_request += '<enviNFe versao = "{0}">'.format(version)
            tag_request += '{0}'.format(body)
            tag_request += '</enviNFe></ns1:nfeDadosMsg></ns0:Body></ns0:Envelope>'

            tag_reponse = '<ns0:Envelope xmlns="http://www.portalfiscal.inf.br/nfe" ' \
                          'xmlns:ns0="http://www.w3.org/2003/05/soap-envelope" ' \
                          'xmlns:ns1="http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao">' \
                          '<ns0:Body><ns1:nfeRetAutorizacaoLoteResult>'
            tag_reponse += '<retConsReciNFe versao="{0}">'.format(version)
            tag_reponse += '<protNFe versao="{0}"><infProt>'.format(version)
            tag_reponse += '<dhRecbto>{0}</dhRecbto>'.format(str(data_resp))
            tag_reponse += '<nProt>{0}</nProt>'.format(str(nprot))
            tag_reponse += '</infProt></protNFe></retConsReciNFe></ns1:nfeRetAutorizacaoLoteResult></ns0:Body></ns0:Envelope>'

            return {"request_xml": eTree.XML(tag_request), "response_xml": eTree.XML(tag_reponse), "total_taxes": total_taxes}
        except StopIteration:
            raise
        except Exception as ex:
            logger.error("Erro ao construir o xml - Exception %s", str(ex))
            return {"request_xml": None, "response_xml": None, "total_taxes": 0}

    def _handle_re_sign_xml(self):
        with FiscalDataRepository(self.mbcontext) as fiscalrepository:
            logger.info("Starting XML Resign Event...")
            conn = None
            try:
                conn = DBDriver().open(self.mbcontext, service_name="FiscalPersistence")
                sql = """SELECT PosId, OrderId, OrderPicture, XMLRequest
                          FROM fiscal.FiscalData
                          WHERE SentToNfce IN (555)
                          ORDER BY OrderId ASC LIMIT 500"""

                cursor = conn.select(sql)
                orders_with_error = 0
                orders_with_success = 0
                for row in cursor:
                    try:
                        pos_id, order_id, order_picture, request = map(row.get_entry, ("PosId", "OrderId", "OrderPicture", "XMLRequest"))
                        logger.info("Resigning Order %s" % order_id)

                        if self.nf_type != "PAF":
                            try:
                                is_in_contingence = True
                                xml_decoded = base64.b64decode(request + "=" * ((4 - len(request) % 4) % 4))
                                req = remove_xml_namespace(xml_decoded)

                                dh_cont = req.find(".//infNFe/ide/dhCont")
                                if dh_cont is None:
                                    dh_cont = req.find(".//NFe/infNFe/ide/dhCont")

                                x_just = req.find(".//infNFe/ide/xJust")
                                if x_just is None:
                                    x_just = req.find(".//NFe/infNFe/ide/xJust")

                                if dh_cont is not None:
                                    dh_cont = dh_cont.text
                                    dh_cont = dh_cont[:-6]
                                    dh_cont = datetime.strptime(dh_cont, "%Y-%m-%dT%H:%M:%S")
                                if x_just is not None:
                                    x_just = x_just.text
                                if dh_cont is None and x_just is None:
                                    dh_cont = datetime.now()
                                    x_just = "Problemas de conexao com a SEFAZ"
                            except Exception as _:
                                dh_cont = datetime.now()
                                x_just = "Problemas de conexao com a SEFAZ"

                                logger.info("Order: {} - dh_cont: {} / xjust: {}".format(order_id, dh_cont, x_just))
                        else:
                            is_in_contingence = False
                            dh_cont = ""
                            x_just = ""
                            logger.info("Order: {} - Not in contingence".format(order_id))

                        order_taker = OrderTaker()
                        order = order_taker.get_order_picture(pos_id, order_id)
                        fiscalrepository.set_order_picture(order_id, base64.b64encode(order))
                        order = eTree.XML(order)

                        order.attrib["posId"] = pos_id

                        fiscal_data = self.fiscal_processor.nfce_request_builder.build_request(order, is_in_contingence, dh_cont, x_just)
                        index1 = fiscal_data[0].index("<NFe")
                        index2 = fiscal_data[0].index("</NFe>")
                        new_req = fiscal_data[0][index1:index2 + 6]
                        status = 0
                        if self.nf_type == "PAF":
                            new_req = "<nfeProc>" + new_req + "<protNFe versao=\"%.2f\" xmlns=\"%s\"><infProt><cStat>100</cStat></infProt></protNFe></nfeProc>" % (3.1 if self.versao_ws in (1, 3) else 4, NfceRequestBuilder.NAMESPACE_NFE)
                            status = 1
                        xml_base64 = base64.b64encode(new_req)

                        fiscalrepository.set_nfce_sent_with_xml(order_id, xml_base64, status)
                        logger.info("XML Resign Order %s OK" % order_id)
                        orders_with_success += 1

                    except Exception as _:
                        orders_with_error += 1
                        logger.exception("Error to build XML of the order %s" % order_id)
                        continue
                if orders_with_error:
                    logger.error("Orders with success: {0}. Orders with error: {1}".format(orders_with_success, orders_with_error))
                    return False, "Orders with success: {0}. Orders with error: {1}".format(orders_with_success, orders_with_error)

            except Exception as _:
                logger.exception("Error to resign XMLs")
                return False, "Error to resign XMLs"
            finally:
                logger.info("Finish XML Resign Event...")
                if conn:
                    conn.close()

        return True, "Success to resigns XMLs. Number of orders resigns: {}".format(orders_with_success)

    def _handle_fiscal_xml_request(self, data, return_data=False):
        conn = None
        base64_xml_response = None
        order_id = None
        try:
            conn = DBDriver().open(self.mbcontext, service_name="FiscalPersistence")
            sql = """SELECT OrderId, XMLRequest
                      FROM fiscal.FiscalData
                      WHERE OrderId=%s""" % data
            cursor = conn.select(sql)
            for row in cursor:
                order_id = row.get_entry(0)
                base64_xml_response = row.get_entry(1)
        except Exception:
            logger.exception("Erro ao buscar XMLRequest")
        finally:
            if conn:
                conn.close()
        if return_data:
            if order_id is None:
                return False, "Invalid Order ID {}".format(data)
            if base64_xml_response is None:
                return False, "No XML for order ID {}".format(order_id)
            return True, base64_xml_response
        else:
            if order_id is None:
                self.mbcontext.MB_EasyEvtSend("PosFiscalXmlError", "", ";".join((order_id, "OrderId inválida ou inexistente no banco - order %s" % data)))
            elif base64_xml_response is None:
                self.mbcontext.MB_EasyEvtSend("PosFiscalXmlError", "", ";".join((order_id, "XML inexistente para order %s" % order_id)))
            else:
                xml_response = base64.b64decode(base64_xml_response)
                compress_obj = zlib.compressobj(zlib.Z_BEST_COMPRESSION, zlib.DEFLATED, 31)
                zipped_xml = compress_obj.compress(xml_response)
                zipped_xml += compress_obj.flush()
                base64_zipped_xml = base64.b64encode(zipped_xml)
                self.mbcontext.MB_EasyEvtSend("PosFiscalXmlResponse", "", ";".join((order_id, base64_zipped_xml)))

    def _handle_check_if_fiscal_xml_is_created_in_folder(self):
        # type: () -> None
        try:
            logger.info("Starting -> _handle_check_if_fiscal_xml_is_created_in_folder")
            date_yesterday, date_yesterday_start, date_yesterday_end = self._get_yesterday_dates()
            fiscal_data_path = self._get_fiscal_xml_sent_path(date_yesterday)

            database_fiscal_data_number_list = self._get_fiscal_data_number_from_database_by_date(date_yesterday_start, date_yesterday_end)

            self._generate_fiscal_xml_not_created(database_fiscal_data_number_list, fiscal_data_path)
            logger.info("Finished -> _handle_check_if_fiscal_xml_is_created_in_folder")
        except Exception as _:
            logger.exception("Error creating XML files")

    def _handle_retry_fiscal_orders_with_exception(self):
        # type: () -> None
        try:
            logger.info("Starting -> _handle_retry_fiscal_orders_with_exception")
            with FiscalDataRepository(self.mbcontext) as fiscal_repository:  # type: fiscalpersistence.FiscalDataRepository
                fiscal_repository.retry_fiscal_orders_with_exception(self.period_to_retry_orders_with_exception)

            logger.info("Finished -> _handle_retry_fiscal_orders_with_exception")
        except Exception as _:
            logger.exception("Error changing status of fiscal orders with exception")

    def _get_fiscal_xml_sent_path(self, date_yesterday):
        fiscal_data_file = str(date_yesterday.year) + '/' + str(date_yesterday.month).zfill(2) + '/' + str(date_yesterday.day).zfill(2)
        fiscal_data_path = os.path.join(self.fiscal_sent_dir, self.xml_enviados, fiscal_data_file)
        return fiscal_data_path

    def _generate_fiscal_xml_not_created(self, database_fiscal_data_number_list, fiscal_data_path):
        self._create_directory_if_not_exists(fiscal_data_path)

        self._verify_if_xml_in_folder_is_in_database_list(database_fiscal_data_number_list, fiscal_data_path)
        self._create_xml_if_it_is_not_in_folder(database_fiscal_data_number_list, fiscal_data_path)

    def _create_xml_if_it_is_not_in_folder(self, database_fiscal_data_number_list, fiscal_data_path):
        conn = None
        try:
            conn = DBDriver().open(self.mbcontext, service_name="FiscalPersistence")
            sql = """SELECT PosId, OrderId, XMLRequest, NumeroNota, NumeroSat FROM FiscalData
                     WHERE NumeroNota IN ({}) """.format("'" + "','".join(database_fiscal_data_number_list) + "'")

            cursor = conn.select(sql)
            for row in cursor:
                numero_nota, order_id, pos_id, xml_request, numero_sat = self._parse_database_info(row)

                inf_id, numero_serie = self._parse_xml_info(xml_request)

                fiscal_xml_path_to_save = self.create_fiscal_xml_path_to_save(inf_id, numero_serie,
                                                                              fiscal_data_path, numero_nota, order_id,
                                                                              pos_id, numero_sat)
                self._save_xml_file_in_folder(fiscal_xml_path_to_save, xml_request)
        except Exception as ex:
            logger.exception("Exception creating XML with error: {}".format(ex))
        finally:
            conn.close()

    def create_fiscal_xml_path_to_save(self, inf_id, numero_serie, fiscal_data_path, numero_nota, order_id, pos_id, numero_sat):
        if self.nf_type in ["NFCE", "PAF"]:
            fiscal_xml_path_to_save = FiscalWrapperEventHandler._generate_nfce_xml_file_name(inf_id,
                                                                                             numero_nota,
                                                                                             order_id,
                                                                                             pos_id,
                                                                                             numero_serie,
                                                                                             fiscal_data_path)
        else:

            fiscal_xml_path_to_save = FiscalWrapperEventHandler._generate_sat_xml_file_name(fiscal_data_path,
                                                                                            numero_nota,
                                                                                            order_id,
                                                                                            pos_id,
                                                                                            numero_sat,
                                                                                            inf_id)
        return fiscal_xml_path_to_save

    @staticmethod
    def _generate_nfce_xml_file_name(infnfe_id, numero_nota, order_id, pos_id, numero_serie, fiscal_data_path):
        fiscal_xml_path_to_save = os.path.join(fiscal_data_path, "{0}_{1}_{2}_nfe_proc_pos{3}_{4}.xml".format(
            numero_serie.zfill(3),
            numero_nota.zfill(9),
            order_id.zfill(9),
            pos_id.zfill(2),
            infnfe_id))
        return fiscal_xml_path_to_save

    @staticmethod
    def _generate_sat_xml_file_name(fiscal_data_path, numero_nota, order_id, pos_id, numero_sat, infcfe_id):
        fiscal_xml_path_to_save = os.path.join(fiscal_data_path, "S{0}_{1}_{2}_response_pos{3}_{4}.xml".format(
            numero_sat[-2:],
            str(numero_nota).zfill(9),
            str(order_id).zfill(9),
            str(pos_id).zfill(2),
            infcfe_id))
        return fiscal_xml_path_to_save

    @staticmethod
    def _save_xml_file_in_folder(fiscal_xml_path_to_save, fiscal_xml_to_save):
        with open(fiscal_xml_path_to_save, "w+") as xml_to_save:
            xml_to_save.write(fiscal_xml_to_save)

    def _parse_xml_info(self, fiscal_xml_to_save):
        fiscal_xml_to_save = remove_xml_namespace(fiscal_xml_to_save)

        key_fiscal_inf = fiscal_xml_to_save.find(".//infNFe") if self.nf_type in ("NFCE", "PAF") else fiscal_xml_to_save.find(".//infCFe")
        data_fiscal_inf = key_fiscal_inf.attrib['Id']

        key_data_fiscal_serie = fiscal_xml_to_save.find(".//serie") if self.nf_type in ("NFCE", "PAF") else fiscal_xml_to_save.find(".//nserieSAT")
        data_fiscal_serie = key_data_fiscal_serie.text.zfill(3)

        return data_fiscal_inf, data_fiscal_serie

    @staticmethod
    def _parse_database_info(row):
        numero_nota = str(row.get_entry("NumeroNota")).zfill(9)
        order_id = str(row.get_entry("OrderId")).zfill(9)
        pos_id = str(row.get_entry("PosId")).zfill(2)
        xml_request = base64.b64decode(row.get_entry("XMLRequest"))
        numero_sat = str(row.get_entry("NumeroSat"))
        return numero_nota, order_id, pos_id, xml_request, numero_sat

    def _verify_if_xml_in_folder_is_in_database_list(self, database_fiscal_data_number_list, fiscal_data_path):
        for xml_file in glob.glob(os.path.join(fiscal_data_path, '*.xml')):
            try:
                xml_fiscal_number = self._get_xml_fiscal_number_from_xml_file(xml_file)

                if xml_fiscal_number in database_fiscal_data_number_list:
                    database_fiscal_data_number_list.remove(xml_fiscal_number)
                elif not 'procInut' in xml_file:
                    self._move_xml_to_inconsistent_folder(fiscal_data_path, xml_file)

            except Exception as _:
                logger.exception("Exception on File: " + xml_file + "\nMoved to folder: " + self.xml_inconsistentes)
                self._move_xml_to_inconsistent_folder(fiscal_data_path, xml_file)

    def _get_xml_fiscal_number_from_xml_file(self, xml_file):
        xml = remove_xml_namespace(eTree.tostring(eTree.parse(xml_file).getroot()))
        key = xml.find(".//nNF") if self.nf_type in ("NFCE", "PAF") else xml.find(".//nCFe")
        return key.text if key is not None else None

    def _move_xml_to_inconsistent_folder(self, fiscal_data_path, xml_file):
        inconsistent_fiscal_data_path = fiscal_data_path.replace(self.xml_enviados, self.xml_inconsistentes)
        self._create_directory_if_not_exists(inconsistent_fiscal_data_path)
        xml_file_new_path = xml_file.replace(self.xml_enviados, self.xml_inconsistentes)
        shutil.move(xml_file, xml_file_new_path)
        logger.info("File: " + xml_file + "\nMoved to folder: " + self.xml_inconsistentes)

    @staticmethod
    def _create_directory_if_not_exists(data_path):
        try:
            if not os.path.exists(data_path):
                os.makedirs(data_path)
        except OSError:
            logger.error("Cannot create path: {}".format(data_path))

    @staticmethod
    def _get_yesterday_dates():
        date_yesterday = datetime.now() - timedelta(days=1)
        date_yesterday_start = datetime(date_yesterday.year, date_yesterday.month, date_yesterday.day, 0, 0, 0)
        date_yesterday_end = datetime(date_yesterday.year, date_yesterday.month, date_yesterday.day, 23, 59, 59)
        return date_yesterday, date_yesterday_start, date_yesterday_end

    def _get_fiscal_data_number_from_database_by_date(self, start_date, end_date):
        # type: (datetime, datetime) -> [unicode]
        fiscal_data_number_list = []
        conn = None

        try:
            conn = DBDriver().open(self.mbcontext, service_name="FiscalPersistence")
            sql = """SELECT NumeroNota, datetime(datanota,'unixepoch','localtime') AS data 
                     FROM fiscal.FiscalData
                     WHERE data > '{}' AND data <= '{}'""".format(start_date, end_date)

            cursor = conn.select(sql)
            for row in cursor:
                fiscal_data_number_list.append(row.get_entry("NumeroNota"))
        except Exception as ex:
            logger.exception("Get fiscal data number list error: " + ex.message)
        finally:
            conn.close()

        return fiscal_data_number_list
