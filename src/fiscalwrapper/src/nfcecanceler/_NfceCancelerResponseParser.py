# -*- coding: utf-8 -*-

import sys

from xml.etree import cElementTree as eTree
from nfcecanceler import NfceCancelerResponse, NfceCancelerResponseParserException


class NfceCancelerResponseParser(object):
    NAMESPACE_SOAP = "http://www.w3.org/2003/05/soap-envelope"
    NAMESPACE_NFE = "http://www.portalfiscal.inf.br/nfe"
    NAMESPACE_RET_CANCELER = "http://www.portalfiscal.inf.br/nfe/wsdl/RecepcaoEvento"
    NAMESPACE_RET_CANCELER_4 = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeRecepcaoEvento4"

    def parse_response(self, response_str, versao_ws):
        # type: (str, int) -> NfceCancelerResponse
        try:
            response_xml = eTree.XML(response_str)
            if versao_ws in (1, 3):
                namespace_canceler = self.NAMESPACE_RET_CANCELER
                tag_result = "nfeRecepcaoEventoResult"
            else:
                namespace_canceler = self.NAMESPACE_RET_CANCELER_4
                tag_result = "nfeResultMsg"
            c_stat = response_xml.find("{{{0}}}Body/{{{1}}}{2}/{{{3}}}retEnvEvento/{{{3}}}retEvento/{{{3}}}infEvento/{{{3}}}cStat"
                                       .format(NfceCancelerResponseParser.NAMESPACE_SOAP,
                                               namespace_canceler,
                                               tag_result,
                                               NfceCancelerResponseParser.NAMESPACE_NFE)).text

            x_motivo = response_xml.find("{{{0}}}Body/{{{1}}}{2}/{{{3}}}retEnvEvento/{{{3}}}retEvento/{{{3}}}infEvento/{{{3}}}xMotivo"
                                         .format(NfceCancelerResponseParser.NAMESPACE_SOAP,
                                                 namespace_canceler,
                                                 tag_result,
                                                 NfceCancelerResponseParser.NAMESPACE_NFE)).text

            n_prot_node = response_xml.find("{{{0}}}Body/{{{1}}}{2}/{{{3}}}retEnvEvento/{{{3}}}retEvento/{{{3}}}infEvento/{{{3}}}nProt"
                                            .format(NfceCancelerResponseParser.NAMESPACE_SOAP,
                                                    namespace_canceler,
                                                    tag_result,
                                                    NfceCancelerResponseParser.NAMESPACE_NFE))

            n_prot = None
            if n_prot_node is not None:
                n_prot = n_prot_node.text

            return NfceCancelerResponse(c_stat, x_motivo, n_prot)
        except Exception as ex:
            error_message = "Erro parseando XML de response: {0}".format(repr(ex)), sys.exc_info()[2]
            raise NfceCancelerResponseParserException(error_message)
