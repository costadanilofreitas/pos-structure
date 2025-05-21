# -*- coding: utf-8 -*-

# noinspection PyUnresolvedReferences
from lxml import etree as lxml_etree
import base64
import glob
import logging
import os
import time
import unicodedata
from datetime import datetime, timedelta
from threading import Thread, Condition, Lock
from xml.etree import cElementTree as eTree
import iso8601
import pem
import sysactions
from common import FiscalParameterController
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from dateutil import tz
from fiscalinterface import FiscalProcessor
from fiscalpersistence import FiscalDataRepository
from old_helper import convert_from_localtime_to_utc, OrderTaker, remove_xml_namespace
from msgbus import MBEasyContext
from nfcebuilder import NfeBuilder, ContextKeys
from nfcebuilder.nfceutil import NfceRequest
from pos_model import OrderParser
from pos_util import SaleLineUtil
from requests import ConnectionError, Timeout, Response
from typing import Optional

loggerThread = logging.getLogger("FiscalWrapperThread")
logger = logging.getLogger("FiscalWrapper")


class NfceRequestBuilder:
    NAMESPACE_NFE = "http://www.portalfiscal.inf.br/nfe"
    NAMESPACE_SOAP = "http://www.w3.org/2003/05/soap-envelope"
    NAMESPACE_AUTORIZACAO = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeAutorizacao"
    NAMESPACE_AUTORIZACAO_4 = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeAutorizacao4"
    NAMESPACE_RET_AUTORIZACAO_4 = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRetAutorizacao4"
    NAMESPACE_CONSULTA_SITUACAO = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeConsulta2"
    NAMESPACE_CONSULTA_SITUACAO_3 = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeConsulta3"
    NAMESPACE_CONSULTA_SITUACAO_4 = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsultaProtocolo4"

    def __init__(self, mbcontext, initial_order_id, crt, cnpj_contribuinte, inscr_estadual,
                 c_uf, uf, c_mun_fg, mod, serie, ambiente, end_logradouro, end_numero, end_compl, bairro, municipio,
                 cep, nome_emit, csc, cid_token, qrcode_base_url, certificate_key_path, certificate_path, order_parser,
                 fiscal_parameter_controller, sale_line_util, nfe_builder, versao_ws, synchronous_mode):
        self.mbcontext = mbcontext
        self.initial_order_id = initial_order_id
        self.crt = crt
        self.cnpj_contribuinte = cnpj_contribuinte
        self.inscr_estadual = inscr_estadual
        self.c_uf = c_uf
        self.uf = uf
        self.c_mun_fg = c_mun_fg
        self.mod = mod
        self.serie = serie
        self.ambiente = ambiente
        self.end_logradouro = end_logradouro
        self.end_numero = end_numero
        self.end_compl = end_compl
        self.bairro = bairro
        self.municipio = municipio
        self.cep = cep
        self.nome_emit = nome_emit
        self.csc = csc
        self.cid_token = cid_token
        self.qrcode_base_url = qrcode_base_url
        self.certificate_key = open(certificate_key_path, "rb").read().replace("\r\n", "\n")
        self.certificate_cert = open(certificate_path, "rb").read().replace("\r\n", "\n")
        self.order_parser = order_parser  # type: OrderParser
        self.fiscal_parameter_controller = fiscal_parameter_controller  # type: FiscalParameterController
        self.sale_line_util = sale_line_util  # type: SaleLineUtil
        self.nfe_builder = nfe_builder  # type: NfeBuilder
        self.versao_ws = versao_ws  # type: int
        self.synchronous_mode = synchronous_mode

    def build_request(self, order, contingencia, dh_contingencia, just_contingencia):
        nfe, data_emissao, serie_nota, numero_nota = self._build_nfe(order, contingencia, dh_contingencia, just_contingencia)

        envi_nfe = """<enviNFe versao="%.2f" xmlns="%s"><idLote>%s</idLote><indSinc>%s</indSinc>%s</enviNFe>""" % (
            3.1 if self.versao_ws in (1, 3) else 4,
            NfceRequestBuilder.NAMESPACE_NFE,
            int(round(time.time() * 1000)),
            "1" if self.synchronous_mode else "0",
            nfe)
        if self.versao_ws in (1, 3):
            envelopado = self.envelopa(envi_nfe, "http://www.portalfiscal.inf.br/nfe/wsdl/NfeAutorizacao", self.c_uf)
        else:
            envelopado = self.envelopa(envi_nfe, self.NAMESPACE_AUTORIZACAO_4, self.c_uf, float(self.versao_ws))
        return envelopado, data_emissao, serie_nota, numero_nota

    def build_consulta(self, recibo):
        request = "<consReciNFe versao=\"%.2f\" xmlns=\"%s\"><tpAmb>%s</tpAmb><nRec>%s</nRec></consReciNFe>" % (
            3.1 if self.versao_ws in (1, 3) else 4,
            NfceRequestBuilder.NAMESPACE_NFE,
            self.ambiente,
            recibo)
        if self.versao_ws in (1, 3):
            envelopado = self.envelopa(request, "http://www.portalfiscal.inf.br/nfe/wsdl/NfeRetAutorizacao", self.c_uf)
        else:
            envelopado = self.envelopa(request, self.NAMESPACE_RET_AUTORIZACAO_4, self.c_uf)
        return envelopado

    def envelopa_lote(self, xmls):
        envi_nfe = """<enviNFe versao="%.2f" xmlns="%s"><idLote>%s</idLote><indSinc>%s</indSinc>%s</enviNFe>""" % (
            3.1 if self.versao_ws in (1, 3) else 4,
            NfceRequestBuilder.NAMESPACE_NFE,
            int(round(time.time() * 1000)),
            "1" if self.synchronous_mode else "0",
            xmls)
        if self.versao_ws in (1, 3):
            envelopado = self.envelopa(envi_nfe, "http://www.portalfiscal.inf.br/nfe/wsdl/NfeAutorizacao", self.c_uf)
        else:
            envelopado = self.envelopa(envi_nfe, self.NAMESPACE_AUTORIZACAO_4, self.c_uf, float(self.versao_ws))
        return envelopado

    def _build_nfe(self, order_xml, contingencia, dh_contingencia, just_contingencia):
        # type: (eTree.ElementTree, bool, Optional[datetime], Optional[str]) -> (str, str, unicode, int)
        try:
            order_xml = order_xml.find("Order") if order_xml.find("Order") else order_xml
            order = self.order_parser.parse_order(order_xml)
        except Exception as ex:
            raise FiscalBuildException("Error parsing order: {}".format(ex.message))

        context = {ContextKeys.is_in_contingency: contingencia, ContextKeys.contingency_datetime: dh_contingencia, ContextKeys.contingency_reason: just_contingencia}
        xml = self.nfe_builder.build_xml(order, context)
        data_emissao, serie_nota, numero_nota = [context.get(ContextKeys.data_emissao), self.serie, context.get(ContextKeys.fiscal_number)]

        logger.info("Order {} final {}. Valor {}".format(order.order_id, context.get("nfce_key")[30:], context.get("total_prod")))

        return xml, data_emissao, serie_nota, numero_nota

    @staticmethod
    def formata_data(data):
        # type: (datetime) -> str
        local_zone = tz.tzlocal()
        data = data.replace(tzinfo=local_zone)
        data_str = data.strftime("%Y-%m-%dT%H:%M:%S%z")
        data_str = data_str[:22] + ":" + data_str[22:]
        return data_str

    @staticmethod
    def envelopa(request, namespace, c_uf, versao_ws=3.1):
        prefix = "<?xml version=\"1.0\" encoding=\"UTF-8\"?><Envelope xmlns=\"{0:s}\"><Header><nfeCabecMsg xmlns=\"{1:s}\"><cUF>{2:s}</cUF><versaoDados>{3:.2f}" \
                 "</versaoDados></nfeCabecMsg></Header><Body><nfeDadosMsg xmlns=\"{4:s}\">".format(
            NfceRequestBuilder.NAMESPACE_SOAP, namespace, c_uf, float(versao_ws), namespace)
        suffix = "</nfeDadosMsg></Body></Envelope>"
        return prefix + request + suffix


