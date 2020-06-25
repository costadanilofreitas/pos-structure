# # -*- coding: utf-8 -*-

import logging
import os
import xml.etree.ElementTree as eTree

import cfgtools
import pyscripts
import sysactions
from cfgtools import Configuration
from old_helper import OrderTaker, PosUtil, config_logger, read_swconfig
from debug_helper import import_pydevd
from clichehelper import ClicheHelper
from messagehandler import MessageHandler
from msgbus import MBEasyContext
from pos_model import OrderParser
from pos_util import SaleLineUtil
from typing import Union

import nfcebuilder
import satbuilder
from common import FiscalParameterController
from eventhandler import FiscalWrapperEventHandler
from ibpttaxprocessor import IbptTaxProcessor
from models import SoftwareDeveloper
from nfce import NfceProcessor, NfceRequestBuilder, NfceContingencia, NfceAutorizador, NfceConnectivityTester, \
    NfceSituationChecker
from nfcebuilder.nfceutil import NfeSigner, XmlEnveloper, NfceRequest
from nfcecanceler import NfceCanceler, NfceCancelerRequestBuilder, NfceCancelerParameters, NfceCancelerResponseParser
from nfcedisabler import OrderDisabler, NfceDisabler, NfceDisablerRequestBuilder, NfceDisablerParameters, \
    NfceDisablerResponseParser, OrderRepository, ProcInutNfeBuilder, ProcInutNfeSaver
from order_retriever import OrderRetrieverService, OrderDataFormatter
from order_retriever.repository import OrderRetrieverRepository
from printer import SatFiscalPrinter, NfceFiscalPrinter
from repository import FiscalParameterRepository
from sat import SatProcessor, SatRequestBuilder, SatServiceFinder, MfeServiceFinder

logger = logging.getLogger("FiscalWrapper")

LOADER_CFG = os.environ["LOADERCFG"]
REQUIRED_SERVICES = "FiscalPersistence|PosController|StoreWideConfig"