class NfceProcessor(FiscalProcessor):
    def __init__(self, mbcontext, nfce_request_builder, nfce_request, nfce_autorizador, nfce_contingencia, url_sefaz, fiscal_sent_dir, versao_ws, synchronous_mode):
        # type: (MBEasyContext, NfceRequestBuilder, NfceRequest, NfceAutorizador, NfceContingencia, str, str, int, bool) -> NfceProcessor
        super(NfceProcessor, self).__init__()

        self.mbcontext = mbcontext
        self.nfce_request_builder = nfce_request_builder
        self.nfce_request = nfce_request
        self.nfce_autorizador = nfce_autorizador
        self.nfce_contingencia = nfce_contingencia
        self.fiscal_sent_dir = fiscal_sent_dir
        self.url_sefaz = url_sefaz
        self.versao_ws = versao_ws
        self.synchronous_mode = synchronous_mode

    def request_fiscal(self, posid, order, tenders, paf=False):
        if self.nfce_contingencia:
            contingencia, dh_contingencia, just_contingencia = self.nfce_contingencia.is_contingencia()
        else:
            contingencia, dh_contingencia, just_contingencia = False, None, None

        order_id = order.get("orderId")
        order_id = order_id.zfill(9)

        logger.info("Gerando XML request para order %s" % order.get("orderId"))
        request, data_emissao, serie_nota, numero_nota,  = self.nfce_request_builder.build_request(order, contingencia, dh_contingencia, just_contingencia)  # type: str
        serie_nota = str(serie_nota).zfill(3)
        numero_nota = str(numero_nota).zfill(9)
        dir_arquivo = os.path.join(data_emissao[0:4], data_emissao[5:7], data_emissao[8:10])

        index1 = request.index("<NFe")
        index2 = request.index("</NFe>")
        request2 = request[index1:index2 + 6]

        index1 = request.index("Id=\"NFe")
        nfe_key = request[index1 + 4:index1 + 51]

        response_consulta = None
        dir_enviados = os.path.join(self.fiscal_sent_dir, "Enviados", dir_arquivo)
        nfe_proc = None

        if not contingencia and self.nfce_autorizador:
            request_file = None
            if not os.path.exists(dir_enviados):
                os.makedirs(dir_enviados)

            try:
                logger.info("Consultando SEFAZ para autorizar Order: %s" % order_id)
                self.nfce_autorizador.logger = logger
                request, response_consulta, tentativas = self.nfce_autorizador.autoriza_notas(request, 3)

                logger.info("Resposta da SEFAZ recebida para Order: %s" % order_id)
                logger.info("Order {} Enviada com a chave {}".format(order_id.zfill(9), nfe_key))

            except (ConnectionError, Timeout) as e:
                logger.warning("Entrando em contingencia. Motivo: %s", e)
                justificativa = "Problemas de conexao com a SEFAZ"

                contingencia, dh_contingencia, just_contingencia = self.nfce_contingencia.entra_contingencia(justificativa)
                request, data_emissao, serie_nota, numero_nota,  = self.nfce_request_builder.build_request(order, contingencia, dh_contingencia, just_contingencia)  # type: str

                index1 = request.index("<NFe")
                index2 = request.index("</NFe>")
                request2 = request[index1:index2 + 6]

                index1 = request.index("Id=\"NFe")
                nfe_key = request[index1 + 4:index1 + 51]

                serie_nota = str(serie_nota).zfill(3)
                numero_nota = str(numero_nota).zfill(9)
                dir_arquivo = os.path.join(data_emissao[0:4], data_emissao[5:7], data_emissao[8:10])
                dir_enviados = os.path.join(self.fiscal_sent_dir, "Enviados", dir_arquivo)
                if not os.path.exists(dir_enviados):
                    os.makedirs(dir_enviados)

                request_file = open(os.path.join(dir_enviados, "{0}_{1}_{2}_request_pos{3}_{4}_contingencia.xml".format(serie_nota, numero_nota, order_id, str(posid).zfill(2), nfe_key)), "w+")

            except Exception as ex:
                logger.exception("Erro tratando NFCE")

                dir_erro = os.path.join(self.fiscal_sent_dir, "Erros")
                if not os.path.exists(dir_erro):
                    os.makedirs(dir_erro)
                request_file = open(os.path.join(dir_erro, "{0}_{1}_{2}_request_pos{3}_{4}.xml".format(serie_nota, numero_nota, order_id, str(posid).zfill(2), nfe_key)), "w+")
                raise ex

            finally:
                try:
                    if request_file:
                        request_file.write(request2)
                        request_file.close()
                except Exception as ex:
                    logger.exception("Erro salvando arquivo request pos: %s, orderid: %s, ex: %s", str(posid), order.get("orderId"), ex)

                if response_consulta is not None:
                    if self.versao_ws == 4:
                        signature_namespace = 'http://www.w3.org/2000/09/xmldsig#'
                        xml_namespaces = lxml_etree.fromstring(response_consulta).iter().next().nsmap
                        for namespace in xml_namespaces:
                            if signature_namespace == xml_namespaces[namespace]:
                                response_consulta = response_consulta.replace(namespace + ":", "")
                                response_consulta = response_consulta.replace("<Signature>", '<Signature xmlns="{}">'.format(signature_namespace))

                    try:
                        nfe_proc = "<nfeProc xmlns=\"http://www.portalfiscal.inf.br/nfe\" versao=\"%.2f\">" % (3.1 if self.versao_ws in (1, 3) else 4)
                        index = response_consulta.index("<protNFe")
                        index2 = response_consulta.index("</protNFe>")
                        prot_nfe = response_consulta[index:index2 + 10]
                        nfe_proc += request2 + prot_nfe + "</nfeProc>"

                        with open(os.path.join(dir_enviados, "{0}_{1}_{2}_nfe_proc_pos{3}_{4}.xml".format(serie_nota, numero_nota, order_id, str(posid).zfill(2), nfe_key)), "w+") as nfe_proc_file:
                            nfe_proc_file.write(nfe_proc)
                    except Exception as _:
                        with open(os.path.join(dir_enviados, "{0}_{1}_{2}_response_pos{3}_{4}.xml".format(serie_nota, numero_nota, order_id, str(posid).zfill(2), nfe_key)), "w+") as response_file:
                            response_file.write(response_consulta)
        else:
            request, data_emissao, serie_nota, numero_nota = self.nfce_request_builder.build_request(order, contingencia, dh_contingencia, just_contingencia)  # type: str
            serie_nota = str(serie_nota).zfill(3)
            numero_nota = str(numero_nota).zfill(9)
            dir_arquivo = os.path.join(data_emissao[0:4], data_emissao[5:7], data_emissao[8:10])
            dir_enviados = os.path.join(self.fiscal_sent_dir, "Enviados", dir_arquivo)

            if not os.path.exists(dir_enviados):
                os.makedirs(dir_enviados)

            with open(os.path.join(dir_enviados, "{0}_{1}_{2}_request_pos{3}_{4}_contingencia.xml".format(serie_nota, numero_nota, order_id, str(int(order.get("originatorId")[3:])).zfill(2), nfe_key)), "w+") as request_file:
                request_file.write(request2)

        emissao_date = convert_from_localtime_to_utc(iso8601.parse_date(data_emissao))
        sysactions.get_posot(sysactions.get_model(posid)).setOrderCustomProperty("FISCALIZATION_DATE", emissao_date.strftime("%Y-%m-%dT%H:%M:%S"))

        return request, response_consulta, nfe_proc

    def do_validation(self, get_days_to_expiration=None):
        try:
            encoded_cert = pem.parse(self.nfce_request_builder.certificate_cert)
            cert = x509.load_pem_x509_certificate(str(encoded_cert[0]), default_backend())
            if get_days_to_expiration:
                return True, str((cert.not_valid_after - datetime.now()).days)
            elif cert.not_valid_after > datetime.now():
                return True, "OK"
            else:
                return False, "Certificado da Loja Expirado"
        except Exception as _:
            logger.exception("Falha na Leitura da Validade do Certificado NFCE")
            return False, "Falha na Leitura da Validade do Certificado NFCE"

    def terminate(self):
        if isinstance(self.nfce_contingencia, NfceContingencia):
            self.nfce_contingencia.finaliza()


class NfceStatus(object):
    NfceAutorizada = "100"
    ServicoParalisadoTemporariamento = "108"
    ServicoParalisadoSemPrevisao = "109"
    DuplicidadeNfce = "204"
    ErroInterno = "999"


class NfceAutorizador(object):
    def __init__(self, nfce_request_builder, nfce_request, url_autorizacao, url_ret_autorizacao, versao_ws, max_tentativas_envio_lote, intervalo_retentativa_lote, send_sleep_time, synchronous_mode):
        # type: (NfceRequestBuilder, NfceRequest, str, str, int, int, int, int, bool) -> NfceAutorizador
        self.nfce_request_builder = nfce_request_builder
        self.nfce_request = nfce_request
        self.url_autorizacao = url_autorizacao
        self.url_ret_autorizacao = url_ret_autorizacao
        self.versao_ws = versao_ws
        self.max_tentativas_envio_lote = max_tentativas_envio_lote
        self.intervalo_retentativa_lote = intervalo_retentativa_lote
        self.send_sleep_time = send_sleep_time
        self.synchronous_mode = synchronous_mode
        self.logger = logger

    def autoriza_notas(self, request, max_tentativas, envio_em_lote=False):
        # type: (str, int, bool) -> (str, str, int)

        self.logger.info("Enviando lote para SEFAZ")
        if self.versao_ws not in (1, 3, 4):
            raise AttributeError("Versão WS Inválida. Parâmetros válidos: 1, 3 e 4")

        if self.synchronous_mode:
            self.logger.info("Preparando para envio em modo síncrono...")

        status_code, response = self._envia_lote_com_retentativa(request)

        if status_code == LoteStatus.RecebidoComSucesso or self.synchronous_mode:
            recibo = None
            if not self.synchronous_mode:
                self.logger.info("Lote recebido com sucesso, tentando obter o recibo...")
                recibo = self._busca_recibo(response)
                self.logger.info("Recibo obtido com sucesso")

            response_nfce, tentativas = self._busca_resposta_do_lote(recibo, max_tentativas, envio_em_lote, response)
            return request, response_nfce, tentativas
        else:
            if status_code in (LoteStatus.ServicoParalisadoTemporariamente,
                               LoteStatus.ServicoParalisadoSemPrevisao,
                               LoteStatus.ErroInterno,
                               LoteStatus.ConsumoIndevido):
                error_msg = "SEFAZ Indisponivel - Status: {}".format(status_code)
                self.logger.error(error_msg)
                raise ConnectionError(error_msg)

            error_msg = "Erro ao enviar lote de NFCe. Codigo: {}".format(status_code)
            self.logger.error(error_msg)
            raise LoteException(error_msg, status_code)

    def _envia_lote_com_retentativa(self, request):
        # type: (str) -> (str, Response)
        tentativa_atual = 0
        response = None
        while tentativa_atual < self.max_tentativas_envio_lote:
            # noinspection PyBroadException
            try:
                if self.versao_ws in (1, 3):
                    soap_act = None
                else:
                    soap_act = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeAutorizacao4/nfeAutorizacaoLote"
                response = self.nfce_request.envia_nfce(request, self.url_autorizacao, soap_act)

                if response.status_code == 200:
                    self.logger.info("Resposta do lote recebida")
                    codigo_retorno = remove_xml_namespace(response.content).find(".//retEnviNFe/cStat").text

                    return codigo_retorno, response
                else:
                    self.logger.info("Sefaz retornou status diferente de 200: {0} e content: {1}".format(response.status_code, response.content))

            except Exception as _:
                if response is not None:
                    self.logger.exception("Erro obtendo codigo retorno: StatusCode: {0}, Body: {1}".format(response.status_code, response.content))
                else:
                    self.logger.exception("Erro obtendo codigo retorno")

            tentativa_atual += 1
        else:
            self.logger.info("Falha ao enviar lote. Excedido numero de tentativas")
            return "999", None

    def _busca_recibo(self, response):
        # type: (Response) -> str

        # Lote foi recebido para processamento com sucesso, vamor pegar o recibo e inicar a consulta
        try:
            xml = remove_xml_namespace(response.content)
            return xml.find(".//infRec/nRec").text
        except Exception:
            error_msg = "Erro ao obter o recibo da NFCe"
            self.logger.exception(error_msg)
            raise FiscalException(error_msg)

    def _busca_resposta_do_lote(self, recibo, max_tentativas, envio_de_lote, resposta_lote):
        # type: (str, int, bool, Response) -> (str, int)

        processado = False
        tentativas = 0

        while not processado and (max_tentativas == -1 or tentativas < max_tentativas):
            try:
                if self.synchronous_mode:
                    response_consulta = resposta_lote
                else:
                    request_consulta = self.nfce_request_builder.build_consulta(recibo)

                    self.logger.info("Consultando status do lote na SEFAZ")
                    if self.versao_ws in (1, 3):
                        soap_act = None
                    else:
                        soap_act = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRetAutorizacao4/nfeAutorizacaoLote"

                    time.sleep(1)  # Tempo aguardando status ser processado antes de tentar obter seu status

                    response_consulta = self.nfce_request.envia_nfce(request_consulta, self.url_ret_autorizacao, soap_act)

                if response_consulta and response_consulta.status_code == 200:
                    nfce_response_xml = eTree.XML(response_consulta.content)
                    status_consulta = self._busca_status_consulta(nfce_response_xml)
                else:
                    if not response_consulta:
                        self.logger.error("Sem resposta da sefaz")
                    else:
                        self.logger.info("Sefaz retornou status diferente de 200: {0} e content: {1}".format(response_consulta.status_code, response_consulta.content))
                    time.sleep(self.intervalo_retentativa_lote)
                    continue
            except Timeout:
                self.logger.exception("Exceção processando o lote, retentando")
                time.sleep(self.send_sleep_time)
                continue
            except Exception as _:
                self.logger.exception("Exceção processando o lote, retentando")
                time.sleep(self.intervalo_retentativa_lote)
                continue
            finally:
                tentativas += 1

            if status_consulta == LoteConsultaStatus.LoteEmProcessamento:
                self.logger.info("Lote ainda não processado. Aguardando processamento... Tentativa: %d - Status: %s" % (tentativas, status_consulta))
                time.sleep(self.intervalo_retentativa_lote)
                continue

            if status_consulta == LoteConsultaStatus.ConsumoIndevido:
                self.logger.error("Falha ao obter status da NFCe. SEFAZ Error 656 - Consumo Indevido")
                raise ConnectionError("Falha ao obter status da NFCe. SEFAZ Error 656 - Consumo Indevido")

            if status_consulta == LoteConsultaStatus.LoteProcessado:
                self.logger.info("Lote ja processado, verificando status do processamento da NFCE")
                if envio_de_lote:
                    return response_consulta.content, tentativas

                self._verifica_status_processamento_nfce(nfce_response_xml)
                return eTree.tostring(nfce_response_xml), tentativas

            if status_consulta == LoteConsultaStatus.ErroInterno:
                msg = "Erro interno não identificado ao tentar obter o status do lote na sefaz. 999 - Erro Interno"
                self.logger.error(msg)
                raise ConnectionError(msg)

            else:
                self.logger.error("Erro ao consultar status do lote NFCe. Codigo: %s", str(status_consulta))
                raise LoteException("Erro ao consultar status do lote NFCe. Codigo: %s" % str(status_consulta), status_consulta)
            
        self.logger.error("Falha ao obter status da NFCe. Excedido Numero de Tentativas")
        raise ConnectionError("Falha ao obter status da NFCe. Excedido Numero de Tentativas")

    def _busca_status_consulta(self, response_consulta_xml):
        # type: (eTree) -> str
        try:
            xml = remove_xml_namespace(eTree.tostring(response_consulta_xml))
            if self.synchronous_mode:
                c_stat = xml.find(".//retEnviNFe/cStat").text
            else:
                c_stat = xml.find(".//retConsReciNFe/cStat").text

            logger.info("Resposta da consulta de lote obtida")
            return c_stat

        except Exception as ex:
            logger.exception("Erro obtendo status consulta: {0}".format(eTree.tostring(response_consulta_xml)))
            raise ex

    @staticmethod
    def _verifica_status_processamento_nfce(response_consulta_xml):
        # type: (eTree) -> None
        response_consulta = eTree.tostring(response_consulta_xml)
        try:
            xml = remove_xml_namespace(response_consulta)

            status_nfce = xml.find(".//infProt/cStat").text
            x_motivo = xml.find(".//infProt/xMotivo").text if xml.find(".//infProt/xMotivo") is not None else None
        except Exception as ex:
            logger.exception("Erro obtendo status protocolo. ResponseXML: {0}".format(response_consulta))
            raise ex

        if x_motivo is None:
            x_motivo = ""
            logger.error("Nao foi possivel encontrar xMotivo: {}".format(response_consulta))

        if status_nfce == NfceStatus.NfceAutorizada:
            logger.info("Protocolo processado com sucesso, finalizado")
            return

        if status_nfce in (NfceStatus.ServicoParalisadoTemporariamento, NfceStatus.ServicoParalisadoSemPrevisao, NfceStatus.ErroInterno):
            logger.error("SEFAZ Indisponivel - Entrando em Contingencia - Status: %s ", status_nfce)
            raise ConnectionError("SEFAZ Indisponivel - Entrando em Contingencia - Status: %s" % status_nfce)
        elif status_nfce == NfceStatus.DuplicidadeNfce:
            logger.info("204 retornado mas mesma nota presente. Vamos aceitar")
        else:
            x_motivo = _remove_accents(x_motivo)
            logger.error("NFCe Nao Autorizada. Status: %s. Motivo: %s", status_nfce, x_motivo)
            raise FiscalException("NFCe Nao Autorizada. Status: %s" % status_nfce, x_motivo)

    @staticmethod
    def _verifica_mesma_nota(response_xml):
        # type: (eTree) -> bool
        try:
            xml = remove_xml_namespace(eTree.tostring(response_xml))
            chave_atual = xml.find(".//infProt/chNFe").text
            x_motivo = xml.find(".//infProt/xMotivo").text

            index = x_motivo.find("[chNFe: ")
            chave_original = x_motivo[index + 8:index + 8 + 44]

            return chave_atual == chave_original

        except Exception as _:
            logger.exception("Erro verificando mesma nota. Xml: " + eTree.tostring(response_xml))
            return False