def main():
    import_pydevd(LOADER_CFG, 9125)

    config_logger(LOADER_CFG, 'FiscalWrapper')
    config_logger(LOADER_CFG, 'FiscalWrapperThread')
    config_logger(LOADER_CFG, 'NfceDisabler')
    config = cfgtools.read(LOADER_CFG)

    service_name = str(config.find_value("FiscalWrapper.ServiceName"))
    service_type = str(config.find_value("FiscalWrapper.ServiceType"))

    xml_enviados = str(config.find_value("FiscalWrapper.XmlEnviados"))
    xml_erros = str(config.find_value("FiscalWrapper.XmlErros"))
    xml_inconsistentes = str(config.find_value("FiscalWrapper.XmlInconsistentes") or "Inconsistentes")
    xml_path = str(config.find_value("FiscalWrapper.XmlPath"))
    crt = int(config.find_value("FiscalWrapper.crt"))
    ibpt_tax_files_path = str(config.find_value("FiscalWrapper.IbptTaxFilesPath") or "../data/server/bundles/fiscalwrapper/ibpttaxfiles")

    mbcontext = MBEasyContext(service_name)
    pyscripts.mbcontext = mbcontext
    sysactions.mbcontext = mbcontext

    nf_type = config.find_value("FiscalWrapper.NFType")  # type: str
    print_customer_name = (config.find_value("FiscalWrapper.PrintCustomerName") or "false").lower() == "true"

    fiscal_printer = None
    fiscal_processor = None

    fiscal_sent_dir = config.find_value("FiscalWrapper.FiscalSentDir").strip()

    message_handler = MessageHandler(mbcontext, service_name, service_type, REQUIRED_SERVICES)

    nome_emit = read_swconfig(mbcontext, "Store.RazaoSocial")
    end_logradouro = read_swconfig(mbcontext, "Store.EndLogradouro")
    end_numero = read_swconfig(mbcontext, "Store.EndNumero").strip() or "S/N"
    end_compl = read_swconfig(mbcontext, "Store.EndCompl").strip()
    bairro = read_swconfig(mbcontext, "Store.Bairro")
    municipio = read_swconfig(mbcontext, "Store.Municipio")
    cep = read_swconfig(mbcontext, "Store.CEP")
    uf = read_swconfig(mbcontext, "Store.UF")
    cnpj_contribuinte = read_swconfig(mbcontext, "Store.CnpjContribuinte")
    inscr_estadual = read_swconfig(mbcontext, "Store.InscEstadual")

    garena_coupons_enabled = (read_swconfig(mbcontext, "Store.GarenaCoupons.Enabled") or "false").lower() == "true"
    garena_fiscal_coupons_layout_header = read_swconfig(mbcontext, "Store.GarenaCoupons.FiscalCouponLayoutHeader")
    garena_fiscal_coupons_layout_footer = read_swconfig(mbcontext, "Store.GarenaCoupons.FiscalCouponLayoutFooter")
    garena_configs = {"enabled": garena_coupons_enabled,
                      "garena_layout_header": garena_fiscal_coupons_layout_header,
                      "garena_layout_footer": garena_fiscal_coupons_layout_footer}

    cliche_helper = ClicheHelper(mbcontext, cnpj_contribuinte, inscr_estadual)

    order_disabler = None
    nfce_contingencia = None
    nfce_situation_checker = None
    nfce_connectivity_tester = None
    nfce_canceler = None
    versao_ws = None

    fiscal_parameters = FiscalParameterRepository(mbcontext).get_fiscal_parameters()

    customer_text_field = config.find_value("FiscalWrapper.PrinterCustomizations.CustomerTextField") or ""

    period_to_retry_orders_with_exception = config.find_value("FiscalWrapper.PeriodToRetryOrdersWithException") or "7"

    order_parser = OrderParser()

    fiscal_parameter_controller = FiscalParameterController(fiscal_parameters)

    ibtp_tax_processor = IbptTaxProcessor(mbcontext, ibpt_tax_files_path, uf, fiscal_parameter_controller)

    sale_line_util = SaleLineUtil()

    if nf_type.upper() == "SAT" or nf_type.upper() == "MFE":
        sat_group = config.find_group("FiscalWrapper.SAT")
        cnpj_sw = sat_group.find_value("CnpjSW")
        sign_ac = sat_group.find_value("SignAC")
        max_sat_number = int(sat_group.find_value("MaxSatNumber"))
        sleep_time = int(sat_group.find_value("SearchSatInterval"))
        if nf_type.upper() == "SAT":
            sat_service_finder = SatServiceFinder(mbcontext, max_sat_number, sleep_time)
        else:
            sat_service_finder = MfeServiceFinder(mbcontext, max_sat_number, sleep_time)

        cfe_builder = _build_sat_builders(crt, cnpj_contribuinte, inscr_estadual, cnpj_sw, sign_ac, fiscal_parameter_controller, sale_line_util, ibtp_tax_processor)

        sat_request_builder = SatRequestBuilder(mbcontext, crt, cnpj_sw, sign_ac, cnpj_contribuinte, inscr_estadual,
                                                order_parser, fiscal_parameter_controller, sale_line_util, cfe_builder,
                                                nf_type.upper() == "MFE")
        fiscal_processor = SatProcessor(mbcontext, sat_service_finder, sat_request_builder, fiscal_sent_dir)
        fiscal_printer = SatFiscalPrinter(mbcontext, print_customer_name, cliche_helper, customer_text_field, garena_configs)

    elif nf_type.upper() in ("NFCE", "PAF"):
        nfce_group = config.find_group("FiscalWrapper.NFCE")

        c_uf = nfce_group.find_value("cUF")
        c_mun_fg = nfce_group.find_value("cMunFG")
        mod = nfce_group.find_value("mod")
        serie = nfce_group.find_value("serie")
        ambiente = nfce_group.find_value("ambiente")
        csc = nfce_group.find_value("csc")
        cid_token = nfce_group.find_value("cid_token")
        initial_order_id = int(nfce_group.find_value("initial_order_id"))
        versao_ws = int(nfce_group.find_value("versao_ws"))
        send_sleep_time = int(nfce_group.find_value("send_sleep_time") or 5)
        check_situation_timeout = int(nfce_group.find_value("CheckSituationTimeout") or 10)
        synchronous_mode = (nfce_group.find_value("synchronous_mode") or "false").lower() == "true"

        software_developer = _read_software_developer_informations(config, uf)

        bundle_dir = os.environ["BUNDLEDIR"]
        certificate_key_path = bundle_dir + nfce_group.find_value("certificate_key_path")
        certificate_path = bundle_dir + nfce_group.find_value("certificate_path")
        nfe_signer = NfeSigner(certificate_key_path, certificate_path)
        sefaz_certificate_path = bundle_dir + nfce_group.find_value("sefaz_certificate_path")

        nfce_urls = _get_nfce_urls(nfce_group, uf, versao_ws, ambiente)

        nfe_builder = _build_nfe_builders(serie, initial_order_id, c_uf, mod, c_mun_fg, ambiente, crt,
                                          cnpj_contribuinte, inscr_estadual, nome_emit, end_logradouro, end_numero,
                                          end_compl, bairro, municipio, uf, cep,
                                          fiscal_parameter_controller, sale_line_util, cid_token, csc, nfce_urls["qrcode_base_url"],
                                          nfe_signer, versao_ws, nfce_urls["qrcode_check_url"], software_developer)
        nfce_request_builder = NfceRequestBuilder(mbcontext, initial_order_id, crt, cnpj_contribuinte, inscr_estadual,
                                                  c_uf, uf, c_mun_fg, mod, serie, ambiente, end_logradouro, end_numero,
                                                  end_compl, bairro, municipio, cep, nome_emit, csc, cid_token,
                                                  nfce_urls["qrcode_base_url"], certificate_key_path, certificate_path, order_parser,
                                                  fiscal_parameter_controller, sale_line_util, nfe_builder, versao_ws, synchronous_mode)
        nfce_request = NfceRequest(certificate_key_path, certificate_path, sefaz_certificate_path, check_situation_timeout)

        max_tantavivas_envio_lote = int(nfce_group.find_value("max_tantavivas_envio_lote") or "3")
        max_tantavivas_envio_contingencia = int(nfce_group.find_value("max_tantavivas_envio_contingencia") or "10")
        intervalo_retentativa_lote = int(nfce_group.find_value("intervalo_retentativa_lote") or "15")

        if nf_type.upper() == "NFCE":
            nfce_connectivity_tester = NfceConnectivityTester(nfce_request, nfce_urls["url_status_servico"], c_uf, versao_ws)
            nfce_situation_checker = NfceSituationChecker(nfce_request, nfce_urls["url_consulta_nfe"], ambiente, c_uf, versao_ws)
            nfce_autorizador = NfceAutorizador(nfce_request_builder, nfce_request, nfce_urls["url_autorizacao"], nfce_urls["url_ret_autorizacao"], versao_ws, max_tantavivas_envio_lote, intervalo_retentativa_lote, send_sleep_time, synchronous_mode)
            nfce_contingencia = NfceContingencia(mbcontext, nfce_request_builder, nfce_autorizador, versao_ws, nfce_situation_checker, fiscal_sent_dir, max_tantavivas_envio_contingencia, synchronous_mode, nfce_connectivity_tester)
            fiscal_printer = NfceFiscalPrinter(mbcontext, print_customer_name, cliche_helper, nfce_urls["qrcode_check_url"], versao_ws, customer_text_field, garena_configs)
        else:
            nfce_request = None
            nfce_autorizador = None
            nfce_contingencia = None
            fiscal_printer = None

        fiscal_processor = NfceProcessor(mbcontext, nfce_request_builder, nfce_request, nfce_autorizador, nfce_contingencia, nfce_urls["qrcode_base_url"], fiscal_sent_dir, versao_ws, synchronous_mode)

        justificativa_inutilizacao = nfce_group.find_value("justificativa_inutilizacao")
        nfce_disabler_parameters = NfceDisablerParameters(initial_order_id, ambiente, c_uf, cnpj_contribuinte, serie, justificativa_inutilizacao)
        nfce_canceler_parameters = NfceCancelerParameters(ambiente, c_uf, cnpj_contribuinte)

        xml_enveloper = XmlEnveloper(c_uf)
        nfce_disabler_request_builder = NfceDisablerRequestBuilder(nfce_disabler_parameters, nfe_signer, xml_enveloper, versao_ws)
        nfce_canceler_request_builder = NfceCancelerRequestBuilder(nfce_canceler_parameters, nfe_signer, xml_enveloper)

        nfce_disabler_response_parser = NfceDisablerResponseParser(versao_ws)
        nfce_canceler_response_parser = NfceCancelerResponseParser()

        nfce_canceler = NfceCanceler(nfce_canceler_request_builder, nfce_canceler_response_parser, nfce_request, nfce_urls["url_cancelamento"], fiscal_sent_dir, versao_ws)

        proc_inut_nfe_builder = ProcInutNfeBuilder()
        proc_inut_nfe_saver = ProcInutNfeSaver(fiscal_sent_dir)
        nfce_disabler = NfceDisabler(nfce_disabler_request_builder, nfce_disabler_response_parser, nfce_request, nfce_urls["url_inutilizacao"], proc_inut_nfe_builder, proc_inut_nfe_saver, versao_ws)

        order_taker = OrderTaker()

        pos_list = PosUtil(mbcontext).get_pos_list()
        order_repository = OrderRepository(mbcontext, pos_list)

        order_disabler = OrderDisabler(order_repository, nfce_disabler, order_taker)

    orser_retriever_repository = OrderRetrieverRepository(mbcontext)

    order_data_formatter = OrderDataFormatter()
    order_retriever_service = OrderRetrieverService(orser_retriever_repository, order_data_formatter)

    event_handler = FiscalWrapperEventHandler(
        mbcontext,
        fiscal_processor,
        fiscal_printer,
        nfce_connectivity_tester,
        nfce_situation_checker,
        order_disabler,
        nfce_canceler,
        fiscal_parameter_controller,
        xml_enviados,
        xml_erros,
        xml_path,
        fiscal_sent_dir,
        nf_type,
        versao_ws,
        ibtp_tax_processor,
        order_retriever_service,
        xml_inconsistentes,
        nfce_contingencia,
        period_to_retry_orders_with_exception)
    message_handler.set_event_handler(event_handler)

    if nfce_contingencia is not None:
        nfce_contingencia.start_contingencia()

    message_handler.subscribe_events([
        "ORDER_MODIFIED",
        "DisableNfceOrder",
        "ReSignXMLs",
        "OrderManagerFiscalXmlRequest",
        "CheckIfFiscalXmlIsCreatedInFolder"
        "RetryFiscalOrdersWithException"
    ])
    message_handler.handle_events()