class NfceConnectivityTester(object):
    def __init__(self, nfce_request, url_status_servico, c_uf, versao_ws):
        self.nfce_request = nfce_request
        self.url_status_servico = url_status_servico
        self.c_uf = c_uf
        self.versao_ws = versao_ws
        self.logger = logger
        self.last_test = None
        self.last_connection_status = False

    def test_connectivity(self):
        if self.last_test and self.last_test > datetime.now() - timedelta(minutes=3):
            return self.last_connection_status

        envi_nfe = """<enviNFe versao="%.2f" xmlns="%s"></enviNFe>""" % (3.1 if self.versao_ws in (1, 3) else 4, NfceRequestBuilder.NAMESPACE_NFE)
        namespace = "http://www.portalfiscal.inf.br/nfe/wsdl/NfeStatusServico2" if self.versao_ws in (1, 3) else "http://www.portalfiscal.inf.br/nfe/wsdl/NFeStatusServico4"
        envelopado = NfceRequestBuilder.envelopa(envi_nfe, namespace, self.c_uf, 3.1 if self.versao_ws in (1, 3) else 4)
        soap_action = None if self.versao_ws in (1, 3) else "http://www.portalfiscal.inf.br/nfe/wsdl/NFeStatusServico4/nfeStatusServicoNF"
        has_connection = False
        try:
            resp = self.nfce_request.envia_nfce(envelopado, self.url_status_servico, soap_action)
            has_connection = resp.status_code == 200
            if has_connection:
                self.logger.info("Sucesso no teste de conexão com a sefaz")
            return has_connection
        except Exception as _:
            self.logger.exception("Falha no teste de conexão com a sefaz")
            return has_connection
        finally:
            self.last_connection_status = has_connection
            self.last_test = datetime.now()


class NfceSituationChecker(object):
    def __init__(self, nfce_request, url_consultar_situacao, ambiente, c_uf, versao_ws):
        self.nfce_request = nfce_request
        self.url_consultar_situacao = url_consultar_situacao
        self.ambiente = ambiente
        self.c_uf = c_uf
        self.versao_ws = versao_ws
        self.logger = logger

    def check_situation_nfe(self, nfe, timeout=None):
        cons_nfe =  """<consSitNFe xmlns="http://www.portalfiscal.inf.br/nfe" versao="%.2f"><tpAmb>%s</tpAmb><xServ>CONSULTAR</xServ><chNFe>%s</chNFe></consSitNFe>""" % (3.1 if self.versao_ws in (1, 3) else 4, self.ambiente, nfe)
        namespace = NfceRequestBuilder.NAMESPACE_CONSULTA_SITUACAO if self.versao_ws in (1, 3) else NfceRequestBuilder.NAMESPACE_CONSULTA_SITUACAO_4
        envelopado = NfceRequestBuilder.envelopa(cons_nfe, namespace, self.c_uf)
        soap_action = NfceRequestBuilder.NAMESPACE_CONSULTA_SITUACAO if self.versao_ws in (1, 3) else "http://www.portalfiscal.inf.br/nfe/wsdl/NFeConsultaProtocolo4/nfeConsultaNF"

        try:
            resp = self.nfce_request.envia_nfce(envelopado, self.url_consultar_situacao, soap_action, timeout)
            if resp.status_code == 200:
                return resp.text
            else:
                msg = "Erro ao consultar situação NFe - Code: {0} / Content: {1}".format(resp.status_code, resp.content)
                self.logger.error(msg)
        except Exception as _:
            msg = "Erro ao consultar situacao NFe"
            self.logger.exception(msg)