def _get_nfce_urls(nfce_group, uf, versao_ws, ambiente):
    urls_path = nfce_group.find_value("urls_path") or "../data/server/bundles/fiscalwrapper/nfce_urls.xml"
    nfce_urls = {}

    if os.path.exists(urls_path):
        logger.info("Reading NFCe URLs from <nfce_urls.xml>...")
        urls_xml = eTree.parse(urls_path).getroot()
        for state in urls_xml.findall("estado"):
            if state.get("uf") == uf:
                for version in state.findall("versao"):
                    if int(version.get("ws")) == versao_ws and version.get("ambiente") == ambiente:
                        for url in version:
                            nfce_urls[url.tag] = str.strip(url.text)

    if not nfce_urls:
        logger.info("NFCe URLs not found in <nfce_urls.xml>, reading from <loader.cfg>...")
        nfce_urls["url_autorizacao"] = nfce_group.find_value("url_autorizacao") or ""
        nfce_urls["url_ret_autorizacao"] = nfce_group.find_value("url_ret_autorizacao") or ""
        nfce_urls["url_inutilizacao"] = nfce_group.find_value("url_inutilizacao") or ""
        nfce_urls["url_cancelamento"] = nfce_group.find_value("url_cancelamento") or ""
        nfce_urls["url_status_servico"] = nfce_group.find_value("url_status_servico") or ""
        nfce_urls["url_consulta_nfe"] = nfce_group.find_value("url_consulta_nfe") or ""
        nfce_urls["qrcode_base_url"] = nfce_group.find_value("qrcode_base_url") or ""
        nfce_urls["qrcode_check_url"] = nfce_group.find_value("qrcode_check_url") or ""


    for url in nfce_urls:
        if not nfce_urls[url]:
            logger.warning("NFCe URL missing: [{}]".format(url))

    return nfce_urls