class NfceContingencia:
    def __init__(self, mbcontext, nfce_request_builder, nfce_autorizador, versao_ws, nfce_situation_checker, fiscal_sent_dir, max_tantavivas_envio_contingencia, synchronous_mode, nfce_connectivity_tester):
        # type: (MBEasyContext, NfceRequestBuilder, NfceAutorizador, int, NfceSituationChecker, unicode, int, bool, NfceConnectivityTester) -> NfceContingencia
        self.mbcontext = mbcontext
        self.nfce_request_builder = nfce_request_builder
        self.nfce_aurotizador = nfce_autorizador
        self.versao_ws = versao_ws
        self.thread_condition = Condition()
        self.contingencia_lock = Lock()
        self.contingencia = False
        self.dh_contingencia = None
        self.just_contingencia = None
        self.running = True
        self.max_tentativas = 1
        self.contingencia_thread = None
        self.nfce_situation_checker = nfce_situation_checker
        self.fiscal_sent_dir = fiscal_sent_dir
        self.force_contingency = False
        self.process_now = False
        self.max_tantavivas_envio_contingencia = max_tantavivas_envio_contingencia
        self.synchronous_mode = synchronous_mode
        self.initial_batch_size = 50 if not self.synchronous_mode else 1
        self.batch_size = self.initial_batch_size
        self.wait_for_start = False
        self.nfce_connectivity_tester = nfce_connectivity_tester

    def start_contingencia(self):
        with FiscalDataRepository(self.mbcontext) as fiscalrepository:
            with self.contingencia_lock:
                if fiscalrepository.get_count_nfce_orders_to_send() == 0 and self.force_contingency is False:
                    self.contingencia = False
                else:
                    self.contingencia = True
                    self.dh_contingencia = datetime.now()
                    self.just_contingencia = "Notas anteriores em contingencia"

        if self.versao_ws not in (1, 3, 4):
            raise Exception("Versão WS Inválida. Parâmetros válidos: 1, 3 e 4")

        self.contingencia_thread = Thread(target=self._processa_contingencia)
        self.contingencia_thread.daemon = True
        self.contingencia_thread.start()

    def is_contingencia(self):
        with self.contingencia_lock:
            return self.contingencia, self.dh_contingencia, self.just_contingencia

    def entra_contingencia(self, justificativa):
        with self.contingencia_lock:
            self.contingencia = True
            self.dh_contingencia = datetime.now()
            self.just_contingencia = justificativa
            with self.thread_condition:
                loggerThread.info("Entrando em contingência...")
                self.wait_for_start = True
                self.thread_condition.notifyAll()

            return self.contingencia, self.dh_contingencia, self.just_contingencia

    def finaliza(self):
        if self.running:
            self.thread_condition.acquire()
            self.running = False
            self.thread_condition.notifyAll()
            self.thread_condition.release()

    def _processa_contingencia(self):
        count = 0
        dir_enviados = os.path.join(self.fiscal_sent_dir, "Enviados")

        while self.running:
            try:
                if self.force_contingency:
                    loggerThread.info("Contingência forçada está ativa. Não tentaremos envio a SEFAZ no momento")
                    return

                self.nfce_connectivity_tester.logger = loggerThread
                connection_working = self.nfce_connectivity_tester.test_connectivity()
                if not connection_working:
                    self._wait(300)
                    continue

                if self.process_now is False and self.contingencia is False and count < 60:
                    self.thread_condition.acquire()
                    self.thread_condition.wait(5)
                    self.thread_condition.release()

                    count += 1
                    continue

                # No release da thread, vamos aguardar para nao tratar uma order que ainda nao esta preparada
                if self.wait_for_start:
                    time.sleep(5)

                self.wait_for_start = False

                count = 0
                with FiscalDataRepository(self.mbcontext) as fiscalrepository:
                    orders_to_send = fiscalrepository.get_nfce_orders_to_send(self.batch_size)
                    qty_orders_selected = len(orders_to_send)

                    if self.synchronous_mode:
                        loggerThread.info("Modo síncrono ativado. Vamos processar pedidos individualmente")
                    else:
                        loggerThread.info("Encontradas {} orders para serem enviadas. Tamanho do lote: {}".format(qty_orders_selected, self.batch_size))

                    if orders_to_send:
                        all_nfces = ""

                        for order_to_send in orders_to_send[:]:
                            try:
                                xml_order_pict = eTree.fromstring(base64.b64decode(order_to_send.order_picture))
                                xml_order_pict = xml_order_pict.find(".//Order") if xml_order_pict.find(".//Order") else xml_order_pict
                                order_state = xml_order_pict.attrib["state"]
                                if order_state != "PAID":
                                    msg = "Order {} nao contém status PAID. Status da order: {}".format(order_to_send.order_id, order_state)
                                    loggerThread.error(msg)
                                    raise Exception(msg)
                            except TypeError as _:
                                loggerThread.error("Erro tratando OrderPicture para order: {}. Vamos tentar regera-lo".format(order_to_send.order_id))

                                try:
                                    time.sleep(2)  # Vamos aguardar a order ser atualizada no banco
                                    order_pict = OrderTaker().get_order_picture(order_to_send.pos_id, order_to_send.order_id)
                                    fiscalrepository.set_order_picture(order_to_send.order_id, base64.b64encode(order_pict))
                                    loggerThread.info("Novo OrderPicture foi gerado com sucesso para order: {}".format(order_to_send.order_id))
                                    order_state = eTree.fromstring(order_pict).attrib["state"]

                                    if order_state != "PAID":
                                        loggerThread.error("Order {} nao contém status PAID. Status da order: {}. Marcando como -999".format(order_to_send.order_id, order_state))
                                        orders_to_send.remove(order_to_send)
                                        fiscalrepository.set_nfce_sent(order_to_send.order_id, -999)
                                        continue

                                except Exception as _:
                                    loggerThread.exception("Erro tentando obter novo OrderPicture! Marcando order {} como invalida.".format(order_to_send.order_id))
                                    fiscalrepository.set_nfce_sent(order_to_send.order_id, -1)
                                    orders_to_send.remove(order_to_send)
                                    continue

                            except Exception as _:
                                loggerThread.info("Order antiga e/ou sem referencia: {}".format(_.message))
                                fiscalrepository.set_nfce_sent(order_to_send.order_id, -1)
                                orders_to_send.remove(order_to_send)
                                continue

                            xml_base64 = order_to_send.xml
                            xml_string = base64.b64decode(xml_base64)
                            all_nfces += xml_string
                            order_to_send.xml = xml_string

                        if not orders_to_send or not all_nfces:
                            loggerThread.info("Nenhuma nota a ser processada. Vamos tentar obter novas notas.")
                            continue
                        else:
                            loggerThread.info("Quantidade de notas a serem processadas: {}".format(len(orders_to_send)))
                            orders_to_send = sorted(orders_to_send, key=lambda x: int(x.order_id))

                        envelopado = self.nfce_request_builder.envelopa_lote(all_nfces)
                        try:
                            self.nfce_aurotizador.logger = loggerThread
                            request, response, tentativas = self.nfce_aurotizador.autoriza_notas(envelopado, self.max_tantavivas_envio_contingencia, True)
                        except LoteException:
                            if not self.synchronous_mode and self.batch_size == self.initial_batch_size:
                                # Se estamos processando um lote inteiro e tivemos algum problema, vamos processar nota a nota
                                self.batch_size = 1
                                loggerThread.info("Problemas com o lote - Enviando XMLs individualmente")
                            else:
                                # Estamos processando uma unica nota e tivemos problemas, marcamos ela como problema e pegamos a próxima
                                fiscalrepository.set_nfce_sent(orders_to_send[0].order_id, -1)
                                loggerThread.info("Marcando XML da order {} como invalido".format(orders_to_send[0].order_id))
                                # Vamos esperar alguns segundos para enviar a proxima nota afim de nao receber 656 da SEFAZ
                                time.sleep(10)

                            # De qualquer maneira, vamos selecionar novas notas para enviar
                            continue

                        except ConnectionError:
                            loggerThread.info("Problemas de Conexao - Aguardando 5 minutos para tentar novamente")
                            self._wait(300)
                            continue

                        protocolos_notas = []
                        try:
                            response_xml = remove_xml_namespace(response)
                            loggerThread.info("Notas processadas com sucesso. Verificando protocolos")
                            protocolos_notas = response_xml.findall(".//infProt")
                        except Exception as _:
                            loggerThread.exception("Erro obtendo protocolo - Response: {}".format(response))

                        loggerThread.info("Quantidade de protocolos a serem processados: {}".format(len(protocolos_notas)))
                        for protocolo in protocolos_notas:
                            try:
                                chave_protocolo = protocolo.find(".//chNFe").text

                                for order in orders_to_send:
                                    order_id = order.order_id.zfill(9)
                                    loggerThread.info("Order a ser processada: {}".format(order_id))
                                    order_xml = remove_xml_namespace(order.xml)
                                    nfe_key = order_xml.find(".//infNFe").attrib['Id']
                                    chave_xml = nfe_key[3:]

                                    if chave_xml == chave_protocolo:
                                        data_emissao = order_xml.find(".//ide/dhEmi").text
                                        serie_nota = order_xml.find(".//ide/serie").text
                                        serie_nota = serie_nota.zfill(3)
                                        numero_nota = order_xml.find(".//ide/nNF").text
                                        numero_nota = numero_nota.zfill(9)
                                        dir_arquivo = os.path.join(data_emissao[0:4], data_emissao[5:7], data_emissao[8:10])
                                        dir_nota = os.path.join(dir_enviados, dir_arquivo)

                                        if not os.path.exists(dir_nota):
                                            os.makedirs(dir_nota)

                                        stat = protocolo.find(".//cStat").text
                                        loggerThread.info("Protocolo encontrado para nota %s; Order: %s; Status: %s", chave_protocolo, order_id, stat)

                                        if stat in ("100", "204", "704", "539", "150", "635"):  # 100 = ok; 204, 539 = duplicidade (ja estava ok); 150 = ok, atrasada;
                                            eTree.register_namespace('', NfceRequestBuilder.NAMESPACE_NFE)

                                            if stat == "539":
                                                try:
                                                    loggerThread.info("Preparando pedido [{}] para ser enviada novamente na próxima tentantiva".format(order_id))
                                                    order_picture = eTree.XML(base64.b64decode(order.order_picture + "=" * ((4 - len(order.order_picture) % 4) % 4)))
                                                    envelopado, data_emissao, serie_nota, numero_nota = self.nfce_request_builder.build_request(order_picture, False, None, None)
                                                    index1 = envelopado.index("<NFe")
                                                    index2 = envelopado.index("</NFe>")
                                                    new_req = envelopado[index1:index2 + 6]
                                                    xml_base64 = base64.b64encode(new_req)
                                                    order.xml = new_req
                                                    loggerThread.info("Marcando pedido [{}] como pendente de envio".format(order_id))
                                                    fiscalrepository.set_nfce_sent_with_xml(order_id, xml_base64, 0)

                                                except FiscalBuildException as _:
                                                    loggerThread.info("Erro montando XML order: [{}] - Buscando Order Picture".format(order.order_id))
                                                    order_picture = OrderTaker().get_order_picture(order.pos_id, order.order_id)
                                                    fiscalrepository.set_order_picture(order.order_id, base64.b64encode(order_picture))

                                                except FiscalException as _:
                                                    loggerThread.info("Marcando XML nota [{}] como invalido".format(order.order_id))
                                                    fiscalrepository.set_nfce_sent(order.order_id, -1)

                                                except Exception as _:
                                                    loggerThread.exception("Erro ao gerar XML da order [{}]".format(order_id))
                                                    fiscalrepository.set_nfce_sent(order.order_id, -1)

                                                break

                                            if stat == "635":
                                                loggerThread.info("Recebemos 635, vamos esgotar as tentativas e aguardar para tentar novamente.")
                                                tentativas = self.max_tentativas + 1
                                                break

                                            if stat in ("204", "704"):
                                                nfe_key = order_xml.find(".//infNFe").attrib['Id']
                                                chave_xml = nfe_key[3:]

                                                # Vamos esperar alguns segundos para checar a situacao da nota afim de nao receber 656 da SEFAZ
                                                retry = 0
                                                fiscal_data = None
                                                while retry < 3:
                                                    time.sleep(5)
                                                    self.nfce_situation_checker.logger = loggerThread
                                                    fiscal_data = self.nfce_situation_checker.check_situation_nfe(chave_xml, timeout=5)
                                                    retry += 1

                                                if not fiscal_data:
                                                    loggerThread.error("Problemas ao tentar consultar a situação da nota na sefaz. "
                                                                       "Vamos tentar novamente depois.")
                                                    break

                                                fiscal_data_xml = remove_xml_namespace(fiscal_data.encode("utf8"))
                                                c_stat = fiscal_data_xml.find(".//retConsSitNFe/cStat")

                                                if c_stat is None:
                                                    loggerThread.error("Campo cStat nao encontrado ou vazio")
                                                    break

                                                c_stat = c_stat.text

                                                loggerThread.info("Protocolo recebido. OrderId: {}; cStat: {}".format(order_id, c_stat))

                                                if c_stat in ("100", "150"):
                                                    inf_prot = fiscal_data_xml.find(".//protNFe/infProt")
                                                    inf_prot.attrib.pop("Id", None)
                                                    protocolo = inf_prot
                                                else:
                                                    fiscalrepository.set_nfce_sent(order.order_id, -1)
                                                    break

                                            nfce_wt_resp = "<nfeProc versao=\"{0:.2f}\" xmlns=\"{1}\">{2}<protNFe versao=\"{0:.2f}\">{3}</protNFe></nfeProc>"\
                                                .format(3.1 if self.versao_ws in (1, 3) else 4, NfceRequestBuilder.NAMESPACE_NFE, order.xml, eTree.tostring(protocolo))

                                            nfce_file_name = "{0}_{1}_{2}_nfe_proc_pos{3}_{4}.xml".format(serie_nota, numero_nota, order_id, str(order.pos_id).zfill(2), nfe_key)

                                            for xml_file in glob.glob(dir_nota + '/*_' + numero_nota + "_" + order_id.zfill(9) + '_request_pos*'):
                                                os.remove(xml_file)

                                            with open(os.path.join(dir_nota, nfce_file_name), "w+") as nfe_proc_file:
                                                nfe_proc_file.write(nfce_wt_resp)

                                            xml_base64 = base64.b64encode(nfce_wt_resp)
                                            fiscalrepository.set_nfce_sent_with_xml(order.order_id, xml_base64, 1)

                                        elif stat not in ("108", "109", "635", "999"):
                                            loggerThread.error("Nota com status desconhecido, vamos invalida-la. Status: {}".format(stat))
                                            fiscalrepository.set_nfce_sent(order.order_id, -1)

                                        orders_to_send.remove(order)
                                        break
                            except Exception as _:
                                loggerThread.exception("Erro tratando protocolo: {}".format(eTree.tostring(protocolo)))
                                continue

                        if tentativas > self.max_tentativas:
                            loggerThread.info("SEFAZ lenta. Não vamos sair da contingência. Aguardando 5 minutos para tentar novamente")
                            self._wait(300)
                            continue

                    # Todas as orders foram enviadas. Vamos verificar se ainda estamos em contingencia
                    if qty_orders_selected < self.batch_size and self.force_contingency is False:
                        # Da ultima vez enviamos menos do que o esperado, verificamos se podemos sair da contingencia
                        with self.contingencia_lock:
                            if fiscalrepository.get_count_nfce_orders_to_send() == 0:
                                loggerThread.info("Saindo da contingencia")
                                self.batch_size = self.initial_batch_size
                                self.contingencia = False

                    if self.synchronous_mode and self.contingencia:
                        time.sleep(1)
                        self.process_now = True
                    else:
                        self.process_now = False
            except Exception as _:
                loggerThread.exception("Erro tratando notas em contingencia")
                self._wait(5)

    def _wait(self, wait_time):
        self.thread_condition.acquire()
        self.thread_condition.wait(wait_time)
        self.thread_condition.release()


class LoteException(Exception):
    def __init__(self, message, error_code):
        super(LoteException, self).__init__()
        self.message = message
        self.error_code = error_code

    def __str__(self):
        return "LoteException Error Code: {0}\\Message: {1}.".format(self.error_code, self.message)


class LoteStatus(object):
    RecebidoComSucesso = "103"
    ServicoParalisadoTemporariamente = "108"
    ServicoParalisadoSemPrevisao = "109"
    ConsumoIndevido = "656"
    ErroInterno = "999"


class LoteConsultaStatus(object):
    LoteProcessado = "104"
    LoteEmProcessamento = "105"
    LoteComFalhaSchema = "225"
    ConsumoIndevido = "656"
    ErroInterno = "999"


class FiscalException(Exception):
    def __init__(self, message, motivo=None):
        # type: (str, str) -> None
        super(FiscalException, self).__init__()
        self.message = message
        self.motivo = motivo

    def __str__(self):
        ret = "FiscalException: " + self.message + "."
        if self.motivo is not None:
            ret += " Motivo: " + self.motivo + "."

        return ret

class FiscalBuildException(Exception):
    def __init__(self, message, motivo=None):
        # type: (str, str) -> None
        super(FiscalBuildException, self).__init__()
        self.message = message
        self.motivo = motivo

    def __str__(self):
        ret = "FiscalBuildException: " + self.message + "."
        if self.motivo is not None:
            ret += " Motivo: " + self.motivo + "."

        return ret


def _remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', unicode(text)) if unicodedata.category(c) != 'Mn')