def _build_nfe_builders(serie, initial_order_id, c_uf, mod, c_mun_fg, ambiente, crt, cnpj_contribuinte,
                        inscr_estadual, nome_emit, end_logradouro, end_numero, end_compl, bairro, municipio, uf, cep,
                        fiscal_parameter_controller, sale_line_util, cid_token, csc, qrcode_base_url, nfe_signer, versao_ws,
                        qrcode_check_url, software_developer):
    ide_builder = nfcebuilder.IdeBuilder(serie, initial_order_id, c_uf, mod, c_mun_fg, ambiente, versao_ws)
    emit_builder = nfcebuilder.EmitBuilder(crt, cnpj_contribuinte, inscr_estadual, nome_emit,
                               end_logradouro, end_numero, end_compl, bairro, c_mun_fg, municipio, uf, cep)
    dest_builder = nfcebuilder.DestinatarioBuilder(ambiente)
    det_list_builder = nfcebuilder.DetListBuilder(nfcebuilder.DetBuilder(ambiente, crt, fiscal_parameter_controller, sale_line_util, versao_ws))
    inf_resp_tec_builder = nfcebuilder.InfRespTecBuilder(software_developer)
    builders = [ide_builder, emit_builder, dest_builder, det_list_builder, nfcebuilder.TotalBuilder(versao_ws),
                nfcebuilder.TranspBuilder(), nfcebuilder.PagBuilder(versao_ws), inf_resp_tec_builder]
    inf_nfe_builder = [nfcebuilder.InfNfeBuilder(builders, c_uf, cnpj_contribuinte, mod, serie, versao_ws)]
    nfe_supl_builder = nfcebuilder.InfNFeSuplBuilder(ambiente, cid_token, csc, qrcode_base_url, qrcode_check_url, versao_ws)
    nfe_builder = nfcebuilder.NfeBuilder(inf_nfe_builder, nfe_signer, nfe_supl_builder)
    return nfe_builder


def _build_sat_builders(crt, cnpj_contribuinte, inscr_estadual, cnpj_sw, sign_ac, fiscal_parameter_controller, sale_line_util, ibtp_tax_processor):
    ide_builder = satbuilder.IdeBuilder(cnpj_sw, sign_ac)
    emit_builder = satbuilder.EmitBuilder(cnpj_contribuinte, inscr_estadual)
    dest_builder = satbuilder.DestinatarioBuilder()
    det_builder = satbuilder.DetBuilder(crt, fiscal_parameter_controller, sale_line_util, ibtp_tax_processor)
    det_list_builder = satbuilder.DetListBuilder(det_builder)
    builders = [ide_builder, emit_builder, dest_builder, det_list_builder, satbuilder.TotalBuilder(), satbuilder.PgtoBuilder()]
    inf_cfe_builder = [satbuilder.InfCfeBuilder(builders)]
    cfe_builder = satbuilder.CfeBuilder(inf_cfe_builder)
    return cfe_builder


def _read_software_developer_informations(config, uf):
    # type: (Configuration, unicode) -> Union[SoftwareDeveloper, None]
    sv_group = config.find_group("FiscalWrapper.SoftwareDeveloper")
    software_developer = SoftwareDeveloper()

    if sv_group:
        software_developer.cnpj = str(sv_group.find_value("CNPJ") or "")
        software_developer.contact = str(sv_group.find_value("Contact") or "")
        software_developer.email = str(sv_group.find_value("Email") or "")
        software_developer.phone = str(sv_group.find_value("Phone") or "")
        software_developer.csrt = str(sv_group.find_value("CSRT") or "")
        software_developer.id_csrt = str(sv_group.find_value("idCSRT") or "")

        enabled_states = sv_group.find_values("States")
        software_developer.enabled = True if uf in enabled_states else False

    return software_developer
